# Lab Inventory & Scheduling Platform
## Design Decisions Log

---

## 📌 Purpose of This Document

This file records the **key architectural and design decisions** made during development.

For each decision, we document:
- The problem being solved
- The chosen solution
- Alternatives considered
- Why the chosen approach was selected

---

## 🧱 1. Database-First Architecture

### ✅ Decision

Build the system as a **database-driven web application using an ORM (Django models)**.

---

### 🤔 Alternatives Considered

- Pure object-oriented system (in-memory objects)
- Extending Microsoft Access directly
- Spreadsheet-driven workflows

---

### ✅ Why This Was Chosen

- Supports multi-user access
- Enables persistent history and audit logging
- Allows complex queries and aggregation
- Handles concurrency safely
- Scales to large datasets

---

### ❌ Why Alternatives Were Rejected

- In-memory objects:
  - No persistence
  - No concurrency control
- Access:
  - Poor multi-user web support
  - Limited extensibility
- Spreadsheets:
  - No structure or integrity guarantees

---

## 🧪 2. Experiment Requirements Model

### ✅ Decision

Represent experiment needs as:

Experiment → EquipmentRequirement → quantity_required
NOT:
Experiment → list of equipment items

---

### 🤔 Alternatives Considered

- Store equipment as a list on experiment objects
- JSON field of required items

---

### ✅ Why This Was Chosen

- Enables reuse of experiments
- Supports scaling per meeting
- Allows aggregation across courses
- Enables conflict detection system

---

### ❌ Why Alternatives Were Rejected

- Lists / JSON:
  - Not queryable
  - Cannot aggregate across experiments
  - Hard to enforce consistency

---

## 📅 3. Use of ScheduleWeek Model

### ✅ Decision

Introduce a `ScheduleWeek` model with:

week_number (authoritative row key)
---

### 🤔 Alternatives Considered

- Use calendar dates
- Use meeting dates directly
- Group by ISO week

---

### ✅ Why This Was Chosen

- Aligns all courses by consistent week numbers
- Avoids calendar/date complexity
- Supports identical structure across courses
- Enables clean grid display

---

### ❌ Why Alternatives Were Rejected

- Dates:
  - Difficult to align across courses
- ISO week:
  - Not intuitive for users
- Direct meetings:
  - No grouping layer

---

## 📊 4. Scheduling Grid Design

### ✅ Decision

Render schedule as:


Rows = week_number
Columns = LabCourse
Cells = WeekMeeting experiments

---

### 🤔 Alternatives Considered

- Course-centric list view
- Calendar-style interface

---

### ✅ Why This Was Chosen

- Provides cross-course visibility
- Enables easy conflict identification
- Matches instructor mental model

---

### ❌ Why Alternatives Were Rejected

- Lists:
  - Hard to compare courses
- Calendar:
  - Too complex for structured lab systems

---

## ⚠️ 5. Conflict Detection System

### ✅ Decision

Compute conflicts by:


total_needed = quantity_required × number_of_stations
sum across ALL courses per week
compare with available inventory

---

### 🤔 Alternatives Considered

- Manual conflict tracking
- Per-course isolated validation

---

### ✅ Why This Was Chosen

- Detects real cross-course conflicts
- Reflects actual resource demand
- Enables proactive planning

---

### ❌ Why Alternatives Were Rejected

- Manual tracking:
  - Error-prone
- Per-course only:
  - Misses overlapping demand

---

## 📦 6. Mixed Inventory Model (Bulk + Individual)

### ✅ Decision

Support both:

- Bulk items (quantity field)
- Individual items (one row per item)

---

### 🤔 Alternatives Considered

- Fully serialized system
- Fully bulk-based system

---

### ✅ Why This Was Chosen

- Reflects real lab inventory:
  - Some items tracked individually (electronics)
  - Others tracked in bulk (meter sticks)
- Flexible and scalable

---

### ❌ Why Alternatives Were Rejected

- Fully serialized:
  - Too much overhead for bulk items
- Fully bulk:
  - Cannot track individual equipment lifecycle

---

## 📏 7. Storage Dimensions & Spatial Data

### ✅ Decision

Store:

- storage_volume_m3
- storage_footprint_m2

on EquipmentType

---

### 🤔 Alternatives Considered

- Ignore spatial data
- Store freeform text

---

### ✅ Why This Was Chosen

- Enables room capacity calculations
- Supports move planning
- Allows aggregation and reporting

---

### ❌ Why Alternatives Were Rejected

- Text fields:
  - Not computable
- No dimensions:
  - Cannot support relocation planning

---

## 🔧 8. Repair Logging as Separate Model

### ✅ Decision

Use an append-only RepairLog table

---

### 🤔 Alternatives Considered

- Store repair fields directly on EquipmentItem
- Overwrite repair history

---

### ✅ Why This Was Chosen

- Maintains full history
- Supports auditing
- Tracks lifecycle over time

---

### ❌ Why Alternatives Were Rejected

- Overwriting:
  - Loses history
- Embedded fields:
  - Cannot track multiple repairs

---

## 📍 9. Location as a Structured Relationship

### ✅ Decision

Use a StorageLocation model (FK from EquipmentItem)

---

### 🤔 Alternatives Considered

- Store location as text

---

### ✅ Why This Was Chosen

- Enables filtering and grouping
- Supports move planning
- Prevents inconsistent naming

---

## 🚚 10. Explicit Support for Lab Move

### ✅ Decision

Design system to support relocation planning from the start

---

### ✅ Why This Was Chosen

- Known upcoming lab move
- Avoids needing redesign later
- Adds immediate operational value

---

### ✅ Features Enabled

- Volume aggregation
- Footprint analysis
- Location tracking
- QR-based item movement

---

## 🤖 11. Documentation for AI-Assisted Development

### ✅ Decision

Create:

- PROJECT_CONTEXT.md
- DEVELOPER_ONBOARDING.md
- DESIGN_DECISIONS.md

---

### ✅ Why This Was Chosen

- Prevents incorrect assumptions by AI tools
- Maintains consistency across development
- Enables onboarding and long-term maintenance

---

## 🎯 Final Guiding Principle

> Every design decision prioritizes **accuracy, scalability, and real-world operational usefulness over convenience or simplicity.**

---

## ✅ Summary

The system intentionally balances:

- flexibility (mixed inventory, reusable experiments)
- structure (relational models, strict relationships)
- usability (grid dashboard)
- real-world constraints (space, repairs, locations)

---

## 🔁 Updating This Document

When making significant changes:

1. Add a new section
2. Document:
   - the problem
   - alternatives
   - final choice
   - reasoning

---

## ✅ One-Line Takeaway

> This system is designed as a data-driven operational platform, not just an inventory tracker — every decision supports that goal.