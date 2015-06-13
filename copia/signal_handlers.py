from prospere.contrib.cabinet import signals as cabinet_signals
from django.core.exceptions import ObjectDoesNotExist

'''
Cabinet
'''
def delete_comment(sender, document_id, **kwargs):
    from prospere.contrib.comment.models import Comments
    from django.contrib.contenttypes.models import ContentType
    from prospere.contrib.cabinet.models import Documents

    content_type = ContentType.objects.get_for_model(Documents)
    Comments.objects.filter(object_pk = document_id, content_type = content_type).delete()

def password_changed(sender, user_id, **kwargs):
    #user_id = kwargs["user_id"]
    from django.contrib.sessions.models import Session
    from models import SessionBonds
    try:
        bond = SessionBonds.objects.get(user = user_id)
        Session.objects.filter(session_key = bond.session_key).delete()
    except ObjectDoesNotExist:
        return

cabinet_signals.document_deleted.connect(delete_comment)
cabinet_signals.user_password_changed.connect(password_changed)

