import time
from django.utils.crypto import salted_hmac, constant_time_compare
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate

class SecurityForm(forms.Form):

    timestamp     = forms.IntegerField(widget=forms.HiddenInput)
    security_hash = forms.CharField(min_length=40, max_length=40, widget=forms.HiddenInput)
    
    def __init__(self, data=None, initial=None):

        if initial is None:
            initial = {}
        initial.update(self.generate_security_data())
        super(SecurityForm, self).__init__(data=data, initial=initial)

    def clean_security_hash(self):
        """Check the security hash."""
        security_hash_dict = {
            'timestamp' : self.data.get("timestamp", ""),
        }
        expected_hash = self.generate_security_hash(**security_hash_dict)
        actual_hash = self.cleaned_data["security_hash"]
        if not constant_time_compare(expected_hash, actual_hash):
            raise forms.ValidationError("Security hash check failed.")
        return actual_hash

    def clean_timestamp(self):
        """Make sure the timestamp isn't too far (> 1 hours) in the past."""
        ts = self.cleaned_data["timestamp"]
        if time.time() - ts > (60 * 60):
            raise forms.ValidationError("Timestamp check failed")
        return ts

    def generate_security_data(self):
        """Generate a dict of security data for "initial" data."""
        timestamp = int(time.time())
        security_dict =   {
            'timestamp'     : str(timestamp),
            'security_hash' : self.generate_security_hash(str(timestamp)),
        }
        return security_dict

    def generate_security_hash(self, timestamp):
        """
        Generate a HMAC security hash from the provided info.
        """
        key_salt = "Ax5Sfs32i45g8ra"
        value = "-".join(timestamp)
        return salted_hmac(key_salt, value).hexdigest()
        
    def get_hidden(self):
        hidden_fields = str(self['timestamp'])
        hidden_fields += str(self['security_hash'])
        return hidden_fields

class EncryptionForm(forms.Form):

    pub_key_n = forms.CharField(widget=forms.HiddenInput)
    pub_key_e = forms.CharField(widget=forms.HiddenInput)
    encryption = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, data=None, initial=None):
        if initial is None:
            initial = {}
        initial.update(self.get_pub_keys())
        super(EncryptionForm, self).__init__(data=data, initial=initial)

    def get_pub_keys(self):
        import rsa
        with open('/www/prospere/rsa/public_key.pem') as public_key_file:
            keydata = public_key_file.read()
        public_key = rsa.PublicKey.load_pkcs1(keydata)
        keys_dict = { 'pub_key_n' : hex(public_key.n),
                      'pub_key_e' : hex(public_key.e),
                      'encryption': 'no_entcription'}
        return keys_dict

    def decrypt(self,field):
        import rsa
        encryption = self.cleaned_data.get('encryption')
        if encryption == 'rsa':

            with open('/www/prospere/rsa/private_key.pem') as private_key_file:
                keydata = private_key_file.read()
            private_key = rsa.PrivateKey.load_pkcs1(keydata)
            pas = rsa.decrypt(field, private_key)
            raise 1
            return rsa.decrypt(field, private_key)
        raise 1
        return field

    def get_encrypt_fields(self):
        hidden_fields = str(self['pub_key_n'])
        hidden_fields += str(self['pub_key_e'])
        hidden_fields += str(self['encryption'])
        return hidden_fields

