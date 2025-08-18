# bot/logging_config.py
import logging
import logging.config
from pathlib import Path

def setup_logging(base_dir: Path):
    logs_dir = base_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / "bot.log"

    LOG_LEVEL = "INFO"  # change to DEBUG for deeper traces

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            # key=value style is very grep/splunk/ELK friendly
            "kv": {
                "format": (
                    "%(asctime)s level=%(levelname)s "
                    "logger=%(name)s "
                    "msg=%(message)s "
                    "func=%(funcName)s line=%(lineno)d "
                    "module=%(module)s"
                ),
                "datefmt": "%Y-%m-%dT%H:%M:%S%z",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": LOG_LEVEL,
                "formatter": "kv",
            },
            "file": {
                # rotate daily at midnight; keep 7 days
                "class": "logging.handlers.TimedRotatingFileHandler",
                "level": LOG_LEVEL,
                "formatter": "kv",
                "filename": str(log_file),
                "when": "midnight",
                "backupCount": 7,
                "encoding": "utf-8",
            },
        },
        "root": {
            "level": LOG_LEVEL,
            "handlers": ["console", "file"],
        },
    }

    logging.config.dictConfig(config)
    logging.getLogger(__name__).info("logging_initialized base_dir=%s file=%s", base_dir, log_file)
