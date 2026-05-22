# Lab Inventory & Scheduling Platform
## Data Dictionary

---

## 📌 Purpose

This document defines every major model and field in the system, including:

- Field meaning
- Data type expectations
- Usage rules
- Critical constraints

It is the authoritative reference for:

- Developers
- Data validation
- AI-assisted coding tools

---

# 📅 SCHEDULING MODELS

---

## LabCourse

Represents a course (does NOT change per term).

| Field | Type | Description |
|------|------|------------|
| id | Integer (PK) | Internal identifier |
| course_code | String | Short identifier (e.g. PHYS 101). Used in UI columns |
| course_title | String | Full course name |
| description | Text | Optional description |

---

## LabOffering

A course offered in a specific academic term.

| Field | Type | Description |
|------|------|------------|
| id | Integer (PK) | Internal identifier |
| lab_course | FK → LabCourse | The base course |
| academic_term | FK → AcademicTerm | ✅ MUST use this field for filtering |
| coordinator | FK → User | Instructor / coordinator |
| default_lab_room | String | Primary room |
| notes | Text | Optional |

---

✅ RULE:

Always filter by offerings__academic_term

---

## AcademicTerm

Represents an academic term.

| Field | Type | Description |
|------|------|------------|
| id | Integer (PK) | Internal identifier |
| name | String | e.g. Fall 2026 |
| start_date | Date | Term start |
| end_date | Date | Term end |

---

## ScheduleWeek

Represents a week within an offering.

| Field | Type | Description |
|------|------|------------|
| id | Integer (PK) | Internal identifier |
| offering | FK → LabOffering | Associated offering |
| week_number | Integer | ✅ CRITICAL FIELD |

---

✅ RULE:

week_number is the ONLY valid field for alignment and grouping

❌ Never use:
- id
- date
- ISO week

---

## WeekMeeting

Represents a specific lab session.

| Field | Type | Description |
|------|------|------------|
| id | Integer (PK) | Internal identifier |
| schedule_week | FK → ScheduleWeek | Parent week |
| meeting_order | Integer | Sequence in week (1, 2) |
| label | String | Optional label (Mon, Wed, etc.) |
| number_of_stations | Integer | ✅ scaling factor |
| experiment | FK → Experiment | Linked lab activity |
| notes | Text | Optional |

---

✅ RULE:

total equipment = quantity_required × number_of_stations

---

# 🧪 EXPERIMENT MODELS

---

## Experiment

Defines a lab experiment.

| Field | Type | Description |
|------|------|------------|
| id | Integer (PK) | Internal identifier |
| experiment_title | String | Name of experiment |

---

## ExperimentEquipmentRequirement

Defines required equipment per experiment.

| Field | Type | Description |
|------|------|------------|
| id | Integer (PK) | Internal identifier |
| experiment | FK → Experiment | Associated experiment |
| equipment_type | FK → EquipmentType | Required equipment type |
| quantity_required | Integer | Units needed per station |

---

✅ RULE:


quantity_required is PER STATION

---

# 📦 INVENTORY MODELS

---

## EquipmentType

Defines a category of equipment.

| Field | Type | Description |
|------|------|------------|
| id | Integer (PK) | Internal identifier |
| name | String | Equipment name |
| storage_volume_m3 | Float | Volume for storage planning |
| storage_footprint_m2 | Float | Floor footprint |

---

✅ Used for:
- space planning
- move planning
- reporting

---

## EquipmentItem

Represents a physical inventory entity.

---

### Core Fields

| Field | Type | Description |
|------|------|------------|
| id | Integer (PK) | Internal identifier |
| equipment_type | FK → EquipmentType | Type of item |
| current_location | FK → StorageLocation | Current location |
| purchase_record | FK | Purchase metadata |

---

### Identification Fields

| Field | Type | Description |
|------|------|------------|
| inventory_tag | String | Barcode / visible ID |
| serial_number | String | Manufacturer ID |
| asset_tag | String | Institutional ID |

---

### Tracking Behavior

| Field | Type | Description |
|------|------|------------|
| tracking_level | Choice | Controls how item is counted |

---

### ✅ Tracking Levels


individual_serialized
individual_non_serialized
bulk

---

### Quantity Field

| Field | Type | Description |
|------|------|------------|
| quantity | Integer | ONLY for bulk items |

---

### ✅ CRITICAL RULES

Bulk items:

tracking_level = bulk
quantity MUST be > 0

Individual items:

tracking_level != bulk
quantity MUST be NULL

---

### Status Field

| Field | Type | Description |
|------|------|------------|
| status | Choice | Availability state |

---

### ✅ Status Values


available
checked_out
under_repair
surplus
retired

---

### ✅ Availability Calculation


available =
SUM(quantity for bulk items)
+
COUNT(individual items)
FILTER:
status = available

---

### QR Code

| Field | Type | Description |
|------|------|------------|
| qr_code_image | Image | Generated QR code |

---

### Spatial Data

| Field | Type | Description |
|------|------|------------|
| storage_volume_m3 | Derived | From EquipmentType |
| storage_footprint_m2 | Derived | From EquipmentType |

---

## StorageLocation

Represents physical storage.

| Field | Type | Description |
|------|------|------------|
| id | Integer (PK) | Internal identifier |
| name | String | Location name (Lab A, Stockroom, etc.) |

---

## PurchaseRecord

Tracks procurement data.

| Field | Type | Description |
|------|------|------------|
| id | Integer (PK) | Internal identifier |
| vendor | String | Supplier |
| cost | Float | Purchase cost |
| date | Date | Purchase date |

---

# 🔧 REPAIR SYSTEM

---

## RepairLog

Tracks equipment repairs (append-only).

| Field | Type | Description |
|------|------|------------|
| id | Integer (PK) | Internal identifier |
| equipment | FK → EquipmentItem | Item being repaired |
| issue_description | Text | Problem description |
| date_reported | Date | Date reported |
| status | String | Repair status |
| outcome | Text | Final result |

---

✅ RULE:

RepairLog is append-only

NEVER overwrite past records.

---

# 📦 REQUEST SYSTEM

---

## EquipmentRequest

Represents user request for equipment.

| Field | Type | Description |
|------|------|------------|
| id | Integer (PK) | Internal identifier |
| request_type | Choice | equipment / experiment |
| equipment_type | FK | Requested equipment |
| experiment | FK | Requested experiment |
| quantity | Integer | Requested quantity |
| location | String | Delivery location |
| start_datetime | DateTime | Start of need |
| end_datetime | DateTime | End of need |
| requested_by | FK → User | Requester |
| status | String | Request state |

---

# 🔁 RELATIONSHIP MAP


LabCourse
→ LabOffering
→ ScheduleWeek
→ WeekMeeting
→ Experiment
→ EquipmentRequirement
→ EquipmentType
→ EquipmentItem

---

# ⚠️ CRITICAL SYSTEM RULES

---

### Scheduling

- Use `week_number`
- Never use IDs for grouping
- Align all courses by week

---

### Inventory

- Bulk = sum quantity
- Individual = count rows
- Must filter by status = available

---

### Equipment Requirements

- Always multiply by `number_of_stations`

---

### Relationships

- Always follow full FK chain
- Do not skip models

---

# ✅ ONE-LINE SUMMARY

This system uses structured relational data to connect scheduling, experiments, inventory, and space planning into a unified operational platform.