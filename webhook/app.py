
#!/usr/bin/env python

import urllib
import urllib2
import json
import csv
import os
import time
import re

from flask import Flask
from flask import request
from flask import make_response

from time import gmtime, strftime

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    result = req.get("result")
    parameters = result.get("parameters")
    contexts = result.get("contexts")
    contextParameters = contexts[0].get("parameters")

    userFacebookId = contextParameters.get("userID") #1063014673817955
    
    page_access_token = "EAAY9RYtqBZAkBAJBjKZAVpd0IoPZCcmOpx1V8Xv98ZB9tFJHWiFcoBMHO5dP48373rUlgxHUQ7hYOyn9J7MjcEytzW1I1vclKygFGfyKZCq6QAxV4jrj4V37CEOmdhh7i6U6BXy39HZBVQuzZB3HIBAtf3aJW6zNPsvdduwm6gm8wZDZD"
    userUrl = "https://graph.facebook.com/v2.6/" + str(userFacebookId) + "?fields=first_name,last_name,profile_pic&access_token=" + page_access_token
    urlRead = urllib.urlopen(userUrl).read()
    userJson = json.loads(urlRead)
    first_name = userJson.get("first_name")
    last_name = userJson.get("last_name")
    profile_pic = userJson.get("profile_pic")

    result = req.get("result")
    parameters = result.get("parameters")
    key = str(result.get("action"))    
    if key == 'locationRecorded':
        lat = str(parameters.get("lat"))
        lon = str(parameters.get("long"))
        locationPostUrl = "http://18.189.47.26:3000/putLoc?location=" + lat + "+" + lon + "&id=" + userFacebookId
        coordinates = urllib.urlopen(locationPostUrl) 
        return makeWebhookResultChoice()
    elif key == 'welcomeMessage':
        return makeWebhookResultWelcome(str(first_name))
    elif key == "userTypeGuest":
        return makeWebhookResultGuestHomeScreen()
    elif key == "guestMainscreenInHome":
        foodType = str(parameters.get("foodType"))
        time = str(parameters.get("time"))
        maxPriceString = str(parameters.get("maxPrice"))
        maxPriceArray = re.findall(r"[-+]?\d*\.\d+|\d+", maxPriceString)
        maxPrice = str(maxPriceArray[0])
        distanceString = str(parameters.get("distance"))
        distanceArray = re.findall(r"[-+]?\d*\.\d+|\d+", distanceString)
        distance = str(distanceArray[0])

        locationUrl = "http://18.189.47.26:3000/loc?id=" + userFacebookId
        coordinates = urllib2.urlopen(locationUrl).read()
        coords = coordinates.split(" ")

        requestPostUrl = "http://18.189.47.26:3000/req?id=" + userFacebookId + "&location=" + coords[0] + "+" + coords[1] + "&desc=" + foodType + "&time=" + time + "&cost=" + maxPrice + "&dist=" + distance
        requestPostUrlResponse = urllib.urlopen(requestPostUrl) 
        return makeWebhookResultGuestOrderConfirmation(foodType, time, maxPrice, distance)
    elif key == "hostMainscreen":
        locationUrl = "http://18.189.47.26:3000/loc?id=" + userFacebookId
        coordinates = urllib2.urlopen(locationUrl).read()
        coords = coordinates.split(" ")

        requestsUrl = "http://18.189.47.26:3000/see?location=" + coords[0] + "+" + coords[1]
        requestsString = urllib2.urlopen(requestsUrl).read()
        requestsJson = json.loads(requestsString)
        for request in requestsJson:
            guestId = request["student"]
            foodType = request["desc"]
            cost = request["cost"]
            time = request["max_time"]
            text = "Food Type Requested: " + foodType + "\n" + "Price of Meal: " + cost + "\n" + "Time to Serve Meal: " + time
            sendOpenRequests(userFacebookId, text, str(guestId))
        return makeWebhookResultChooseRequest()
    elif key == "match":
        locationUrl = "http://18.189.47.26:3000/loc?id=" + userFacebookId
        coordinates = urllib2.urlopen(locationUrl).read()
        coords = coordinates.split(" ")

        guestId = str(parameters.get("userFacebookId"))

        sendMatchMap(guestId, coords)

        return makeWebhookResultEndService(guestId)
    elif key == "endService":
        guestId = str(parameters.get("userFacebookId"))
        receipt = "Please be sure to pay your host the agreed price."
        sendMessage(guestId, receipt)

        return makeWebhookResultBye(first_name)
    else:
        return {
            "speech": "Error",
            "displayText": "Error",
            "data": {"facebook": facebook_message},
            #"contextOut": [],
            "source": "apiai-python-webhook-sample"
        }

def sendMessage(senderID, text):
    data = {
        "recipient":{
            "id": senderID
        },
        "message": {
            "text": text
        }
    }

    jsonData = json.dumps(data, indent=4)
    req = urllib2.Request("https://graph.facebook.com/v2.6/me/messages?access_token=EAAY9RYtqBZAkBAJBjKZAVpd0IoPZCcmOpx1V8Xv98ZB9tFJHWiFcoBMHO5dP48373rUlgxHUQ7hYOyn9J7MjcEytzW1I1vclKygFGfyKZCq6QAxV4jrj4V37CEOmdhh7i6U6BXy39HZBVQuzZB3HIBAtf3aJW6zNPsvdduwm6gm8wZDZD", jsonData, {'Content-Type': 'application/json'})
    f = urllib2.urlopen(req)
    return f

def sendOpenRequests(senderID, text, guestID):
    data = {
        "recipient":{
            "id": senderID
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload":{
                    "template_type":"button",
                    "text":str(text),
                    "buttons":[
                        {
                            "type":"postback",
                            "title": "Claim",
                            "payload": "id: " + str(guestID),
                        }
                    ]
                }
            }
        }
    }

    jsonData = json.dumps(data, indent=4)
    req = urllib2.Request("https://graph.facebook.com/v2.6/me/messages?access_token=EAAY9RYtqBZAkBAJBjKZAVpd0IoPZCcmOpx1V8Xv98ZB9tFJHWiFcoBMHO5dP48373rUlgxHUQ7hYOyn9J7MjcEytzW1I1vclKygFGfyKZCq6QAxV4jrj4V37CEOmdhh7i6U6BXy39HZBVQuzZB3HIBAtf3aJW6zNPsvdduwm6gm8wZDZD", jsonData, {'Content-Type': 'application/json'})
    f = urllib2.urlopen(req)
    return f

def sendMatchMap(senderID, coords):
    picUrl = "https://maps.googleapis.com/maps/api/staticmap?size=600x600&markers=color:red%7Clabel:S%7C" + coords[0] + ',' + coords[1] + "&key=AIzaSyDDL7nCwQ9fZpFDN_X9K55txG8zcFFkQ3o"

    data = {
        "recipient":{
            "id": senderID
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload":{
                    "template_type":"generic",
                    "elements":[
                        {
                            "title":"Please go to the above shown location at your requested time for your meal.",
                            "image_url": picUrl,
                            "subtitle": "HomeBites: Connecting hosts and guests through home-cooked meals.",
                        }
                    ]
                }
            }
        }
    }

    jsonData = json.dumps(data, indent=4)
    req = urllib2.Request("https://graph.facebook.com/v2.6/me/messages?access_token=EAAY9RYtqBZAkBAJBjKZAVpd0IoPZCcmOpx1V8Xv98ZB9tFJHWiFcoBMHO5dP48373rUlgxHUQ7hYOyn9J7MjcEytzW1I1vclKygFGfyKZCq6QAxV4jrj4V37CEOmdhh7i6U6BXy39HZBVQuzZB3HIBAtf3aJW6zNPsvdduwm6gm8wZDZD", jsonData, {'Content-Type': 'application/json'})
    f = urllib2.urlopen(req)
    return f

def makeWebhookResultWelcome(first_name):
    facebook_message = {
        "attachment": {
            "type": "template",
            "payload":{
                "template_type":"generic",
                "elements":[
                    {
                        "title":"Hey " + first_name + ", welcome to HomeBites! Please share your location to get started.",
                        "image_url": "https://scontent-yyz1-1.xx.fbcdn.net/t31.0-8/14305328_1789982957925713_4821186365540198594_o.jpg",
                        "subtitle": "HomeBites: Connecting hosts and guests through home-cooked meals.",
                    }
                ]
            }
        }
    }
    #print(json.dumps(slack_message))

    return {
        "speech": "welcome",
        "displayText": "welcome",
        "data": {"facebook": facebook_message},
        #"contextOut": [],
        "source": "apiai-python-webhook-sample"
    }

def makeWebhookResultBye(first_name):
    facebook_message = {
        "attachment": {
            "type": "template",
            "payload":{
                "template_type":"generic",
                "elements":[
                    {
                        "title":"Thanks for using HomeBites " + first_name + "!",
                        "image_url": "https://scontent-yyz1-1.xx.fbcdn.net/t31.0-8/14305328_1789982957925713_4821186365540198594_o.jpg",
                        "subtitle": "HomeBites: Connecting hosts and guests through home-cooked meals.",
                    }
                ]
            }
        }
    }
    #print(json.dumps(slack_message))

    return {
        "speech": "welcome",
        "displayText": "welcome",
        "data": {"facebook": facebook_message},
        #"contextOut": [],
        "source": "apiai-python-webhook-sample"
    }

def makeWebhookResultChooseRequest():
    facebook_message = {
        "attachment": {
            "type": "template",
            "payload":{
                "template_type":"generic",
                "elements":[
                    {
                        "title":"Please choose one of the open requests listed above.",
                        "image_url": "https://scontent.fash1-1.fna.fbcdn.net/v/t1.0-9/14322403_1790092294581446_8955059859612861890_n.png?oh=fd28927b0e33b008806a3f7704388aaa&oe=5878C66A",
                        "subtitle": "HomeBites: Connecting hosts and guests through home-cooked meals.",
                    }
                ]
            }
        }
    }
    #print(json.dumps(slack_message))

    return {
        "speech": "welcome",
        "displayText": "welcome",
        "data": {"facebook": facebook_message},
        #"contextOut": [],
        "source": "apiai-python-webhook-sample"
    }

def makeWebhookResultEndService(guestId):
    facebook_message = {
        "attachment": {
            "type": "template",
            "payload":{
                "template_type":"generic",
                "elements":[
                    {
                        "title":"Please click end service when the dinner is over.",
                        "image_url": "https://scontent.fash1-1.fna.fbcdn.net/v/t1.0-9/14322403_1790092294581446_8955059859612861890_n.png?oh=fd28927b0e33b008806a3f7704388aaa&oe=5878C66A",
                        "subtitle": "HomeBites: Connecting hosts and guests through home-cooked meals.",
                        "buttons":[
                            {
                                "type":"postback",
                                "title": "End Service",
                                "payload": "endService: " + str(guestId)
                            }
                        ]
                    }
                ]
            }
        }
    }
    #print(json.dumps(slack_message))

    return {
        "speech": "welcome",
        "displayText": "welcome",
        "data": {"facebook": facebook_message},
        #"contextOut": [],
        "source": "apiai-python-webhook-sample"
    }

def makeWebhookResultChoice():
    facebook_message = {
        "attachment": {
            "type": "template",
            "payload":{
                "template_type":"generic",
                "elements":[
                    {
                        "title":"Are you a host or a guest?",
                        "image_url": "https://scontent.xx.fbcdn.net/v/t1.0-9/14344071_1789841581273184_4051637143203412423_n.jpg?oh=8524b380390ad9694c1a777da8750dbd&oe=583BEA47",
                        "subtitle": "HomeBites: Connecting hosts and guests through home-cooked meals.",
                        "buttons":[
                            {
                                "type":"postback",
                                "title": "Host",
                                "payload": "userTypeHost"
                            },
                            {
                                "type":"postback",
                                "title": "Guest",
                                "payload": "userTypeGuest"
                            }
                        ]
                    }
                ]
            }
        }
    }
    #print(json.dumps(slack_message))

    return {
        "speech": "welcome",
        "displayText": "welcome",
        "data": {"facebook": facebook_message},
        #"contextOut": [],
        "source": "apiai-python-webhook-sample"
    }

def makeWebhookResultGuestHomeScreen():
    facebook_message = {
        "attachment": {
            "type": "template",
            "payload":{
                "template_type":"generic",
                "elements":[
                    {
                        "title":"Would you like to go to the Host's home or have the food delivered to you?",
                        "image_url": "https://scontent.fash1-1.fna.fbcdn.net/v/t1.0-9/14322210_1790067741250568_3411285455221311596_n.png?oh=b1e7a3eecb7b470af4ff15c4cd264ee7&oe=58803DC3",
                        "subtitle": "HomeBites: Connecting hosts and guests through home-cooked meals.",
                        "buttons":[
                            {
                                "type":"postback",
                                "title": "Dine In",
                                "payload": "userTypeGuestInHome"
                            },
                            {
                                "type":"postback",
                                "title": "Delivery",
                                "payload": "userTypeGuestInHome"
                            }
                        ]
                    }
                ]
            }
        }
    }
    #print(json.dumps(slack_message))

    return {
        "speech": "welcome",
        "displayText": "welcome",
        "data": {"facebook": facebook_message},
        #"contextOut": [],
        "source": "apiai-python-webhook-sample"
    }

def makeWebhookResultGuestOrderConfirmation(foodType, time, maxPrice, distance):
    facebook_message = {
        "attachment": {
            "type": "template",
            "payload":{
                "template_type":"generic",
                "elements":[
                    {
                        "title":"Great! We'll alert you as soon as your placed order is claimed by a host.",
                        "image_url": "https://scontent-yyz1-1.xx.fbcdn.net/v/t1.0-9/14330042_1789992471258095_5938472203081591516_n.png?oh=86f2d2a29c18c95158a1e7593738db04&oe=587706AA",
                        "subtitle": foodType + " ; " + time + " ; $" + maxPrice + " ; " + distance + " miles",
                    }
                ]
            }
        }
    }
    #print(json.dumps(slack_message))

    return {
        "speech": "welcome",
        "displayText": "welcome",
        "data": {"facebook": facebook_message},
        #"contextOut": [],
        "source": "apiai-python-webhook-sample"
    }

def makeWebhookResultCards(first_name):
    facebook_message = {
        "attachment": {
            "type": "template",
            "payload":{
                "template_type":"generic",
                "elements":[
                    {
                        "title":"Hey " + first_name + ", welcome to HomeBites! Are you a host or a guest?",
                        "image_url": "https://scontent.xx.fbcdn.net/v/t1.0-9/14344071_1789841581273184_4051637143203412423_n.jpg?oh=8524b380390ad9694c1a777da8750dbd&oe=583BEA47",
                        "subtitle": "HomeBites: Connecting hosts and guests through home-cooked meals.",
                        "buttons":[
                            {
                                "type":"postback",
                                "title": "Host",
                                "payload": "userTypeHost"
                            },
                            {
                                "type":"postback",
                                "title": "Guest",
                                "payload": "userTypeGuest"
                            }
                        ]
                    },
                    {
                        "title":"Hey " + first_name + ", welcome to HomeBites! Are you a host or a guest?",
                        "image_url": "https://scontent.xx.fbcdn.net/v/t1.0-9/14344071_1789841581273184_4051637143203412423_n.jpg?oh=8524b380390ad9694c1a777da8750dbd&oe=583BEA47",
                        "subtitle": "HomeBites: Connecting hosts and guests through home-cooked meals.",
                        "buttons":[
                            {
                                "type":"postback",
                                "title": "Host",
                                "payload": "userTypeHost"
                            },
                            {
                                "type":"postback",
                                "title": "Guest",
                                "payload": "userTypeGuest"
                            }
                        ]
                    }
                ]
            }
        }
    }
    #print(json.dumps(slack_message))

    return {
        "speech": "welcome",
        "displayText": "welcome",
        "data": {"facebook": facebook_message},
        #"contextOut": [],
        "source": "apiai-python-webhook-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=False, port=port, host='0.0.0.0')