from django.dispatch import Signal


# A new bookmark was added.
bookmark_added = Signal(providing_args=["request", "type", "object"])

# A bookmark was deleted.
bookmark_deleted = Signal(providing_args=["request", "type", "object"])
