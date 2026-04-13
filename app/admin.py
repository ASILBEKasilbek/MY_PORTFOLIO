from django.contrib import admin
from django.utils.html import format_html
from .models import Project, Skills, ContactMessage, SiteSettings, Order


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("🔍 SEO sozlamalari", {
            "fields": ("site_title", "site_description", "site_keywords"),
        }),
        ("🖼️ Rasmlar", {
            "fields": ("profile_image", "favicon", "og_image", "preloader_bg"),
            "description": "Profil rasmi, favicon va boshqa rasmlarni shu yerdan yuklang",
        }),
        ("👤 Shaxsiy ma'lumotlar", {
            "fields": ("full_name", "first_name", "job_title", "ready_badge", "typing_phrases", "hero_description"),
        }),
        ("📝 Men haqimda bo'lim", {
            "fields": ("about_subtitle", "about_text_1", "about_text_2", "about_tags"),
        }),
        ("📊 Statistika", {
            "fields": ("stat_experience", "stat_projects", "stat_clients", "stat_quality"),
        }),
        ("📞 Aloqa ma'lumotlari", {
            "fields": ("phone", "contact_email", "location"),
        }),
        ("🌐 Ijtimoiy tarmoqlar", {
            "fields": ("github_url", "linkedin_url", "telegram_url", "upwork_url", "instagram_url"),
        }),
        ("📄 CV/Resume", {
            "fields": ("resume_file",),
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj, _ = SiteSettings.objects.get_or_create(pk=1)
        from django.shortcuts import redirect
        from django.urls import reverse
        return redirect(reverse("admin:app_sitesettings_change", args=[obj.pk]))


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "preview_image", "created_at")
    search_fields = ("title", "content")
    list_filter = ("created_at",)
    readonly_fields = ("created_at", "updated_at")

    def preview_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:50px;border-radius:6px;">', obj.image.url)
        return "-"
    preview_image.short_description = "Rasm"


@admin.register(Skills)
class SkillsAdmin(admin.ModelAdmin):
    list_display = ("title", "percent", "progress_bar")
    list_editable = ("percent",)

    def progress_bar(self, obj):
        color = "#6366f1" if obj.percent >= 70 else "#8b5cf6" if obj.percent >= 40 else "#ec4899"
        return format_html(
            '<div style="width:150px;background:#e2e8f0;border-radius:999px;height:8px;">'
            '<div style="width:{}%;background:{};border-radius:999px;height:8px;"></div></div>',
            obj.percent, color
        )
    progress_bar.short_description = "Daraja"


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "short_message", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("name", "phone", "message")
    readonly_fields = ("name", "phone", "message", "created_at")
    list_editable = ("is_read",)
    actions = ["mark_as_read"]

    def short_message(self, obj):
        return obj.message[:60] + "..." if len(obj.message) > 60 else obj.message
    short_message.short_description = "Xabar"

    def phone(self, obj):
        return obj.phone
    phone.short_description = "Telefon"

    @admin.action(description="O'qilgan deb belgilash")
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'phone', 'city', 'utm_source', 'colored_price', 'items_count', 'status', 'created_at')
    list_filter = ('status', 'utm_source', 'city', 'created_at')
    search_fields = ('first_name', 'last_name', 'phone', 'email')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = "Mijoz"

    def colored_price(self, obj):
        color = "#f59e0b" if obj.total_price > 50000 else "#34d399"
        return format_html('<span style="color:{};font-weight:600;">{:,.0f} ₸</span>', color, obj.total_price)
    colored_price.short_description = "Summa"

