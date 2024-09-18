from flask import Flask, request
import requests
import numpy as np

app = Flask(__name__)

#route that takes the time advanced from container time 
@app.route('/advance', methods=['POST'])
def advance():
    # These will be the parameters of the request
    date = {'day': 21, 'month': 9, 'year': 2024} # {'day': int, 'month': int, 'year': int}
    time = {'hh': 10, 'mm': 30} # {'hh': int, 'mm': int}
    minutes = 30 #request.get_json()['minutes'] # int
    
    # Database: n_drones(date, n_drones), schedule(order_package, drone_id, start_time, end_time)
    n_drones = loadN_drones(date)
    schedule = loadSchedule()

    print(f"n_drones: {n_drones}")
    print(f"schedule: {schedule}")

    url = 'http://drones:8080/advance'

    for _ in range(minutes):
        if time['hh'] >= 8 and time['hh'] < 20:
            data = {'schedule': schedule, 'time': time}
            response = requests.post(url, json=data)
            info = response.text # {drone1: {battery1 : value, battery2 : value, status : value(charging , delivering, going_back), is_strong_wind : value }, ...}

            date, time = updateDateTime(date, time)
            schedule = updateSchedule(schedule, info)
            saveSchedule(schedule)
        else:
            date, time = updateDateTime(date, time)
            if time['hh'] == 0 and time['mm'] == 0:
                n_drones, schedule = createDailySchedule(date)
                saveSchedule(schedule)

    return 'Advanced'

def createDailySchedule(date):
    orders = getOrdersOfTheDay(date) # [{order_date_time{}, delivery_date{}, order_id, address, num_packages, priority}, ...]

    packages = {}
    for order in orders:
        for package_index in range(order['num_packages']):
            order_package = f"{order['order_id']}_{package_index + 1}"
            packages[order_package] = {'priority': order['priority'], 'duration': generate_truncated_gaussian_value()} # {order_package: {priority: int, duration: int}, ...}
            
    # TODO: Implement priority-based scheduling

    # Start: 9:00    End: 18:00    Extra: 20:00

# TODO
def updateSchedule(schedule, info):
    return {'drone1': [{'index': '1_1', 'time': {'start': '10:30', 'end': '11:00'}}, {'index': '1_2', 'time': {'start': '11:00', 'end': '11:45'}}],
            'drone2': [{'index': '1_3', 'time': {'start': '10:00', 'end': '10:40'}}, {'index': '1_4', 'time': {'start': '10:40', 'end': '12:00'}}],
            'drone3': [{'index': '1_5', 'time': {'start': '10:00', 'end': '11:30'}}, {'index': '1_6', 'time': {'start': '11:30', 'end': '12:00'}}],
            }

# Function to generate a truncated discrete Gaussian value
def generate_truncated_gaussian_value(mu = 60, min_val = 20, max_val = 120):
    sigma = (max_val - min_val) / 6  # Standard deviation covering 99.7% of the values between 20 and 120
    while True:
        value = np.random.normal(mu, sigma)  # Generate a value from the Gaussian distribution
        discrete_value = round(value)  # Round to the nearest integer
        if min_val <= discrete_value <= max_val:  # Apply truncation
            return discrete_value

# Alessio
def loadN_drones(date):
    url = 'http://order-manager:8080/loadN_drones'
    response = requests.post(url, json={'date': date})
    return response.json()['n_drones']

def saveN_drones(date, n_drones):
    url = 'http://order-manager:8080/saveN_drones'
    response = requests.post(url, json={'date': date,'n_drones':n_drones})
    return response.text

def loadSchedule():
    url = 'http://order-manager:8080/loadSchedule'
    response = requests.get(url)
    return response.json()

def emptySchedule():
    url = 'http://order-manager:8080/emptySchedule'
    response = requests.get(url)
    return response.text

def saveSchedule(schedule):
    url = 'http://order-manager:8080/saveSchedule'
    response = requests.post(url, json={'schedule': schedule})
    return response.text

def updateDateTime(date, time, minutes=1):
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

#function that asks to order-manager for all orders of the day passed as parameter and return a list of struct, each struct is an order.
def getOrdersOfTheDay(day):
    url = 'http://order-manager:8080/getOrdersOfTheDay'
    response = requests.post(url, json={'delivery_date': day})
    return response.json()

#function that asks to order-manager to modify the Status of all lines having ID_Order and Num_Package
def updateStatusOfProducts(order_package, status):
    # These will be the parameters of the request
    order_package = "PROVA01_1"
    status = "Delivered"

    url = 'http://order-manager:8080/updateStatusProducts'
    response = requests.post(url, json={'order-package': order_package, "status": status})

if __name__ == '__main__':
    app.run(debug=True)
