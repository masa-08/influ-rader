import os
from typing import Any, List

import toml
from error import ConfigError, ReadEnvError
from loguru import logger


class Config:
    GOOGLE = "GOOGLE_APPLICATION_CREDENTIALS"
    TWITTER = "TWITTER_BAREAR_TOKEN"
    DISCORD = "DISCORD_BOT_TOKEN"
    CHANNEL = "DISCORD_CHANNEL_ID"
    ENVIRONMENTAL_VARIABLES = [GOOGLE, TWITTER, DISCORD, CHANNEL]

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
        if not self.__validate_environmental_variables():
            raise ReadEnvError
        self.google_credential = os.environ.get(self.GOOGLE)
        self.twitter_barear_token = os.environ.get(self.TWITTER)
        self.discord_bot_token = os.environ.get(self.DISCORD)
        try:
            self.discord_channel_id = int(os.environ.get(self.CHANNEL) or "")
        except ValueError:
            logger.exception("Discord channel id should be integer value")
            raise ReadEnvError

    def __validate_environmental_variables(self) -> bool:
        unset_variables = [v for v in self.ENVIRONMENTAL_VARIABLES if os.environ.get(v) is None]
        if unset_variables:
            logger.error(f"Failed to read these environmental variables: `{unset_variables}`")
            return False
        return True
