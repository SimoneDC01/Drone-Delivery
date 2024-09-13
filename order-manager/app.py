from flask import Flask, request

app = Flask(__name__)

#route in which the manager insert the order arrived from user-manager into the dataset
@app.route('/sendOrder', methods=['POST'])
def sendOrder():
    data = request.get_json()
    return '[ORDER MANAGER]'

#TO-DO
#route in which the manager takes order from dataset and responds to scheduler
@app.route('/getOrdersOfTheDay', methods=['POST'])
def getOrdersOfTheDay():
    data = request.get_json()
    return '[ORDER MANAGER]'

if __name__ == '__main__':
    app.run(debug=True)
