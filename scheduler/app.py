from flask import Flask, request
import requests

app = Flask(__name__)

#route for respond with delivery_information on order_id to user-manager
@app.route('/getDeliveryInfo', methods=['POST'])
def getDeliveryInfo():
    order_id = request.get_json()['order_id']
    return order_id + '[SCHEDULER]'

@app.route('/advance', methods=['POST'])
def advance():
    minutes = request.get_json()['minutes']
    
    url = 'http://drones:8080/advance'
    data = {'minutes': minutes}
    response = requests.post(url, json=data)
    return response.text + '[SCHEDULER]'

@app.route('/getOrdersOfTheDay', methods=['POST'])
def getOrdersOfTheDay():
    url = 'http://order-manager:8080/getOrdersOfTheDay'
    response = requests.post(url, json={})
    return response.text + '[SCHEDULER]'

if __name__ == '__main__':
    app.run(debug=True)
