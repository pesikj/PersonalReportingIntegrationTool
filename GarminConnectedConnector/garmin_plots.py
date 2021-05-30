import pandas
from matplotlib.figure import Figure

ACTIVITIES = {
    "running": ["running", "trail_running", "street_running"],
    "cycling": ["cycling", "road_biking", "mountain_biking"]
}


def get_data():
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


def activity_types():
    activities = get_data()
    return activities["type"].unique()


def running_plot(activity):
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    activities = get_data()
    activities = activities[activities["type"].isin(ACTIVITIES[activity])]
    activities = activities[activities["year"].isin([2015, 2019, 2020, 2021])]

    activities_plot = activities[["year", "week", "distance"]]
    activities_plot = activities_plot.groupby(["year", "week"]).sum().reset_index()
    activities_plot = activities_plot.pivot(index="week", columns='year', values='distance')
    activities_plot = activities_plot.fillna(0)
    activities_plot = activities_plot.cumsum()
    activities_plot.plot(ax=axis)
    return fig
