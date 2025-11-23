from django.contrib import admin

from contacts.models import ContactRequest, ContactAttachment


class ContactAttachmentInline(admin.TabularInline):
    model = ContactAttachment
    extra = 3
    fields = ("contact_request", "file")
    readonly_fields = ("uploaded_at",)
    ordering = ("-uploaded_at",)
    show_change_link = True


@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ["request_type", "email", "subject", "created_at", "is_processed"]
    list_filter = ["request_type", "is_processed", "created_at"]
    search_fields = ["email", "subject", "message"]
    readonly_fields = ["created_at", "ip_address"]
