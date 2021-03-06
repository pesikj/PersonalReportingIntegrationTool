import freedcamp_integration
from datetime import datetime
from datetime import timedelta

freedcamp_integration.load_items_with_offset("contFreedcampTasks", "tasks", "FreedcampTaskID", "project_id", {"id": "FreedcampTaskID"}, ["0", "active"], {})
datefrom = (datetime.today() - timedelta(days=14))
timestamp = datetime.timestamp(datefrom)
datefrom_str = datefrom.strftime('%Y-%m-%d')
freedcamp_integration.load_items_with_offset("contFreedcampTimes", "times", "FreedcampTimeID", "project_id", {"id": "FreedcampTimeID"}, [datefrom_str], {}, {"date_ts" :timestamp})

