from prospere.contrib.comment.models import Comments
from django.contrib import admin

class CommentsAdmin(admin.ModelAdmin):
    list_filter = (u'is_moderate',)

    actions = ['make_moderate', 'delete']

    def get_actions(self, request):
        actions = super(CommentsAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def make_moderate(self, request, queryset):
        queryset.update(is_moderate=True)
        self.message_user(request, "successfully marked as moderated.")

    def delete(self, request, queryset):
        for comment in queryset:
            comment.deep_delete()
        self.message_user(request, "successfully deleted.")

    make_moderate.short_description = "Mark this comments as moderated."
    
admin.site.register(Comments,CommentsAdmin)
