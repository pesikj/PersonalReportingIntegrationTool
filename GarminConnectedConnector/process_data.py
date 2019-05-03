import os
import json
from datetime import datetime
import common

dir_name = 'garminexport/activities'

files = [i for i in os.listdir(dir_name) if i.endswith("_summary.json")]

jsonConfig = common.jsonConfig
logger = common.logger

for file in files:
    activity_data = {}
    with open(os.path.join(dir_name, file), encoding='utf-8') as f:
        data = json.load(f)
    activity_ID = data['activityId']
    activity_data["GarminActivityID"] = activity_ID
    activity_type = data['activityTypeDTO']['typeKey']
    activity_data["ActivityType"] = activity_type
    activity_data["EventType"] = data['eventTypeDTO']['typeKey']
    activity_data["DeviceID"] = data['metadataDTO']['deviceMetaDataDTO']['deviceId']

    if "locationName" in data:
        activity_data["LocationName"] = data['locationName']

    activity_data["DurationInHours"] = float(data['summaryDTO']['duration']) / 3600

    if 'distance' in data['summaryDTO']:
        activity_data["DistanceInKilometers"] = float(data['summaryDTO']['distance'])/1000
    if 'averageSpeed' in data['summaryDTO']:
        activity_data["AverageSpeed"] = float(data['summaryDTO']['averageSpeed']) * 3.6
    if 'elevationGain' in data['summaryDTO']:
        activity_data["ElevationGain"] = float(data['summaryDTO']['elevationGain'])
        activity_data["ElevationLoss"] = float(data['summaryDTO']['elevationLoss'])
    if 'maxSpeed' in data['summaryDTO']:
        activity_data["MaxSpeed"] = data['summaryDTO']['maxSpeed']

    if "AverageHR" in data['summaryDTO']:
        activity_data["AverageHR"] = data['summaryDTO']['averageHR']
        activity_data["MaxHR"] = data['summaryDTO']['maxHR']
        activity_data["TrainingEffect"] = data['summaryDTO']['trainingEffect']

    #"2014-04-25T17:16:25.0"
    activity_data["StartDate"] = datetime.strptime(data['summaryDTO']['startTimeLocal'], '%Y-%m-%dT%H:%M:%S.%f').strftime(r'%Y-%m-%d %H:%M:%S')

    query = { 'query': """SELECT * FROM c where c.{0} = {1} and c.{2} = "{3}" """.format("GarminActivityID", str(activity_ID), "ActivityType", activity_type) }
    results = common.client.QueryItems('dbs/' + jsonConfig["CosmosDB"]["Database"] + '/colls/' + jsonConfig['CosmosDB']['contActivities'], query)
    if len(list(results)) == 0:
        common.client.CreateItem('dbs/' + jsonConfig["CosmosDB"]["Database"] + '/colls/' + jsonConfig['CosmosDB']['contActivities'], activity_data)
    else:
        doc = list(results)[0]
        activity_data["id"] = doc["id"]
        common.client.ReplaceItem(doc["_self"], activity_data)

