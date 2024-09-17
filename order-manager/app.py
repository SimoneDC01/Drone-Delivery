import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)


#route in which the manager insert the order arrived from user-manager into the dataset
@app.route('/sendOrder', methods=['POST'])
def sendOrder():
    data = request.get_json()
    Date_time_order=data['Date_time_order']
    Delivery_day=data['Delivery_day']
    ID_Order=data['ID_Order']
    Address=data['Address']
    Num_packages=data['Num_packages']
    Priority=data['Priority']
    Packages=data['Packages']
    # Connect to the SQLite database
    conn = sqlite3.connect('orders.sqlite')  # 'orders.db' is assumed to be in the same directory
    cursor = conn.cursor()
    # Insert the order into the table
    cursor.execute('''
        INSERT INTO Orders (Date_time_order, Delivery_day, ID_Order, Address, Num_packages, Priority )
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (Date_time_order, Delivery_day, ID_Order, Address, Num_packages, Priority))

    # Commit the transaction and close the connection
    conn.commit()
    for i in range (0,Num_packages):
        Num_package=i+1
        for j in range (0,len(Packages[i])):
            Description=Packages[i][j]
            Status="In Elaborazione"

            cursor.execute('''
            INSERT INTO Products (ID_Order, Num_package, Description, Status )
            VALUES (?, ?, ?, ?)
            ''', (ID_Order, Num_package, Description, Status ))

            # Commit the transaction and close the connection
            conn.commit()

    conn.close()

    return 'Ordine inserito!'


#route in which the manager takes order from dataset and responds to scheduler
@app.route('/getOrdersOfTheDay', methods=['POST'])
def getOrdersOfTheDay():
    Delivery_day = request.get_json()['Delivery_day']
    conn = sqlite3.connect('orders.sqlite')  # 'orders.db' is assumed to be in the same directory
    cursor = conn.cursor()

    cursor.execute('''
        SELECT Date_time_order, Delivery_day, ID_Order, Address, Num_packages, Priority  FROM Orders WHERE Delivery_day = ?
    ''', (Delivery_day,))

    orders = cursor.fetchall()
    if orders==[]:
        return "No orders for this day"

    # Chiude la connessione (non serve commit per SELECT)
    conn.close()

    # Trasforma i dati in un formato leggibile, ad esempio in un dizionario per ogni riga
    orders_list = []
    for order in orders:
        orders_list.append({
            'Date_time_order': order[0],
            'Delivery_day': order[1],
            'ID_Order': order[2],
            'Address': order[3],
            'Num_packages': order[4],
            'Priority': order[5]
        })
    # Restituisce i risultati come JSON
    return orders_list




#route of update of the status of the products
@app.route('/UpdateStatusProducts', methods=['POST'])
def UpdateStatusProducts():
    data = request.get_json()
    Order_Package=data['Order-Package']
    Order=Order_Package[0]
    Package=Order_Package[1]
    Status=data['Status']
    # Connect to the SQLite database
    conn = sqlite3.connect('orders.sqlite')  # 'orders.db' is assumed to be in the same directory
    cursor = conn.cursor()
    # Esegui l'aggiornamento nella tabella Products
    cursor.execute('''
        UPDATE Products
        SET Status = ?
        WHERE ID_Order = ? AND Num_package = ?
    ''', (Status, Order, Package))

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()

    return 'Products modified'



@app.route('/getDeliveryInfo', methods=['POST'])
def get_delivery_info():
    data = request.get_json()
    ID_Order = data['ID_Order']
    conn = sqlite3.connect('orders.sqlite')  # 'orders.db' is assumed to be in the same directory
    cursor = conn.cursor()

    cursor.execute('''
        SELECT Description, Status  FROM Products WHERE ID_Order = ?
    ''', (ID_Order,))

    products = cursor.fetchall()
    if products==[]:
        return "The order does not exists"
    products_list = []
    for product in products:
        products_list.append({
            'Description':product[0],
            'Status': product[1]
        })
    # Chiude la connessione (non serve commit per SELECT)
    conn.close()    
    # Restituisce i risultati come JSON
    return products_list




if __name__ == '__main__':
    app.run(debug=True)
