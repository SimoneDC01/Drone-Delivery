from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import requests
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('time.sqlite')
    conn.row_factory = sqlite3.Row  # Per permettere di accedere ai dati come dizionari
    return conn

#route for respond with delivery_information on order_id to user-manager
@app.route('/advance', methods=['POST'])
def getDeliveryInfo():
    minutes = request.get_json()['minutes']
    #select date and time values in database
    conn = get_db_connection()
    query = "SELECT date, time FROM time LIMIT 1"
    row = conn.execute(query).fetchone()

    if row:
        date_parts = row['date'].split('/')
        day = int(date_parts[0])
        month = int(date_parts[1])
        year = int(date_parts[2])

        time_parts = row['time'].split(':')
        hour = int(time_parts[0])
        min = int(time_parts[1])

        date = {'day' : day, 'month': month, 'year' : year}
        time = {'hh' : hour, 'mm' : min }

        min += int(minutes)

        if min > 59:
            min -= 60
            hour += 1

        if hour >= 24:
            hour -= 24
            day += 1

            days_in_month = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                days_in_month[1] = 29
            else:
                days_in_month[1] = 28

            if day > days_in_month[month - 1]:
                day = 1
                month += 1
                if month > 12:
                    month = 1
                    year += 1

    new_date = f"{day:02d}/{month:02d}/{year:04d}"
    new_time = f"{hour:02d}:{min:02d}"

    url = 'http://scheduler:8080/advance'
    data = {'minutes': minutes, 'date': date, 'time' : time}
    response = requests.post(url, json=data)

    #update of date and time
    update_query = "UPDATE time SET date = ?, time = ?"
    conn.execute(update_query, (new_date, new_time))
    conn.commit()  

    conn.close()

    url = 'http://user-manager:8080/date_and_time_new'
    data = {'date_and_time': new_date+" "+new_time}
    requests.post(url, json=data)
    return jsonify({'date': new_date, 'time': new_time})

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
