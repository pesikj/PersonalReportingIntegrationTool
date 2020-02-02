from datetime import datetime
from datetime import timedelta
import json
import common
import azure.cosmos.cosmos_client as cosmos_client
import re
import datetime


jsonConfig = common.jsonConfig

collection_link = 'dbs/' + jsonConfig["CosmosDB"]["Database"] + '/colls/' + jsonConfig['CosmosDB']['contBuxferTransactions']
documentlist = list(common.client.ReadItems(collection_link))
buxfer_ids_list = []
for doc in documentlist:
    description = doc.get('description')
    p = re.compile(r'\d{11}')
    result = p.findall(description)
    if len(result) > 0:
        buxfer_ids_list.append(result[-1])

collection_link = 'dbs/' + jsonConfig["CosmosDB"]["Database"] + '/colls/' + jsonConfig['CosmosDB']['contBankTransactions']
documentlist = list(common.client.ReadItems(collection_link))
for doc in documentlist:
    id = doc.get('BankTransactionID')
    date = doc.get('BankStatementTransactionDate')
    date = datetime.datetime.strptime(date, r'%Y-%m-%d').date()
    if date >= datetime.date(2019, 9, 1):
        if id not in buxfer_ids_list:
            print(id)