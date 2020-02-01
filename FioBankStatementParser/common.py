import json
import logging
import azure.cosmos.cosmos_client as cosmos_client

with open("config.json", encoding="UTF-8") as f:
    jsonConfig = json.load(f, encoding="utf8")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = cosmos_client.CosmosClient(url_connection=jsonConfig["CosmosDB"]["Endpoint"], auth={
                                    'masterKey': jsonConfig["CosmosDB"]["PrimaryKeyRW"]})