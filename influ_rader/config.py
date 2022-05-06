import os
from typing import Any, List

from loguru import logger
import toml

from error import ConfigError
from error import ReadEnvError

class Config():
    def __init__(self) -> None:
        self.__load_config_file()
        self.__load_environmental_variable()


    def __load_config_file(self) -> None:
        try:
            config = toml.load("./config.toml")
            if not self.__validate_config_file(config):
                raise ConfigError
            self.target_users: List[str] = config["target"]["users"]
        except toml.TomlDecodeError:
            logger.exception("TomlDecodeError")
            raise ConfigError
        except ConfigError:
            logger.exception("Config validation was failed")
            raise


    def __validate_config_file(self, config: dict[str, Any]) -> bool:
        return ("target" in config) and ("users" in config["target"])


    def __load_environmental_variable(self) -> None:
        google_credential = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if google_credential is None:
            logger.exception("Failed to read environmental variable: `GOOGLE_APPLICATION_CREDENTIALS`")
            raise ReadEnvError
        self.google_credential = google_credential
