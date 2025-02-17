from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime, date, timedelta
from django.utils.timezone import now
from django.db.models import Sum
from .models import Course, Student, Payment, Expense
from .forms import CourseForm, StudentForm, ExpenseForm, PaymentForm
import json


@login_required
def home(request):
    # Get current year
    current_year = datetime.now().year

    # Month names
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    # Prepare a list of dictionaries with month, payments, and expenses
    monthly_data = []
    for month in range(1, 13):
        total_payments = Payment.objects.filter(date__year=current_year, date__month=month).aggregate(Sum('amount'))['amount__sum'] or 0
        total_expenses = Expense.objects.filter(date__year=current_year, date__month=month).aggregate(Sum('amount'))['amount__sum'] or 0

        # Convert Decimal to float to avoid JSON serialization error
        monthly_data.append({
            "month": months[month - 1],
            "payments": float(total_payments),
            "expenses": float(total_expenses)
        })

    # Fetch students and check due payments
    today = datetime.today().date()
    alerts = []

    for student in Student.objects.filter(is_active=True):  # Only active students
        last_payment = student.get_last_payment_date()

        if last_payment == "No payments" or last_payment is None:
            continue  # Skip students with no payments

        if isinstance(last_payment, str):
            last_payment = datetime.strptime(last_payment, "%Y-%m-%d").date()  # Convert string to date

        if student.course:  # Ensure student has a course
            if student.course.frequency == "monthly":
                next_due_date = last_payment + timedelta(days=30)
            else:
                next_due_date = None  # Single-payment courses do not have recurring due dates

            if next_due_date:
                days_until_due = (next_due_date - today).days

                if 0 <= days_until_due <= 3:  # Due in 3 or fewer days
                    alerts.append({"student_name": student.name, "due_date": next_due_date, "urgent": False})
                elif days_until_due < 0:  # Already overdue
                    alerts.append({"student_name": student.name, "due_date": next_due_date, "urgent": True})

    # Pass data to the template
    context = {
        "monthly_data": monthly_data,
        "months": json.dumps([data["month"] for data in monthly_data]),
        "payments_per_month": json.dumps([data["payments"] for data in monthly_data]),
        "expenses_per_month": json.dumps([data["expenses"] for data in monthly_data]),
        "alerts": alerts,
    }

    return render(request, 'home.html', context)


def monthly_details(request, month):
    # Convert month name to number
    month_number = datetime.strptime(month, "%B").month

    # Get current year
    current_year = datetime.now().year

    # Filter payments & expenses for selected month
    payments = Payment.objects.filter(date__year=current_year, date__month=month_number)
    expenses = Expense.objects.filter(date__year=current_year, date__month=month_number)

    context = {
        "month": month,
        "payments": payments,
        "expenses": expenses,
    }

    return render(request, 'monthly_details.html', context)


# COURSE VIEWS


def list_course(request):
    courses = Course.objects.all()
    return render(request, 'list_course.html', {'courses': courses})


def add_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_course')
    else:
        form = CourseForm()
    return render(request, 'add_course.html', {'form': form})


def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('list_course')
    else:
        form = CourseForm(instance=course)

    return render(request, 'edit_course.html', {'form': form, 'course': course})


def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        course.delete()
        return redirect('list_course')

    return render(request, 'confirm_delete_course.html', {'course': course})


# STUDENT VIEWS


def list_student(request):
    status = request.GET.get('status', 'active')  # Default to active students

    if status == 'inactive':
        students = Student.objects.filter(is_active=False)
    else:
        students = Student.objects.filter(is_active=True)

    context = {
        'students': students,
        'status': status
    }

    return render(request, 'list_student.html', context)


def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_student')
    else:
        form = StudentForm()

    return render(request, 'add_student.html', {'form': form})


def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('list_student')
    else:
        form = StudentForm(instance=student)

    return render(request, 'edit_student.html', {'form': form, 'student': student})


def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    if request.method == 'POST':
        student.delete()
        return redirect('list_student')  # Redirect back to student list

    return render(request, 'confirm_delete_student.html', {'student': student})


# PAYMENT VIEWS


def list_payment(request):
    today = now().date()
    selected_month = request.GET.get('month', today.strftime('%Y-%m'))  # Default: current month (YYYY-MM)

    try:
        year, month = map(int, selected_month.split('-'))
    except ValueError:
        year, month = today.year, today.month  # Fallback in case of invalid input

    # Filter payments by selected month
    payments = Payment.objects.filter(date__year=year, date__month=month).order_by('-date')

    # Generate month options (last 12 months)
    months = [(today.replace(month=i).strftime('%Y-%m'), today.replace(month=i).strftime('%B %Y')) for i in
              range(1, 13)]

    return render(request, 'list_payment.html', {
        'payments': payments,
        'selected_month': selected_month,
        'months': months,
    })


def add_payment(request):
    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_payment')
    else:
        form = PaymentForm()

    return render(request, 'add_payment.html', {'form': form})


def edit_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)

    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            form.save()
            return redirect('list_payment')  # Redirect back to payment list
    else:
        form = PaymentForm(instance=payment)

    return render(request, 'edit_payment.html', {'form': form, 'payment': payment})


def delete_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)

    if request.method == 'POST':
        payment.delete()
        return redirect('list_payment')  # Redirect back to payment list

    return render(request, 'confirm_delete_payment.html', {'payment': payment})


# EXPENSE VIEWS


def list_expense(request):
    today = now().date()
    selected_month = request.GET.get('month', today.strftime('%Y-%m'))  # Default: current month (YYYY-MM)

    try:
        year, month = map(int, selected_month.split('-'))
    except ValueError:
        year, month = today.year, today.month  # Fallback in case of invalid input

    # Filter payments by selected month
    expenses = Expense.objects.filter(date__year=year, date__month=month).order_by('-date')

    # Generate month options (last 12 months)
    months = [(today.replace(month=i).strftime('%Y-%m'), today.replace(month=i).strftime('%B %Y')) for i in
              range(1, 13)]

    return render(request, 'list_expense.html', {
        'expenses': expenses,
        'selected_month': selected_month,
        'months': months,
    })


def add_expense(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_expense')
    else:
        form = ExpenseForm()

    return render(request, 'add_expense.html', {'form': form})


def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('list_expense')  # Redirect back to expense list
    else:
        form = ExpenseForm(instance=expense)

    return render(request, 'edit_expense.html', {'form': form, 'expense': expense})


def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)

    if request.method == 'POST':
        expense.delete()
        return redirect('list_expense')  # Redirect back to expense list

    return render(request, 'confirm_delete_expense.html', {'expense': expense})

