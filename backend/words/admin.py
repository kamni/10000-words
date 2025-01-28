from django.contrib import admin

from .models import (
    Conjugation,
    Document,
    LearningTracker,
    Sentence,
    SentenceOrder,
    Word,
    WordOrder,
)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'language', 'user']
    actions = ['full_delete']

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def full_delete(self, request, obj):
        for doc in obj:
            doc.delete()


@admin.register(Sentence)
class SentenceAdmin(admin.ModelAdmin):
    list_display = ['text', 'language', 'user']


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ['root_word', 'language', 'user']


@admin.register(WordOrder)
class WordOrderAdmin(admin.ModelAdmin):
    list_display = ['sentence', 'word', 'order']


@admin.register(SentenceOrder)
class SentenceOrderAdmin(admin.ModelAdmin):
    list_display = ['document', 'sentence', 'order']


@admin.register(Conjugation)
class ConjugationAdmin(admin.ModelAdmin):
    list_display = ['text', 'word', 'language', 'user']


@admin.register(LearningTracker)
class LearningTrackerAdmin(admin.ModelAdmin):
    list_display = ['conjugation', 'language', 'status', 'user']
