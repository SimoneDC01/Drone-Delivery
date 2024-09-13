from flask import Flask, request
import threading
import pika
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/getProductsInfo', methods=['POST'])
def get_products_info():
    data = request.get_json()
    name = data['asins']

    # Process the name and return a response
    response = {'message': f'Hello, {name}!'}
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)