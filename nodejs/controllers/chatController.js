const axios = require('axios');
const backendUrl = 'http://localhost:5000';

const postChat = async (req, res) => {
    console.log("Received request to /api/chat");
    try {
        const response = await axios.post(`${backendUrl}/api/v1/chat`, req.body);
        res.json(response.data);
    } catch (error) {
        res.status(error.response ? error.response.status : 500).json({
            message: error.message,
        });
    }
};

module.exports = {
    postChat,
};
