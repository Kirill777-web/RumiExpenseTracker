from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum

# Create your models here.

SELECT_CATEGORY_CHOICES = [
    ('Food', 'Food'),
    ('Transport', 'Transport'),
    ('Entertainment', 'Entertainment'),
    ('Health', 'Health'),
    ('Other', 'Other'),
    ('Shopping', 'Shopping'),
    ('Rent', 'Rent'),
    ('Bills', 'Bills'),
]

ADD_EXPENSE_CHOICES = [
    ('Income', 'Income'),
    ('Expense', 'Expense'),
]

PROFESSION_CHOICES = [
    ('Student', 'Student'),
    ('Employee', 'Employee'),
    ('Business', 'Business'),
    ('Other', 'Other'),
]


class AddMoneyInfo(models.Model):
    user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    add_money = models.CharField(max_length=10, choices=ADD_EXPENSE_CHOICES)
    quantity = models.BigIntegerField()
    Date = models.DateTimeField(default=now)
    Category = models.CharField(
        max_length=20, choices=SELECT_CATEGORY_CHOICES, default='Shopping')

    class Meta:
        verbose_name = 'Add Money Info'
        verbose_name_plural = 'Add Money Info'
        db_table = 'addmoney'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profession = models.CharField(max_length=20, choices=PROFESSION_CHOICES)
    Savings = models.IntegerField(null=True, blank=True)
    income = models.IntegerField(null=True, blank=True)
    image = models.ImageField(upload_to='profile_pics', blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'
