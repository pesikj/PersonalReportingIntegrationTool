import time
import common
import hashlib
import urllib3
import hmac
import json

jsonConfig = common.jsonConfig

FreedcampAPIKey = jsonConfig["Freedcamp"]["FreedcampAPIKey"]
FreedcampAPISecret = jsonConfig["Freedcamp"]["FreedcampAPISecret"]

unixTimestamp = str(round(time.time(), 0))
hashed = hmac.new(bytes(FreedcampAPISecret, 'UTF-8'), bytes(FreedcampAPIKey + unixTimestamp, 'UTF-8'), hashlib.sha1).hexdigest()

UrlSecurityString = "?api_key=" + FreedcampAPIKey + "&timestamp=" + unixTimestamp + "&hash=" + hashed

url = "https://freedcamp.com/api/v1/projects/" + UrlSecurityString

http = urllib3.PoolManager()
response = http.request("GET", url)
responseJson = json.loads(response.data.decode('utf-8'))

for project in responseJson["data"]["projects"]:
    projectID = project["project_id"]
    projectName = project["project_name"]
    output = "{0} {1} \n".format(projectID, projectName)
    print(output)
