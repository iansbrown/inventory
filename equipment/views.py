from django.shortcuts import render
from django.db.models import Sum
from equipment.models import PurchaseRecord
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test
from equipment.forms import PurchaseRecordForm
from django.contrib import messages


def is_purchasing_user(user):
    return user.groups.filter(name="Purchasing").exists()


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
        total=Sum("total_cost")
    )["total"] or 0

    recent_purchases = PurchaseRecord.objects.order_by(
        "-purchase_date"
    )[:15]

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


def post_login_redirect(request):
    user = request.user

    # ✅ If user is in Purchasing group → send to dashboard
    if user.groups.filter(name="Purchasing").exists():
        return redirect("purchasing_dashboard")

    # ✅ Otherwise go to normal admin
    return redirect("/admin/")
