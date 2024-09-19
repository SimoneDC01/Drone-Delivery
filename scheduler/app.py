from flask import Flask, request
import requests
import numpy as np
import math
import copy

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

    url = 'http://drones:8080/advance'

    for _ in range(minutes):
        if time['hh'] >= 8 and time['hh'] < 20:
            data = {'schedule': schedule, 'time': time}
            response = requests.post(url, json=data)
            info = response.text # {drone1: {battery1: value, battery2: value, status: value(charging , delivering, going_back), is_strong_wind: value }, ...}

            date, time = updateDateTime(date, time)
            schedule = updateSchedule(schedule, info)
            saveSchedule(schedule)
        else:
            date, time = updateDateTime(date, time)
            if time['hh'] == 0 and time['mm'] == 0:
                n_drones, schedule = createDailySchedule(date)
                saveN_drones(date, n_drones)
                saveSchedule(schedule)

    return schedule

def createDailySchedule(date):
    orders = getOrdersOfTheDay(date) # [{order_date_time{}, delivery_date{}, order_id, address, num_packages, priority}, ...]

    packages = {}
    for order in orders:
        for package_index in range(order['num_packages']):
            order_package = f"{order['order_id']}_{package_index + 1}"
            packages[order_package] = {'priority': order['priority'], 'duration': generate_truncated_gaussian_value()} # {order_package: {priority: int, duration: int}, ...}

    total_duration = sum([package['duration'] for package in packages.values()])
    print(total_duration / 540, math.ceil(total_duration / 540))
    n_drones = math.ceil(total_duration / 540) # 9 hours = 540 minutes

    # Start: 9:00    End: 18:00    Extra: 20:00

    schedule = None
    while not schedule:
        schedule = getOptimizedGreedySchedule(n_drones, packages, date)
        if not schedule: n_drones += 1

    print(n_drones)
    for drone, drone_schedule in schedule.items():
        print(drone)
        for event in drone_schedule:
            print(event)
    return n_drones, schedule

def getOptimizedGreedySchedule(n_drones, packages, date):
    # Sort packages by priority and then by duration
    packages = dict(sorted(packages.items(), key=lambda item: (item[1]['priority'], item[1]['duration']), reverse=True))
    end_times = {f'drone{i + 1}': {'hh': 9, 'mm': 0} for i in range(n_drones)} # {drone1: {hh: int, mm: int}, ...}
    batteries = {f'drone{i + 1}': 120 for i in range(n_drones)} # {drone1: int, ...}
    schedule = {f'drone{i + 1}': [] for i in range(n_drones)} # {drone1: [{index: str, time: {start: str, end: str}}, ...], ...}

    for order_package, p_d in packages.items():
        duration = p_d['duration']
        virtual_end_times = end_times.copy()
        for drone, battery in batteries.items():
            if battery < duration:
                recharge_time = math.ceil((duration - battery) / 3) # Recharge is 3x faster than discharge
                virtual_end_date, virtual_end_times[drone] = updateDateTime(date, end_times[drone], recharge_time)
                if virtual_end_date != date: return None

        chosen = min(end_times, key=lambda drone: (virtual_end_times[drone]['hh'], virtual_end_times[drone]['mm']))
        if virtual_end_times[chosen] != end_times[chosen]:
            time_diff = (virtual_end_times[chosen]['hh'] - end_times[chosen]['hh']) * 60 + (virtual_end_times[chosen]['mm'] - end_times[chosen]['mm'])
            batteries[chosen] = min(batteries[chosen] + time_diff * 3, 120) # Recharge is 3x faster than discharge
            schedule[chosen].append({'index': 'recharge', 'time': {'start': f"{str(end_times[chosen]['hh']).zfill(2)}:{str(end_times[chosen]['mm']).zfill(2)}", 'end': f"{str(virtual_end_times[chosen]['hh']).zfill(2)}:{str(virtual_end_times[chosen]['mm']).zfill(2)}"}})
            end_times[chosen] = virtual_end_times[chosen]

        new_date, new_end_time = updateDateTime(date, end_times[chosen], duration)
        if new_date != date: return None
        if new_end_time['hh'] >= 18: return None

        schedule[chosen].append({'index': order_package, 'time': {'start': f"{str(end_times[chosen]['hh']).zfill(2)}:{str(end_times[chosen]['mm']).zfill(2)}", 'end': f"{str(new_end_time['hh']).zfill(2)}:{str(new_end_time['mm']).zfill(2)}"}})
        end_times[chosen] = new_end_time
        batteries[chosen] -= duration

    return schedule

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

def loadN_drones(date):
    url = 'http://data-manager:8080/loadN_drones'
    response = requests.post(url, json={'date': date})
    return response.json()['n_drones']

def saveN_drones(date, n_drones):
    url = 'http://data-manager:8080/saveN_drones'
    response = requests.post(url, json={'date': date,'n_drones':n_drones})
    return response.text

def loadSchedule():
    url = 'http://data-manager:8080/loadSchedule'
    response = requests.get(url)
    return response.json()

def emptySchedule():
    url = 'http://data-manager:8080/emptySchedule'
    response = requests.get(url)
    return response.text

def saveSchedule(schedule):
    url = 'http://data-manager:8080/saveSchedule'
    response = requests.post(url, json={'schedule': schedule})
    return response.text

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

#function that asks to data-manager for all orders of the day passed as parameter and return a list of struct, each struct is an order.
def getOrdersOfTheDay(day):
    url = 'http://data-manager:8080/getOrdersOfTheDay'
    response = requests.post(url, json={'delivery_date': day})
    return response.json()

#function that asks to data-manager to modify the Status of all lines having ID_Order and Num_Package
def updateStatusOfProducts(order_package, status):
    # These will be the parameters of the request
    order_package = "PROVA01_1"
    status = "Delivered"

    url = 'http://data-manager:8080/updateStatusProducts'
    response = requests.post(url, json={'order-package': order_package, "status": status})

if __name__ == '__main__':
    app.run(debug=True)
