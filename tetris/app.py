from flask import Flask, request
import threading
import pika

app = Flask(__name__)

@app.route('/getPackaging', methods=['POST'])
def getPackaging():
    data = request.get_json()
    return data + 'Tetris!'

if __name__ == '__main__':
    app.run(debug=True)