from django.shortcuts import render
from django.db.models import Sum
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from equipment.forms import PurchaseRecordForm, RepairLogForm, EquipmentRequestForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django import forms
from collections import defaultdict
from django.utils import timezone
from datetime import date
from scheduling.models import (
    AcademicTerm,
    LabCourse,
    LabOffering,
    ScheduleWeek,
    WeekMeeting,
    LabSection,
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
    EquipmentRequest,
    ExperimentEquipmentRequirement,
)

def is_purchasing_user(user):
    return user.groups.filter(name="Purchasing").exists()

def is_instructor(user):
    return user.groups.filter(name="Instructor").exists()

def get_default_term():
    today = date.today()

    # current term
    current = AcademicTerm.objects.filter(
        start_date__lte=today,
        end_date__gte=today
    ).first()

    if current:
        return current

    # upcoming term
    upcoming = AcademicTerm.objects.filter(
        start_date__gt=today
    ).order_by("start_date").first()

    return upcoming


@user_passes_test(is_purchasing_user)

def purchasing_dashboard_view(request):

    # Handle form submission
    if request.method == "POST":
        form = PurchaseRecordForm(request.POST)

        if form.is_valid():
            form.save()
        
            # Add success message
            messages.success(request, "Purchase added successfully.")
        
            return redirect("purchasing_dashboard")
        
    else:
        form = PurchaseRecordForm()

    # Summary data
    total_spent = PurchaseRecord.objects.aggregate(
        total=Sum("extended_cost")
    )["total"] or 0

    recent_purchases = PurchaseRecord.objects.order_by("-date_ordered")[:15]

    return render(
        request,
        "equipment/purchasing_dashboard.html",
        {
            "total_spent": total_spent,
            "recent_purchases": recent_purchases,
            "form": form,   # NEW
        }
    )


User = get_user_model()


@login_required
def home_dashboard_view(request):
    user = request.user

    context = {
        "is_purchasing": user.groups.filter(name="Purchasing").exists(),
        "is_admin": user.is_superuser or user.is_staff,
        "is_instructor": user.groups.filter(name="Instructor").exists(),
    }

    return render(request, "equipment/home_dashboard.html", context)


def root_redirect_view(request):
    if request.user.is_authenticated:
        return redirect("home_dashboard")

    return redirect("login")



@login_required
def repair_dashboard_view(request):

    # Handle form submission
    if request.method == "POST":
        form = RepairLogForm(request.POST)

        if form.is_valid():
            repair = form.save(commit=False)

            # auto-fill today's date if missing
            if not repair.date_reported:
                repair.date_reported = timezone.now().date()

            repair.save()

            messages.success(request, "Repair request submitted.")
            return redirect("repair_dashboard")
    else:
        form = RepairLogForm()

    # Open repairs (no repair_action yet)
    open_repairs = RepairLog.objects.filter(
        repair_action__exact=""
    ).select_related("equipment")

    # Recently resolved (optional)
    recent_resolved = RepairLog.objects.exclude(
        repair_action__exact=""
    ).order_by("-created_at")[:10]

    return render(
        request,
        "equipment/repair_dashboard.html",
        {
            "form": form,
            "open_repairs": open_repairs,
            "recent_resolved": recent_resolved,
        }
    )


@login_required
def request_dashboard_view(request):

    if request.method == "POST":
        form = EquipmentRequestForm(request.POST)

        if form.is_valid():
            req = form.save(commit=False)
            req.requested_by = request.user
            req.save()

            messages.success(request, "Request submitted.")
            return redirect("request_dashboard")
    else:
        form = EquipmentRequestForm()

    # pending requests
    pending_requests = EquipmentRequest.objects.filter(
        status="pending"
    ).order_by("-created_at")

    return render(
        request,
        "equipment/request_dashboard.html",
        {
            "form": form,
            "pending_requests": pending_requests,
        }
    )

@login_required
@user_passes_test(is_instructor)
def experiment_dashboard_view(request):

    experiments = Experiment.objects.prefetch_related(
        "equipment_requirements__equipment_type"
    ).order_by("experiment_title")

    return render(
        request,
        "equipment/experiment_dashboard.html",
        {
            "experiments": experiments,
        }
    )


@login_required
def scheduling_dashboard_view(request):

    # STEP 1 — Determine term
    term_id = request.GET.get("term")

    if term_id:
        selected_term = AcademicTerm.objects.get(id=term_id)
    else:
        today = date.today()

        selected_term = AcademicTerm.objects.filter(
            start_date__lte=today,
            end_date__gte=today
        ).first()

        if not selected_term:
            selected_term = AcademicTerm.objects.order_by("start_date").first()

    terms = AcademicTerm.objects.all().order_by("-start_date")

    # STEP 2 — Get courses
    

    courses = LabCourse.objects.filter(
        offerings__academic_term=selected_term
    ).distinct().prefetch_related(
        "offerings__schedule_weeks__meetings__experiment__equipment_requirements"
    )

                           

    # STEP 3 — Build schedule by week
    course_schedule = {}
    
    for course in courses:
        weekly = defaultdict(list)
    
        for offering in course.offerings.all():
            for week in offering.schedule_weeks.all():
                for meeting in week.meetings.all():
                    week_num = week.id   # simple key for now
                    weekly[week_num].append(meeting)
    
        course_schedule[course] = dict(weekly)


    # STEP 4 — Aggregate requirements
    weekly_requirements = defaultdict(lambda: defaultdict(int))

    for course, weeks in course_schedule.items():
        for week, meetings in weeks.items():
            for meeting in meetings:
                exp = meeting.experiment
                
                if not exp:   
                    continue


                for req in exp.equipment_requirements.all():
                    weekly_requirements[week][req.equipment_type] += req.quantity_required

    # STEP 5 — Availability (simple count)
    availability = {}
    
    for eq_type in EquipmentType.objects.all():
        total = EquipmentItem.objects.filter(
            equipment_type=eq_type
        ).aggregate(
            total_qty=Sum("quantity")
        )["total_qty"]
    
        availability[eq_type] = total if total is not None else 0

    # STEP 6 — Detect conflicts
    conflicts = {}

    for week, reqs in weekly_requirements.items():
        week_conflicts = []

        for eq_type, needed in reqs.items():
            available = availability.get(eq_type, 0)

            if needed > available:
                week_conflicts.append({
                    "equipment_type": eq_type,
                    "needed": needed,
                    "available": available,
                })

        if week_conflicts:
            conflicts[week] = week_conflicts

    return render(
        request,
        "equipment/scheduling_dashboard.html",
        {
            "terms": terms,
            "selected_term": selected_term,
            "course_schedule": course_schedule,
            "conflicts": conflicts,
        }
    )
