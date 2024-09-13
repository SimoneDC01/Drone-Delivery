from flask import Flask, request
import threading
import pika
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

temporary_order_storage=[]

#route that takes list of asins from frontend and call apiamazon and tetris and return information of prodoct and cost, time and orders id to frontend
@app.route('/getProductsInfo', methods=['POST'])
def get_products_info():
    data = request.get_json()
    name = data['asins']
    url = 'http://amazon-api:8080/getProductsInfo'
    data = {'asins': name}
    response_amazon = requests.post(url, json=data)
    url = 'http://tetris:8080/getPackaging'
    data={"data":response_amazon.text}
    response_tetris = requests.post(url, json=data)
    return jsonify(response_amazon.text + response_tetris.text)
    #save the datas in a structure
    


#route that takes order_id from frontend and ask to scheduler and return the response to the frontend
@app.route('/getDeliveryInfo', methods=['POST'])
def get_delivery_info():
    data = request.get_json()
    name = data['order_id']
    url = 'http://scheduler:8080/getDeliveryInfo'
    data = {'order_id': name}
    response = requests.post(url, json=data)
    return jsonify(response.text)

#route that takes the address and send all order_info to order-manager
@app.route('/sendAddressInfo', methods=['POST'])
def send_Address_Info():
    data = request.get_json()
    address = data['address']
    url = 'http://order-manager:8080/sendOrder'
    data = {'address': address,'order_info':["order_id","data","altro"]}
    response = requests.post(url, json=data)
    return jsonify(response.text)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)