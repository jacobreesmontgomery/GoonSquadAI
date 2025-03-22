const axios = require('axios');
const backendUrl = 'http://localhost:5000';

const getBasicStats = async (req, res) => {
    console.log("Received request to /api/activities/basic-stats");
    try {
        const response = await axios.get(`${backendUrl}/api/v1/activities/basic-stats`);
        res.json(response.data);
    } catch (error) {
        res.status(error.response ? error.response.status : 500).json({
            message: error.message,
        });
    }
};

const getDetailedStats = async (req, res) => {
    console.log("Received request to /api/activities/detailed-stats");
    try {
        const response = await axios.get(`${backendUrl}/api/v1/activities/detailed-stats`);
        res.json(response.data);
    } catch (error) {
        res.status(error.response ? error.response.status : 500).json({
            message: error.message,
        });
    }
};

module.exports = {
    getBasicStats,
    getDetailedStats,
};
