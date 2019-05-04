import json
import azure.cosmos.cosmos_client as cosmos_client
import logging

with open("config.json", encoding="UTF-8") as f:
    jsonConfig = json.load(f, encoding="utf8")

client = cosmos_client.CosmosClient(url_connection=jsonConfig["CosmosDB"]["Endpoint"], auth={
                                    'masterKey': jsonConfig["CosmosDB"]["PrimaryKeyRW"]})

logging.basicConfig(level=logging.INFO, filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
