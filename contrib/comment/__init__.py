
def get_comment_form(object, request):
    '''
    Return comment form for object
    '''
    from forms import CommentForm, BondCommentForm
    if request.user.is_authenticated():
        form = BondCommentForm(target_object=object)
    else:
        form = CommentForm(target_object=object)
    form.hidden = form.get_hidden()
    form.json_hidden = form.get_json_hidden_fields()
    return form

