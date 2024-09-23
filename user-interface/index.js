const express = require('express');
const path = require('path');
const app = express();
const WebSocket = require('ws');
const http = require('http');
const server = http.createServer(app);
const wss = new WebSocket.Server({ noServer: true });
const clients = [];
const session = require('express-session');
const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy;
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(session({
    secret: 'secret_key', // Cambia questa stringa con una chiave segreta sicura
    resave: false,
    saveUninitialized: true,
    cookie: { secure: false, maxAge: null } // Metti a 'true' se usi HTTPS
}));

// Inizializza Passport
app.use(passport.initialize());
app.use(passport.session());

// Configura Passport con Google OAuth 2.0
passport.use(new GoogleStrategy({
    clientID:"563567641294-ampf5264b5ipe08je7m68dlcjt3s54v8.apps.googleusercontent.com",
    clientSecret:"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",
    callbackURL: '/auth/google/callback'
  },
  (accessToken, refreshToken, profile, done) => {
    // Il profilo dell'utente Google viene passato qui
    // Puoi decidere cosa salvare nella sessione, per esempio l'email
    return done(null, profile.emails[0].value);
  }
));

// Serializzare l'utente nella sessione
passport.serializeUser((user, done) => {
    done(null, user);  // Qui salvi tutto il profilo, ma puoi decidere di salvare solo l'email ad esempio: user.emails[0].value
});

// Deserializzare l'utente dalla sessione
passport.deserializeUser((user, done) => {
    done(null, user);
});
// Route per avviare l'autenticazione con Google
app.get('/auth/google',
    passport.authenticate('google', { scope: ['profile', 'email'] })
  );
  
  // Callback di Google OAuth, dove si ritorna dopo l'autenticazione
  app.get('/auth/google/callback', 
    passport.authenticate('google', { failureRedirect: '/' }),
    (req, res) => {
      // Successo nell'autenticazione, redirect a una pagina protetta
      res.redirect('/orders');
    }
  );

  app.get('/', (req, res) =>{ 
    const filePath = path.resolve("public", 'home.html');
    res.sendFile(filePath);
});  
app.get('/orders', (req, res) =>{ 
    if (req.isAuthenticated()){
        const filePath = path.resolve("public", 'orders.html');
            res.sendFile(filePath);
    }
    else {
        // Se l'utente non è autenticato, fai una GET a '/'
        res.redirect('/');  // Puoi cambiare '/' con qualsiasi rotta desideri
    }
    
});
app.get('/track',(req,res)=>{
    if (req.isAuthenticated()){
    const filePath = path.resolve("public", 'track.html');
    res.sendFile(filePath);
    }
    else {
        // Se l'utente non è autenticato, fai una GET a '/'
        res.redirect('/');  // Puoi cambiare '/' con qualsiasi rotta desideri
    }
})
app.get('/checkout', (req, res) =>{ 
    if (req.isAuthenticated()){
    const filePath = path.resolve("public", 'checkout.html');
    res.sendFile(filePath);
    }
    else {
        // Se l'utente non è autenticato, fai una GET a '/'
        res.redirect('/');  // Puoi cambiare '/' con qualsiasi rotta desideri
    }
});

app.post('/confirm', (req, res) => {
    if (req.isAuthenticated()){
    try {
        // Controlla se i dati sono presenti
        const data = req.body.data ? JSON.parse(req.body.data) : null;
        
        if (!data) {
            return res.status(400).send('No data provided');
        }

        // Restituisci la pagina HTML con i dati
        res.send(`
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Confirm</title>
                <style>
                    body {
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background-color: #f5f5f5;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        padding: 20px;
                    }
        
                    h1 {
                        color: #007bff;
                        margin-bottom: 20px;
                    }
        
                    .product-list {
                        list-style: none;
                        padding: 0;
                        margin-bottom: 20px;
                    }
        
                    .product-item {
                        display: flex;
                        align-items: center;
                        margin-bottom: 10px;
                    }
        
                    .product-item::before {
                        content: "●";
                        margin-right: 10px;
                    }
        
                    .product-item.green::before {
                        color: green;
                    }
        
                    .product-item.red::before {
                        color: red;
                    }
        
                    .product-item span.green {
                        color: green;
                        margin-left: 20px;
                        font-weight: bold;
                    }
        
                    .product-item span.red {
                        color: red;
                        margin-left: 20px;
                        font-weight: bold;
                    }
        
                    .price-table {
                        width: 50%;
                        margin-top: 20px;
                        border-collapse: collapse;
                        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
                        background-color: white;
                    }
        
                    .price-table th, .price-table td {
                        padding: 10px;
                        border: 1px solid #ddd;
                        text-align: left;
                    }
        
                    .price-table th {
                        background-color: #007bff;
                        color: white;
                    }
        
                    .price-table td {
                        font-weight: bold;
                    }
        
                    button {
                        background-color: #28a745;
                        color: white;
                        font-size: 1.2em;
                        padding: 10px 20px;
                        border: none;
                        border-radius: 8px;
                        cursor: pointer;
                        margin-top: 20px;
                    }
        
                    button.disabled {
                        background-color: gray;
                        cursor: not-allowed;
                    }
        
                    button:hover:not(.disabled) {
                        background-color: #218838;
                    }
                </style>
            </head>
            <body>
                <h1>Confirm Your Order</h1>
                
                <div id="content">
                    <!-- Elenco prodotti -->
                    <ul class="product-list" id="productList"></ul>
        
                    <!-- Tabella del prezzo (visibile solo se problems è vuoto) -->
                    <table class="price-table" id="priceTable">
                        <thead>
                            <tr>
                                <th>Item</th>
                                <th>Price</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>Delivery</td>
                                <td>5.00 €</td>
                            </tr>
                            <tr>
                                <td>Nr of packages (${data.packages.length})</td>
                                <td id="packagePrice"></td>
                            </tr>
                            <tr>
                                <td>Priority (${data.priority})</td>
                                <td id="priorityPrice"></td>
                            </tr>
                            <tr>
                                <td>Total</td>
                                <td id="totalPrice"></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
        
                <button id="checkoutButton" onclick="window.location.href='http://localhost:3000/checkout'">Go to Checkout</button>
        
                <script>
                    const data = ${JSON.stringify(data)}; // Inseriamo i dati
                    const productList = document.getElementById('productList');
                    const priceTable = document.getElementById('priceTable');
                    const checkoutButton = document.getElementById('checkoutButton');
        
                    const problems = data.problems || [];
        
                    // Funzione per verificare se un prodotto è in problems
                    function isProductInProblems(product) {
                        return problems.find(problem => problem.description === product);
                    }
        
                    if (problems.length === 0) {
                        // Se non ci sono problemi, mostra i prodotti normalmente
                        data.packages.forEach(packageGroup => {
                            packageGroup.forEach(product => {
                                const li = document.createElement('li');
                                li.classList.add('product-item', 'green');
                                li.innerHTML = product + '<span class="green">The product falls within the expected parameters.</span>';
                                productList.appendChild(li);
                            });
                        });
        
                        // Prezzi
                        const packagePrice = data.packages.length -1 + '.00 €';
                        const priorityPrice = data.priority + '.00 €';
        
                        // Calcolo totale
                        const total = 5 + data.packages.length + parseInt(data.priority);
        
                        document.getElementById('packagePrice').textContent = packagePrice;
                        document.getElementById('priorityPrice').textContent = priorityPrice;
                        document.getElementById('totalPrice').textContent = total + '.00 €';
                    } else {
                        // Se ci sono problemi, mostra i prodotti con pallino rosso e scritta rossa
                        data.packages.forEach(packageGroup => {
                            packageGroup.forEach(product => {
                                const li = document.createElement('li');
                                const problem = isProductInProblems(product);
                                
                                if (problem) {
                                    li.classList.add('product-item', 'red');
                                    li.innerHTML = product + '<span class="red">' + problem.problem + '</span>';
                                } else {
                                    li.classList.add('product-item', 'green');
                                    li.innerHTML = product + '<span class="green">The product falls within the expected parameters.</span>';
                                }
        
                                productList.appendChild(li);
                            });
                        });
        
                        // Nascondi la tabella dei prezzi e disabilita il pulsante checkout
                        priceTable.style.display = 'none';
                        checkoutButton.classList.add('disabled');
                        checkoutButton.disabled = true;
                    }
                </script>
            </body>
            </html>
        `);
        
        
        
    } catch (error) {
        res.status(500).send('Error parsing JSON data');
    }
}
});



app.post('/thankyou', (req, res) =>{ 
    if (req.isAuthenticated()){
    try {
        // Controlla se i dati sono presenti
        const data = req.body.data ? JSON.parse(req.body.data) : null;
        
        if (!data) {
            return res.status(400).send('No data provided');
        }

        // Restituisci la pagina HTML con i dati
        res.send(`
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Thank You</title>
                <style>
                    /* Stili di base */
                    * {
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                    }
        
                    body {
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background-color: #e6f2ff;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        background-image: url('https://example.com/drone-background.jpg'); /* Sostituisci con un URL valido */
                        background-size: cover;
                        background-position: center;
                        color: #333;
                    }
        
                    .container {
                        text-align: center;
                        background: rgba(255, 255, 255, 0.9);
                        padding: 40px;
                        border-radius: 12px;
                        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
                        width: 400px;
                    }
        
                    h1 {
                        font-size: 2.5em;
                        color: #28a745;
                        margin-bottom: 20px;
                    }
        
                    p {
                        font-size: 1.2em;
                        margin-bottom: 20px;
                        color: #333;
                    }
        
                    .order-id {
                        font-weight: bold;
                        color: #007bff;
                        font-size: 1.5em;
                        margin: 20px 0;
                    }
        
                    button {
                        background-color: #007bff;
                        color: white;
                        font-size: 1.2em;
                        padding: 10px 20px;
                        border: none;
                        border-radius: 8px;
                        cursor: pointer;
                        transition: background-color 0.3s ease;
                        margin-top: 20px;
                    }
        
                    button:hover {
                        background-color: #0056b3;
                    }
        
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Thank You!</h1>
                    <p>Your order has been placed successfully.</p>
                    <div class="order-id">Order ID: ${data}</div>  <!-- Visualizza l'Order ID in modo prominente -->
                    <button onclick="window.location.href='http://localhost:3000/orders'">Back to Orders</button>
                </div>
            </body>
            </html>
        `);
        
    } catch (error) {
        res.status(500).send('Error parsing JSON data');
    }
}
});

app.get('/getDeliveryInfo', (req, res) => {
    const name = req.user
    const payload = { email: name };
    
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
    var email=req.user
    const payload = { address: name ,email: email};
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
    const  date_and_time = JSON.stringify(req.body);
    clients.forEach((client) => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(date_and_time);
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
    // Gestione dei messaggi WebSocket
    ws.on('message', (message) => {
        console.log(`Received WebSocket message: ${message}`);
    });
});


server.listen(3000, () => {
    console.log('Server started on port 3000');
});

