from flask import Flask, request, jsonify
import requests
import random

transition_states = {
    (0, 0): [0.95, 0.05],   # From (No Wind, No Wind) to No Wind o Strong Wind
    (0, 1): [0.4, 0.6],   # From (No Wind, Strong Wind) to No Wind o Strong Wind
    (1, 0): [0.66, 0.35],     # From (Strong Wind, No Wind) to No Wind o Strong Wind
    (1, 1): [0.035, 0.965], # From (Strong Wind, Strong Wind) to No Wind o Strong Wind
}

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
    #schedule = request.get_json()['schedule']   # {drone1: [{order,package : (start,end)}, {order,package : (start,end)}, ... ], drone2:  [{package}, {package}, {order,package : (start,end)}, {order,package : (start,end)}, ... ], ... } 

    #time = request.get_json()['time']           # {hh : value, mm : value}

    return str(get_wind()) + '[DRONES]'                # {drone1: {battery1 : value, battery2 : value, status : value(charging , delivering, going_back), is_strong_wind : value }, drone2 : {battery1 : value, battery2 : value, status : value(charging , delivering, going_back), is_strong_wind : value }, ... } 

if __name__ == '__main__':                      
    app.run(debug=True)
