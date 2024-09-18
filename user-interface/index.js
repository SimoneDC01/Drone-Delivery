const express = require('express');
const path = require('path');
const app = express();
const WebSocket = require('ws');
const http = require('http');
const server = http.createServer(app);
const wss = new WebSocket.Server({ noServer: true });
const clients = [];
app.use(express.json());


app.get('/', (req, res) =>{ 
    const filePath = path.resolve("public", 'index.html');
    res.sendFile(filePath);
});



app.get('/getDeliveryInfo', (req, res) => {
    const name = req.query.order_id;
    const payload = { order_id: name };
    
    fetch(`http://user-manager:8080/getDeliveryInfo`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        res.json(data);
    }).catch(error => {
        res.status(500).json({ error: error.message });
    });
});


app.get('/getProductsInfo', (req, res) => {
    const name = req.query.asins;
    const priority = req.query.priority
    const payload = { asins: name, priority: priority };
    
    fetch(`http://user-manager:8080/getProductsInfo`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        res.json(data);
    }).catch(error => {
        res.status(500).json({ error: error.message });
    });
});

app.get('/sendAddressInfo', (req, res) => {
    const name = req.query.address;
    const payload = { address: name };
    
    fetch(`http://user-manager:8080/sendAddressInfo`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        res.json(data);
    }).catch(error => {
        res.status(500).json({ error: error.message });
    });
});



app.get('/date_and_time_request', (req, res) => {
    fetch(`http://user-manager:8080/date_and_time_request`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        res.json(data);
    }).catch(error => {
        res.status(500).json({ error: error.message });
    });
});



//part of websocket 

app.post('/date_and_time_new', (req, res) => {
    // Invia il messaggio a tutti i client connessi
    const { date_and_time } = req.body;
    clients.forEach((client) => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(`Messaggio dal server: ${date_and_time}`);
        }
    });
    res.send('Messaggio inviato ai client connessi');
});

// Gestione dell'upgrade per WebSocket
server.on('upgrade', (request, socket, head) => {
    wss.handleUpgrade(request, socket, head, (ws) => {
        wss.emit('connection', ws, request);
        clients.push(ws);
    });
});

wss.on('connection', (ws) => {
    console.log('New WebSocket connection');
    // Gestione dei messaggi WebSocket
    ws.on('message', (message) => {
        console.log(`Received WebSocket message: ${message}`);
    });
});


server.listen(3000, () => {
    console.log('Server in ascolto su http://localhost:3000');
});

