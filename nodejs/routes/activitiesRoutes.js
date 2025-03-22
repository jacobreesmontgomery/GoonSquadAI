const express = require('express');
const router = express.Router();
const activitiesController = require('../controllers/activitiesController');

router.get('/basic-stats', activitiesController.getBasicStats);
router.get('/detailed-stats', activitiesController.getDetailedStats);

module.exports = router;
