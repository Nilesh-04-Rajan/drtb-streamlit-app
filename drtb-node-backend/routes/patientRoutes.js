const express = require('express');
const router = express.Router();
const axios = require('axios');
const Patient = require('../models/Patient');

router.post('/', async (req, res) => {
    try {
        const input = req.body;

        // Call Flask API
        const response = await axios.post('http://127.0.0.1:5000/predict', input);
        const { prediction, result } = response.data;

        // Save to MongoDB
        const newPatient = new Patient({ ...input, prediction, result });
        await newPatient.save();

        res.json({ prediction, result });
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Prediction failed', details: err.message });
    }
});

module.exports = router;
// This code defines a route for handling patient data and predictions in an Express.js application.