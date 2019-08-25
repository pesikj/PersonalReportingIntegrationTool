import buxfer_integration
from datetime import datetime
from datetime import timedelta
import json

with open("config.json", encoding="UTF-8") as f:
    jsonConfig = json.load(f, encoding="utf8")

buxfer_integration.DownloadTransactionFromBuxfer('2010-08-20', '2019-08-24')