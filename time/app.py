from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

#route for respond with delivery_information on order_id to user-manager
@app.route('/advance', methods=['POST'])
def getDeliveryInfo():
    minutes = request.get_json()['minutes']
    #upgrade date and time values in database
    url = 'http://scheduler:8080/advance'
    data = {'minutes': minutes}
    response = requests.post(url, json=data)
    url = 'http://user-manager:8080/date_and_time_new'
    data = {'date_and_time': "date_and_time_new"}
    requests.post(url, json=data)
    #take date and time from database
    return jsonify("data + time "+response.text + '[TIME]')

@app.route('/date_and_time_request', methods=['POST'])
def date_and_time_request():
    #take date and time from database
    return jsonify("date + time" + '[TIME]')

if __name__ == '__main__':
    app.run(debug=True)
