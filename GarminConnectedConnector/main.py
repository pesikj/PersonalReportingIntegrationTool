import os
import json
from datetime import datetime
import common

import argparse
from datetime import timedelta
import getpass
from garminexport.garminexport.garminclient import GarminClient
import garminexport.garminexport.backup
from garminexport.garminexport.backup import export_formats
from garminexport.garminexport.retryer import (
    Retryer, ExponentialBackoffDelayStrategy, MaxRetriesStopStrategy)
import logging
import os
import re
import sys
import traceback

import dateutil

jsonConfig = common.jsonConfig
logger = common.logger

dir_name = jsonConfig['Garmin']['ExportDirectory']
username = jsonConfig['Garmin']['Username']
password = jsonConfig['Garmin']['Password']
max_retries = jsonConfig['Garmin']['MaxRetries']
export_format = [jsonConfig['Garmin']['Format']]

try:
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)

    # set up a retryer that will handle retries of failed activity
    # downloads
    retryer = Retryer(
        delay_strategy=ExponentialBackoffDelayStrategy(
            initial_delay=timedelta(seconds=1)),
        stop_strategy=MaxRetriesStopStrategy(max_retries))


    with GarminClient(username, password) as client:
        # get all activity ids and timestamps from Garmin account
        logger.info("scanning activities for %s ...", username)
        activities = set(retryer.call(client.list_activities))
        logger.info("account has a total of %d activities", len(activities))

        missing_activities = garminexport.garminexport.backup.need_backup(
            activities, dir_name, export_format)
        backed_up = activities - missing_activities
        logger.info("%s contains %d backed up activities",
            dir_name, len(backed_up))

        logger.info("activities that aren't backed up: %d",
                    len(missing_activities))

        for index, activity in enumerate(missing_activities):
            id, start = activity
            logger.info("backing up activity %d from %s (%d out of %d) ..." % (id, start, index+1, len(missing_activities)))
            try:
                garminexport.garminexport.backup.download(
                    client, activity, retryer, dir_name,
                    export_format)
            except Exception as e:
                logger.error(u"failed with exception: %s", e)
except Exception as e:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    logger.error(u"failed with exception: %s", str(e))


files = [i for i in os.listdir(dir_name) if i.endswith("_summary.json")]

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

