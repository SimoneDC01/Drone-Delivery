from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

#route for respond with delivery_information on order_id to user-manager
@app.route('/advance', methods=['POST'])
def advance():
    minutes = request.get_json()['minutes']
    return minutes + '[DRONES]'

if __name__ == '__main__':
    app.run(debug=True)
