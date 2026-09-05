from cmath import log
from enum import Enum
from logging import Logger
import datetime
import logging
import json

class JsonFormatter(logging.Formatter):

    def format(self, record):
        log_data = {
            "timestamp": datetime.datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "func_name": record.funcName
        }

        if hasattr(record, "context"):
            log_data.update(record.context)

        return json.dumps(log_data, indent=4)

def get_logger(name: str,) -> Logger:
    logger = logging.getLogger("app_logger")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    return logger