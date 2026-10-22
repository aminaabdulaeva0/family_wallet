import pandas as pd
from prophet import Prophet
from datetime import datetime, timedelta
from .models import Expense
import logging

logging.getLogger('prophet').setLevel(logging.WARNING)
logging.getLogger('cmdstanpy').setLevel(logging.WARNING)

def get_forecast(user, days=7):
    start_date = datetime.now().date() - timedelta(days=90)
    expenses = Expense.objects.filter(user=user, date__gte=start_date).values('date', 'amount')

    if not expenses:
        return None

    df = pd.DataFrame(list(expenses))
    df = df.groupby('date')['amount'].sum().reset_index()
    df = df.rename(columns={'date': 'ds', 'amount': 'y'})
    
    # Защита от выбросов (не больше 100к в день)
    df['y'] = df['y'].clip(upper=100000)

    m = Prophet(daily_seasonality=False, weekly_seasonality=True, yearly_seasonality=False)
    m.fit(df)

    future = m.make_future_dataframe(periods=days)
    forecast = m.predict(future)

    tomorrow = datetime.now().date() + timedelta(days=1)
    future_forecast = forecast[forecast['ds'].dt.date >= tomorrow].copy()
    
    # Убираем минусы
    future_forecast['yhat'] = future_forecast['yhat'].clip(lower=0)

    # Данные для столбиков
    chart_data = []
    max_amount = max(future_forecast['yhat']) if not future_forecast.empty else 1
    if max_amount == 0: max_amount = 1

    for _, row in future_forecast.iterrows():
        chart_data.append({
            'date': row['ds'].strftime('%d.%m'),
            'amount': round(row['yhat'], 2),
            'height': (row['yhat'] / max_amount) * 100
        })

    # Итоговые цифры
    summary = []
    if days >= 1:
        summary.append({'period': 'Завтра', 'amount': round(future_forecast.iloc[0]['yhat'], 2)})
    if days >= 7:
        summary.append({'period': 'Следующая неделя', 'amount': round(future_forecast.iloc[:7]['yhat'].sum(), 2)})
    if days >= 30:
        summary.append({'period': 'Следующий месяц', 'amount': round(future_forecast.iloc[:30]['yhat'].sum(), 2)})

    return {
        'chart_data': chart_data,
        'summary': summary
    }
