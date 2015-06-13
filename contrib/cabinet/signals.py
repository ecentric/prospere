from django.dispatch import Signal

user_password_changed = Signal(providing_args=["user_id"])
document_deleted = Signal(providing_args=["document_id"])
document_created = Signal(providing_args=["document_id"])

