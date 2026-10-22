from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('food', 'Еда'),
        ('transport', 'Транспорт'),
        ('fun', 'Развлечения'),
        ('health', 'Здоровье'),
        ('other', 'Другое'),
    ]
    
    title = models.CharField(max_length=100, verbose_name="Название")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other', verbose_name="Категория")
    date = models.DateField(auto_now_add=True, verbose_name="Дата")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Кто потратил")

def __str__(self):
        return f"{self.title} — {self.amount}"
