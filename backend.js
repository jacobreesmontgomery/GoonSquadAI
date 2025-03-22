const express = require('express');
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

// Routes
const activitiesRoutes = require('./nodejs/routes/activitiesRoutes');
const chatRoutes = require('./nodejs/routes/chatRoutes');
const newAthleteRoutes = require('./nodejs/routes/newAthleteRoutes');
app.use('/api/activities', activitiesRoutes);
app.use('/api/chat', chatRoutes);
app.use('/api/new-athlete', newAthleteRoutes);

// Start the server
app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
});
