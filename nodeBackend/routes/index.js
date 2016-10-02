var express = require('express')
var router = express.Router();

var reqController = require('../controllers/req-controller')


router.get('/req/', reqController.requestFood);
router.get('/see/', reqController.seeRequests);
router.get('/loc/', reqController.locByID);
router.get('/idToReq/', reqController.reqByID);
router.get('/putLoc/', reqController.putLocID);

module.exports = router;
