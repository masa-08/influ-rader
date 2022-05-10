from typing import List, Optional

from db import Db
from discord.ext import commands, tasks
from error import DbOperationError, TwitterRequestError, BotError
from loguru import logger
from twitter import Twitter


class TwitterCog(commands.Cog):
    def __init__(self, bot: commands.Bot, twitter: Twitter, db: Db, target_users: List[str], channel: int) -> None:
        super().__init__()
        self.bot = bot
        self.twitter = twitter
        self.db = db
        self.channel_id = channel
        try:
            self.target_user_ids = [u.id for u in self.twitter.get_users(target_users)]
        except TwitterRequestError:
            logger.exception("Failed to get user ids.")
            raise
        self.diff_users_followings.start()

    @tasks.loop(hours=24) # 1日に1回実行する
    async def diff_users_followings(self) -> None:
        result_twitter = self.__get_users_following_from_twitter(self.target_user_ids)
        result_db = self.__get_users_followings_from_db(self.target_user_ids)
        diff_twitter_db = await self.diff_users_followings_twitter_db(result_twitter or {}, result_db or {})
        await self.diff_users_followings_db_twitter(result_db or {}, result_twitter or {})

        await self.__display(diff_twitter_db)

    async def diff_users_followings_twitter_db(
        self, from_twitter: dict[str, List[str]], from_db: dict[str, List[str]]
    ) -> dict[str, List[str]]:
        diff = self.__diff_users_followings_twitter_db(from_twitter, from_db)
        self.__add_users_followings(diff)
        return diff

    async def diff_users_followings_db_twitter(
        self, from_db: dict[str, List[str]], from_twitter: dict[str, List[str]]
    ) -> None:
        diff = self.__diff_users_followings_db_twitter(from_db, from_twitter)
        self.__remove_users_followings(diff)

    @diff_users_followings.before_loop
    async def before_diff_user_following(self) -> None:
        logger.info("Waiting for the bot to be ready...")
        await self.bot.wait_until_ready()

    def __get_user_followings_from_twitter(self, user_id: int) -> Optional[List[str]]:
        try:
            following = self.twitter.get_user_id_following(user_id)
        except TwitterRequestError:
            logger.exception("Failed to get user following.")
            return None
        except Exception:
            logger.exception("Something wrong...")
            return None
        return [str(f) for f in following]

    def __get_users_following_from_twitter(self, user_ids: List[int]) -> Optional[dict[str, List[str]]]:
        users_following: dict[str, List[str]] = {}
        try:
            for user_id in user_ids:
                following = self.__get_user_followings_from_twitter(user_id)
                if following is not None:
                    users_following[str(user_id)] = following
        except TwitterRequestError:
            logger.exception("Failed to get users following from Twitter")
            return None
        return users_following

    def __get_user_followings_from_db(self, user_id: str) -> Optional[List[str]]:
        user = self.db.get(user_id)
        if user is None or "followings" not in user:
            return None
        return user["followings"]

    def __get_users_followings_from_db(self, user_ids: List[str]) -> Optional[dict[str, List[str]]]:
        users_following: dict[str, List[str]] = {}
        try:
            for user_id in user_ids:
                following = self.__get_user_followings_from_db(str(user_id))
                if following is not None:
                    users_following[str(user_id)] = following
        except DbOperationError:
            logger.exception("Failed to get users following from DB")
            return None
        return users_following

    def __diff_list(self, src: List[str], dst: List[str]) -> List[str]:
        return list(set(src) - set(dst))

    def __diff_user_followings_twitter_db(self, from_twitter: List[str], from_db: List[str]) -> List[str]:
        return self.__diff_list(from_twitter, from_db)

    def __diff_user_followings_db_twitter(self, from_db: List[str], from_twitter: List[str]) -> List[str]:
        return self.__diff_list(from_db, from_twitter)

    def __diff_users_followings_twitter_db(
        self, from_twitter: dict[str, List[str]], from_db: dict[str, List[str]]
    ) -> dict[str, List[str]]:
        """
        Twitterからのレスポンスに含まれていて、DBに保存されていないfollowingsを抽出する
        対象のユーザが新たにフォローした人を抽出できる想定
        """
        return {
            k: self.__diff_user_followings_twitter_db(v, from_db[k]) if k in from_db else v
            for k, v in from_twitter.items()
        }

    def __diff_users_followings_db_twitter(
        self, from_db: dict[str, List[str]], from_twitter: dict[str, List[str]]
    ) -> dict[str, List[str]]:
        """
        DBに保存されていて、Twitterからのレスポンスに含まれていないfollowingsを抽出する
        対象のユーザがフォロー解除した人を抽出できる想定
        """
        return {
            k: self.__diff_user_followings_db_twitter(v, from_twitter[k]) if k in from_twitter else v
            for k, v in from_db.items()
        }

    def __add_user_followings(self, key: str, value: List[str]) -> None:
        if self.db.has_record(key):
            try:
                self.db.add_to_array(key, "followings", value)
            except DbOperationError:
                return
            else:
                logger.info(f"Add followings for user id `{key}`")
        else:
            try:
                self.db.add(key, {"followings": value})
            except DbOperationError:
                return
            else:
                logger.info(f"Add followings for user id `{key}`")

    def __add_users_followings(self, diffs: dict[str, List[str]]) -> None:
        for k, v in diffs.items():
            if v:  # MEMO: 差分があるときだけ実行する
                self.__add_user_followings(k, v)

    def __remove_user_followings(self, key: str, value: List[str]) -> None:
        if not self.db.has_record(key):
            return
        try:
            self.db.remove_from_array(key, "followings", value)
        except DbOperationError:
            return
        else:
            logger.info(f"Remove followings for user id `{key}`")

    def __remove_users_followings(self, diffs: dict[str, List[str]]) -> None:
        for k, v in diffs.items():
            if v:  # MEMO: 差分があるときだけ実行する
                self.__remove_user_followings(k, v)

    async def __display(self, diffs: dict[str, List[str]]) -> None:
        url = "https://twitter.com/"
        channel = self.bot.get_channel(self.channel_id)
        print(channel)
        if channel is None:
            logger.error(f"Failed to get a channel with id `{self.channel_id}`")
            raise BotError

        for target_user_id, following_user_ids in diffs.items():
            try:
                target_user = self.twitter.get_user(int(target_user_id))
                user_ids = [int(v) for v in following_user_ids]
                usernames = [f"{url}{v.username}" for v in self.twitter.get_users_by_ids(user_ids)]
            except TwitterRequestError:
                continue
            if usernames:
                message = f"**{target_user.name}(@{target_user.username})**が新しくフォローしたアカウント\n" + "\n".join(usernames)
                await channel.send(message)
