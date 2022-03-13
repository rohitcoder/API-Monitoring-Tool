from twilio.rest import Client
from pymongo import MongoClient
from tinydb import TinyDB, Query
import requests, yaml, os, time, yaml, logging

logging.basicConfig(filename='error.log', encoding='utf-8', level=logging.ERROR)
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
    if logType == 'info':
        logging.info(msg)
    elif logType == 'error':
        logging.error(msg)
    elif logType == 'debug':
        logging.debug(msg)
    elif logType == 'warning':
        logging.warning(msg)
    else:
        logging.warning(msg)

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
    print(message)
    try:
        account_sid = config['TWILIO_ACCOUNT_SID']
        auth_token = config['TWILIO_AUTH_TOKEN']
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=message,
            from_=config['TWILIO_FROM'],
            to=config['PHONE_TO_TEXT']
        )
    except Exception as e:
        DoLogging("error", "Error occurred for twillio message: {}".format(e))
    return message

def SlackAlert(msg):
    '''
    return requests.post(config['SLACK_WEBHOOK'], json={"text": msg})
    '''

def Notify(msg):
    """
    Notify(msg)
    Send a message to Slack and Twilio.
    """
    SlackAlert(msg)
    sendTwiliomessage(msg)

def LogicBuilder(keyToCheck, valueToCheck, operator, message):
    print("Checking value: {} {} {}".format(keyToCheck, operator, valueToCheck))
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