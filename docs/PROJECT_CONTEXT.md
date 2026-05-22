# Lab Inventory & Scheduling Platform – Project Context

---

## 🧾 Original Project Prompt

This system originated from the following request:

"I am a University physics lab manager and I need to create a program to keep track of inventory and which items are used for specific lab experiments. I want you to act as my lead programmer and program designer. Because most physics faculty and students use python, I would prefer to use that as the basis for the backend of the program. I want the program to have a web interface a so others in the department can access it from any platform. I have a Microsoft Access database with all the equipment purchased since 2012 but it does not have all the data I would like the program to have for each item. I want each Item to have an identifier like a bar code. I also want to record the storage footprint of the item and its dimensions when set up. I would also like the ability to store images of the item as well as its location. Its also important that we keep a log of each item's repair history and a log of any changes that are made to any of its attributes. My first thought was to make an equipment class where each item is instantiated as an object and also to make an experiment class where each object contains a list of items that belong to that experiment. I am not sure if this is the most efficient way to go about this though so I want your thought on how to proceed…"

---

## 🧠 Initial Design Direction (Architectural Foundation)

The initial design guidance established a critical principle:

> **Build a database-driven web application using Python and an ORM, not a purely in-memory object system.**

### Core architectural rules established:

- The **database is the source of truth**
- Python classes (Django models) map to database tables
- Objects are loaded from the database, not persistently stored in memory
- Relationships must be modeled in the database, not Python lists
- Logging, history, and auditing must be first-class features

---

## 🔄 Evolution of the System

The project evolved significantly from the original concept:

### Initial concept:
- Equipment tracking
- Experiment-to-item mapping

---

### Expanded system (current state):

- ✅ Course scheduling (term → weeks → meetings)
- ✅ Experiment-based equipment requirements
- ✅ Conflict detection across courses
- ✅ Mixed inventory model (bulk + individual tracking)
- ✅ Repair-aware availability
- ✅ Location-aware inventory
- ✅ Spatial planning (volume + footprint)
- ✅ Move / relocation support
- ✅ Web-based multi-user access

---

## 🎯 Core System Concept

The system integrates **scheduling, experiments, and inventory**:

LabCourse
→ LabOffering
→ ScheduleWeek
→ WeekMeeting
→ Experiment
→ EquipmentRequirement
→ EquipmentItem

---

## 📅 Scheduling System (CRITICAL STRUCTURE)

### LabCourse
Defines course identity:
- course_code (used in UI)
- course_title

---

### LabOffering
Represents a course in a term:
- FK → lab_course
- FK → academic_term ✅ (NOT "term")

---

### ScheduleWeek
Defines week structure:
- FK → offering
- week_number ✅ (CRITICAL)

✅ ALL scheduling alignment depends on this field

---

### WeekMeeting
Represents an individual lab session:
- FK → schedule_week (related_name="meetings")
- experiment
- number_of_stations ✅ (CRITICAL)

---

## 📊 Scheduling Rules (MUST FOLLOW)

- ALWAYS group by `week_number`
- NEVER use `week.id` or dates
- ALWAYS traverse:

offering → schedule_weeks → meetings

---

## 🧪 Experiment System

### Experiment
Defines a lab

---

### ExperimentEquipmentRequirement

Defines:


equipment_type + quantity_required
(per station)

---

### ✅ CRITICAL RULE


total_required = quantity_required × number_of_stations

---

## 📦 Inventory System

### EquipmentItem

Supports 3 tracking modes:


tracking_level =

bulk
individual_serialized
individual_non_serialized


---

### ✅ Behavior Rules

| Type | quantity |
|------|---------|
Bulk | MUST be set |
Individual | MUST be NULL |

---

### ✅ Availability Calculation


available =
SUM(bulk quantities)
+
COUNT(individual items)
FILTER: status = available

---

## 🔧 Repair System

### RepairLog

- append-only history
- never overwrite
- affects availability

---

## 📏 Spatial & Move Planning

Included intentionally to support lab relocation.

### Data:

- storage_volume_m3
- storage_footprint_m2
- current_location
- QR code tracking

---

### Enables:

- room capacity planning
- equipment distribution
- move execution tracking

---

## 🏫 Lab Setup Automation

The system replaces manual processes by:

- defining equipment per experiment
- scaling by number_of_stations
- generating setup requirements per week/course

---

## ⚠️ Conflict Detection System

### Logic:

For each week:

1. Aggregate all meetings across courses
2. Compute:

quantity_required × number_of_stations
3. Sum by equipment type
4. Compare with availability

---

### Conflict condition:


if required > available → conflict

---

## 🧩 Key Model Relationships (DO NOT CHANGE)


LabCourse → offerings
LabOffering → schedule_weeks
ScheduleWeek → meetings
WeekMeeting → experiment
Experiment → equipment_requirements

---

## 🚫 Known Pitfalls (DO NOT REPEAT)

- ❌ Using `term` instead of `academic_term`
- ❌ Skipping ScheduleWeek in queries
- ❌ Using incorrect related_name
- ❌ Using `.count()` alone for inventory
- ❌ Not multiplying by number_of_stations
- ❌ Using IDs instead of week_number

---

## 📊 UI Rules

- Home URL: `/home/`
- Admin branding overridden
- Schedule grid:
  - columns = course_code
  - rows = week_number

---

## 🗃️ Data Migration (Access → Django)

- Access used only as source
- Data migrated via scripts
- New schema fully redesigned
- Access retained as archival reference

---

## ✅ Current System Capabilities

- Scheduling dashboard (grid-based)
- Cross-course conflict detection
- Experiment requirement system
- Mixed inventory tracking
- Repair tracking
- Spatial planning support
- QR-based tracking

---

## 🚀 Future Direction

- UI/UX improvements
- conflict resolution suggestions
- reporting dashboards
- move simulation tools

---

## 🎯 Guiding Principle

> This system is a **data-driven operational planning platform**, not just an inventory tracker.

All decisions must prioritize:

- data accuracy
- real-world usability
- scalability
- consistency

---

## ✅ One-Line Summary

This platform integrates scheduling, experiments, inventory, and spatial data into a single system that enables accurate lab operations and planning.