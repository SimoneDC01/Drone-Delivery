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



#LEGGILO SIMONE
#function that asks to order-manager for all orders of the day passed as parameter and return a list of struct, each struct is an order.
def getOrdersOfTheDay():
    url = 'http://order-manager:8080/getOrdersOfTheDay'
    day="21/09/2024"
    response = requests.post(url, json={'Delivery_day':day})
    print(response.text)

if __name__ == '__main__':
    app.run(debug=True)
