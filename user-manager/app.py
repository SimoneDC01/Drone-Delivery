from flask import Flask, request, jsonify
import requests
import string
import random

app = Flask(__name__)

temporary_order_storage={'priority':None,'num_packages':None,'packages':None}

#route that takes list of asins from frontend and call apiamazon and tetris and return information of prodoct and cost, time and orders id to frontend
@app.route('/getProductsInfo', methods=['POST'])
def get_products_info():
    data = request.get_json()
    prodList = data.get('asins') #list of products
    temporary_order_storage['priority'] = data.get('priority')
    url = 'http://amazon-api:8080/getProductsInfo'
    data = {'asins': prodList}
    response_amazon = requests.post(url, json=data)
    url = 'http://tetris:8080/getPackaging'
    data={"data":response_amazon.json(), 'priority':temporary_order_storage['priority']}
    response_tetris = requests.post(url, json=data)
    temporary_order_storage['num_packages'] = response_tetris.json()['Num_packages']
    temporary_order_storage['packages'] = response_tetris.json()['Packages']
    return temporary_order_storage['packages']
    #write better the return
    


#route that takes order_id from frontend and ask to scheduler and return the response to the frontend
@app.route('/getDeliveryInfo', methods=['POST'])
def get_delivery_info():
    data = request.get_json()
    email = data['email']
    url = 'http://data-manager:8080/getDeliveryInfo'
    data = {'email': email}
    response = requests.post(url, json=data)
    return response.json()

#route that takes the address and send all order_info to data-manager
@app.route('/sendAddressInfo', methods=['POST'])
def send_Address_Info():
    data = request.get_json()
    address = data.get('address')
    email=data.get('email')
    date = date_and_time_request()['date'] 
    time = date_and_time_request()['time']
    dateTime = date + ',' + time

    #delivery day computation
    day = int(date.split('/')[0])
    month = int(date.split('/')[1])
    year = int(date.split('/')[2])
    day += 1
    days_in_month = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        days_in_month[1] = 29
    else:
        days_in_month[1] = 28

    if day > days_in_month[month - 1]:
        day = 1
        month += 1
        if month > 12:
            month = 1
            year += 1
    delivery_day = f"{day:02d}/{month:02d}/{year:04d}"

    #id_order generation
    caratteri_legibili = string.ascii_letters + string.digits  # Include lettere maiuscole, minuscole e numeri
    id_order = ''.join(random.choice(caratteri_legibili) for _ in range(10))

    url = 'http://data-manager:8080/sendOrder'
    data = {'email':email,'Date_time_order': dateTime, 'Delivery_day':delivery_day, 'ID_Order' : id_order, 'Address':address, 'Num_packages':temporary_order_storage['num_packages'], 'Priority':int(temporary_order_storage['priority']), 'Packages':temporary_order_storage['packages']}
    response = requests.post(url, json=data)
    
    return jsonify(data['ID_Order'])


@app.route('/date_and_time_request', methods=['POST'])
def date_and_time_request():
    url = 'http://time:8080/date_and_time_request'
    response = requests.post(url)
    return response.json()



@app.route('/date_and_time_new', methods=['POST'])
def date_and_time_new():
    date=request.get_json()['date']
    time=request.get_json()['time']
    url = 'http://user-interface:3000/date_and_time_new'
    response=requests.post(url, json={'date':date, 'time':time})
    
    return jsonify(response.text + '[USER MANAGER]')
    
   



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)