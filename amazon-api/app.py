from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/getProductsInfo', methods=['POST'])
def getProductsInfo():
    asins = request.get_json()['asins']
    if isinstance(asins, list):
        return [{'description':'prod1', 'weight': 30, 'dimension': '20x30x15'}, {'description':'prod2', 'weight': 40, 'dimension': '10x30x15'}]
    else:
        return [{'description':'prod1', 'weight': 30, 'dimension': '20x30x15'}, {'description':'prod2', 'weight': 40, 'dimension': '10x30x15'}]
    
if __name__ == '__main__':
    app.run(debug=True)