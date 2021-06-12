import datetime
import json

import pandas
from garminconnect import (
    Garmin,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
    GarminConnectAuthenticationError,
)
from matplotlib.figure import Figure

import common

ACTIVITIES = {
    "running": ["running", "trail_running", "street_running"],
    "cycling": ["cycling", "road_biking", "mountain_biking"]
}

LOAD_UNTIL = datetime.date(2013, 1, 1)


class GarminConnector:
    @property
    def activities_metadata(self):
        return {
            "loaded_activities": self.loaded_activities
        }

    @property
    def loaded_activities(self):
        return self.activities.shape[0]

    @staticmethod
    def load_data_batch(client, start):
        activities = client.get_activities(start, 1)
        try:
            activities = str(activities).replace("'", '"').replace("None", '""')
            activities = activities.replace("False", '"False"').replace("True", '"True"')
            activities = json.loads(activities)
            activities = pandas.DataFrame(activities)
            activities["startTimeLocal"] = pandas.to_datetime(activities["startTimeLocal"])
            return activities
        except KeyError as err:
            return None

    def load_data(self, from_index=0, to_index=10):
        try:
            json_config = common.jsonConfig
            client = Garmin(json_config['Garmin']['Username'], json_config['Garmin']['Password'])
            activities = self.activities
            for start in range(from_index, to_index, 1):
                print(start)
                new_activities = self.load_data_batch(client, start)
                if new_activities is not None:
                    activities = pandas.concat([activities, new_activities], ignore_index=True)
                    activities = activities.drop_duplicates(subset=["activityId"])
            activities.to_json("data.json")
            activities.to_excel("data.xlsx")
            self.activities = activities
            return activities
        except (
                GarminConnectConnectionError,
                GarminConnectAuthenticationError,
                GarminConnectTooManyRequestsError,
        ) as err:
            print("Error occurred during Garmin Connect Client get stats: %s" % err)

    def running_plot(self, activity):
        if self.activities.shape[0] > 0:
            fig = Figure()
            axis = fig.add_subplot(1, 1, 1)
            activities = self.activities
            activities = activities[activities["type"].isin(ACTIVITIES[activity])]
            activities = activities[activities["year"].isin([2015, 2019, 2020, 2021])]

            activities_plot = activities[["year", "week", "distance"]]
            activities_plot = activities_plot.groupby(["year", "week"]).sum().reset_index()
            activities_plot = activities_plot.pivot(index="week", columns='year', values='distance')
            activities_plot = activities_plot.fillna(0)
            activities_plot = activities_plot.cumsum()
            activities_plot.plot(ax=axis)
            return fig

    @staticmethod
    def get_data():
        try:
            activities = pandas.read_json("data.json")
            activities["startTimeLocal"] = pandas.to_datetime(activities["startTimeLocal"], unit='ms')
            activities = activities.drop_duplicates(subset=["activityId"])
            activities["year"] = activities["startTimeLocal"].dt.year
            activities["week"] = activities["startTimeLocal"].dt.isocalendar().week
            activities.set_index("startTimeLocal")
            activities = activities.sort_index(ascending=False)
            activities["distance"] = activities["distance"] / 1000
            activities["type"] = activities["activityType"].map(lambda x: x['typeKey'])
            return activities
        except ValueError as err:
            return pandas.DataFrame()

    def activity_types(self):
        return self.activities["type"].unique()

    def __init__(self):
        self.activities = self.get_data()


garmin_connector = GarminConnector()
