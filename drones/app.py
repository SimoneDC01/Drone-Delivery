from flask import Flask, request, jsonify
import requests
import random

# Drones status
CHARGING = 0
DELIVERING = 1
GOING_BACK = 2

MAX_BATTERY = 120
CHARGE_VELOCITY = 3
class Drone:
    def __init__(self):
        self.battery1 = MAX_BATTERY
        self.battery2 = MAX_BATTERY
        self.status = CHARGING
        self.is_strong_wind = False
        self.states_history = [0, 0]

    def __str__(self):
        return ("{" + f"battery1 : {self.battery1}, battery2 : {self.battery2}, "
                f"status : {self.status}, is_strong_wind : {self.is_strong_wind}, states_history : {self.states_history}" + "}")
    def __repr__(self):
        return ("{" + f"battery1 : {self.battery1}, battery2 : {self.battery2}, "
                f"status : {self.status}, is_strong_wind : {self.is_strong_wind}, states_history : {self.states_history}" + "}")

transition_states = {
    (0, 0): [0.95, 0.05],   # From (No Wind, No Wind) to No Wind o Strong Wind
    (0, 1): [0.4, 0.6],   # From (No Wind, Strong Wind) to No Wind o Strong Wind
    (1, 0): [0.6, 0.4],     # From (Strong Wind, No Wind) to No Wind o Strong Wind
    (1, 1): [0.12, 0.88], # From (Strong Wind, Strong Wind) to No Wind o Strong Wind
}

my_drones = {}

# given the history of the drone state, simulate the wind strenght for the current state
def get_wind(states_history):
    last_state = (states_history[-2], states_history[-1])
    next_state = random.choices([0, 1], weights=transition_states[last_state])[0]
    states_history.append(next_state)
    return next_state

# convert time expressed with string format to a tuple format
def extract_time(time):
    hours, minutes = time.split(':')
    hours = int(hours)
    minutes = int(minutes)
    return hours, minutes

# given the package information and the time, return if the drone is delivering or going back
def get_deliver_status(package, time) :
    deliver_duration = extract_time(package['time']['end'])[1] + (extract_time(package['time']['end'])[0] - extract_time(package['time']['start'])[0]) * 60 - extract_time(package['time']['start'])[1]
    half_delivery_time = extract_time(package['time']['start'])[0] + (deliver_duration/2 + extract_time(package['time']['start'])[1]) // 60, (extract_time(package['time']['start'])[1] + (deliver_duration/2)) % 60
    if(time <= half_delivery_time) :
        return DELIVERING
    else :
        return GOING_BACK
    
    
app = Flask(__name__)

# schedule for developing phase
#schedule = {'drone1': [{'index': '1_2', 'time': {'start': '2:30', 'end': '2:40'}}, {'index': '2_1', 'time' : {'start': '2:40', 'end': '2:50'}}], 
#                'drone2': [{'index': '3_1', 'time': {'start': '2:30', 'end': '2:50'}}, {'index': '4_1', 'time' : {'start': '2:50', 'end': '3:10'}}] 
#               }

#route for respond with delivery_information on order_id to user-manager
@app.route('/advance', methods=['POST'])
def advance():
    schedule = request.get_json()['schedule']   # {drone1: [{order,package : (start,end)}, {order,package : (start,end)}, ... ], drone2:  [{order,package : (start,end)}, {order,package : (start,end)}, ... ], ... } 

    #print(list(schedule.keys()))
    time = request.get_json()['time']['hh'], request.get_json()['time']['mm']           # {hh : value, mm : value}
    
    drones_list = list(schedule.keys())
    
    # for each drone of the schedule
    for drone in drones_list : 
        if(not drone in my_drones.keys()) :
            my_drones [drone] = Drone()
        # search the current  package of the drone
        for package in schedule[drone] :
            if(time<extract_time(package['time']['end'])):
                # the drone is charging
                if(package['index'] == '-1_-1') :
                    my_drones[drone].status = CHARGING
                    my_drones[drone].is_strong_wind = False
                    my_drones[drone].states_history.append(0)
                    
                    if my_drones[drone].battery1 < MAX_BATTERY :
                        my_drones[drone].battery1 += CHARGE_VELOCITY
                        if my_drones[drone].battery1 > MAX_BATTERY :
                            my_drones[drone].battery1 =  MAX_BATTERY
                    
                    if my_drones[drone].battery2 < MAX_BATTERY :
                        my_drones[drone].battery2 += CHARGE_VELOCITY
                        if my_drones[drone].battery2 > MAX_BATTERY :
                            my_drones[drone].battery2 =  MAX_BATTERY
                # simulate the wind and update involved values
                else :
                    wind = get_wind(my_drones[drone].states_history)
                    my_drones[drone].battery1 -= 1
                    if(wind == 1):
                        my_drones[drone].battery2 -= 1
                        my_drones[drone].is_strong_wind = True
                    else:
                        my_drones[drone].is_strong_wind = False

                    my_drones[drone].status = get_deliver_status(package, time)  
                    
                break

    return str(my_drones)                # { 'drone1' : {battery1 : value, battery2 : value, status : value, is_strong_wind : value }, 'drone2' : {battery1 : value, battery2 : value, status : value, is_strong_wind : value }, ... } 

if __name__ == '__main__':                      
    app.run(debug=True)
