from django import forms
from models import Documents
from tinymce.widgets import TinyMCE
from django.conf import settings

class AddSectionForm(forms.Form):
    section_caption = forms.CharField(min_length=1,max_length=30)
    def clean_section_caption(self):
        caption = self.cleaned_data.get('section_caption')
        if not len(caption):
            raise forms.ValidationError("wrong caption")
        return caption


DOCUMENT_DESCRIPTION_MAX_LENGTH = getattr(settings,'DOCUMENT_DESCRIPTION_MAX_LENGTH', 3000)

class BaseSaveDocumentForm(forms.Form):
    
    title = forms.CharField(max_length=30,min_length=5)
    #description = forms.CharField(widget = forms.Textarea,max_length = DOCUMENT_DESCRIPTION_MAX_LENGTH)
    html_description = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}),max_length = DOCUMENT_DESCRIPTION_MAX_LENGTH)

    cost = forms.DecimalField(max_digits=5, decimal_places=2, required = False)

    def clean_file(self):
        file = self.cleaned_data.get('file', False)
        if file:
            if file._size > 50 * 1024 * 1024:
                raise forms.ValidationError("Файл слишком большого размера ( > 50mb )")
        return file

    def check_file_size(self, request, storage, old_file_size):
        from django.core.files import File
        file = File(self['file'].value())

        if storage.mem_busy + file.size - old_file_size <= storage.mem_limit:
            return True
        self._errors['file'] = self.error_class(['Недостаточно места для загрузки файла'])
        return False

    def check(self,request, storage, old_file_size = 0):
        flag = self.is_valid()
        if self['file'].value(): flag = self.check_file_size(request, storage, old_file_size) and flag
        return flag
        
class AddDocumentForm(BaseSaveDocumentForm):
    file = forms.FileField()
    is_free = forms.BooleanField(required=False)
    
class EditDocumentForm(BaseSaveDocumentForm):
    file = forms.FileField(required=False)

class VoteForm(forms.Form):
    mark = forms.DecimalField(max_digits=2, decimal_places=1,widget=forms.HiddenInput)
    count_vote = forms.IntegerField(widget=forms.HiddenInput)
    id = forms.IntegerField(widget=forms.HiddenInput)
