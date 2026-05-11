from django.contrib import admin, messages
from django.utils.html import format_html
from equipment.duplication import duplicate_equipment_item
from equipment.duplication import sequential_tag_generator


from .forms import (
    EquipmentItemAdminForm,
    ExperimentAdminForm,
    StorageLocationAdminForm,
)

from .models import (
    EquipmentItem,
    PurchaseRecord,
    StorageLocation,
    RepairLog,
    EquipmentImage,
    Experiment,
    EquipmentExperiment,
    EquipmentType,
    ExperimentEquipmentRequirement,
)

from django.conf import settings

admin.site.site_header = f"Physics and Astronomy Equipment Inventory ({settings.ENVIRONMENT_NAME})"
admin.site.site_title = "Inventory Admin"
admin.site.index_title = "Inventory Management"
admin.site.login_template = "admin/login.html"

#admin.site.register(EquipmentItem)
#admin.site.register(PurchaseRecord)

@admin.action(description="Duplicate selected equipment items")
def duplicate_items(modeladmin, request, queryset):
    for item in queryset:
        duplicates = duplicate_equipment_item(
            original_item=item,
            count=15,  # default; we’ll improve this next
            inventory_tag_generator=sequential_tag_generator(
                item.inventory_tag or item.name
            ),
        )

        messages.success(
            request,
            f"Created {len(duplicates)} duplicates of {item}"
        )

class UniversityAdminSite(admin.AdminSite):
    site_header = "UWM Physics and Astronomy Equipment Inventory"
    site_title = "Inventory Admin"
    index_title = "Inventory Management"

    def each_context(self, request):
        context = super().each_context(request)
        context["custom_admin_css"] = True
        return context

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
    
class ExperimentEquipmentRequirementInline(admin.TabularInline):
    model = ExperimentEquipmentRequirement
    autocomplete_fields = ("equipment_type",)
    extra = 1

    
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

@admin.register(EquipmentType)
class EquipmentTypeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "manufacturer",
        "model_number",
        "storage_volume_display",
    )
    search_fields = ("name", "model_number")

    def storage_volume_display(self, obj):
        if obj.storage_volume_m3 is None:
            return "—"
        return f"{obj.storage_volume_m3:.3f} m³"

@admin.register(EquipmentItem)
class EquipmentItemAdmin(admin.ModelAdmin):
    
    #form = EquipmentItemAdminForm
    
    #autocomplete_fields = ("equipment_type",)


    inlines = [
        RepairLogInline,
        EquipmentImageInline,
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
                #"storage_volume_m3",
                #"storage_area_m2",
                #"storage_area_ft2",
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
        ("Bulk Creation", {
            "fields": (
                "create_duplicates",
                "duplicate_count",
                "inventory_tag_prefix",
            ),
            "classes": ("collapse",),
        }),
    )
    def storage_volume_display(self, obj):
        if not obj.equipment_type:
            return "—"
        vol = obj.equipment_type.storage_volume_m3
        return f"{vol:.3f} m³" if vol else "—"
    
    def save_model(self, request, obj, form, change):
        # Save the original object first
        super().save_model(request, obj, form, change)
    
        create_duplicates = form.cleaned_data.get("create_duplicates")
        duplicate_count = form.cleaned_data.get("duplicate_count")
        tag_prefix = form.cleaned_data.get("inventory_tag_prefix")
    
        if create_duplicates and duplicate_count and duplicate_count > 1:
            duplicates_to_create = duplicate_count - 1
    
            gen = None
            if tag_prefix:
                gen = sequential_tag_generator(tag_prefix)
    
            duplicates = duplicate_equipment_item(
                original_item=obj,
                count=duplicates_to_create,
                inventory_tag_generator=gen,
            )
    
            messages.success(
                request,
                f"Created {len(duplicates) + 1} identical equipment items."
            )
            
            '''
    def has_storage_dimensions(self, obj):
        return bool(obj.storage_length and obj.storage_width)

    has_storage_dimensions.boolean = True
    has_storage_dimensions.short_description = "Has Storage Dimensions"
    '''

    autocomplete_fields = ("purchase_record", "current_location")

    readonly_fields = (
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
    form = StorageLocationAdminForm
    
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

        ("Usable Capacity", {
            "fields": (
                "dimension_unit",
                "usable_length_input",
                "usable_width_input",
                "usable_height_input",
            )
        }),

        ("Notes", {
            "fields": ("location_notes",)
        }),
    )
    


@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    """
    Admin configuration for Experiment.

    Experiments do not have intrinsic dimensions.
    All storage requirements are derived from linked equipment.
    """

    # ------------------------------------------------------------------
    # List View
    # ------------------------------------------------------------------

    list_display = (
        "course_code",
        "experiment_title",
        "preferred_lab_type",
        "requires_fixed_installation",
        "move_sensitive",
        "storage_volume_display",
        "storage_footprint_display",
    )

    list_filter = (
        "course_code",
        "preferred_lab_type",
        "requires_fixed_installation",
        "move_sensitive",
    )

    search_fields = (
        "course_code",
        "experiment_title",
    )

    # ------------------------------------------------------------------
    # Detail View
    # ------------------------------------------------------------------

    readonly_fields = (
        "storage_volume_display",
        "storage_footprint_display",
        "created_at",
        "updated_at",
    )

    inlines = [ExperimentEquipmentRequirementInline]
    

    # ------------------------------------------------------------------
    # Read-only display helpers
    # ------------------------------------------------------------------

    def storage_volume_display(self, obj):
        vol = obj.storage_volume_m3
        if vol is None:
            return "—"
        return f"{vol:.3f} m³"

    storage_volume_display.short_description = "Storage Volume"

    def storage_footprint_display(self, obj):
        area = obj.storage_footprint_m2
        if area is None:
            return "—"
        return f"{area:.3f} m²"

    storage_footprint_display.short_description = "Storage Footprint"