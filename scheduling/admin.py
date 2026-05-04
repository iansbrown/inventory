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

@admin.register(AcademicTerm)
class AcademicTermAdmin(admin.ModelAdmin):
    list_display = ("name", "term_type", "start_date", "end_date")
    list_filter = ("term_type",)
    ordering = ("start_date",)


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
    list_display = (
        "lab_course",
        "academic_term",
        "coordinator",
        "default_lab_room",
    )
    list_filter = (
        "academic_term",
        "lab_course",
    )
    search_fields = (
        "lab_course__course_code",
        "lab_course__course_title",
    )

    inlines = [
        ScheduleWeekInline,
        LabSectionInline,
    ]
    
