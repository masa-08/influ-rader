import time
from typing import List, Union, overload

import tweepy
from loguru import logger
from tweepy import Paginator, Response, TooManyRequests

from influ_rader.error import TwitterRequestError


class User(tweepy.User):
    def __init__(self, data) -> None:
        super().__init__(data)


class Twitter:
    def __init__(self, bearer_token: str) -> None:
        self.__client = tweepy.Client(bearer_token=bearer_token)
        self.__retry_interval = 15 * 60  # 15分

    @overload
    def get_user(self, arg: int) -> User:
        ...

    @overload
    def get_user(self, arg: str) -> User:
        ...

    def get_user(self, arg: Union[int, str]) -> User:
        """
        ユーザ情報を取得する
        arg: ユーザID(int) or ユーザ名(str)

        Twitter APIの制限に引っかかった際にAPIリクエストをリトライできるようにループ内でリクエスト処理を行う
        """
        for i in range(10):  # リトライ上限は10回
            try:
                res = self.__client.get_user(id=arg) if isinstance(arg, int) else self.__client.get_user(username=arg)
            except TooManyRequests:
                logger.warning("Twitter API request limit reached. Wait 15 minitue and retry.")
                time.sleep(self.__retry_interval)  # 15分待つ
            else:
                if len(res.errors) != 0:
                    raise TwitterRequestError()
                return User(res.data)
        logger.error("Failed to get user data for 10 times due to some reason...")
        raise TwitterRequestError()

    # TODO: ジェネリクスとかでget_usersメソッドと統合する
    def get_users_by_ids(self, user_ids: List[int]) -> List[User]:
        try:
            users = [self.get_user(i) for i in user_ids]
        except TwitterRequestError:
            logger.exception("Failed to get users info from Twitter API")
            raise
        return users

    def get_users(self, usernames: List[str]) -> List[User]:
        try:
            users = [self.get_user(u) for u in usernames]
        except TwitterRequestError:
            logger.exception("Failed to get users info from Twitter API")
            raise
        return users

    def get_user_id_following(self, user_id: int) -> List[int]:
        following: List[int] = []
        try:
            for res in Paginator(self.__client.get_users_following, id=user_id, max_results=1000):
                r: Response = res  # 型付け
                if len(r.errors) != 0:
                    raise TwitterRequestError()
                following += [u.id for u in [User(d) for d in r.data]]
        except TooManyRequests:
            logger.exception("Failed to get user id following data because of Twitter API threshold")
            raise TwitterRequestError()
        except TwitterRequestError:
            raise
        return following

    def get_users_id_following(self, user_ids: List[int]) -> dict[int, List[int]]:
        users_following: dict[int, List[int]] = {}
        for user_id in user_ids:
            try:
                following = self.get_user_id_following(user_id)
                users_following[user_id] = following
            except TwitterRequestError:
                logger.exception("Failed to get following from Twitter API")
                raise
        return users_following
