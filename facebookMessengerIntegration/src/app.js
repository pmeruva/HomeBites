'use strict';

const apiai = require('apiai');
const express = require('express');
const bodyParser = require('body-parser');
const uuid = require('node-uuid');
const request = require('request');
const JSONbig = require('json-bigint');

const REST_PORT = (process.env.PORT || 5000);
const APIAI_ACCESS_TOKEN = process.env.APIAI_ACCESS_TOKEN;
const APIAI_LANG = process.env.APIAI_LANG || 'en';
const FB_VERIFY_TOKEN = process.env.FB_VERIFY_TOKEN;
const FB_PAGE_ACCESS_TOKEN = process.env.FB_PAGE_ACCESS_TOKEN;

const apiAiService = apiai(APIAI_ACCESS_TOKEN, {language: APIAI_LANG, requestSource: "fb"});
const sessionIds = new Map();

function processEvent(event) {
    var sender = event.sender.id.toString();

    if (event.message && event.message.text){
        var text = event.message.text;
    }
    else{
        var text = event.postback.payload;
    }

    // Handle a text message from this sender
    if (!sessionIds.has(sender)) {
        sessionIds.set(sender, uuid.v1());
    }

    console.log("Text", text);

    let apiaiRequest = apiAiService.textRequest(text,
        {
            sessionId: sessionIds.get(sender),
            contexts:[{
                name: "userID",
                parameters:{
                    userID: event.sender.id
                }
            }
            ]
        });

    apiaiRequest.on('response', (response) => {
        if (isDefined(response.result)) {
            let responseText = response.result.fulfillment.speech;
            let responseData = response.result.fulfillment.data;
            let action = response.result.action;

            if (isDefined(responseData) && isDefined(responseData.facebook)) {
                try {
                    console.log('Response as formatted message');
                    sendFBMessage(sender, responseData.facebook);
                } catch (err) {
                    sendFBMessage(sender, {text: err.message });
                }
            } else if (isDefined(responseText)) {
                console.log('Response as text message');
                // facebook API limit for text length is 320,
                // so we split message if needed
                var splittedText = splitResponse(responseText);

                for (var i = 0; i < splittedText.length; i++) {
                    sendFBMessage(sender, {text: splittedText[i]});
                }
            }

        }
    });

    apiaiRequest.on('error', (error) => console.error(error));
    apiaiRequest.end();
}

function processEventLocation(event, lat, long) {
    var sender = event.sender.id.toString();
    var latitude = lat.toString();
    var longitude = long.toString();
    var text = "lat:" + latitude + ", " + "long:" + longitude;

    // Handle a text message from this sender
    if (!sessionIds.has(sender)) {
        sessionIds.set(sender, uuid.v1());
    }

    console.log("Text", text);

    let apiaiRequest = apiAiService.textRequest(text,
        {
            sessionId: sessionIds.get(sender),
            contexts:[{
                name: "userID",
                parameters:{
                    userID: event.sender.id
                }
            }
            ]
        });

    apiaiRequest.on('response', (response) => {
        if (isDefined(response.result)) {
            let responseText = response.result.fulfillment.speech;
            let responseData = response.result.fulfillment.data;
            let action = response.result.action;

            if (isDefined(responseData) && isDefined(responseData.facebook)) {
                try {
                    console.log('Response as formatted message');
                    sendFBMessage(sender, responseData.facebook);
                } catch (err) {
                    sendFBMessage(sender, {text: err.message });
                }
            } else if (isDefined(responseText)) {
                console.log('Response as text message');
                // facebook API limit for text length is 320,
                // so we split message if needed
                var splittedText = splitResponse(responseText);

                for (var i = 0; i < splittedText.length; i++) {
                    sendFBMessage(sender, {text: splittedText[i]});
                }
            }

        }
    });

    apiaiRequest.on('error', (error) => console.error(error));
    apiaiRequest.end();
}

function splitResponse(str) {
    if (str.length <= 320)
    {
        return [str];
    }

    var result = chunkString(str, 300);

    return result;

}

function chunkString(s, len)
{
    var curr = len, prev = 0;

    var output = [];

    while(s[curr]) {
        if(s[curr++] == ' ') {
            output.push(s.substring(prev,curr));
            prev = curr;
            curr += len;
        }
        else
        {
            var currReverse = curr;
            do {
                if(s.substring(currReverse - 1, currReverse) == ' ')
                {
                    output.push(s.substring(prev,currReverse));
                    prev = currReverse;
                    curr = currReverse + len;
                    break;
                }
                currReverse--;
            } while(currReverse > prev)
        }
    }
    output.push(s.substr(prev));
    return output;
}

function sendFBMessage(sender, messageData) {
    request({
        url: 'https://graph.facebook.com/v2.6/me/messages',
        qs: {access_token: FB_PAGE_ACCESS_TOKEN},
        method: 'POST',
        json: {
            recipient: {id: sender},
            message: messageData
        }
    }, function (error, response, body) {
        if (error) {
            console.log('Error sending message: ', error);
        } else if (response.body.error) {
            console.log('Error: ', response.body.error);
        }
    });
}

function doSubscribeRequest() {
    request({
            method: 'POST',
            url: "https://graph.facebook.com/v2.6/me/subscribed_apps?access_token=" + FB_PAGE_ACCESS_TOKEN
        },
        function (error, response, body) {
            if (error) {
                console.error('Error while subscription: ', error);
            } else {
                console.log('Subscription result: ', response.body);
            }
        });
}

function isDefined(obj) {
    if (typeof obj == 'undefined') {
        return false;
    }

    if (!obj) {
        return false;
    }

    return obj != null;
}

function sendSqueakOptions(sender) {
    let messageData = { 
            text:"What happened?",
            quick_replies:[
                {
                    content_type:"text",
                    title: "Speeding",
                    payload: "speeding"
                },
                {
                    content_type:"text",
                    title: "Harsh Breaking",
                    payload: "harsh_breaking"
                },
                {
                    content_type:"text",
                    title: "Near Miss",
                    payload: "near_miss"
                },
                {
                    content_type:"text",
                    title: "Jumped a Red Light",
                    payload: "jumped_redlight"
                },
                {
                    content_type:"text",
                    title: "Driving Wrong Way",
                    payload: "driving_on_wrong_side_of_road"
                },
                {
                    content_type:"text",
                    title: "Other",
                    payload: "squeakOther"
                }
            ]
        }
    
    request({
        url: 'https://graph.facebook.com/v2.6/me/messages',
        qs: {access_token:FB_PAGE_ACCESS_TOKEN},
        method: 'POST',
        json: {
            recipient: {id:sender},
            message: messageData,
        }
    }, function(error, response, body) {
        if (error) {
            console.log('Error sending messages: ', error)
        } else if (response.body.error) {
            console.log('Error: ', response.body.error)
        }
    })
}

const app = express();

app.use(bodyParser.text({ type: 'application/json' }));

app.get('/webhook/', function (req, res) {
    if (req.query['hub.verify_token'] == FB_VERIFY_TOKEN) {
        res.send(req.query['hub.challenge']);
        
        setTimeout(function () {
            doSubscribeRequest();
        }, 3000);
    } else {
        res.send('Error, wrong validation token');
    }
});

app.post('/webhook/', function (req, res) {
    try {

        var data = JSONbig.parse(req.body);
        var messaging_events = data.entry[0].messaging;
        for (var i = 0; i < messaging_events.length; i++) {
            let event = data.entry[0].messaging[i];
            let sender = event.sender.id;
            if(event.message){
                if (event.message.text){
                    sendFBMessage(sender, "testingSuccesful")
                    processEvent(event)
                }else if (event.message.attachments[0].payload.coordinates){
                    //let text = JSON.stringify(event.message.attachments[0].payload.coordinates.lat)
                    let lat = String(event.message.attachments[0].payload.coordinates.lat)
                    let long = String(event.message.attachments[0].payload.coordinates.long)
                    processEventLocation(event, lat, long)
                }
            }
            if(event.postback){
                processEvent(event);
            }
        }
        return res.status(200).json({
            status: "ok"
        });
    } catch (err) {
        return res.status(400).json({
            status: "error",
            error: err
        });
    }

});

app.listen(REST_PORT, function () {
    console.log('Rest service ready on port ' + REST_PORT);
});

doSubscribeRequest();