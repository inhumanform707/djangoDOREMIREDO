from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('courses/', views.list_course, name='list_course'),
    path('courses/add/', views.add_course, name='add_course'),
    path('courses/edit/<int:course_id>/', views.edit_course, name='edit_course'),
    path('courses/delete/<int:course_id>/', views.delete_course, name='delete_course'),
    path('students/', views.list_student, name='list_student'),
    path('students/add/', views.add_student, name='add_student'),
    path('students/edit/<int:student_id>/', views.edit_student, name='edit_student'),
    path('students/delete/<int:student_id>', views.delete_student, name='delete_student'),
    path('payments/', views.list_payment, name='list_payment'),
    path('payments/add/', views.add_payment, name='add_payment'),
    path('payments/edit/<int:payment_id>/', views.edit_payment, name='edit_payment'),
    path('payments/delete/<int:payment_id>/', views.delete_payment, name='delete_payment'),
    path('expenses/', views.list_expense, name='list_expense'),
    path('expenses/add/', views.add_expense, name='add_expense'),
    path('expenses/edit/<int:expense_id>/', views.edit_expense, name='edit_expense'),
    path('expenses/delete/<int:expense_id>/', views.delete_expense, name='delete_expense'),
    path('monthly_details/<str:month>/', views.monthly_details, name='monthly_details'),
]




