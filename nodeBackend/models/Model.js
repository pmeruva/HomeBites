var DocumentClient = require("documentdb").DocumentClient;

Models = {};

var endpoint = "https://jarvis.documents.azure.com:443/";
var authKey  = "sg7k455ig7EwVfe214VmziWIeHdae9iQsHqutLDOZAZddX9icXJSSTvAAIiFlkPd8YKireyfrIeaqQPDceC92w==";

Models.client  = new DocumentClient(endpoint, {"masterKey": authKey});


var databaseDefinition = {"id": "homeBites"};
var requestDefinition = {"id": "requests"};
var userDefinition = {"id": "users"};

Models.client.createDatabase(databaseDefinition, function(err, database){
  if (err) throw err;
  Models.client.createCollection(database._self, requestDefinition, function(err, requestCollection){
    if (err) throw err;
    Models.requests = requestCollection;
  });
  Models.client.createCollection(database._self, userDefinition, function(err, userCollection){
    if (err) throw err;
      Models.users = userCollection;
  });

  console.log("collections created");

});

module.exports = Models;
