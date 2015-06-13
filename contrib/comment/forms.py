import time
from django import forms
from django.utils.crypto import salted_hmac, constant_time_compare

import settings
COMMENT_MAX_LENGTH = getattr(settings,'COMMENT_MAX_LENGTH', 3000)

class CommentSecurityForm(forms.Form):
    """
    Handles the security aspects (anti-spoofing) for comment forms.
    """
    content_type  = forms.CharField(widget=forms.HiddenInput)
    object_pk     = forms.CharField(widget=forms.HiddenInput)
    comment_id        = forms.IntegerField(widget=forms.HiddenInput, required=False)

    timestamp     = forms.IntegerField(widget=forms.HiddenInput)
    security_hash = forms.CharField(min_length=40, max_length=40, widget=forms.HiddenInput)
    trick = forms.CharField(required=False)
    
    def __init__(self, target_object=None, data=None, initial=None):
    	if not target_object is None:
            self.target_object = target_object
            if initial is None:
                initial = {}
            initial.update(self.generate_security_data())
        super(CommentSecurityForm, self).__init__(data=data, initial=initial)

    def clean_parent(self):
        parent = self.cleaned_data["parent"]
        if not parent: return None
        else: return parent
        
    def clean_security_hash(self):
        """Check the security hash."""
        security_hash_dict = {
            'content_type' : self.data.get("content_type", ""),
            'object_pk' : self.data.get("object_pk", ""),
            'timestamp' : self.data.get("timestamp", ""),
        }
        expected_hash = self.generate_security_hash(**security_hash_dict)
        actual_hash = self.cleaned_data["security_hash"]
        if not constant_time_compare(expected_hash, actual_hash):
            raise forms.ValidationError("Security hash check failed.")
        return actual_hash

    def clean_timestamp(self):
        """Make sure the timestamp isn't too far (> 2 hours) in the past."""
        ts = self.cleaned_data["timestamp"]
        if time.time() - ts > (2 * 60 * 60):
            raise forms.ValidationError("Timestamp check failed")
        return ts

    def generate_security_data(self):
        """Generate a dict of security data for "initial" data."""
        timestamp = int(time.time())
        security_dict =   {
            'content_type'  : str(self.target_object._meta),
            'object_pk'     : str(self.target_object._get_pk_val()),
            'timestamp'     : str(timestamp),
            'security_hash' : self.initial_security_hash(timestamp),
        }
        return security_dict

    def initial_security_hash(self, timestamp):
        """
        Generate the initial security hash from self.content_object
        and a (unix) timestamp.
        """

        initial_security_dict = {
            'content_type' : str(self.target_object._meta),
            'object_pk' : str(self.target_object._get_pk_val()),
            'timestamp' : str(timestamp),
          }
        return self.generate_security_hash(**initial_security_dict)

    def generate_security_hash(self, content_type, object_pk, timestamp):
        """
        Generate a HMAC security hash from the provided info.
        """
        info = (content_type, object_pk, timestamp)
        key_salt = "Ax5Sfs32i45g8ra"
        value = "-".join(info)
        return salted_hmac(key_salt, value).hexdigest()
        
    def clean_trick(self):
        """Check that nothing's been entered into the honeypot."""
        value = self.cleaned_data["trick"]
        if value:
            raise forms.ValidationError("try spam attack: not empty trick")
        return value
        
    def get_hidden(self):
        hidden_fields = str(self['content_type'])
        hidden_fields += str(self['object_pk'])
        hidden_fields += str(self['timestamp'])
        hidden_fields += str(self['security_hash'])
        hidden_fields += "<p style='display:none;'>"+str(self['trick'])+"</p>"
        return hidden_fields

    def get_json_hidden_fields(self):
        import json
        
        fields = { 'content_type' : self['content_type'].value() , 
                   'object_pk' : self['object_pk'].value() , 
                   'timestamp' : self['timestamp'].value() ,
                   'security_hash' : self['security_hash'].value(),
                   'trick' : '' }
        return json.dumps(fields, sort_keys=True, indent=2)
        
class CommentForm(CommentSecurityForm):
    
    name = forms.CharField(max_length=20)
    comment = forms.CharField(max_length=COMMENT_MAX_LENGTH,widget=forms.Textarea)

class BondCommentForm(CommentSecurityForm):
    
    comment = forms.CharField(max_length=COMMENT_MAX_LENGTH,widget=forms.Textarea)

