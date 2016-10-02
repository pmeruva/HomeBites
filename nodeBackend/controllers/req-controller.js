var Models = require('../models/Model.js');
var geolib = require('geolib');

RequestController = {};

/*
 * Request a food item for the night. Puts a request in our SQL databases
 * @param id        the ID of the student requesting the food
 * @param location  the location of the student requesting food
 * @param desc      the food style DESCription requested
 * @param cost      the maximum price willing to be paid
 * @param time      the maximum time willing to wait for food
 * @return 'DONE' if request input was successful.
 */
RequestController.requestFood = function(req, res, next){
  var id         = req.query.id,
      location   = req.query.location,
      desc       = req.query.desc,
      dist       = parseFloat(req.query.dist),
      max_time   = req.query.time,
      cost       = req.query.cost;

  var request = {
    "student"  : id,
    "desc"     : desc,
    "cost"     : cost,
    "location" : location,
    "max_time" : max_time,
    "st_time"  : Date.now(),
    "distance" : dist,
    "isOpen"   : 1
  };

  console.log(request);

  Models.client.createDocument(Models.requests._self, request, function(err, doc){
    if (err) return next(err);
    console.log(doc);
    res.send(doc);
  });

  var querySpec = {
      query: 'SELECT * FROM docs d WHERE d.fbID = @id',
      parameters: [{
          name: '@id',
          value: id
      }]
  };
  Models.client.queryDocuments(Models.users._self, querySpec).toArray(function(err, users){
    if (users.length > 0){
      user = users[0];
      Models.client.deleteDocument(user._self, function(err){
        if(err) return next(err);
      });
    }
      var user = {
        "fbID"       : id,
        "location" : location
      }

      Models.client.createDocument(Models.users._self, user, function(err, doc){
        if (err) return next(err);
      });

  });
};

/*
 * Looks at nearby requests for food.
 * @param location the location of the server
 * @return SQL rows of all open requests within (5 km?)
 *
 */
RequestController.seeRequests = function(req, res, next){
  var location = req.query.location;

  var reqQuer = {
    query: "SELECT * FROM docs d where d.isOpen = 1"
  }
  Models.client.queryDocuments(Models.requests._self, reqQuer).toArray(function(err, reqs){
    if (err) return next(err);
    for (var index in reqs){
      var request = reqs[index];
      //calculate distance to host location
      request.distTo = RequestController.distCalc(location, request.location);

      //remove if too far away
      if(request.distTo > request.dist || request.max_time < Date.now()) {
        reqs.splice(index, 1);
      }
    }

    //sort by decreasing distance
    reqs.sort(function(r1, r2){
      return r1.distTo - r2.distTo;
    });
    res.send(JSON.stringify(reqs));
  });
};

/*
 * Updates the Location of an ID
 * @param id        the FbID of the person
 * @param location  the new location of the person
 * @returns DONE if success, else nothing.
 */
 RequestController.putLocID = function(req, res, next){
   var location = req.query.location,
       id       = req.query.id;

   var querySpec = {
       query: 'SELECT * FROM docs d WHERE d.fbID = @id',
       parameters: [{
           name: '@id',
           value: id
       }]
   };
   Models.client.queryDocuments(Models.users._self, querySpec).toArray(function(err, users){
     if (users.length > 0){
       user = users[0];
       Models.client.deleteDocument(user._self, function(err){
         if(err){
           console.log(err);
           return next(err);
         }
       });
     }
       var user = {
         "fbID"       : id,
         "location"   : location
       }

       Models.client.createDocument(Models.users._self, user, function(err, doc){
         if (err) return next(err);
       });
   });

   res.send("DONE");
 }

/*
 * Finds a location (lat long form) based on an ID
 * @params id the id of the facebook user to search the location from
 * @return the location (lat long) of the facebook user when last using our bot.
 */
 RequestController.locByID = function(req, res, next){
   var id = req.query.id;
   console.log('id');

   var userQuer = {
     query: 'SELECT * FROM docs d WHERE d.fbID = @id',
     parameters: [{
         name: '@id',
         value: id
     }]
   };

   Models.client.queryDocuments(Models.users._self, userQuer).toArray(function(err, users){
     if (err) return next(err);
     if (users.length < 1){
       res.send("null");
     }
     console.log(users);
     res.send(users[0].location);
   });
 };

 /*
  * Finds a request based on an ID
  * @params id the id of the facebook user to search from
  * @return the request of the facebook user when last using our bot.
  */
  RequestController.reqByID = function(req, res, next){
    var id = req.query.id;
    console.log('id');

    var userQuer = {
      query: 'SELECT * FROM docs d WHERE d.fbID = @id',
      parameters: [{
          name: '@id',
          value: id
      }]
    };

    Models.client.queryDocuments(Models.requests._self, userQuer).toArray(function(err, users){
      if (err) return next(err);
      if (users.length < 1){
        res.send("null");
      }
      console.log(users);
      res.send(users[users.length-1]);
    });
  };


RequestController.distCalc = function(point1, point2){

  console.log(point1);
  console.log(point2);
  geo1 = point1.split(' ');
  geo2 = point2.split(' ');

  loc1 = {
    latitude  : parseFloat(geo1[0]),
    longitude : parseFloat(geo1[1])
  }

  loc2 = {
    latitude  : parseFloat(geo2[0]),
    longitude : parseFloat(geo2[1])
  }

  console.log(loc1);
  console.log(loc2);

  return geolib.getDistance(loc1, loc2, 10) * 0.621;
};

//It's good habit to have this at the very end
module.exports = RequestController;
