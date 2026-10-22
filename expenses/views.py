from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Expense
from .forms import ExpenseForm
from django.contrib.auth.forms import UserCreationForm

def landing(request):
    return render(request, 'expenses/landing.html')

@login_required
def index(request, expense_id=None):
    instance = None
    if expense_id:
        # Пытаемся найти расход, принадлежащий текущему пользователю
        instance = Expense.objects.get(id=expense_id, user=request.user)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=instance)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user  # Привязываем к тому, кто вошел
            expense.save()
            return redirect('index')
    else:
        form = ExpenseForm(instance=instance)

    # Показываем ТОЛЬКО расходы текущего пользователя
    expenses_list = Expense.objects.filter(user=request.user).order_by('-date')
    total_sum = expenses_list.aggregate(total=Sum('amount'))['total'] or 0

    return render(request, 'expenses/index.html', {
        'expenses': expenses_list,
        'form': form,
        'total_sum': total_sum,
        'edit_id': expense_id,
    })

@login_required
def delete_expense(request, expense_id):
    # Удалить можно только свой расход
    expense = Expense.objects.get(id=expense_id, user=request.user)
    expense.delete()
    return redirect('index')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
