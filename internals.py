from twilio.rest import Client
from pymongo import MongoClient
from tinydb import TinyDB, Query
import requests, yaml, os, time, yaml

absolutePath = os.getcwd()

with open(os.path.join(os.path.dirname(__file__), 'config.yaml'), 'r') as ymlfile:
    try:
        config = yaml.safe_load(ymlfile)
    except yaml.YAMLError as exc:
        raise Exception("Error parsing config file: {}".format(exc))

mongoConnection = MongoClient(config['MONGO_URL'])

def MongoInsertOne(collection, data):
    return mongoConnection[config['MONGO_DB']][collection].insert_one(data)

def MongoFind(collection, query):
    return mongoConnection[config['MONGO_DB']][collection].find(query)

def MongoInsertMany(collection, data):
    return mongoConnection[config['MONGO_DB']][collection].insert_many(data)

def DoLogging(logType, msg):
    print("[{}] {}".format(logType, msg))

def getConfig():
    return config

def ReadTinyDB(fileName, tableName):
    """
    ReadTinyDB(fileName, tableName)
    Read data from a TinyDB file.
    """
    db = TinyDB(os.path.join(absolutePath, fileName))
    return db.table(tableName)

def WriteToTinyDB(fileName, tableName, data):
    """
    WriteToTinyDB(fileName, tableName, data)
    Write data to a TinyDB file.
    """
    db = TinyDB(os.path.join(absolutePath, fileName))
    db.table(tableName).insert(data)
    return db.table(tableName)

def ReadYaml(fileName):
    """
    ReadYaml(fileName)
    Read data from a YAML file.
    """
    with open(os.path.join(absolutePath, fileName), 'r') as ymlfile:
        try:
            config = yaml.safe_load(ymlfile)
        except yaml.YAMLError as exc:
            DoLogging("error", "Error parsing config file: {}".format(exc))
    return config

def sendTwiliomessage(message):
    ## send message only when last message sent more than 5 mins ago, to save msg credits
    last_message = ReadTinyDB('last_message.json', 'last_message')
    if last_message.all() == [] or last_message.all()[0]['timestamp'] < round(time.time() * 1000) - 300000:
        try:
            account_sid = config['TWILIO_ACCOUNT_SID']
            auth_token = config['TWILIO_AUTH_TOKEN']
            client = Client(account_sid, auth_token)
            message = client.messages.create(
                body=message,
                from_=config['TWILIO_PHONE_NUMBER'],
                to=config['PHONE_TO_TEXT']
            )
            WriteToTinyDB('last_message.json', 'last_message', {'timestamp': round(time.time() * 1000)})
            return message
        except Exception as e:
            DoLogging("error", "Error occurred for twillio message: {}".format(e))
    return message

def SlackAlert(msg):
    return requests.post(config['SLACK_WEBHOOK'], json={"text": msg})

def Notify(msg):
    """
    Notify(msg)
    Send a message to Slack and Twilio.
    """
    print(msg)
    SlackAlert(msg)
    sendTwiliomessage(msg)

def LogicBuilder(keyToCheck, valueToCheck, operator, message):
    if operator == '>':
        if keyToCheck > valueToCheck:
            Notify(message)
    elif operator == '<':
        if keyToCheck < valueToCheck:
            Notify(message)
    elif operator == '==':
        if keyToCheck == valueToCheck:
            Notify(message)
    elif operator == '!=':
        if keyToCheck != valueToCheck:
            Notify(message)
    else:
        print("Invalid operator: " + operator)
        exit(1)