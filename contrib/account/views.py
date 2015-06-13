#coding: utf-8 
from django.shortcuts import render_to_response,redirect
from django.http import HttpResponse
from django.template import RequestContext
from django.views.generic.simple import direct_to_template
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from forms import ChangeProfile
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.views.decorators.cache import never_cache

from prospere.lib import set_get_argument

from  hashlib import md5
import time
from django.core.files.storage import default_storage
from PIL import Image
from cStringIO import StringIO
import os

from django.conf import settings
SECRET_KEY = getattr(settings,'SECRET_KEY')
permissions = getattr(settings,'FILE_UPLOAD_PERMISSIONS')

def json_response(x):
    import json
    return HttpResponse(json.dumps(x, sort_keys=True, indent=2),
                        content_type='application/json; charset=UTF-8')

def get_picture_name(key_salt=''):
    timestamp = int(time.time())
    hash = md5(str(timestamp)+key_salt+SECRET_KEY).hexdigest()
    relative_dir = '/'.join(['picture', hash[0:2]])
    dir = '/'.join([settings.MEDIA_ROOT, relative_dir])
    if not os.path.exists(dir):
        os.mkdir(dir,permissions)
    filename = '/'.join([relative_dir, hash[2:]])+'.jpg'
    filename = default_storage.get_available_name(filename)
    return filename

def handle_upload_picture(upload_picture):
    image = Image.open(StringIO(upload_picture.read()))
    if image.mode not in ('L', 'RGB'):
        image = image.convert('RGB')

    radio = float(image.size[1]) / image.size[0]
    width = 200
    height = int(width*radio)
    if height > 400: height = 400

    picture = image.resize((width,height),Image.ANTIALIAS)
    small_width = 200
    if height<width: small_width = height;
    small_picture = picture.crop((0,0,small_width,small_width)).resize((30,30),Image.ANTIALIAS)
    
    picture_name = get_picture_name()
    file = default_storage.open(picture_name, 'wb')    
    picture.save(file, format='JPEG')
    file.close()
    
    small_picture_name = get_picture_name('small')
    file = default_storage.open(small_picture_name, 'wb')    
    small_picture.save(file, format='JPEG')
    file.close()
    
    return picture_name, small_picture_name

@login_required(redirect_field_name=None)
def save_profile(request,extra_context=None):

    if request.method == 'POST':
        redirect_to = request.POST.get('next', reverse("prospere_user_page", kwargs={'username' : request.user.username }))
        form = ChangeProfile(request.POST, request.FILES)

        if form.is_valid():
            profile = request.user.get_profile()

            required_save_user = False
            required_save_profile = False

            if form.cleaned_data['picture']:
                picture_name, small_picture_name = handle_upload_picture(form.cleaned_data['picture'])
                
                profile.delete_picture()
                profile.delete_small_picture()
                
                profile.picture = picture_name
                profile.small_picture = small_picture_name
                
                required_save_profile = True
            
            if form.cleaned_data['first_name']:
                request.user.first_name = form.cleaned_data['first_name']
                required_save_user = True
            
            if form.cleaned_data['last_name']:
                request.user.last_name = form.cleaned_data['last_name']
                required_save_user = True

            if form.cleaned_data['description']:
                profile.description = form.cleaned_data['description']
                required_save_profile = True

            if required_save_user: request.user.save()
            if required_save_profile: profile.save()

            if required_save_user or required_save_profile:
                redirect_to = set_get_argument(redirect_to,"message","account_profile_saved")

            return redirect(redirect_to)

        redirect_to = set_get_argument(redirect_to,"message","account_profile_not_saved")
        return redirect(redirect_to)

    return direct_to_template(request,'error.html')

@login_required(redirect_field_name=None)
def add_bookmark(request):
    from forms import AddBookmark
    from models import Bookmarks
    import signals
    from models import bookmark_choices

    if request.method == 'POST':
        form = AddBookmark(request.POST)
        if form.is_valid():
            if not form.cleaned_data['type'] in [b[0] for b in bookmark_choices]: return json_response({ 'success' : False })
            Bookmarks.objects.create(user = request.user, type = form.cleaned_data['type'], 
                                     object = form.cleaned_data['object'])

            signals.bookmark_added.send(sender = None,
                                        request = request,
                                        type = form.cleaned_data['type'],
                                        object = form.cleaned_data['object'])

            return json_response({ 'success' : True })

    return json_response({ 'success' : False })

@login_required(redirect_field_name=None)
def delete_bookmark(request):
    from models import Bookmarks
    import signals

    if request.method == 'POST':
        bookmark_type = request.POST.get('type', False)
        bookmark_object = request.POST.get('object', False)
        if not bookmark_type or not bookmark_object: return json_response({ 'success' : False })

        try:
            Bookmarks.objects.get(user = request.user, type = bookmark_type, object = bookmark_object).delete()
        except ObjectDoesNotExist:
            return json_response({ 'success' : False })

        signals.bookmark_deleted.send(sender = None,
                                      request = request,
                                      type = bookmark_type,
                                      object = bookmark_object)

        return json_response({ 'success' : True })

    return json_response({ 'success' : False })

@never_cache
def get_bookmarks(request):
    user_id = request.GET.get('id',False)
    if not user_id:
        return json_response({ 'success' : False, 'error' : 'id missed' })
    user_id = int(user_id)
    from prospere.copia.views import make_bookmark_list
    bookmarks = make_bookmark_list(user_id)

    return json_response({ 'success' : True, 'bookmarks' : bookmarks })

def check_username(request):
    username = request.GET.get('username', False)
    if not username: return json_response({ 'success' : False })
    count = User.objects.filter(username = username).count()
    if count == 0: return json_response({ 'success' : True, 'username_free' : True })
    else: return json_response({ 'success' : True, 'username_free' : False })

