from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

#route for respond with delivery_information on order_id to user-manager
@app.route('/advance', methods=['POST'])
def getDeliveryInfo():
    minutes = request.get_json()['minutes']

    url = 'http://scheduler:8080/advance'
    data = {'minutes': minutes}
    response = requests.post(url, json=data)
    return jsonify(response.text + '[TIME]')

if __name__ == '__main__':
    app.run(debug=True)
