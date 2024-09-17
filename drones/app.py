from flask import Flask, request, jsonify
import requests
import random

# Drones status
CHARGING = 0
DELIVERING = 1
GOING_BACK = 2

MAX_BATTERY = 120
class Drone:
    def __init__(self):
        self.battery1 = MAX_BATTERY
        self.battery2 = MAX_BATTERY
        self.status = CHARGING
        self.is_strong_wind = False
        self.states_history = [0, 0]

    def __str__(self):
        return (f"Drone(battery1 : {self.battery1}, battery2 : {self.battery2}, "
                f"status : {self.status}, is_strong_wind : {self.is_strong_wind})")

transition_states = {
    (0, 0): [0.95, 0.05],   # From (No Wind, No Wind) to No Wind o Strong Wind
    (0, 1): [0.4, 0.6],   # From (No Wind, Strong Wind) to No Wind o Strong Wind
    (1, 0): [0.6, 0.4],     # From (Strong Wind, No Wind) to No Wind o Strong Wind
    (1, 1): [0.12, 0.88], # From (Strong Wind, Strong Wind) to No Wind o Strong Wind
}

my_drones = {}

states_history = [0,0]

def get_wind():
    last_state = (states_history[-2], states_history[-1])
    next_state = random.choices([0, 1], weights=transition_states[last_state])[0]
    states_history.append(next_state)
    return next_state

app = Flask(__name__)

#route for respond with delivery_information on order_id to user-manager
@app.route('/advance', methods=['POST'])
def advance():
    #schedule = request.get_json()['schedule']   # {drone1: [{order,package : (start,end)}, {order,package : (start,end)}, ... ], drone2:  [{order,package : (start,end)}, {order,package : (start,end)}, ... ], ... } 
    schedule = {'drone1': [{'1,2' : '((2 : 30), (2 : 40))'}, {'2,1' : '((2 : 40), (2 : 50))'} ], 'drone2':  [{'3,1' : '((2 : 30 ),(2 : 50))'}, {'4, 1' : '((2 : 50), (3:10))' } ] }

    print(list(schedule.keys()))
    
    drones_list = list(schedule.keys())
    
    for el in drones_list : 
        my_drones [el] = Drone()
        print(schedule[el])

    
    
    #time = request.get_json()['time']           # {hh : value, mm : value}

    return str(get_wind()) + '[DRONES]'                # {drone1: {battery1 : value, battery2 : value, status : value(charging , delivering, going_back), is_strong_wind : value }, drone2 : {battery1 : value, battery2 : value, status : value(charging , delivering, going_back), is_strong_wind : value }, ... } 

if __name__ == '__main__':                      
    app.run(debug=True)
