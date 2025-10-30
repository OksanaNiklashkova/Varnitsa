from django.contrib import admin

from blog.models import Photo, Publication


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 3
    fields = ("image", "caption", "order")
    readonly_fields = ("created_at",)
    ordering = ("order",)
    show_change_link = True


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    inlines = [PhotoInline]
    list_display = ("title", "created_at", "is_published", "publication_type")
    list_filter = ("is_published", "created_at")
    search_fields = ("title", "text")
