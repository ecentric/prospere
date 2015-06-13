def vote_document(document, score):
    from decimal import Decimal
    from models import Documents

    if type(document) == int or type(document) == long:
        document = Documents.objects.get(id = int(document))
    document.mark = (document.mark*document.count_vote+Decimal(str(score)))/(document.count_vote+1)
    document.count_vote += 1
    document.save()
