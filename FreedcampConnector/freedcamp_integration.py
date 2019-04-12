import time
import common
import hashlib
import urllib3
import hmac
import json

def get_address(address_name):
    with open("freedcamp_urls.json", encoding="UTF-8") as f:
        jsonFreddcampURLs = json.load(f, encoding="utf8")
    return jsonFreddcampURLs[address_name]

def generate_security_address():
    jsonConfig = common.jsonConfig
    FreedcampAPIKey = jsonConfig["Freedcamp"]["FreedcampAPIKey"]
    FreedcampAPISecret = jsonConfig["Freedcamp"]["FreedcampAPISecret"]
    unixTimestamp = str(round(time.time(), 0))
    hashed = hmac.new(bytes(FreedcampAPISecret, 'UTF-8'), bytes(FreedcampAPIKey + unixTimestamp, 'UTF-8'), hashlib.sha1).hexdigest()
    UrlSecurityString = "?api_key=" + FreedcampAPIKey + "&timestamp=" + unixTimestamp + "&hash=" + hashed
    return UrlSecurityString

def call_freedcamp_API(url):
    http = urllib3.PoolManager()
    response = http.request("GET", url)
    return json.loads(response.data.decode('utf-8'))

def load_projects():
    url = get_address("projects") + generate_security_address()
    projects_call_response = call_freedcamp_API(url)
    for project in projects_call_response["data"]["projects"]:
        projectID = project["project_id"]
        projectName = project["project_name"]
        output = "{0} {1} \n".format(projectID, projectName)
        print(output)

load_projects()