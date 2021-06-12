import json
import logging

with open("config.json", encoding="UTF-8") as f:
    jsonConfig = json.load(f)

logging.basicConfig(level=logging.INFO, filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
