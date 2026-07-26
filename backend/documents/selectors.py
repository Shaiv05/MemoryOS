from .models import Document


def documents_for_user(user):
    return Document.objects.filter(owner=user)
