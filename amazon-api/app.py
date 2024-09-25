import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/getProductsInfo', methods=['POST'])
def getProductsInfo():
    asins = request.get_json()['asins']

    url = "https://real-time-amazon-data.p.rapidapi.com/product-details"
    querystring = {"asin": asins, "country":"IT"}

    headers = {
        "x-rapidapi-key": "3f50d721e5mshec3bbab93d99701p15dbffjsn8b15d28c99a5",
        "x-rapidapi-host": "real-time-amazon-data.p.rapidapi.com"
    }

    api_response = requests.get(url, headers=headers, params=querystring)
    
    api_response = api_response.json()
   
    response = []
    
    if(type(api_response['data']) == dict):
        new_product = {}
        new_product['description'] = api_response['data']['product_title']
        if 'Dimensioni prodotto' in list(api_response['data']['product_information'].keys()):
            dimension, weight = api_response['data']['product_information']['Dimensioni prodotto'].split(';')
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

    else :
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