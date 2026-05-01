from django.contrib import admin
from django.utils.html import format_html


from .models import (
    EquipmentItem,
    PurchaseRecord,
    StorageLocation,
    RepairLog,
    EquipmentImage,
    Experiment,
    EquipmentExperiment,
)

from django.contrib import admin
from django.conf import settings

admin.site.site_header = f"Physics and Astronomy Equipment Inventory ({settings.ENVIRONMENT_NAME})"
admin.site.site_title = "Inventory Admin"
admin.site.index_title = "Inventory Management"
admin.site.login_template = "admin/login.html"

#admin.site.register(EquipmentItem)
#admin.site.register(PurchaseRecord)

class RepairLogInline(admin.TabularInline):
    model = RepairLog
    extra = 0
    fields = (
        "date_reported",
        "issue_description",
        "repair_action",
        "performed_by",
        "repair_cost",
        "outcome",
        "move_related",
    )
    readonly_fields = ()
    show_change_link = True
    
class EquipmentImageInline(admin.TabularInline):
    model = EquipmentImage
    extra = 0
    fields = (
        "image_preview",
        "image",
        "image_type",
        "caption",
        "date_taken",
    )
    readonly_fields = ("image_preview",)
    show_change_link = True

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<a href="{0}" target="_blank">'
                '<img src="{0}" style="max-height: 120px; max-width: 160px;" />'
                '</a>',
                obj.image.url
            )
        return "No image"
    
    
    image_preview.short_description = "Preview"
    
class EquipmentExperimentInline(admin.TabularInline):
    model = EquipmentExperiment
    extra = 0
    autocomplete_fields = ("experiment",)
    fields = (
        "experiment",
        "quantity_used",
        "is_core_to_experiment",
        "temporary_substitution_allowed",
        "storage_group_label",
        "notes",
    )
    show_change_link = True
    
class EquipmentItemInline(admin.TabularInline):
    model = EquipmentItem
    extra = 0
    fields = (
        "inventory_tag",
        "name",
        "tracking_level",
        "quantity",
        "serial_number",
        "asset_tag",
        "current_location",
        "status",
    )
    autocomplete_fields = ("current_location",)
    show_change_link = True

@admin.register(EquipmentItem)
class EquipmentItemAdmin(admin.ModelAdmin):
    inlines = [
        RepairLogInline,
        EquipmentImageInline,
        EquipmentExperimentInline,
    ]

    list_display = (
        "inventory_tag",
        "name",
        "tracking_level",
        "status",
        "current_location",
        "has_storage_dimensions",
    )

    list_filter = (
        "tracking_level",
        "status",
        "access_frequency",
        "current_location",
        "migration_flags",
    )
    
    search_fields = (
        "inventory_tag",
        "name",
        "keywords",
        "serial_number",
        "asset_tag",
    )

    ordering = ("inventory_tag",)

    fieldsets = (
        ("Procurement", {
            "fields": (
                "purchase_record",
            )
        }),
        ("Identification", {
            "fields": (
                "inventory_tag",
                "name",
                "description",
                "keywords",
                "category",
                "manufacturer",
                "model_number",
                "serial_number",
                "asset_tag",
            )
        }),
        ("Tracking", {
            "fields": (
                "tracking_level",
                "quantity",
                "status",
            )
        }),
    
        ("Location & Storage", {
            "fields": (
                "current_location",
                "storage_length",
                "storage_width",
                "storage_height",
                "storage_footprint_area",
                "storage_volume",
            )
        }),
        ("Constraints", {
            "fields": (
                "weight",
                "is_stackable",
                "max_stack_height",
                "storage_orientation",
                "requires_heavy_duty_shelving",
            )
        }),
        ("Environment & Usage", {
            "fields": (
                "requires_climate_control",
                "requires_dark_storage",
                "requires_secure_storage",
                "access_frequency",
            )
        }),
        ("Notes & Migration", {
            "fields": (
                "handling_notes",
                "migration_flags",
            )
        }),
        ("Metadata", {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )
    
    def has_storage_dimensions(self, obj):
        return bool(obj.storage_length and obj.storage_width)

    has_storage_dimensions.boolean = True
    has_storage_dimensions.short_description = "Has Storage Dimensions"


    autocomplete_fields = ("purchase_record", "current_location")

    readonly_fields = (
        "storage_footprint_area",
        "storage_volume",
        "created_at",
        "updated_at",
    )
    
    @admin.action(description="Clear migration flags (mark reviewed)")
    def clear_migration_flags(self, request, queryset):
        queryset.update(migration_flags="")
        
    actions = ["clear_migration_flags"]


@admin.register(PurchaseRecord)
class PurchaseRecordAdmin(admin.ModelAdmin):

    inlines = [
        EquipmentItemInline,
    ]

    
    list_display = (
        "vendor",
        "fiscal_year",
        "date_ordered",
        "date_received",
        "legacy_access_id",
    )

    list_filter = (
        "fiscal_year",
        "vendor",
    )

    search_fields = (
        "vendor",
        "order_number",
        "po_number",
        "legacy_access_id",
    )

    ordering = ("-date_ordered",)

    fieldsets = (
        ("Purchase Info", {
            "fields": (
                "vendor",
                "fiscal_year",
                "date_ordered",
                "date_received",
                "order_number",
                "po_number",
                "payment_method",
            )
        }),
        ("Costs", {
            "fields": (
                "item_unit_cost",
                "shipping_cost",
                "tax",
                "discount",
                "extended_cost",
            )
        }),
        ("Backorder", {
            "fields": (
                "backorder_flag",
                "backorder_quantity",
                "backorder_received_date",
            )
        }),
        ("Planning & Notes", {
            "fields": (
                "purchase_relevance_notes",
                "replacement_priority",
                "notes",
            )
        }),
        ("Metadata", {
            "fields": (
                "legacy_access_id",
                "created_at",
                "updated_at",
            )
        }),
    )

    readonly_fields = (
        "legacy_access_id",
        "created_at",
        "updated_at",
    )
    
@admin.register(StorageLocation)
class StorageLocationAdmin(admin.ModelAdmin):
    list_display = (
        "building",
        "room",
        "cabinet",
        "shelf",
        "location_type",
        "is_final_location",
    )

    list_filter = (
        "location_type",
        "is_final_location",
    )

    search_fields = (
        "room",
        "cabinet",
        "shelf",
        "location_notes",
    )

    ordering = ("location_type", "building", "room")

    fieldsets = (
        ("Location Identity", {
            "fields": ("building", "room", "cabinet", "shelf")
        }),
        ("Classification", {
            "fields": ("location_type", "is_final_location")
        }),
        ("Capacity (Optional)", {
            "fields": ("floor_area_allocated", "volume_capacity", "weight_capacity")
        }),
        ("Notes", {
            "fields": ("location_notes",)
        }),
    )
    
@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    search_fields = (
        "course_code",
        "experiment_title",
        "description",
    )
    list_display = (
        "course_code",
        "experiment_title",
        "preferred_lab_type",
    )