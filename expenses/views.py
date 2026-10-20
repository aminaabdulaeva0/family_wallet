# Create your views here.
from django.shortcuts import render, redirect
from .models import Expense
from .forms import ExpenseForm
from django.db.models import Sum

def index(request, expense_id=None):
    # Если передан ID, значит мы хотим редактировать существующий расход
    instance = None
    if expense_id:
        instance = Expense.objects.get(id=expense_id)

    if request.method == 'POST':
        # Если instance передан, форма обновит запись, а не создаст новую
        form = ExpenseForm(request.POST, instance=instance) 
        if form.is_valid():
            form.save()
            return redirect('index')  # Возвращаемся на чистую главную
    else:
        # Если мы просто открыли страницу, форма пустая (или заполнена данными для редактирования)
        form = ExpenseForm(instance=instance)

    expenses_list = Expense.objects.all().order_by('-date')
    total_sum = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0

    return render(request, 'expenses/index.html', {
        'expenses': expenses_list,
        'form': form,
        'total_sum': total_sum,
        'edit_id': expense_id, # Передаем ID в шаблон, чтобы знать, что мы редактируем
    })

def delete_expense(request, expense_id):
    expense = Expense.objects.get(id=expense_id)  # Находим расход по ID
    expense.delete()  # Удаляем его из базы
    return redirect('index')  # Возвращаемся на главную
