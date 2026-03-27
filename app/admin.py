from django.contrib import admin
from .models import Project,Skills
from .models import ContactMessage




admin.site.register(Project)
admin.site.register(Skills)
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at")
    search_fields = ("name", "email", "message")

