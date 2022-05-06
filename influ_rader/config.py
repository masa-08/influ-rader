from typing import Any
from loguru import logger
import toml

from error import ConfigError

class Config():
    def __init__(self) -> None:
        self.config = self.__load()


    def __load(self) -> dict[str, Any]:
        try:
            config = toml.load("./config.toml")
            if not self.__validate(config):
                raise ConfigError
        except toml.TomlDecodeError:
            logger.exception("TomlDecodeError")
            raise ConfigError
        except ConfigError:
            logger.exception("Config validation was failed")
            raise
        return config


    def __validate(self, config: dict[str, Any]) -> bool:
        return ("target" in config) and ("users" in config["target"])

