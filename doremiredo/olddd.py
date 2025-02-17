from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum, Max
from collections import defaultdict
from datetime import datetime, date, timedelta
from .models import Course, Student, Payment, Expense
from .forms import CourseForm, StudentForm, ExpenseForm, PaymentForm


def home(request):
    # Get the current year
    current_year = date.today().year

    # Generate month names and numbers
    months = [(date(current_year, i, 1).strftime('%B'), i) for i in range(1, 13)]

    # Initialize month_data list
    month_data = []

    for month_name, month_number in months:
        total_payments = Payment.objects.filter(
            date__year=current_year, date__month=month_number
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        total_expenses = Expense.objects.filter(
            date__year=current_year, date__month=month_number
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        month_data.append((month_name, total_payments, total_expenses, month_number))

    # Get today's date and the next 3 days
    today = date.today()
    three_days_later = today + timedelta(days=3)

    # Prepare lists for due and overdue students
    due_students = []
    overdue_students = []

    # Fetch the latest payment per student
    latest_payments = Payment.objects.values('student').annotate(latest_payment=Max('date'))

    # Convert queryset into a dictionary for easy lookup
    student_latest_payment = {p['student']: p['latest_payment'] for p in latest_payments}

    print("\n DEBUG: Latest Payments Per Student:")
    for student_id, last_paid_date in student_latest_payment.items():
        print(f"  Student ID: {student_id} | Last Paid: {last_paid_date}")

    for student in Student.objects.all():
        last_paid_date = student_latest_payment.get(student.id)

        if last_paid_date:
            due_date = last_paid_date + timedelta(days=30)  # Expected next payment date

            print(f"   Checking {student.name} | Last Paid: {last_paid_date} | Due: {due_date}")

            if today <= due_date <= three_days_later:
                print(f"   Alert: {student.name} is due soon!")
                due_students.append({'name': student.name, 'due_date': due_date})

            elif due_date < today:
                print(f"   Overdue: {student.name} is overdue!")
                overdue_students.append({'name': student.name, 'due_date': due_date})

    context = {
        'month_data': month_data,
        'due_students': due_students,
        'overdue_students': overdue_students,
        'today': today,
    }

    return render(request, 'home.html', context)


def monthly_details(request, month_number):
    current_year = datetime.now().year

    # Get payments and expenses for the selected month
    payments = Payment.objects.filter(date__year=current_year, date__month=month_number)
    expenses = Expense.objects.filter(date__year=current_year, date__month=month_number)

    # Convert month number to month name
    month_name = datetime(current_year, month_number, 1).strftime('%B')

    context = {
        'month_name': month_name,
        'payments': payments,
        'expenses': expenses
    }

    return render(request, 'monthly_details.html', context)








