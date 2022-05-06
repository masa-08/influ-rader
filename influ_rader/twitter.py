from typing import List
from loguru import logger
import tweepy

from error import TwitterRequestError


class User(tweepy.User):
    def __init__(self, data):
        super().__init__(data)


class Twitter():
    def __init__(self, bearer_token: str) -> None:
        self.__client = tweepy.Client(bearer_token=bearer_token)


    def get_user(self, username: str) -> User:
        res = self.__client.get_user(username=username)
        if len(res.errors) != 0:
            raise TwitterRequestError()
        return User(res.data)


    def get_users(self, usernames: List[str]) -> List[User]:
        try:
            users = [self.get_user(u) for u in usernames]
        except TwitterRequestError:
            logger.exception("Failed to get users info from Twitter API")
            raise
        return users


    def get_user_id_following(self, user_id: int) -> List[int]:
        following: List[int] = []
        next_token: str = ""
        while True:
            pagination_token = next_token if next_token else None
            res = self.__client.get_users_following(id=user_id, max_results=1000, pagination_token=pagination_token)
            if len(res.errors) != 0:
                raise TwitterRequestError()

            # TwitterのユーザIDだけ抽出する
            following += [u.id for u in [User(d) for d in res.data]]
            # 最終ページまで確認できたらループを抜ける
            if  "next_token" not in res.meta:
                break
            next_token = res.meta["next_token"]
        return following


    def get_users_id_following(self, user_ids: List[int]) -> dict[int, List[int]]:
        users_following: dict[int, List[int]] = {}
        for user_id in user_ids:
            try:
                following = self.get_user_id_following(user_id)
                users_following[user_id] = following
            except TwitterRequestError:
                logger("Failed to get following from Twitter API")
                raise
        return users_following