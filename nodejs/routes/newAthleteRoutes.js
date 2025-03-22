const express = require('express');
const router = express.Router();
const newAthleteController = require('../controllers/newAthleteController');

router.get('/strava-auth', newAthleteController.redirectToStravaAuth);

module.exports = router;
