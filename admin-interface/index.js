const express = require('express');
const path = require('path');
const app = express();

app.get('/', (req, res) =>{ 
    const filePath = path.resolve("public", 'index.html');
    res.sendFile(filePath);
});

app.get('/advance', (req, res) => {
    const minutes = req.query.minutes;
    const payload = { minutes: minutes };

    fetch(`http://time:8080/advance`, {
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
    fetch(`http://time:8080/date_and_time_request`, {
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


app.listen(5000, () => {
    console.log('Server started on port 5000');
});