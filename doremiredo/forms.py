from django import forms
from .models import Course, Student, Expense, Payment
from datetime import date


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'price', 'description', 'frequency']


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'course', 'second_child', 'third_child', 'is_active']


class PaymentForm(forms.ModelForm):
    date = forms.DateField(
        initial=date.today,  # Set default to today's date
        widget=forms.DateInput(attrs={'type': 'date'})  # Enable calendar picker
    )

    class Meta:
        model = Payment
        fields = ['student', 'amount', 'date', 'model']


class ExpenseForm(forms.ModelForm):
    date = forms.DateField(
        initial=date.today,  # Set default to today's date
        widget=forms.DateInput(attrs={'type': 'date'})  # Enable calendar picker
    )

    class Meta:
        model = Expense
        fields = ['name', 'amount', 'date']


