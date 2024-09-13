from flask import Flask, request
import threading
import pika
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/getProductsInfo', methods=['POST'])
def getProductsInfo():
    asins = request.get_json()['asins']
    if isinstance(asins, list):
        return 'OK'
    else:
        return 'KO'

if __name__ == '__main__':
    app.run(debug=True)