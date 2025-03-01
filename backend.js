const express = require('express');
const axios = require('axios');
const app = express();
const cors = require('cors');
const port = 5001;

// Use CORS middleware for cross-origin requests
app.use(cors());

// Middleware to parse JSON bodies
app.use(express.json());

// Static file serving middleware
const directory = 'C:/Users/17178/Desktop/GITHUB_PROJECTS/GoonSquadAI/python'
app.use('/files', express.static(directory));

const backendUrl = 'http://localhost:5000';

// Route to handle requests and forward to FastAPI backend
app.get('/api/activities/basic-stats', async (req, res) => {
    console.log("Received request to /api/activities/basic-stats")
    try {
        const response = await axios.get(`${backendUrl}/api/activities/basic-stats`);
        res.json(response.data);
    } catch (error) {
        res.status(error.response ? error.response.status : 500).json({
            message: error.message,
        });
    }
});

app.get('/api/activities/detailed-stats', async (req, res) => {
    console.log("Received request to /api/activities/detailed-stats")
    try {
        const response = await axios.get(`${backendUrl}/api/activities/detailed-stats`);
        res.json(response.data);
    } catch (error) {
        res.status(error.response ? error.response.status : 500).json({
            message: error.message,
        });
    }
});

app.post('/api/chat', async (req, res) => {
    console.log("Received request to /api/chat")
    try {
        const response = await axios.post(`${backendUrl}/api/chat`, req.body);
        res.json(response.data);
    } catch (error) {
        res.status(error.response ? error.response.status : 500).json({
            message: error.message,
        });
    }
});

app.get('/api/new-athlete/strava-auth', async (req, res) => {
    console.log('Redirecting to Strava OAuth');
    res.redirect(`${backendUrl}/api/new-athlete`);
})

// Start the server
app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
});
