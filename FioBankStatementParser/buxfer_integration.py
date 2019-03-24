import xml.etree.cElementTree as ET
import urllib3
from datetime import datetime
import re
import json
import azure.cosmos.cosmos_client as cosmos_client
import sys
import re
import base64
from urllib.parse import urlencode
import requests
import common

jsonConfig = common.jsonConfig
logger = common.logger
urllib3.disable_warnings()

with open("AccountsBuxferIDs.json", encoding="UTF-8") as f:
    jsonAccounts = json.load(f, encoding="UTF-8")
with open("BankTransactionTypesMapping.json", encoding="UTF-8") as f:
    jsonTransactionTypes = json.load(f, encoding="UTF-8")
with open("AutoTaggingStrings.json", encoding="UTF-8") as f:
    jsonAutoTaggingStrings = json.load(f, encoding="UTF-8")

def LoginToBuxfer():
    username = jsonConfig["Buxfer"]["Username"]
    password = jsonConfig["Buxfer"]["Password"]
    base = "https://www.buxfer.com/api"
    url  = base + "/login?userid=" + username + "&password=" + password

    http = urllib3.PoolManager()
    response = http.request("GET", url)
    if (response.status != 200):
        logger.error("Error logging to Buxfer.")
        logger.error(response.text)
    responseJson = json.loads(response.data.decode('utf-8'))
    token = responseJson["response"]["token"]
    
    return token

def SendBankTransactionToBuxfer(token, dictTransaction):
    dictTransactionBuxfer = {}
    if ("UserIdentification" in dictTransaction):
        description = dictTransaction["UserIdentification"]
    elif ("RecieverMessage" in dictTransaction):
        description = dictTransaction["RecieverMessage"]
    elif ("Comment" in dictTransaction):
        description = dictTransaction["Comment"]
    else:
        description = "No description added"
    description += "; Bank ID: " + dictTransaction["BankTransactionID"]
    transactionType = jsonTransactionTypes[dictTransaction["BankTransactionType"]]

    if ("Výběr z bankomatu" in description):
        transactionType = "transfer"
    else:
        accountNumber = dictTransaction["Account"] + "/" + dictTransaction["AccountBankCode"]
        if ("ContraAccount" in dictTransaction and "ContraAccountBankCode" in dictTransaction):
            contraAccountNumber = dictTransaction["ContraAccount"] + "/" + dictTransaction["ContraAccountBankCode"]
        if (contraAccountNumber in jsonAccounts):
            transactionType = "transfer"
            if (float(dictTransaction["Amount"]) < 0):
                dictTransactionBuxfer["fromAccountId"] = jsonAccounts[accountNumber]
                dictTransactionBuxfer["toAccountId"] = jsonAccounts[contraAccountNumber]
            else:
                dictTransactionBuxfer["toAccountId"] = jsonAccounts[accountNumber]
                dictTransactionBuxfer["fromAccountId"] = jsonAccounts[contraAccountNumber]
        else:
            dictTransactionBuxfer["accountId"] = jsonAccounts[accountNumber]
    
    tags = ""
    if (transactionType == "transfer"):
            tags = "Money Transfer"
    else:
        for autoTaggingString in jsonAutoTaggingStrings:
            if (autoTaggingString in description):
                tags = jsonAutoTaggingStrings[autoTaggingString]
                break
    if (len(tags) == 0):
        if (float(dictTransaction["Amount"]) > 0):
            tags = "Unidentified Incomes"
        else:
            tags = "Unidentified Expenses"
    dictTransactionBuxfer["type"] = transactionType
    dictTransactionBuxfer["amount"] = "%8.2f" % abs(float(dictTransaction["Amount"]))
    dictTransactionBuxfer["description"] = description
    dictTransactionBuxfer["date"] = dictTransaction["TransactionDate"]
    dictTransactionBuxfer["tags"] = tags

    http = urllib3.PoolManager()
    url = "https://www.buxfer.com/api/add_transaction?token=" + token
    response = http.request("POST", url, dictTransactionBuxfer)
    if (response.status != 200):
        logger.error("Error sending transaction to Buxfer.")
        logger.error(response.text)
        logger.error(dictTransactionBuxfer)

    
def DownloadTransactionFromBuxfer(token, startDate):
    dictStartDate = {}
    dictStartDate = startDate
    http = urllib3.PoolManager()
    url = "https://www.buxfer.com/api/transactions?token=" + token
    response = http.request("POST", url, dictStartDate)
    if (response.status != 200):
        logger.error("Error logging to Buxfer.")
        logger.error(response.text)
    responseJson = json.loads(response.data.decode('utf-8'))
    transactionCount = int(responseJson["response"]["numTransactions"])
    pages = transactionCount/25 + 1
    for x in range(pages, 1, -1):
        0
        
