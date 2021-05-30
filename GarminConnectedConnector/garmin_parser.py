import datetime
import json

import pandas
from garminconnect import (
    Garmin,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
    GarminConnectAuthenticationError,
)

import common

LOAD_UNTIL = datetime.date(2013, 1, 1)


def load_data_batch(client, start):
    activities = client.get_activities(start, 1)
    activities = str(activities).replace("'", '"').replace("None", '""')
    activities = activities.replace("False", '"False"').replace("True", '"True"')
    activities = json.loads(activities)
    activities = pandas.DataFrame(activities)
    activities["startTimeLocal"] = pandas.to_datetime(activities["startTimeLocal"])
    return activities


def load_data():
    try:
        json_config = common.jsonConfig
        client = Garmin(json_config['Garmin']['Username'], json_config['Garmin']['Password'])
        activities = pandas.DataFrame()
        for start in range(0, 1500, 1):
            new_activities = load_data_batch(client, start)
            if new_activities is not None:
                activities = pandas.concat([activities, new_activities], ignore_index=True)
            else:
                break
            start += 10
            print(activities["startTimeLocal"].min())
            activities.to_json("data.json")
        return activities
    except (
            GarminConnectConnectionError,
            GarminConnectAuthenticationError,
            GarminConnectTooManyRequestsError,
    ) as err:
        print("Error occurred during Garmin Connect Client get stats: %s" % err)
        quit()
