import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/getProductsInfo', methods=['POST'])
def getProductsInfo():
    asins = request.get_json()['asins']

    url = "https://real-time-amazon-data.p.rapidapi.com/product-details"
    print('asins:', asins)
    querystring = {"asin": asins, "country":"IT"}

    headers = {
        "x-rapidapi-key": "cb82ab18e8mshe9881372c01458cp17d187jsnec161c018cfb",
        "x-rapidapi-host": "real-time-amazon-data.p.rapidapi.com"
    }

    api_response = requests.get(url, headers=headers, params=querystring)
    
    api_response = api_response.json()
    
    response = []
    for el in api_response['data'] :
        new_product = {}
        new_product['description'] = el['product_title']
        if 'Dimensioni prodotto' in list(el['product_information'].keys()):
            dimension, weight = el['product_information']['Dimensioni prodotto'].split(';')
            dimension = dimension.replace(' ','')
            dimension = dimension.replace('cm','')
            weight = weight.replace('kg','')
            weight = weight.replace(' ','')
            new_product['weight'] = weight
            new_product['dimension'] = dimension
        else :
            new_product['weight'] = None
            new_product['dimension'] = None
        
        response.append(new_product)
    
    return response
    
if __name__ == '__main__':
    app.run(debug=True)