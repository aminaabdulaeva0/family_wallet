from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Expense
from .forms import ExpenseForm
from django.contrib.auth.forms import UserCreationForm
from datetime import datetime, timedelta 

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
@login_required
def reports(request):
    period = request.GET.get('period', 'month')
    
    today = datetime.now().date()
    if period == 'today':
        start_date = today
    elif period == '3days':
        start_date = today - timedelta(days=3)
    elif period == 'week':
        start_date = today - timedelta(days=7)
    else: # month
        start_date = today - timedelta(days=30)

    expenses = Expense.objects.filter(user=request.user, date__gte=start_date)
    
    # --- Данные для КРУГОВОЙ диаграммы ---
    category_data = expenses.values('category').annotate(total=Sum('amount'))
    total_all = expenses.aggregate(total=Sum('amount'))['total'] or 0
    
    report_data = []
    category_names = dict(Expense.CATEGORY_CHOICES)
    colors = ['#800020', '#D4AF37', '#34495e', '#27ae60', '#3498db']
    
    current_angle = 0
    gradient_parts = []
    
    temp_data = []
    for item in category_data:
        cat_key = item['category']
        cat_name = category_names.get(cat_key, cat_key)
        amount = item['total']
        percent = round((amount / total_all) * 100, 1) if total_all > 0 else 0
        temp_data.append({'name': cat_name, 'amount': amount, 'percent': percent})
    
    temp_data = sorted(temp_data, key=lambda x: x['amount'], reverse=True)
    
    for i, item in enumerate(temp_data):
        color = colors[i % len(colors)]
        angle = (item['amount'] / total_all) * 360 if total_all > 0 else 0
        gradient_parts.append(f"{color} {current_angle}deg {current_angle + angle}deg")
        current_angle += angle
        item['color'] = color
        report_data.append(item)
    
    gradient_css = f"conic-gradient({', '.join(gradient_parts)})" if gradient_parts else "#eee"

    # --- Данные для СТОЛБЧАТОЙ диаграммы (по дням) ---
    # Группируем по дате и считаем сумму за каждый день
    daily_data = expenses.values('date').annotate(total=Sum('amount')).order_by('date')
    
    bar_data = []
    max_daily_amount = max([d['total'] for d in daily_data]) if daily_data else 1
    
    for day in daily_data:
        # Вычисляем высоту столбика в процентах от максимального значения
        height_percent = (day['total'] / max_daily_amount) * 100
        bar_data.append({
            'date': day['date'].strftime('%d.%m'),
            'amount': day['total'],
            'height': height_percent
        })

    return render(request, 'expenses/reports.html', {
        'report_data': report_data,
        'total_all': total_all,
        'current_period': period,
        'gradient_css': gradient_css,
        'bar_data': bar_data, # Передаем данные для столбиков
    })
