from bot import Bot
from config import Config
from db import Db
from twitter import Twitter


def main() -> None:
    config = Config()
    twitter = Twitter(config.twitter_barear_token)
    db = Db(config.google_credential)
    bot = Bot(db, twitter, config.target_users, config.discord_channel_id)
    bot.run(config.discord_bot_token)


if __name__ == "__main__":
    main()
