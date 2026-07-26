import json
import os
from typing import List, Dict

from django.db import transaction
from openai import OpenAI

from .models import Node, Edge


def extract_entities_and_relationships(text: str) -> Dict:
    """
    Uses OpenAI to extract entities and their relationships from text.
    Returns a dictionary with 'nodes' and 'edges'.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"nodes": [], "edges": []}

    client = OpenAI(api_key=api_key)
    
    system_prompt = (
        "You are an expert at knowledge graph extraction. Extract key entities and their relationships from the provided text. "
        "Entities must be one of: person, project, company, technology, topic, concept. "
        "Relationships must be one of: works_on, uses, belongs_to, references, related_to. "
        "Return the result ONLY as a JSON object with 'nodes' (title, type, description) and 'edges' (source, target, type, description)."
    )
    
    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Extraction error: {e}")
        return {"nodes": [], "edges": []}


@transaction.atomic
def process_document_for_graph(user, document):
    """
    Processes a document to extract and save graph nodes and edges.
    """
    # Use existing extraction logic to get full text
    from documents.services.extraction import extract_document_text
    
    try:
        full_text = extract_document_text(document)
        # For large documents, we might want to process in chunks, 
        # but for MVP we'll take a significant slice or the whole text if it fits.
        # Let's take the first 4000 chars for now.
        sample_text = full_text[:4000]
        
        extracted_data = extract_entities_and_relationships(sample_text)
        
        nodes_created = []
        for node_data in extracted_data.get("nodes", []):
            node, created = Node.objects.get_or_create(
                owner=user,
                title=node_data["title"][:255],
                node_type=node_data.get("type", "topic"),
                defaults={
                    "description": node_data.get("description", ""),
                }
            )
            node.source_documents.add(document)
            nodes_created.append(node)
            
        for edge_data in extracted_data.get("edges", []):
            try:
                source_node = Node.objects.get(owner=user, title=edge_data["source"])
                target_node = Node.objects.get(owner=user, title=edge_data["target"])
                
                Edge.objects.get_or_create(
                    owner=user,
                    source=source_node,
                    target=target_node,
                    relationship_type=edge_data.get("type", "related_to"),
                    defaults={
                        "description": edge_data.get("description", ""),
                    }
                )
            except Node.DoesNotExist:
                continue
                
        return True
    except Exception as e:
        print(f"Graph processing error: {e}")
        return False
