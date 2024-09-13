from flask import Flask, request

app = Flask(__name__)


#route that takes information on products and return number of packets, total cost and estimated delivery time or 
# message of limit breaking if one or more prodoct are out of range
@app.route('/getPackaging', methods=['POST'])
def getPackaging():
    data = request.get_json()["data"]
    return 'Tetris!'

if __name__ == '__main__':
    app.run(debug=True)