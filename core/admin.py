from django.contrib import admin
from .models import Article, ArticleCategory, Consultation, Project, ProjectImage, SiteSettings, TeamMember


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ('position', 'image_asset', 'image_upload', 'image_alt')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'location', 'order', 'featured_order', 'is_published')
    list_editable = ('order', 'featured_order', 'is_published')
    list_filter = ('category', 'is_published')
    search_fields = ('title', 'location')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProjectImageInline]
    save_on_top = True


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'date_display', 'is_published')
    list_editable = ('is_published',)
    list_filter = ('category', 'is_published')
    search_fields = ('title', 'body_html')
    prepopulated_fields = {'slug': ('title',)}
    save_on_top = True


@admin.register(ArticleCategory)
class ArticleCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'position')
    list_editable = ('position',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.slug == 'other':
            return ('name', 'slug')
        return ()

    def has_delete_permission(self, request, obj=None):
        return obj is None or obj.slug != 'other'

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop('delete_selected', None)
        return actions


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'position', 'is_active')
    list_editable = ('position', 'is_active')
    search_fields = ('name', 'role')


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'subject', 'status', 'created_at')
    list_filter = ('status', 'subject', 'created_at')
    search_fields = ('name', 'phone', 'message')
    readonly_fields = ('name', 'phone', 'subject', 'message', 'created_at')
    fields = ('name', 'phone', 'subject', 'message', 'created_at', 'status', 'admin_notes')
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.site_header = 'مدیریت پاک سرا کارن'
admin.site.site_title = 'پاک سرا کارن'
admin.site.index_title = 'مدیریت محتوای سایت'
