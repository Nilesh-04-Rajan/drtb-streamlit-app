const mongoose = require('mongoose');

const patientSchema = new mongoose.Schema({
    age: Number,
    gender: Number,
    heartRate: Number,
    respRate: Number,
    weight: Number,
    cd4rslt: Number,
    cultureResult: Number,
    afbMicroscopy: Number,
    tbHistory: Number,
    fever: Number,
    weightLoss: Number,
    hivStatus: Number,
    hivCd4Low: Number,
    prediction: Number,
    result: String,
    createdAt: { type: Date, default: Date.now }
});

module.exports = mongoose.model('Patient', patientSchema);
// This code defines a Mongoose schema for a Patient model in a Node.js application.