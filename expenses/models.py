from django.db import models
from django.utils import timezone
from django.utils.timezone import now
from django.contrib.auth.models import User

SELECT_CATEGORY_CHOICES = [
    ('Food', 'Food'),
    ('Transport', 'Transport'),
    ('Entertainment', 'Entertainment'),
    ('Health', 'Health'),
    ('Other', 'Other'),
    ('Shopping', 'Shopping'),
    ('Rent', 'Rent'),
    ('Bills', 'Bills'),
    ('Salary', 'Salary'),
]

ADD_EXPENSE_CHOICES = [
    ('Income', 'Income'),
    ('Expense', 'Expense'),
]


class AddMoneyInfo(models.Model):
    user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    add_money = models.CharField(max_length=10, choices=ADD_EXPENSE_CHOICES)
    quantity = models.BigIntegerField()
    description = models.TextField(max_length=100)
    Date = models.DateTimeField(default=timezone.now)
    Category = models.CharField(
        max_length=20, choices=SELECT_CATEGORY_CHOICES, default='Shopping')

    class Meta:
        verbose_name = 'Add Money Info'
        verbose_name_plural = 'Add Money Info'
        db_table = 'addmoney'
