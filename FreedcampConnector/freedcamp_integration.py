import time
import common
import hashlib
import urllib3
import hmac
import json
from datetime import datetime
from datetime import timedelta

jsonConfig = common.jsonConfig
logger = common.logger

def get_address(address_name, filters = []):
    with open("freedcamp_urls.json", encoding="UTF-8") as f:
        jsonFreddcampURLs = json.load(f, encoding="utf8")
        url = jsonFreddcampURLs[address_name]
        url = url.format(*filters)
    return url

def get_fields_to_compare(data_array_name):
    with open("fields_to_compare.json", encoding="UTF-8") as f:
        json_fields_to_compare = json.load(f, encoding="utf8")
        fields_to_compare = json_fields_to_compare[data_array_name]
    return fields_to_compare

def generate_security_address(parameters_passed = False):
    jsonConfig = common.jsonConfig
    FreedcampAPIKey = jsonConfig["Freedcamp"]["FreedcampAPIKey"]
    FreedcampAPISecret = jsonConfig["Freedcamp"]["FreedcampAPISecret"]
    unixTimestamp = str(round(time.time(), 0))
    hashed = hmac.new(bytes(FreedcampAPISecret, 'UTF-8'), bytes(FreedcampAPIKey + unixTimestamp, 'UTF-8'), hashlib.sha1).hexdigest()
    first_symbol = "?" if parameters_passed == False else "&"
    UrlSecurityString = first_symbol + "api_key=" + FreedcampAPIKey + "&timestamp=" + unixTimestamp + "&hash=" + hashed
    return UrlSecurityString

def call_freedcamp_API(url):
    http = urllib3.PoolManager()
    response = http.request("GET", url)
    return json.loads(response.data.decode('utf-8'))

def load_projects():
    url = get_address("projects") + generate_security_address(False)
    projects_call_response = call_freedcamp_API(url)
    for project in projects_call_response["data"]["projects"]:
        project["FreedcampProjectID"] = project.pop("project_id")
        try:
            common.client.CreateItem('dbs/' + jsonConfig["CosmosDB"]["Database"] + '/colls/' + jsonConfig["CosmosDB"]["contFreedcampProjects"], project)
        except Exception as inst:
            logger.error("Error writing to database.")
            logger.error(project)
            logger.error(inst)

def load_items_with_offset(context_name, data_array_name, cosmos_id_name, cosmos_db_partition_key, rename_fields = {}, parameter_list = [], item_filter = {}):
    offset = 0
    limit = jsonConfig["Freedcamp"]["LineLimit"]
    has_more = True
    fields_to_compare = get_fields_to_compare(data_array_name)
    while has_more == True:
        parameter = parameter_list + [limit, offset]
        url = get_address(data_array_name, parameter) + generate_security_address(True)
        freedcamp_call_response = call_freedcamp_API(url)
        for item in freedcamp_call_response["data"][data_array_name]:
            for field, value in item_filter.items():
                if item[field] == value:
                    continue
            for old_name, new_name in rename_fields.items():
                item[new_name] = item.pop(old_name)

            query = { "query": """SELECT * FROM c where c.{0} = "{1}"  and c.{2} = "{3}" """.format(cosmos_id_name, item[cosmos_id_name], cosmos_db_partition_key, item[cosmos_db_partition_key]) }
            results = common.client.QueryItems('dbs/' + jsonConfig["CosmosDB"]["Database"] + '/colls/' + jsonConfig["CosmosDB"][context_name], query)
            if len(list(results)) == 0:
                try:
                    common.client.CreateItem('dbs/' + jsonConfig["CosmosDB"]["Database"] + '/colls/' + jsonConfig["CosmosDB"][context_name], item)
                except Exception as inst:
                    logger.error("Error writing to database.")
                    logger.error(item)
                    logger.error(inst)
            else:
                doc = list(results)[0]
                update_needed = False
                for field in fields_to_compare: 
                    if doc[field] != item[field]:
                        update_needed = True
                        break
                if update_needed:
                    item["id"] = doc["id"]
                    try:
                        common.client.ReplaceItem(doc["_self"], item)
                    except Exception as inst:
                        logger.error("Error replacing record.")
                        logger.error(item)
                        logger.error(inst)
        has_more = freedcamp_call_response["data"]["meta"]["has_more"]
        offset += int(limit)

load_projects()
load_items_with_offset("contFreedcampTasks", "tasks", "FreedcampTaskID", "project_id", {"id": "FreedcampTaskID"}, ["0", "active"], {})
datefrom = (datetime.today() - timedelta(days=45)).strftime('%Y-%m-%d')
load_items_with_offset("contFreedcampTimes", "times", "FreedcampTimeID", "project_id", {"id": "FreedcampTimeID"}, [datefrom], {})
