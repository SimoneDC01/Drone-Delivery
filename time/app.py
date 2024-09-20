from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import requests
import sqlite3
import copy

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('time.sqlite')
    conn.row_factory = sqlite3.Row  # Per permettere di accedere ai dati come dizionari
    return conn

#route for respond with delivery_information on order_id to user-manager
@app.route('/advance', methods=['POST'])
def advance():
    minutes = int(request.get_json()['minutes'])
    #select date and time values in database
    conn = get_db_connection()
    query = "SELECT date, time FROM time LIMIT 1"
    row = conn.execute(query).fetchone()

    date_parts = row['date'].split('/')
    day = int(date_parts[0])
    month = int(date_parts[1])
    year = int(date_parts[2])

    time_parts = row['time'].split(':')
    hour = int(time_parts[0])
    min = int(time_parts[1])

    date = {'day' : day, 'month': month, 'year' : year}
    time = {'hh' : hour, 'mm' : min }

    new_date, new_time = updateDateTime(date, time, minutes)

    new_date = f"{new_date['day']:02d}/{new_date['month']:02d}/{new_date['year']:04d}"
    new_time = f"{new_time['hh']:02d}:{new_time['mm']:02d}"

    url = 'http://scheduler:8080/advance'
    data = {'minutes': minutes, 'date': date, 'time' : time}
    response = requests.post(url, json=data).json()
    schedule = response['schedule']
    log = response['log']

    #update of date and time
    update_query = "UPDATE time SET date = ?, time = ?"
    conn.execute(update_query, (new_date, new_time))
    conn.commit()  

    conn.close()

    url = 'http://user-manager:8080/date_and_time_new'
    data = {'date_and_time': new_date+" "+new_time}
    requests.post(url, json=data)

    return jsonify({'date': new_date, 'time': new_time,'schedule': schedule, 'log': log})

def updateDateTime(date, time, minutes = 1):
    date = copy.deepcopy(date)
    time = copy.deepcopy(time)

    time['mm'] += minutes

    if time['mm'] >= 60:
        extra_hours = time['mm'] // 60
        time['mm'] %= 60
        time['hh'] += extra_hours

    if time['hh'] >= 24:
        extra_days = time['hh'] // 24
        time['hh'] %= 24
        date['day'] += extra_days

    is_leap_year = date['year'] % 4 == 0 and (date['year'] % 100 != 0 or date['year'] % 400 == 0)

    if date['month'] in [4, 6, 9, 11]:
        days_in_current_month = 30
    elif date['month'] == 2:
        days_in_current_month = 29 if is_leap_year else 28
    else:
        days_in_current_month = 31

    while date['day'] > days_in_current_month:
        date['day'] -= days_in_current_month
        date['month'] += 1

        if date['month'] > 12:
            date['month'] = 1
            date['year'] += 1

        if date['month'] in [4, 6, 9, 11]:
            days_in_current_month = 30
        elif date['month'] == 2:
            days_in_current_month = 29 if is_leap_year else 28
        else:
            days_in_current_month = 31

    return date, time

@app.route('/date_and_time_request', methods=['POST'])
def date_and_time_request():
    conn = get_db_connection()
    query = "SELECT date, time FROM time LIMIT 1"
    row = conn.execute(query).fetchone()
    conn.close()

    if row:
        date_time_data = {'date': row['date'], 'time': row['time']}
    else:
        date_time_data = {'error': 'No data found'}

    return jsonify(date_time_data)


if __name__ == '__main__':
    app.run(debug=True)
