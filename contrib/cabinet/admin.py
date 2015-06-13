from prospere.contrib.cabinet.models import Documents, Storages, Sections, StorageBans
from django.contrib import admin
from prospere.contrib.cabinet.signals import user_password_changed

from prospere.lib import ContainerFkObjects

MEM_BAN = 5242880 # 5M

class DocumentsAdmin(admin.ModelAdmin):
    list_filter = (u'is_moderated', u'is_shared')
    list_display = ('id','user','title','description','is_free', 'is_shared')
    actions = ['delete', 'set_moderated', 'delete_and_add_ban', 'change_password_and_delete']

    def get_actions(self, request):
        actions = super(DocumentsAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def delete(self, request, queryset):
        for document in queryset:
            document.delete()
        self.message_user(request, "successfully deleted.")

    def set_moderated(self, request, queryset):
        queryset.update(is_moderated=True)
        self.message_user(request, "successfully marked as moderated.")

    def delete_and_add_ban(self, request, queryset):
        
        storage_list = set()
        for doc in queryset:
            storage_list.add(doc.storage_id)
        for storage_id in storage_list:
            count_new_bans = 0
            for document in queryset:
                if storage_id == document.storage_id : 
                    count_new_bans += 1
                    storage = document.storage
            amount_mem_ban = MEM_BAN * count_new_bans

            if amount_mem_ban > storage.mem_limit: amount_mem_ban = storage.mem_limit
            
            StorageBans.objects.create(storage = storage, is_processed = True, amount_of_ban = amount_mem_ban)

            storage.mem_limit = storage.mem_limit - amount_mem_ban
            storage.save()

        self.delete(request, queryset)
        self.message_user(request, "successfully deleted and ban added.")


    def change_password_and_delete(self, request, queryset):
        for document in queryset:
            document.user.set_password('XTDfcGeCUl')
            document.user.save()

            user_password_changed.send( sender = None, user_id = document.user_id)

        self.delete(request,queryset)

        self.message_user(request, "successfully password changed.")

    def queryset(self, request):
         return Documents.all_objects

    delete.short_description = "Delete."
    set_moderated.short_description = "Mark as moderated."
    delete_and_add_ban.short_description = "Delete and ban."
    change_password_and_delete.short_description = "Delete and reset password."

class SectionAdmin(admin.ModelAdmin):
    list_filter = (u'is_shared',)
    list_display = ('caption', 'is_shared',)

    def get_actions(self, request):
        actions = super(SectionAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def queryset(self, request):
         return Sections.objects

admin.site.register(Documents, DocumentsAdmin)
admin.site.register(Storages)
admin.site.register(Sections, SectionAdmin)
admin.site.register(StorageBans)

