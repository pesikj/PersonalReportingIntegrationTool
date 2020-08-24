import urllib3
import common
import json
import base64
from urllib.parse import urlencode
import azure.cosmos.cosmos_client as cosmos_client
import math

jsonConfig = common.jsonConfig

def LoginToBuxfer():
    username = jsonConfig["Buxfer"]["Username"]
    password = jsonConfig["Buxfer"]["Password"]
    base = "https://www.buxfer.com/api"
    url  = base + "/login?userid=" + username + "&password=" + password

    http = urllib3.PoolManager()
    response = http.request("GET", url)
    responseJson = json.loads(response.data.decode('utf-8'))
    token = responseJson["response"]["token"]
    
    return token

token = LoginToBuxfer()

def DownloadTransactionFromBuxfer(startDate, endDate):
    dictStartDate = {}
    dictStartDate["startDate"] = startDate
    dictStartDate["endDate"] = endDate
    http = urllib3.PoolManager()
    url = "https://www.buxfer.com/api/transactions?token=" + token
    response = http.request("POST", url, dictStartDate)
    if (response.status != 200):
        logger.error("Error logging to Buxfer.")
        logger.error(response.text)
    responseJson = json.loads(response.data.decode('utf-8'))
    transactionCount = int(responseJson["response"]["numTransactions"])
    pages = math.ceil(transactionCount/25) + 1
    for currPage in range(pages, 0, -1):
        dictPage = dictStartDate
        dictPage["page"] = currPage
        response = http.request("POST", url, dictPage)
        responseTransactionsJson = json.loads(response.data.decode('utf-8'))
        if (response.status != 200):
            logger.error("Error logging to Buxfer.")
            logger.error(response.text)
        for transaction in responseTransactionsJson["response"]["transactions"]:
            transaction["BuxferTransactionID"] = transaction.pop("id")
            query = { 'query': """SELECT * FROM c where c.{0} = {1} and c.{2} = '{3}' """.format("BuxferTransactionID", str(transaction["BuxferTransactionID"]), 'transactionType', str(transaction["transactionType"])) }
            results = common.client.QueryItems('dbs/' + jsonConfig["CosmosDB"]["Database"] + '/colls/' + jsonConfig['CosmosDB']['contBuxferTransactions'], query)
            if len(list(results)) == 0:
                common.client.CreateItem('dbs/' + jsonConfig["CosmosDB"]["Database"] + '/colls/' + jsonConfig['CosmosDB']['contBuxferTransactions'], transaction)
            else:
                doc = list(results)[0]
                transaction["id"] = doc["id"]
                common.client.ReplaceItem(doc["_self"], transaction)
