from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin configuration for Review."""
    list_display = ['user', 'session', 'rating', 'title', 'created_at']
    list_filter = ['rating', 'session', 'created_at']
    search_fields = ['user__username', 'session__title', 'title', 'comment']
    date_hierarchy = 'created_at'