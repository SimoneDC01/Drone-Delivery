from flask import Flask, request
import threading
import pika
import requests

app = Flask(__name__)

def getProductsInfo(asins = ['1', '2', '3']):
    url = 'http://amazon-api:8080/getProductsInfo'
    data = {'asins': asins}
    response = requests.post(url, json=data)
    return response

if __name__ == '__main__':
    app.run(debug=True)