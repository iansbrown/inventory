from django.contrib import admin, messages
from django.utils.html import format_html
from equipment.duplication import duplicate_equipment_item
from equipment.duplication import sequential_tag_generator
from equipment.utils import can_schedule_experiment

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
    """
    Repair history for an individual equipment item.
    Item-level lifecycle data; does not belong on EquipmentType.
    """
    model = RepairLog
    extra = 0
    show_change_link = True
    ordering = ("-date_reported",)

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
    can_delete = False 

    
class EquipmentImageInline(admin.TabularInline):
    
    """
    Images associated with a specific equipment item.
    Item-level documentation; not shared across EquipmentType.
    """

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
        try:
            if obj.image and hasattr(obj.image, "url"):
                return format_html(
                    '<a href="{}" target="_blank">'
                    '<img src="{}" style="max-height: 120px; max-width: 160px;" />'
                    '</a>',
                    obj.image.url,
                    obj.image.url,
                )
        except Exception:
            pass
        return "No image"

    
    
    image_preview.short_description = "Preview"
    
class ExperimentEquipmentRequirementInline(admin.TabularInline):
   
    """
    Defines how many units of an equipment type
    are required for an experiment.
    """

    model = ExperimentEquipmentRequirement
    fk_name = "experiment"
    extra = 1
    
    autocomplete_fields = ("equipment_type",)

    fields = (
        "equipment_type",
        "quantity_required",
    )


    
class EquipmentItemInline(admin.TabularInline):
    """
    Read-only view of individual items belonging to an equipment type.
    Lifecycle and inventory-level data only.
    """
    model = EquipmentItem
    fk_name = "equipment_type"
    extra = 0
    show_change_link = True
    can_delete = False

    fields = (
        "inventory_tag",
        "tracking_level",
        "serial_number",
        "asset_tag",
        "current_location",
        "status",
    )

    autocomplete_fields = ("current_location",)

    readonly_fields = (
        "inventory_tag",
        "tracking_level",
        "serial_number",
        "asset_tag",
        "current_location",
        "status",
    )

class PurchaseEquipmentItemInline(admin.TabularInline):
    """
    Equipment items created as part of this purchase.
    Instance-level view; does not manage type-level properties.
    """
    model = EquipmentItem
    fk_name = "purchase_record"
    extra = 0
    show_change_link = True

    fields = (
        "inventory_tag",
        "equipment_type",
        "tracking_level",
        "serial_number",
        "asset_tag",
        "current_location",
        "status",
    )

    autocomplete_fields = (
        "equipment_type",
        "current_location",
    )

    readonly_fields = (
        "inventory_tag",
        "equipment_type",
        "tracking_level",
        "serial_number",
        "asset_tag",
        "current_location",
        "status",
    )

@admin.register(EquipmentType)
class EquipmentTypeAdmin(admin.ModelAdmin):
    """
    Admin for interchangeable equipment types.
    All physical and storage properties live here.
    """

    list_display = (
        "name",
        "category",
        "manufacturer",
        "model_number",
        "has_storage_dimensions",
        "storage_volume_display",
    )

    list_filter = (
        "category",
        "manufacturer",
        "requires_heavy_duty_shelving",
        "requires_climate_control",
        "requires_secure_storage",
        "storage_orientation",
    )

    search_fields = (
        "name",
        "model_number",
        "manufacturer",
        "keywords",
    )

    ordering = ("name",)

    fieldsets = (
        ("Identification", {
            "fields": (
                "name",
                "description",
                "keywords",
                "category",
                "manufacturer",
                "model_number",
            )
        }),
        ("Physical Constraints", {
            "fields": (
                "weight",
                "is_stackable",
                "max_stack_height",
                "storage_orientation",
                "requires_heavy_duty_shelving",
            )
        }),
        ("Environmental Requirements", {
            "fields": (
                "requires_climate_control",
                "requires_dark_storage",
                "requires_secure_storage",
                "hazard_class",
            )
        }),
        ("Storage Dimensions (Canonical, meters)", {
            "fields": (
                "dimension_unit",
                "storage_length_input",
                "storage_width_input",
                "storage_height_input",

            )
        }),
        ("Derived Storage (Read‑Only)", {
            "fields": (
                "storage_footprint_display",
                "storage_volume_display",
            )
        }),
        ("Metadata", {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )

    readonly_fields = (
        "storage_footprint_display",
        "storage_volume_display",
        "created_at",
        "updated_at",
    )

    # --- Read-only display helpers ---

    def storage_volume_display(self, obj):
        vol = obj.storage_volume_m3
        return f"{vol:.3f} m³" if vol is not None else "—"

    storage_volume_display.short_description = "Storage Volume"

    def storage_footprint_display(self, obj):
        area = obj.storage_footprint_m2
        return f"{area:.3f} m²" if area is not None else "—"

    storage_footprint_display.short_description = "Storage Footprint"

    # No inlines
    inlines = [EquipmentItemInline]


@admin.register(EquipmentItem)
class EquipmentItemAdmin(admin.ModelAdmin):
    """
    Admin for individual equipment items.
    Physical characteristics live on EquipmentType.
    This admin is lifecycle- and tracking-focused.
    """

    list_display = (
        "inventory_tag",
        "equipment_type",
        "tracking_level",
        "status",
        "current_location",
        "access_frequency",
    )

    list_filter = (
        "tracking_level",
        "status",
        "access_frequency",
        "equipment_type",
    )

    search_fields = (
        "inventory_tag",
        "serial_number",
        "asset_tag",
    )

    ordering = ("inventory_tag",)

    fields = (
        # Identification
        "inventory_tag",
        "equipment_type",
        "serial_number",
        "asset_tag",

        # Relationships
        "purchase_record",
        "current_location",

        # Tracking & lifecycle
        "tracking_level",
        "status",
        "access_frequency",

        # Notes
        "handling_notes",
        "migration_flags",

        # Metadata
        "created_at",
        "updated_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    # Inlines
    '''inlines = [RepairLogInline,
               EquipmentImageInline]'''

@admin.register(PurchaseRecord)
class PurchaseRecordAdmin(admin.ModelAdmin):

    inlines = [
        PurchaseEquipmentItemInline,
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
        "usable_floor_area_display",
    )
    
    readonly_fields = ("usable_floor_area_display",)
    
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

        ("Capacity", {
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
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
    
        # Explicitly mark form-only fields as safe
        for name in (
            "usable_length_input",
            "usable_width_input",
            "usable_height_input",
        ):
            if name in form.base_fields:
                form.base_fields[name].required = False
    
        return form
    
    def usable_floor_area_display(self, obj):
        area = obj.usable_floor_area_m2
        return f"{area:.2f} m²" if area else "—"

    usable_floor_area_display.short_description = "Usable Floor Area"



@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    """
    Admin configuration for Experiment.
    Storage is derived from required equipment types.
    """

    list_display = (
        "course_code",
        "experiment_title",
        "preferred_lab_type",
        "requires_fixed_installation",
        "move_sensitive",
        "storage_volume_display",
        "storage_footprint_display",
        #"schedulable",
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

    fieldsets = (
        ("Identity", {
            "fields": (
                "course_code",
                "experiment_title",
                "preferred_lab_type",
            )
        }),
        ("Constraints", {
            "fields": (
                "requires_fixed_installation",
                "move_sensitive",
            )
        }),
        ("Derived Storage", {
            "fields": (
                "storage_volume_display",
                "storage_footprint_display",
            )
        }),
        ("Metadata", {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )

    readonly_fields = (
        "storage_volume_display",
        "storage_footprint_display",
        "created_at",
        "updated_at",
    )

    inlines = [ExperimentEquipmentRequirementInline]
    @admin.display(description="Storage Volume")
    def storage_volume_display(self, obj):
        vol = obj.storage_volume_m3
        return f"{vol:.3f} m³" if vol is not None else "—"

    storage_volume_display.short_description = "Storage Volume"

    @admin.display(description="Storage Footprint")
    def storage_footprint_display(self, obj):
        area = obj.storage_footprint_m2
        return f"{area:.3f} m²" if area is not None else "—"

    storage_footprint_display.short_description = "Storage Footprint"
    
    

    @admin.display(boolean=True, description="Schedulable")
    def schedulable(self, obj):
        try:
            return can_schedule_experiment(obj)
        except Exception:
            return False

    
    schedulable.boolean = True
    schedulable.short_description = "Schedulable"
