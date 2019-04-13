import time
import common
import hashlib
import urllib3
import hmac
import json

jsonConfig = common.jsonConfig
logger = common.logger

def get_address(address_name, filters = []):
    with open("freedcamp_urls.json", encoding="UTF-8") as f:
        jsonFreddcampURLs = json.load(f, encoding="utf8")
        url = jsonFreddcampURLs[address_name]
        url = url.format(*filters)
    return url

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

def load_tasks(archived_projects_tasks = False, archived_tasklists_taks = False):
    offset = 0
    limit = jsonConfig["Freedcamp"]["LineLimit"]
    has_more = True
    while has_more == True:
        parameter = ["0", limit, offset] if archived_projects_tasks == False else ["1", limit, offset]
        url = get_address("tasks", parameter) + generate_security_address(True)
        tasks_call_response = call_freedcamp_API(url)
        for task in tasks_call_response["data"]["tasks"]:
            if archived_tasklists_taks == False and task["f_archived_list"] == True:
                continue
            task["FreedcampTaskID"] = task.pop("id")
            try:
                common.client.CreateItem('dbs/' + jsonConfig["CosmosDB"]["Database"] + '/colls/' + jsonConfig["CosmosDB"]["contFreedcampTasks"], task)
            except Exception as inst:
                logger.error("Error writing to database.")
                logger.error(task)
                logger.error(inst)
        has_more = tasks_call_response["data"]["meta"]["has_more"]
        offset += int(limit)

load_projects()
load_tasks(True, True)