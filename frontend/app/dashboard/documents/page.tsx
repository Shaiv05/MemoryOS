"use client";

import { useEffect, useState } from "react";
import Sidebar from "@/components/layout/Sidebar";
import DocumentForm from "@/components/documents/DocumentForm";
import DocumentList from "@/components/documents/DocumentList";
import { useAuth } from "@/hooks/useAuth";
import {
  createDocument,
  deleteDocument,
  getDocuments,
  reprocessDocument,
} from "@/services/documents";
import type { CreateDocumentInput, Document } from "@/types/document";

const getErrorMessage = (error: unknown) => {
  const response = (
    error as {
      response?: { data?: { detail?: string; non_field_errors?: string[] } };
    }
  ).response;

  return (
    response?.data?.detail ||
    response?.data?.non_field_errors?.[0] ||
    "Document action failed."
  );
};

export default function DocumentsPage() {
  const { token } = useAuth({ required: true });
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    if (!token) return;

    let ignore = false;
    getDocuments()
      .then((data) => {
        if (!ignore) {
          setDocuments(data);
          setLoading(false);
        }
      })
      .catch((err: unknown) => {
        if (!ignore) {
          setError(getErrorMessage(err));
          setLoading(false);
        }
      });

    return () => {
      ignore = true;
    };
  }, [token, refreshKey]);

  const refreshDocuments = () => {
    setLoading(true);
    setRefreshKey((current) => current + 1);
  };

  const handleCreate = async (input: CreateDocumentInput) => {
    setSaving(true);
    setError("");

    try {
      await createDocument(input);
      refreshDocuments();
    } catch (err: unknown) {
      setError(getErrorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: number) => {
    setError("");
    await deleteDocument(id);
    refreshDocuments();
  };

  const handleReprocess = async (id: number) => {
    setError("");
    await reprocessDocument(id);
    refreshDocuments();
  };

  if (!token) return null;

  return (
    <div className="flex min-h-screen bg-black text-white">
      <Sidebar />

      <main className="flex-1 p-8">
        <div className="max-w-5xl">
          <h1 className="mb-8 text-4xl font-bold">Documents</h1>

          <DocumentForm onSubmit={handleCreate} loading={saving} />

          {error && (
            <p className="mb-6 rounded border border-red-900/60 bg-red-950/60 p-3 text-sm text-red-300">
              {error}
            </p>
          )}

          {loading ? (
            <p className="text-zinc-400">Loading...</p>
          ) : (
            <DocumentList
              documents={documents}
              onDelete={handleDelete}
              onReprocess={handleReprocess}
            />
          )}
        </div>
      </main>
    </div>
  );
}
