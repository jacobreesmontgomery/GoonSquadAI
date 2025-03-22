const axios = require('axios');
const backendUrl = 'http://localhost:5000';

const redirectToStravaAuth = async (req, res) => {
    console.log('Redirecting to Strava OAuth');
    res.redirect(`${backendUrl}/api/new-athlete`);
};

module.exports = {
    redirectToStravaAuth,
};
