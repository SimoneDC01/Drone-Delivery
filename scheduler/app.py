from flask import Flask, request
import requests

app = Flask(__name__)

#route that takes the time advanced from container time 
@app.route('/advance', methods=['POST'])
def advance():
    date = {'day': 21, 'month': 9, 'year': 2024} # {'day': int, 'month': int, 'year': int}
    time = {'hh': 12, 'mm': 0} # {'hh': int, 'mm': int}
    minutes = 30 #request.get_json()['minutes'] # int
    
    orders = getOrdersOfTheDay(date) # address, order_date_time{day, month, year, hh, mm}, delivery_date{day, month, year}, order_id, num_packages, priority
    print(orders)

    n_drones = 10 # need a database to store calculated number of drones and the schedule
    schedule = {'drone1': [{'1_1': {'start': '10:30', 'end': '11:00'}}, {'1_2': {'start': '11:00', 'end': '11:45'}}],
                'drone2': [{'1_3': {'start': '10:00', 'end': '10:40'}}, {'1_4': {'start': '10:40', 'end': '12:00'}}],
                'drone3': [{'1_5': {'start': '10:00', 'end': '11:30'}}, {'1_6': {'start': '11:30', 'end': '12:00'}}],
                }

    url = 'http://drones:8080/advance'

    for minute in range(minutes):
        data = {'schedule': schedule, 'time': time}
        response = requests.post(url, json=data)
        info = response.text # {drone1: {battery1 : value, battery2 : value, status : value(charging , delivering, going_back), is_strong_wind : value }, drone2 : {battery1 : value, battery2 : value, status : value(charging , delivering, going_back), is_strong_wind : value }, ... }
        
        # update schedule
        schedule = updateSchedule(schedule, info)
        # update time
        date, time = updateDateTime(date, time)
            


    return response.text + '[SCHEDULER]'

def updateSchedule(schedule, info):
    return {'drone1': [{'1_1': {'start': '10:30', 'end': '11:00'}}, {'1_2': {'start': '11:00', 'end': '11:45'}}],
            'drone2': [{'1_3': {'start': '10:00', 'end': '10:40'}}, {'1_4': {'start': '10:40', 'end': '12:00'}}],
            'drone3': [{'1_5': {'start': '10:00', 'end': '11:30'}}, {'1_6': {'start': '11:30', 'end': '12:00'}}],
            }

def updateDateTime(date, time, minutes = 1):
    time['mm'] += minutes
    if time['mm'] >= 60:
        time['mm'] -= 60
        time['hh'] += 1
        if time['hh'] >= 24:
            time['hh'] -= 24
            date['day'] += 1
            if date['day'] > 31:
                date['day'] -= 31
                date['month'] += 1
            elif date['day'] > 30 and date['month'] in [4, 6, 9, 11]:
                date['day'] -= 30
                date['month'] += 1
            elif date['day'] > 29 and date['month'] == 2 and date['year'] % 4 == 0 and (date['year'] % 100 != 0 or date['year'] % 400 == 0):
                date['day'] -= 29
                date['month'] += 1
            elif date['day'] > 28 and date['month'] == 2:
                date['day'] -= 28
                date['month'] += 1
            if date['month'] > 12:
                date['month'] -= 12
                date['year'] += 1
    return date, time

#function that asks to order-manager for all orders of the day passed as parameter and return a list of struct, each struct is an order.
def getOrdersOfTheDay(day):
    url = 'http://order-manager:8080/getOrdersOfTheDay'
    response = requests.post(url, json={'delivery_date': day})
    return response.text

#function that asks to order-manager to modify the Status of all lines having ID_Order and Num_Package
def UpdateStatusOfProducts():
    url = 'http://order-manager:8080/UpdateStatusProducts'
    order_package = "PROVA01_1"
    status = "Delivered"
    response = requests.post(url, json={'order-package': order_package, "status": status})
    print(response.text)

if __name__ == '__main__':
    app.run(debug=True)
