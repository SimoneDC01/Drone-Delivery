const express = require('express');
const path = require('path');
const app = express();

app.get('/', (req, res) =>{ 
    const filePath = path.resolve("public", 'index.html');
    res.sendFile(filePath);
});

app.get('/getProductsInfo', (req, res) => {
    const name = req.query.asins;
    const payload = { asins: name };

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

app.listen(3000, () => {
    console.log('Server started on port 3000');
});