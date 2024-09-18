import sqlite3
from flask import Flask, request, jsonify
from datetime import datetime
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
    delivery_date = request.get_json()['delivery_date']
    day = str(delivery_date['day']) if delivery_date['day'] > 9 else '0' + str(delivery_date['day'])
    month = str(delivery_date['month']) if delivery_date['month'] > 9 else '0' + str(delivery_date['month'])
    year = str(delivery_date['year'])
    delivery_date = day + '/' + month + '/' + year
    conn = sqlite3.connect('orders.sqlite')  # 'orders.db' is assumed to be in the same directory
    cursor = conn.cursor()

    cursor.execute('''
        SELECT Date_time_order, Delivery_day, ID_Order, Address, Num_packages, Priority  FROM Orders WHERE Delivery_day = ?
    ''', (delivery_date,))

    orders = cursor.fetchall()
    # Chiude la connessione (non serve commit per SELECT)
    conn.close()

    # Trasforma i dati in un formato leggibile, ad esempio in un dizionario per ogni riga
    orders_list = []
    for order in orders:
        order_date_time_str = order[0]
        delivery_date_str = order[1]

        # Converti la stringa in un oggetto datetime
        order_datetime = datetime.strptime(order_date_time_str, "%d/%m/%Y,%H:%M")
        delivery_date = datetime.strptime(delivery_date_str, "%d/%m/%Y")

        # Crea la struttura con i campi separati
        
        orders_list.append({
            'order_date_time': {
            'day': order_datetime.day,
            'month': order_datetime.month,
            'year': order_datetime.year,
            'hh': order_datetime.hour,
            'mm': order_datetime.minute
            },
            'delivery_date': {
                'day': delivery_date.day,
                'month': delivery_date.month,
                'year': delivery_date.year
            },
            'order_id': order[2],
            'address': order[3],
            'num_packages': order[4],
            'priority': order[5]
        })
    # Restituisce i risultati come JSON
    return orders_list




#route of update of the status of the products
@app.route('/updateStatusProducts', methods=['POST'])
def updateStatusProducts():
    data = request.get_json()
    Order_Package=data['order-package'].split("_",1)
    Order=Order_Package[0]
    Package=int(Order_Package[1])
    Status=data['status']
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










@app.route('/loadN_drones', methods=['POST'])
def loadN_drones():
    date = request.get_json()['date']
    date = str(date['day']).zfill(2) + "/" + str(date['month']).zfill(2) + "/" + str(date['year'])
    conn = sqlite3.connect('scheduler.sqlite')  # 'orders.db' is assumed to be in the same directory
    cursor = conn.cursor()

    cursor.execute('''
        SELECT n_drones  FROM n_drones WHERE date = ?
    ''', (date,))

    n_drones = cursor.fetchone()
    conn.close()
    
    return jsonify({'n_drones':n_drones[0]})


@app.route('/saveN_drones', methods=['POST'])
def saveN_drones():
    date = request.get_json()['date']
    n_drones=request.get_json()['n_drones']
    date = str(date['day']).zfill(2) + "/" + str(date['month']).zfill(2) + "/" + str(date['year'])
    conn = sqlite3.connect('scheduler.sqlite')  # 'orders.db' is assumed to be in the same directory
    cursor = conn.cursor()

    # Esegui l'inserimento nella tabella n_drones
    cursor.execute('''
        INSERT INTO n_drones (date, n_drones)
        VALUES (?, ?)
    ''', (date, n_drones))

    # Salva le modifiche
    conn.commit()
    conn.close()
    
    return "record insert correctly!"


@app.route('/emptySchedule', methods=['GET'])
def emptySchedule():
    conn = sqlite3.connect('scheduler.sqlite')
    cursor = conn.cursor()

    try:
        # Esegui il comando per svuotare la tabella schedule
        cursor.execute('DELETE FROM schedule')

        # Salva le modifiche
        conn.commit()
    except sqlite3.Error as e:
        print(f"Errore durante la cancellazione della tabella: {e}")
    finally:
        # Chiudi la connessione al database
        conn.close()

    return "database empty"




@app.route('/saveSchedule', methods=['POST'])
def saveSchedule():
    emptySchedule()
    schedule = request.get_json()['schedule']
    conn = sqlite3.connect('scheduler.sqlite')
    cursor = conn.cursor()

    try:
        # Itera su ogni drone nella struttura
        for drone, tasks in schedule.items():
            # Estrai il drone_id (numero dopo "drone")
            drone_id = int(drone.replace('drone', ''))

            # Itera su ogni task per quel drone
            for task in tasks:
                order_package = task['index']
                start_time = task['time']['start']
                end_time = task['time']['end']

                # Inserisci i dati nella tabella schedule
                cursor.execute('''
                    INSERT INTO schedule (order_package, drone_id, start, end)
                    VALUES (?, ?, ?, ?)
                ''', (order_package, drone_id, start_time, end_time))

        # Salva le modifiche
        conn.commit()
    except sqlite3.Error as e:
        print(f"Errore durante l'inserimento dei dati: {e}")
    finally:
        # Chiudi la connessione al database
        conn.close()

    return "schedule insert correctly"




@app.route('/loadSchedule', methods=['GET'])
def loadSchedule():
    # Connessione al database
    conn = sqlite3.connect('scheduler.sqlite')
    cursor = conn.cursor()

    
    # Esegui la query per recuperare tutti i record ordinati per drone_id e start
    cursor.execute('''
        SELECT order_package, drone_id, start, end
        FROM schedule
        ORDER BY drone_id, start
    ''')
    
    # Recupera tutti i record
    records = cursor.fetchall()

    # Struttura per contenere il risultato
    schedule = {}

    # Itera su ogni record e costruisci la struttura
    for order_package, drone_id, start_time, end_time in records:
        drone_key = f"drone{drone_id}"  # Crea la chiave in base al drone_id

        # Se il drone non è già nella struttura, aggiungilo
        if drone_key not in schedule:
            schedule[drone_key] = []

        # Aggiungi la task nella lista del drone
        schedule[drone_key].append({
            'index': order_package,
            'time': {
                'start': start_time,
                'end': end_time
            }
        })

    conn.close()
    # Ritorna il risultato in formato JSON
    return jsonify(schedule)



if __name__ == '__main__':
    app.run(debug=True)
