import json
from collections import defaultdict
from datetime import datetime,timedelta
from flask import render_template
import plotly.graph_objects as go
from app import app

try:
    with app.open_resource('data/users.json') as f:
      users = json.load(f)['users']
    with app.open_resource('data/simulations.json') as f:
      simulations = json.load(f)['simulations']
except (FileNotFoundError, json.JSONDecodeError) as e:
    printf(f"Error loading files: {e}")
    users = []
    simulations = []

def process_data():
    company_user_counts = defaultdict(int)
    for user in users:
        simulation_id = user['simulation_id']
        company_id = next((sim['company_id'] for sim in simulations if sim['simulation_id'] == simulation_id), None)
        if company_id:
            company_user_counts[company_id] += 1
    
    daily_user_counts = defaultdict(int)
    for user in users:
          excel_date = user.get('signup_datetime')
          if excel_date is not None:
            try:
                signup_datetime = datetime(1900, 1,1) + timedelta(days=excel_date)  
                signup_date = signup_datetime.date()
                daily_user_counts[signup_date] += 1
            except (TypeError, OverflowError) as e:
                print(f"Error processing date for user {user}: {e}")
    
    return company_user_counts, daily_user_counts

@app.route('/')
def index():
    company_user_counts, daily_user_counts = process_data()

    company_table = []
    for company_id, user_count in company_user_counts.items():
        company_name = next((sim['company_name'] for sim in simulations if sim['company_id'] == company_id), 'Unknown')
        company_table.append({'company_name': company_name, 'user_count': user_count})

    dates = list(daily_user_counts.keys())
    counts = list(daily_user_counts.values())
  

    data = [dict(
        type='scatter',
        mode='markers',
        x=dates,
        y=counts,
        marker=dict(
            color='rgba(0, 116, 217, 0.8)',
            line=dict(
                color='rgb(0, 0, 0)',
                width=1
            )
        )
    )]

    layout = dict(
        xaxis=dict(title='Tarih'),
        yaxis=dict(title='Kullanıcı Sayısı')
    )

    fig = go.Figure(data=data, layout=layout)
    graph_html = fig.to_html(full_html=False)

    return render_template('index.html', company_table=company_table, graph_html=graph_html)
    
