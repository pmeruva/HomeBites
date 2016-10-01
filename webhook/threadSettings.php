
<html>
<head>
<title>Online PHP Script Execution</title>
</head>
<body>
<?php

    $url = 'https://graph.facebook.com/v2.6/me/thread_settings?access_token=EAANZBjIqMJggBAEqgInd77HcmU45zIK14ZAbZCj0AdSZAjn3wE90wJWsLZCZAiLsceb1pNZChwaawKY5SdEgtjkNSVwQbeLQ25DOhTKeAZCVk0OM9iSXVHcxNd61b9vRN6aH9EbZBM0VFDzZAVcqZBvAPtgJ3u6S95cCa3R8ZBT9PVX18QZDZD';
    $data = 
    '{
        "setting_type":"call_to_actions",
        "thread_state":"new_thread",
        "call_to_actions":[
            {
                "payload":"hey",
            }
        ]
    }';
    
    //$data_real = json_encode($data);
    
    $ch = curl_init();
    $format="json";
    $ch = curl_init($url);                                                                      
    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST");                                                                     
    curl_setopt($ch, CURLOPT_POSTFIELDS, $data);                                                                  
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);                                                                      
    curl_setopt($ch, CURLOPT_HTTPHEADER, array(                                                                          
        'Content-Type: application/json',                                                                                
        'Content-Length: ' . strlen($data))                                                                       
    );                                                                                                                   
    $result = curl_exec($ch);
    curl_close($ch);
    echo $result;
    
    
?>
</body>
</html>








<html>
<head>
<title>Online PHP Script Execution</title>
</head>
<body>
<?php

    $url = 'https://graph.facebook.com/v2.6/me/thread_settings?access_token=EAANZBjIqMJggBAEqgInd77HcmU45zIK14ZAbZCj0AdSZAjn3wE90wJWsLZCZAiLsceb1pNZChwaawKY5SdEgtjkNSVwQbeLQ25DOhTKeAZCVk0OM9iSXVHcxNd61b9vRN6aH9EbZBM0VFDzZAVcqZBvAPtgJ3u6S95cCa3R8ZBT9PVX18QZDZD';
    $data = 
    '{
        "setting_type":"greeting",
        "thread_state":"new_thread",
        "greeting":{
            "text":"Welcome to the HAMS User Bot! Please press GET STARTED to begin Squeaking away!",
        }
    }';
    
    //$data_real = json_encode($data);
    
    $ch = curl_init();
    $format="json";
    $ch = curl_init($url);                                                                      
    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST");                                                                     
    curl_setopt($ch, CURLOPT_POSTFIELDS, $data);                                                                  
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);                                                                      
    curl_setopt($ch, CURLOPT_HTTPHEADER, array(                                                                          
        'Content-Type: application/json',                                                                                
        'Content-Length: ' . strlen($data))                                                                       
    );                                                                                                                   
    $result = curl_exec($ch);
    curl_close($ch);
    echo $result;
    
    
?>
</body>
</html>


<html>
<head>
<title>Online PHP Script Execution</title>
</head>
<body>
<?php

    $url = 'https://graph.facebook.com/v2.6/me/thread_settings?access_token=EAANZBjIqMJggBAEqgInd77HcmU45zIK14ZAbZCj0AdSZAjn3wE90wJWsLZCZAiLsceb1pNZChwaawKY5SdEgtjkNSVwQbeLQ25DOhTKeAZCVk0OM9iSXVHcxNd61b9vRN6aH9EbZBM0VFDzZAVcqZBvAPtgJ3u6S95cCa3R8ZBT9PVX18QZDZD';
    $data = 
    '{
        "setting_type":"call_to_actions",
        "thread_state":"existing_thread",
        "call_to_actions":[
            {
                "type":"postback",
                "title":"Start New Ride Sequence",
                "payload":"hey"
            },
            {
                "type":"postback",
                "title":"Where is my cab?",
                "payload":"location"
            },
            {
                "type":"postback",
                "title":"Squeak!",
                "payload":"squeak"
            },
            {
                "type":"postback",
                "title":"PANIC!",
                "payload":"panic"
            }
        ]
    }';
    
    //$data_real = json_encode($data);
    
    $ch = curl_init();
    $format="json";
    $ch = curl_init($url);                                                                      
    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST");                                                                     
    curl_setopt($ch, CURLOPT_POSTFIELDS, $data);                                                                  
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);                                                                      
    curl_setopt($ch, CURLOPT_HTTPHEADER, array(                                                                          
        'Content-Type: application/json',                                                                                
        'Content-Length: ' . strlen($data))                                                                       
    );                                                                                                                   
    $result = curl_exec($ch);
    curl_close($ch);
    echo $result;
    
    
?>
</body>
</html>