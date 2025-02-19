from django.db import models


class Course(models.Model):
    MONTHLY = 'monthly'
    SINGLE = 'single'

    FREQUENCY_CHOICES = [
        (MONTHLY, 'Monthly'),
        (SINGLE, 'Single'),
    ]

    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=4, decimal_places=0)
    description = models.TextField(blank=True)
    frequency = models.CharField(
        max_length=10,
        choices=FREQUENCY_CHOICES,
        default=MONTHLY
    )

    def __str__(self):
        return self.name


class Student(models.Model):
    name = models.CharField(max_length=100, unique=True)
    second_child = models.BooleanField(default=False)
    third_child = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_last_payment_date(self):
        """Returns the most recent payment date for this student."""
        last_payment = Payment.objects.filter(student=self).order_by('-date').first()
        return last_payment.date if last_payment else "No payments"


class Payment(models.Model):
    CASH = 'cash'
    M_BANKING = 'm_banking'
    CARD = 'card'

    MODEL_CHOICES = [
        (CASH, 'cash'),
        (M_BANKING, 'm_banking'),
        (CARD, 'card')
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=0)
    date = models.DateField()
    model = models.CharField(max_length=10, choices=MODEL_CHOICES, default=CASH)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.student.name} - {self.amount} on {self.date}"

    def get_course_price(self):
        """ Returns the price of the course the student is enrolled in. """
        return self.student.course.price if self.student.course else None  # Handle case where student has no course

    def get_course(self):
        """ Returns the course the student is enrolled in. """
        return self.student.course if self.student.course else None


class Expense(models.Model):
    name = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} - {self.amount} on {self.date}"
