# ruff: noqa
from .development import *

print("Using testing settings")

# Disable all logging output in testing
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "handlers": {
        "null": {
            "level": "DEBUG",
            "class": "logging.NullHandler",
        },
    },
    "loggers": {
        "": {  # catches all loggers
            "handlers": ["null"],
            "level": "CRITICAL",
        },
    },
}
