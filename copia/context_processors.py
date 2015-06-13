from django.conf import settings
def url(request):
    current_url = request.get_full_path()
    is_uri = not '?' in current_url
    if is_uri: get_separator = '?'
    else: get_separator = '&'

    csrf_cookie_name = getattr(settings,'CSRF_COOKIE_NAME')
    if (csrf_cookie_name in request.COOKIES): csrf = request.COOKIES[csrf_cookie_name] 
    else: csrf = ''
    return { 'csrf' : csrf,
             'current_url' : current_url, 
             'is_uri' : is_uri,
             'get_separator' : get_separator }

def my_page(request):
    context={}
    if request.user.is_authenticated():
        context['profile'] = request.user.get_profile()
        context['image'] = context['profile'].get_picture_url()
    return context
