import parse_statement as parst
import buxfer_integration as bux
import common

collection_link ='dbs/' + common.jsonConfig["CosmosDB"]["Database"] + '/colls/' + common.jsonConfig["CosmosDB"]["contBankTransactions"]

query = {
                "query": "SELECT * FROM c WHERE c.BankTransactionID = @BankTransactionID",
                "parameters": [ { "name":"@BankTransactionID", "value": "17719674008" } ]
                }
results = list(common.client.QueryItems(collection_link, query))

for dictTransaction in results:
    dictTransaction["Account"] = common.jsonConfig["FioBank"]["AccountNumber"]
    dictTransaction["AccountBankCode"] = common.jsonConfig["FioBank"]["AccountBankCode"]
    bux.SendBankTransactionToBuxfer(dictTransaction)

    