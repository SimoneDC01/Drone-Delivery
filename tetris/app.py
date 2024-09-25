from flask import Flask, request
import http.client
import urllib.parse
import json
import ast

app = Flask(__name__)


#route that takes information on products and return number of packets, total cost and estimated delivery time or 
# message of limit breaking if one or more prodoct are out of range
@app.route('/getPackaging', methods=['POST'])
def getPackaging():
    data = request.get_json()["data"]
    problems=[]
    payload = []
    packages = []
    for el in data :
        if el['dimension'] and el['weight']: 
            new_item = {}
            new_item["id"] = el['description']
            new_item["w"], new_item["h"], new_item["d"] = el['dimension'].split('x')
            new_item["wg"] = el['weight']
            new_item["q"] = 1
            new_item["vr"] = True
            payload.append(new_item)
        else :
            problems.append({'description':el['description'],'problem':'missing dimension or weight'})
    conn = http.client.HTTPConnection(host='global-api.3dbinpacking.com', port=80)
    data = {"username": "ciprotti.1936617@studenti.uniroma1.it", "api_key": "a7f3b144adfbfd5c36f143584fa39fde",   "items": payload,
                                                            "bins": [
                                                                {"id": "Pack", "h": 120, "w": 120, "d": 120, "wg": 0, "max_wg": 10, "q": None, "cost":0, "type":"pallet"}
                                                                    ],
                                                            "params": {"images_background_color": "255,255,255", "images_bin_border_color": "59,59,59", "images_bin_fill_color": "230,230,230",
                                                                    "images_item_border_color": "22,22,22", "images_item_fill_color": "255,193,6", "images_item_back_border_color": "22,22,22",
                                                                    "images_sbs_last_item_fill_color": "177,14,14", "images_sbs_last_item_border_color": "22,22,22", "images_format": "svg",
                                                                    "images_width": 50, "images_height": 50, "images_source": "", "stats": 0, "item_coordinates": 1, "images_complete": 1,
                                                                    "images_sbs": 1, "images_separated": 0, "optimization_mode":"bins_number", "images_version":2}
                                                            }
    params =  urllib.parse.urlencode( {'query':json.dumps(data)} )
    headers = {"Content-type": "application/x-www-form-urlencoded",
        "Accept": "text/plain"}
    conn.request( "POST", "/packer/packIntoMany", params, headers )
    content = conn.getresponse( ).read( )
    conn.close( )
    content = ast.literal_eval(content.decode('utf-8'))
    num_bins = len(content['response']['bins_packed'])
    for el in content['response']['not_packed_items'] :
        problems.append({'description': el['id'], 'problem': 'exceed in weight or dimension. Max dimensions: 120x120x120cm. Max weight:10kg'})
    for el in content['response']['bins_packed'] :
        pack= []
        for item in el['items'] :
            pack.append(item['id'])
        packages.append(pack)
    return {'Num_packages':num_bins, 'Packages':packages,'problems':problems}

if __name__ == '__main__':
    app.run(debug=True)