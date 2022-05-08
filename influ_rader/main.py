from config import Config
from twitter import Twitter
from db import Db
from bot import Bot

def main() -> None:
    config = Config()
    twitter = Twitter(config.twitter_barear_token)
    db = Db(config.google_credential)
    bot = Bot(db, twitter, config.target_users, config.discord_channel_id)
    bot.run(config.discord_bot_token)


if __name__ == "__main__":
    main()
