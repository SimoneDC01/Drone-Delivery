const express = require('express');
const amqp = require('amqplib/callback_api');
const app = express();
const port = 3000;

app.use(express.static('public'));
app.use(express.json());
/*
// Funzione per connettersi a RabbitMQ e ricevere messaggi
function receiveMessages(retryInterval = 5000) {
    amqp.connect('amqp://rabbitmq', (error0, connection) => {
        if (error0) {
            console.error("Error connecting to RabbitMQ:", error0.message);
            console.log(`Retrying in ${retryInterval / 1000} seconds...`);
            return setTimeout(() => receiveMessages(retryInterval), retryInterval);
        }

        connection.createChannel((error1, channel) => {
            if (error1) {
                throw error1;
            }

            const queue = 'hello';

            channel.assertQueue(queue, {
                durable: false
            });

            console.log(`[*] Waiting for messages in ${queue}. To exit press CTRL+C`);

            channel.consume(queue, (msg) => {
                console.log(`[x] Received ${msg.content.toString()}`);
            }, {
                noAck: true
            });
        });
    });
}

// Avvia la ricezione dei messaggi
receiveMessages();
*/

app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
});