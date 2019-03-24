import json
import logging

with open("Config.json", encoding="UTF-8") as f:
    jsonConfig = json.load(f, encoding="utf8")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
