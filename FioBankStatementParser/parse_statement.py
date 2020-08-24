import xml.etree.cElementTree as ET
import urllib3
from datetime import datetime
import re
import json
import sys
import re
import base64
import buxfer_integration as bux
import common

jsonConfig = common.jsonConfig
logger = common.logger
urllib3.disable_warnings()

with open("BankStatementMapping.json", encoding="UTF-8") as f:
    jsonMappingFile = json.load(f, encoding="utf8")

def SaveValueToList(dict, key, value):
    if (value):
        dict[key] = value

def GetElementValue(transaction, elementName):
    element = transaction.findall("./" + elementName)
    if len(element) > 0:
        return element[0].text
    else:
        return None

def CopyTransactionFromBankToBuxfer():
    url = jsonConfig["FioBank"]["url"]
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    if (response.status != 200):
        logger.error("Error getting data from bank.")
        raise ValueError("Error getting data from bank.")
    root = ET.fromstring(response.data)

    for transaction in root[1]:
        dictTransactionData = {}
        for columnName in jsonMappingFile:
            SaveValueToList(dictTransactionData, columnName, GetElementValue(transaction, jsonMappingFile[columnName]))

        userIdentification = GetElementValue(transaction, "column_7")
        bankStatementTransactionDate = datetime.strptime(GetElementValue(transaction, "column_0")[:10], r'%Y-%m-%d').strftime(r'%Y-%m-%d')
        if (userIdentification):
            reTransactionDate = re.findall(r"\d{1,2}[.]\d{1,2}[.]\d{4}", userIdentification)
            if (reTransactionDate):
                SaveValueToList(dictTransactionData, "TransactionDate", datetime.strptime(reTransactionDate[0], '%d.%m.%Y').strftime(r'%Y-%m-%d'))
            else:
                SaveValueToList(dictTransactionData, "TransactionDate", bankStatementTransactionDate)
        else:
            SaveValueToList(dictTransactionData, "TransactionDate", bankStatementTransactionDate)
            
        SaveValueToList(dictTransactionData, "BankStatementTransactionDate", bankStatementTransactionDate)
        SaveValueToList(dictTransactionData, "Account", jsonConfig["FioBank"]["AccountNumber"])
        SaveValueToList(dictTransactionData, "AccountBankCode", jsonConfig["FioBank"]["AccountBankCode"])
        
        try:
            common.client.CreateItem('dbs/' + jsonConfig["CosmosDB"]["Database"] + '/colls/' + jsonConfig["CosmosDB"]["contBankTransactions"], dictTransactionData)
            
        except Exception as inst:
            logger.error("Error writing to database.")
            logger.error(dictTransactionData)
            logger.error(inst)
        bux.SendBankTransactionToBuxfer(dictTransactionData)
        
