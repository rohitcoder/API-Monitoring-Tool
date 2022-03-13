import os, time, requests, yaml, json
from internals import *

config = getConfig()
endpoints = config['endpoints']

## Let's iterate over the endpoints and get the response times and status codes

for endpoint in endpoints:
    request_start_time = time.time()
    url = endpoint['url']
    method = endpoint['method']
    alert_conditions = endpoint['alert_conditions'] if 'alert_conditions' in endpoint else []
    headers = {}
    if 'headers' in endpoint:
        for header in endpoint['headers']:
            for key, value in header.items():
                headers[key] = value
    body = endpoint['body'] if 'body' in endpoint else None
    response = requests.request(method, url, headers=headers, data=body)
    request_end_time = time.time()
    response_time = round(float((request_end_time - request_start_time) * 1000), 2)
    ## Let's work on the alert conditions now
    for alert_condition in alert_conditions:
        print("\nWorking on alert condition: " + alert_condition['name'])
        if alert_condition['type'] == 'response_time':
            LogicBuilder(float(response_time), float(alert_condition['value']), alert_condition['operator'], alert_condition['message'].replace('{value}', str(response_time)))
        elif alert_condition['type'] == 'status_code':
            LogicBuilder(int(response.status_code), int(alert_condition['value']), alert_condition['operator'], alert_condition['message'].replace('{value}', str(response.status_code)))
    
    ## Now storing data
    MongoInsertOne("response_times", {"url": url, "response_time": response_time, "status_code": response.status_code, "timestamp": round(time.time() * 1000)})