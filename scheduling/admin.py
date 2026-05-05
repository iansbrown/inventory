# -*- coding: utf-8 -*-
"""
Created on Mon May  4 14:30:09 2026

@author: ianbrown
"""

from django.contrib import admin

from .models import (
    AcademicTerm,
    LabCourse,
    LabOffering,
    ScheduleWeek,
    WeekMeeting,
    LabSection,
)

from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render, get_object_or_404
from collections import defaultdict
from equipment.models import EquipmentExperiment
from scheduling.conflicts import detect_equipment_conflicts


@admin.register(AcademicTerm)
class AcademicTermAdmin(admin.ModelAdmin):
    list_display = ("name", "term_type", "start_date", "end_date")
       
    def get_urls(self):
            urls = super().get_urls()
            custom_urls = [
                path(
                    "<int:term_id>/equipment-conflicts/",
                    self.admin_site.admin_view(self.equipment_conflicts_view),
                    name="term_equipment_conflicts",
                ),
            ]
            return custom_urls + urls
        
    def equipment_conflicts_view(self, request, term_id):
        term = get_object_or_404(AcademicTerm, pk=term_id)

        conflict_data = []

        for offering in term.lab_offerings.select_related(
            "lab_course", "coordinator"
        ).prefetch_related("schedule_weeks__meetings__experiment"):
            offering_conflicts = []

            for week in offering.schedule_weeks.all():
                equipment_map = defaultdict(int)

                for meeting in week.meetings.all():
                    for link in EquipmentExperiment.objects.filter(
                        experiment=meeting.experiment
                    ):
                        if link.equipment_item:
                            equipment_map[link.equipment_item] += (
                                link.quantity_used or 1
                            )

                conflicts = detect_equipment_conflicts(equipment_map)

                if conflicts:
                    offering_conflicts.append({
                        "week": week,
                        "conflicts": conflicts,
                    })

            if offering_conflicts:
                conflict_data.append({
                    "offering": offering,
                    "weeks": offering_conflicts,
                })

        context = dict(
            self.admin_site.each_context(request),
            term=term,
            conflict_data=conflict_data,
        )

        return render(
            request,
            "admin/scheduling/term_equipment_conflicts.html",
            context,
        )
    
    list_filter = ("term_type",)
    ordering = ("start_date",)
    readonly_fields = ("equipment_conflicts_link",)

    def equipment_conflicts_link(self, obj):
        return format_html(
            '<a class="button" href="{}">View Equipment Conflicts</a>',
            f"{obj.id}/equipment-conflicts/"
        )

    equipment_conflicts_link.short_description = ""
    
    fieldsets = (
        (None, {
            "fields": ("name", "term_type", "start_date", "end_date"),
        }),
        ("Logistics", {
            "fields": ("equipment_conflicts_link",),
        }),
    )

@admin.register(LabCourse)
class LabCourseAdmin(admin.ModelAdmin):
    list_display = ("course_code", "course_title")
    search_fields = ("course_code", "course_title")
    

class WeekMeetingInline(admin.TabularInline):
    model = WeekMeeting
    extra = 0
    fields = (
        "meeting_order",
        "label",
        "experiment",
        "notes",
    )
    ordering = ("meeting_order",)
    autocomplete_fields = ("experiment",)
    
@admin.register(ScheduleWeek)
class ScheduleWeekAdmin(admin.ModelAdmin):
    list_display = (
        "lab_offering",
        "week_number",
        "week_start_date",
    )
    ordering = ("week_number",)
    inlines = [WeekMeetingInline]
    
class ScheduleWeekInline(admin.TabularInline):
    model = ScheduleWeek
    extra = 0
    fields = (
        "week_number",
        "week_start_date",
        "notes",
    )
    ordering = ("week_number",)

class LabSectionInline(admin.TabularInline):
    model = LabSection
    extra = 0
    fields = (
        "section_code",
        "instructor",
        "meeting_day",
        "meeting_time",
        "room",
    )
    autocomplete_fields = ("instructor",)

@admin.register(LabOffering)
class LabOfferingAdmin(admin.ModelAdmin):
     
    def has_equipment_conflicts(self, obj):
        """
        Returns True if ANY week in this offering has conflicts.
        """
        for week in obj.schedule_weeks.prefetch_related("meetings__experiment"):
            equipment_map = defaultdict(int)
    
            for meeting in week.meetings.all():
                for link in EquipmentExperiment.objects.filter(
                    experiment=meeting.experiment
                ):
                    if link.equipment_item:
                        equipment_map[link.equipment_item] += link.quantity_used or 1
    
            if detect_equipment_conflicts(equipment_map):
                return True

        return False
    
    has_equipment_conflicts.boolean = True
    has_equipment_conflicts.short_description = "Equipment Conflicts"
    
    def conflict_summary(self, obj):
        """
        Returns an HTML summary of weeks with conflicts.
        """
        rows = []
    
        for week in obj.schedule_weeks.prefetch_related("meetings__experiment"):
            equipment_map = defaultdict(int)
    
            for meeting in week.meetings.all():
                for link in EquipmentExperiment.objects.filter(
                    experiment=meeting.experiment
                ):
                    if link.equipment_item:
                        equipment_map[link.equipment_item] += link.quantity_used or 1
    
            conflicts = detect_equipment_conflicts(equipment_map)
    
            if conflicts:
                rows.append(
                    f"<li><strong>Week {week.week_number}</strong>: "
                    f"{len(conflicts)} conflict(s)</li>"
                )
    
        if not rows:
            return "No equipment conflicts detected."
    
        return format_html(
            "<ul>{}</ul>",
            format_html("".join(rows))
        )
    
    conflict_summary.short_description = "Equipment Conflict Summary"


    list_display = (
        "lab_course",
        "academic_term",
        "coordinator",
        "default_lab_room",
        "has_equipment_conflicts",
    )
    list_filter = (
        "academic_term",
        "lab_course",
    )
    search_fields = (
        "lab_course__course_code",
        "lab_course__course_title",
    )
    readonly_fields = ("conflict_summary",)
    fieldsets = (
        (None, {
            "fields": (
                "lab_course",
                "academic_term",
                "coordinator",
                "default_lab_room",
            )
        }),
        ("Equipment Warnings", {
            "fields": ("conflict_summary",),
        }),
    )

    inlines = [
        ScheduleWeekInline,
        LabSectionInline,
    ]
    
