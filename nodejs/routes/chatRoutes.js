const express = require('express');
const router = express.Router();
const chatController = require('../controllers/chatController');

router.post('/process-question', chatController.postChat);

module.exports = router;
