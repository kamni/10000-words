from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'language_code', 'user']
    actions = ['full_delete']

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def full_delete(self, request, obj):
        for doc in obj:
            doc.delete()
