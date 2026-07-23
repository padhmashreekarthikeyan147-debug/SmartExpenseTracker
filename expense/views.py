from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from requests import request
from .forms import RegisterForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Expense
from .forms import ExpenseForm
from .utils import predict_category
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
import json

import csv
import pandas as pd
from django.http import HttpResponse
from django.core.paginator import Paginator
from reportlab.pdfgen import canvas
from django.db.models import Sum

from .models import Budget
from .forms import BudgetForm
def register(request):

    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():

            user = form.save()
            login(request, user)
            return redirect('dashboard')

    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


def user_login(request):

    if request.method == "POST":

        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():

            user = form.get_user()
            login(request, user)
            return redirect('dashboard')

    else:

        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


def user_logout(request):

    logout(request)
    return redirect('login')


@login_required
def dashboard(request):

    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    expenses = Expense.objects.filter(user=request.user)

    # Dashboard Cards
    total = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    today_total = expenses.filter(
        date=today
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    week_total = expenses.filter(
        date__gte=week_start
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    month_total = expenses.filter(
        date__gte=month_start
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    budget = Budget.objects.filter(user=request.user).first()

    budget_amount = budget.amount if budget else 0

    remaining = budget_amount - month_total

    alert = False

    if budget and month_total > budget.amount:
        alert = True

    # Pie & Bar Chart
    category_data = (
        expenses.values('category')
        .annotate(total=Sum('amount'))
        .order_by('category')
    )

    labels = []
    values = []

    for item in category_data:
        labels.append(item["category"])
        values.append(float(item["total"]))

    # Monthly Line Chart
    monthly = (
        expenses.values("date__month")
        .annotate(total=Sum("amount"))
        .order_by("date__month")
    )

    months = []
    monthly_values = []

    for item in monthly:
        months.append(str(item["date__month"]))
        monthly_values.append(float(item["total"]))

    context = {
        "total": total,
        "today_total": today_total,
        "week_total": week_total,
        "month_total": month_total,

        "labels": json.dumps(labels),
        "values": json.dumps(values),

        "months": json.dumps(months),
        "monthly_values": json.dumps(monthly_values),
        "budget": budget_amount,
        "remaining": remaining,
        "alert": alert,
    }

    return render(request, "dashboard.html", context)

@login_required
def expense_list(request):

    expense_list = Expense.objects.filter(user=request.user).order_by("-date")

    paginator = Paginator(expense_list, 10)

    page = request.GET.get("page")

    expenses = paginator.get_page(page)

    context = {
        "expenses": expenses,
        "total": expense_list.aggregate(Sum("amount"))["amount__sum"] or 0,
    }

    return render(request, "expense_list.html", context)

@login_required
def add_expense(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST)

        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user

            if not expense.category:
                expense.category = "Others"

            expense.save()

            return redirect("expense_list")
        else:
            return render(request, "add_expense.html", {
        "form": form,
        "errors": form.errors
    })
    else:
        form = ExpenseForm()

    return render(request, "add_expense.html", {"form": form})

@login_required
def edit_expense(request, pk):

    expense = get_object_or_404(
        Expense,
        pk=pk,
        user=request.user
    )

    if request.method == "POST":

        form = ExpenseForm(request.POST, instance=expense)

        if form.is_valid():
            form.save()
            return redirect('expense_list')

    else:

        form = ExpenseForm(instance=expense)

    return render(request, 'edit_expense.html', {'form': form})


@login_required
def delete_expense(request, pk):

    expense = get_object_or_404(
        Expense,
        pk=pk,
        user=request.user
    )

    expense.delete()

    return redirect('expense_list')


@login_required
def export_csv(request):

    response = HttpResponse(content_type="text/csv")

    response["Content-Disposition"] = 'attachment; filename="expenses.csv"'

    writer = csv.writer(response)

    writer.writerow([
        "Description",
        "Category",
        "Amount",
        "Date"
    ])

    expenses = Expense.objects.filter(user=request.user)

    for expense in expenses:

        writer.writerow([
            expense.description,
            expense.category,
            expense.amount,
            expense.date
        ])

    return response

@login_required
def export_pdf(request):

    response = HttpResponse(content_type="application/pdf")

    response["Content-Disposition"] = 'attachment; filename="expenses.pdf"'

    p = canvas.Canvas(response)

    p.setFont("Helvetica-Bold",16)

    p.drawString(180,800,"Expense Report")

    y = 760

    expenses = Expense.objects.filter(user=request.user)

    for expense in expenses:

        line = f"{expense.date} | {expense.description} | ₹{expense.amount} | {expense.category}"

        p.setFont("Helvetica",10)

        p.drawString(40,y,line)

        y -= 20

        if y < 50:

            p.showPage()

            y = 800

    p.save()

    return response

@login_required
def budget(request):

    budget, created = Budget.objects.get_or_create(user=request.user)

    if request.method == "POST":

        form = BudgetForm(request.POST, instance=budget)

        if form.is_valid():
            form.save()
            return redirect("dashboard")

    else:

        form = BudgetForm(instance=budget)

    return render(request, "budget.html", {
        "form": form
    })

@login_required
def profile(request):

    expenses = Expense.objects.filter(user=request.user)

    context = {

        "total_count": expenses.count(),

        "total": expenses.aggregate(
            Sum("amount")
        )["amount__sum"] or 0

    }

    return render(
        request,
        "profile.html",
        context
    )