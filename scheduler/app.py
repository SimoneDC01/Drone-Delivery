from flask import Flask, request
import requests

app = Flask(__name__)

#route that takes the time advanced from container time 
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

#function that asks to order-manager to modify the Status of all lines having ID_Order and Num_Package
def UpdateStatusOfProdocts():
    url = 'http://order-manager:8080/UpdateStatusProducts'
    Order_Package=["PROVA01",1]
    Status="Delivered"
    response = requests.post(url, json={'Order-Package':Order_Package,"Status":Status})
    print(response.text)

if __name__ == '__main__':
    app.run(debug=True)
