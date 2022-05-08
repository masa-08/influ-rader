from typing import List
from discord.ext import commands
from loguru import logger

from db import Db
from twitter import Twitter
from cogs.twitter_cog import TwitterCog

class Bot(commands.Bot):
    EXTENSIONS = ["cogs.twitter_cog"]

    def __init__(self, db: Db, twitter: Twitter, targets: List[str], channel: int, command_prefix="!") -> None:
        super().__init__(command_prefix=command_prefix)
        self.add_cog(TwitterCog(self, twitter, db, targets, channel))


    async def on_ready(self):
        logger.info(f"{self.user.name} is ready!!")
