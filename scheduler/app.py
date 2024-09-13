from flask import Flask, request
import threading
import pika

app = Flask(__name__)

def sendMessage():
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='hello')
    channel.basic_publish(exchange='', routing_key='hello', body='Hello World!')
    print(" [x] Sent 'Hello World!'")
    connection.close()

@app.route('/hello', methods=['GET'])
def hello():
    name = request.args.get('name')
    if name is None:
        return "Errore: parametro 'name' non fornito", 400
    
    # Set a timeout of 5 seconds to call sendMessage
    timer = threading.Timer(5.0, sendMessage)
    timer.start()
    
    return f"Hello, {name}!"

if __name__ == '__main__':
    app.run(debug=True)