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
    
});
app.get('/track',(req,res)=>{
    if (req.isAuthenticated()){
    const filePath = path.resolve("public", 'track.html');
    res.sendFile(filePath);
    }
})
app.get('/checkout', (req, res) =>{ 
    if (req.isAuthenticated()){
    const filePath = path.resolve("public", 'checkout.html');
    res.sendFile(filePath);
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
            </head>
            <body>
                <div id="content">
                    <pre>${JSON.stringify(data, null, 2)}</pre>  <!-- Mostra i dati in formato JSON -->
                </div>
                <button onclick="window.location.href='http://localhost:3000/checkout'">Go to checkout</button>
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
                <title>Confirm</title>
            </head>
            <body>
                <div id="content">
                    <pre>${JSON.stringify(data, null, 2)}</pre>  <!-- Mostra i dati in formato JSON -->
                </div>
                <button onclick="window.location.href='http://localhost:3000/orders'">Back to orders</button>
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
    // Gestione dei messaggi WebSocket
    ws.on('message', (message) => {
        console.log(`Received WebSocket message: ${message}`);
    });
});


server.listen(3000, () => {
    console.log('Server started on port 3000');
});

