from flask import Flask, request
import requests
import numpy as np
import math
import copy

app = Flask(__name__)

# [hh:mm] drone1 has detected strong wind conditions while delivering package PROVA_1.
# [hh:mm] Schedule has been recalculated.
# [hh:mm] drone1 has delivered package PROVA_1.
# [hh:mm] drone1 has recharged batteries.

log = []
logged_packages = []
delivered = []

#route that takes the time advanced from container time 
@app.route('/advance', methods=['POST'])
def advance():
    date = request.get_json()['date'] # {'day': int, 'month': int, 'year': int}
    time = request.get_json()['time'] # {'hh': int, 'mm': int}
    minutes = int(request.get_json()['minutes']) # int
    
    # Database: n_drones(date, n_drones), schedule(order_package, drone_id, start_time, end_time, duration, priority)
    n_drones = loadN_drones(date)
    schedule = loadSchedule()

    today_last_time = getTodayLastTime(schedule) # {'hh': int, 'mm': int}

    url = 'http://drones:8080/advance'

    for _ in range(minutes):
        if time['hh'] >= 9 and (time['hh'] < today_last_time['hh'] or (time['hh'] == today_last_time['hh'] and time['mm'] < today_last_time['mm'])):
            data = {'schedule': schedule, 'time': time}
            response = requests.post(url, json=data).json()
            info = response['info'] # {drone1: {battery1: value, battery2: value, is_strong_wind: value }, ...}
            to_notify = response['to_notify']
            for order_package in to_notify:
                updateStatusOfProducts(order_package, 'delivered')
                delivered.append(order_package)

            date, time = updateDateTime(date, time)

            old_schedule = copy.deepcopy(schedule)
            schedule = updateSchedule(n_drones, schedule, info, date, time)

            if schedule != old_schedule:
                log.append(f"[{str(time['hh']).zfill(2)}:{str(time['mm']).zfill(2)}] Schedule has been recalculated.")
                # SCHEDULE    {drone1: [{index: str, time: {start: str, end: str}, duration: int, priority: int}, ...], ...}
                for _, packages in schedule.items():
                    for package in packages:
                        if package['index'] not in delivered:
                            start_struct = {'hh': int(package['time']['start'].split(':')[0]), 'mm': int(package['time']['start'].split(':')[1])}
                            estimated_delivery = updateDateTime(date, start_struct, package['duration'] // 2)[1]
                            # TODO: Append to list and call function only at the end
                            updateStatusOfProducts(package['index'], f'{str(estimated_delivery["hh"]).zfill(2)}:{str(estimated_delivery["mm"]).zfill(2)}')
                        
                today_last_time = getTodayLastTime(schedule)
                saveSchedule(schedule)
        else:
            date, time = updateDateTime(date, time)
            if time['hh'] == 0 and time['mm'] == 0:
                today_last_time = {'hh': 9, 'mm': 1}
                log.clear()
                logged_packages.clear()
                delivered.clear()

                n_drones, schedule = createDailySchedule(date)

                for _, packages in schedule.items():
                    for package in packages:
                        if package['index'] not in delivered:
                            start_struct = {'hh': int(package['time']['start'].split(':')[0]), 'mm': int(package['time']['start'].split(':')[1])}
                            estimated_delivery = updateDateTime(date, start_struct, package['duration'] // 2)[1]
                            # TODO: Append to list and call function only at the end
                            updateStatusOfProducts(package['index'], f'{str(estimated_delivery["hh"]).zfill(2)}:{str(estimated_delivery["mm"]).zfill(2)}')

                saveN_drones(date, n_drones)
                saveSchedule(schedule)

    return {'schedule': schedule, 'log': log}

def getTodayLastTime(schedule):
    if schedule == None or schedule == {}: return {'hh': 9, 'mm': 0}

    last_times = []
    for _, packages in schedule.items():
        last_time = packages[-1]['time']['end']
        last_times.append({'hh': int(last_time.split(':')[0]), 'mm': int(last_time.split(':')[1])})
    return max(last_times, key=lambda time: (time['hh'], time['mm']))

def createDailySchedule(date):
    orders = getOrdersOfTheDay(date) # [{order_date_time{}, delivery_date{}, order_id, address, num_packages, priority}, ...]

    packages = {}
    for order in orders:
        for package_index in range(order['num_packages']):
            order_package = f"{order['order_id']}_{package_index + 1}"
            packages[order_package] = {'priority': order['priority'], 'duration': generate_truncated_gaussian_value()} # {order_package: {priority: int, duration: int}, ...}

    total_duration = sum([package['duration'] for package in packages.values()])
    n_drones = math.ceil(total_duration / 540) # 9 hours = 540 minutes

    # Start: 9:00    End: 18:00

    schedule = None
    while schedule == None:
        schedule = getOptimizedGreedySchedule(n_drones, packages, date)
        if schedule == None: n_drones += 1
    
    return n_drones, schedule

def getOptimizedGreedySchedule(n_drones, packages, date, end_times = None, batteries = None, schedule = None, limited = True):
    # Sort packages by priority and then by duration
    packages = dict(sorted(packages.items(), key=lambda item: (item[1]['priority'], item[1]['duration'], item[0]), reverse=True))

    if end_times == None: end_times = {f'drone{i + 1}': {'hh': 9, 'mm': 0} for i in range(n_drones)} # {drone1: {hh: int, mm: int}, ...}
    if batteries == None: batteries = {f'drone{i + 1}': (240, 120) for i in range(n_drones)} # {drone1: int, ...}
    if schedule == None: schedule = {f'drone{i + 1}': [] for i in range(n_drones)} # {drone1: [{index: str, time: {start: str, end: str}, duration: int, priority: int}, ...], ...}

    for order_package, p_d in packages.items():
        duration = p_d['duration']
        priority = p_d['priority']

        virtual_end_times = end_times.copy()
        for drone, battery in batteries.items():
            standard_battery = battery[0]
            auxiliary_battery = battery[1]
            lowest_battery = min(standard_battery, auxiliary_battery)
            if lowest_battery < duration:
                recharge_time = math.ceil((duration - lowest_battery) / 3) # Recharge is 3x faster than discharge
                virtual_end_date, virtual_end_times[drone] = updateDateTime(date, end_times[drone], recharge_time)
                if virtual_end_date != date: return None

        chosen = min(end_times, key=lambda drone: (virtual_end_times[drone]['hh'], virtual_end_times[drone]['mm']))
        if virtual_end_times[chosen] != end_times[chosen]:
            time_diff = (virtual_end_times[chosen]['hh'] - end_times[chosen]['hh']) * 60 + (virtual_end_times[chosen]['mm'] - end_times[chosen]['mm'])
            schedule[chosen].append({'index': 'recharge', 'time': {'start': f"{str(end_times[chosen]['hh']).zfill(2)}:{str(end_times[chosen]['mm']).zfill(2)}", 'end': f"{str(virtual_end_times[chosen]['hh']).zfill(2)}:{str(virtual_end_times[chosen]['mm']).zfill(2)}"}, 'duration': time_diff, 'priority': 0 if batteries[chosen][0] < batteries[chosen][1] else 1})
            batteries[chosen] = min(batteries[chosen][0] + time_diff * 3, 240), min(batteries[chosen][1] + time_diff * 3, 120) # Recharge is 3x faster than discharge
            end_times[chosen] = virtual_end_times[chosen]

        new_date, new_end_time = updateDateTime(date, end_times[chosen], duration)
        if new_date != date: return None
        if limited and new_end_time['hh'] >= 18: return None

        schedule[chosen].append({'index': order_package, 'time': {'start': f"{str(end_times[chosen]['hh']).zfill(2)}:{str(end_times[chosen]['mm']).zfill(2)}", 'end': f"{str(new_end_time['hh']).zfill(2)}:{str(new_end_time['mm']).zfill(2)}"}, 'duration': duration, 'priority': priority})
        end_times[chosen] = new_end_time
        batteries[chosen] = batteries[chosen][0] - duration, batteries[chosen][1]

    return schedule

def updateSchedule(n_drones, schedule, info, date, time):
    # INFO        {drone1: {battery1: value, battery2: value, is_strong_wind: value }, ...}
    # PACKAGES    {order_package: {priority: int, duration: int}, ...}
    # END_TIMES   {drone1: {hh: int, mm: int}, ...}
    # BATTERIES   {drone1: (int, int), ...}
    # SCHEDULE    {drone1: [{index: str, time: {start: str, end: str}, duration: int, priority: int}, ...], ...}

    for drone, drone_info in info.items():
        if drone_info['is_strong_wind']:
            order_package = getCurrentPackage(schedule[drone], time)[1]['index']
            message = f"[{str(time['hh']).zfill(2)}:{str(time['mm']).zfill(2)}] {drone} has detected strong wind conditions while delivering package {order_package}."
            if (drone, order_package) not in logged_packages:
                log.append(message)
                logged_packages.append((drone, order_package))
            break

    packages = {}
    end_times = {f'drone{i + 1}': time for i in range(n_drones)}
    batteries = {}
    
    for drone, drone_info in info.items():

        current_package_index, current_package = getCurrentPackage(schedule[drone], time) # {'index': 'PROVA01_1', 'time': {'start': '10:15', 'end': '11:25'}, 'duration': 70, 'priority': 4}
        if current_package == None: continue

        if f'{str(time['hh']).zfill(2)}:{str(time['mm']).zfill(2)}' == current_package['time']['end']:
            if current_package['index'] != 'recharge':
                log.append(f"[{str(time['hh']).zfill(2)}:{str(time['mm']).zfill(2)}] {drone} returned to the base after delivering package {current_package['index']}.")
            else:
                log.append(f"[{str(time['hh']).zfill(2)}:{str(time['mm']).zfill(2)}] {drone} has recharged batteries.")

        # Append packages after current_package to packages
        for i in range(current_package_index + 1, len(schedule[drone])):
            package = schedule[drone][i]
            if package['index'] == 'recharge': continue
            packages[package['index']] = {'priority': package['priority'], 'duration': package['duration']}

        # Set end_times[drone] to end of current_package
        if current_package != None:
            end_times[drone] = {'hh': int(current_package['time']['end'].split(':')[0]), 'mm': int(current_package['time']['end'].split(':')[1])}

        time_diff = (end_times[drone]['hh'] - time['hh']) * 60 + (end_times[drone]['mm'] - time['mm'])
        
        # Set batteries to drone_info['battery1'] - time_diff, drone_info['battery2']
        batteries[drone] = drone_info['battery1'] - time_diff, drone_info['battery2']
        
        # Isolate the past/present schedule from the future schedule
        schedule[drone] = schedule[drone][:current_package_index + 1]

    schedule = getOptimizedGreedySchedule(n_drones, packages, date, end_times, batteries, schedule, limited = False)

    return schedule

def getCurrentPackage(packages, time):
    for i, package in enumerate(packages):
        start_hh, start_mm = int(package['time']['start'].split(':')[0]), int(package['time']['start'].split(':')[1])
        end_hh, end_mm = int(package['time']['end'].split(':')[0]), int(package['time']['end'].split(':')[1])
        start_minutes = start_hh * 60 + start_mm
        end_minutes = end_hh * 60 + end_mm
        current_minutes = time['hh'] * 60 + time['mm']
        if start_minutes < current_minutes <= end_minutes:
            return i, package
    return None, None

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
    url = 'http://data-manager:8080/updateStatusProducts'
    response = requests.post(url, json={'order-package': order_package, "status": status})

if __name__ == '__main__':
    app.run(debug=True)
