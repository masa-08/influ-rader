import pytest
import requests
from pytest_mock import MockerFixture
from tweepy import Response, TooManyRequests

from influ_rader.error import TwitterRequestError
from influ_rader.twitter import Twitter, User


@pytest.fixture
def twitter():
    return Twitter(bearer_token="test")


@pytest.fixture
def user():
    return User({"id": 1, "name": "ユーザ‍ーA", "username": "usera"})


@pytest.fixture
def response(user):
    return Response(data=user, includes={}, errors=[], meta={})


@pytest.fixture
def error_response():
    return Response(data={}, includes={}, errors=[{"value": "someerror", "title": "Not Found Error"}], meta={})


def test_get_user_with_valid_id(mocker: MockerFixture, twitter: Twitter, response: Response) -> None:
    """
    正常にユーザーデータを取得できた場合、その値を返すこと
    """
    client_mock = mocker.MagicMock()
    client_mock.get_user = mocker.Mock(return_value=response)
    mocker.patch.object(twitter, "_Twitter__client", client_mock)

    assert twitter.get_user(1) == User({"id": 1, "name": "ユーザーA", "username": "usera"})
    assert twitter.get_user("usera") == User({"id": 1, "name": "ユーザーA", "username": "usera"})


def test_get_user_with_res_errors(mocker: MockerFixture, twitter: Twitter, error_response: Response) -> None:
    """
    ユーザーデータを取得できずにエラーが返された場合、TwitterRequestError例外が発生すること
    """
    client_mock = mocker.MagicMock()
    client_mock.get_user = mocker.Mock(return_value=error_response)
    mocker.patch.object(twitter, "_Twitter__client", client_mock)

    with pytest.raises(TwitterRequestError):
        _ = twitter.get_user(0)
    with pytest.raises(TwitterRequestError):
        _ = twitter.get_user("usera")


def test_get_user_with_less_than_10_times_too_many_requests_exception(
    mocker: MockerFixture, twitter: Twitter, response: Response
) -> None:
    """
    Twitter APIの取得制限に引っかかった場合、一定時間待機後に再度リクエストを実施し、ユーザーデータを取得できること
    シナリオ:
        - 1回目のリクエスト: tweepy.TooManyRequestsエラー
        - 2回目のリクエスト: 正常にユーザーデータを取得
    """
    client_mock = mocker.MagicMock()
    client_mock.get_user = mocker.Mock(
        return_value=response,
        side_effect=[
            TooManyRequests(response=requests.Response()),
            response,
            TooManyRequests(response=requests.Response()),
            response,
        ],
    )
    mocker.patch.object(twitter, "_Twitter__client", client_mock)
    mocker.patch.object(twitter, "_Twitter__retry_interval", 0.1)  # テストなので、待ち時間を0.1秒に短縮する

    assert twitter.get_user(1) == User({"id": 1, "name": "ユーザーA", "username": "usera"})
    assert client_mock.get_user.call_count == 2

    assert twitter.get_user("usera") == User({"id": 1, "name": "ユーザーA", "username": "usera"})
    assert client_mock.get_user.call_count == 4


def test_get_user_with_10_times_too_many_requests_exception(
    mocker: MockerFixture, twitter: Twitter, response: Response
) -> None:
    """
    Twitter APIの取得制限に10回連続で引っかかった場合、TwitterRequestError例外が発生すること
    """
    client_mock = mocker.MagicMock()
    client_mock.get_user = mocker.Mock(return_value=response, side_effect=TooManyRequests(response=requests.Response()))
    mocker.patch.object(twitter, "_Twitter__client", client_mock)
    mocker.patch.object(twitter, "_Twitter__retry_interval", 0.1)  # テストなので、待ち時間を0.1秒に短縮する

    with pytest.raises(TwitterRequestError):
        _ = twitter.get_user(0)
    with pytest.raises(TwitterRequestError):
        _ = twitter.get_user("usera")


def test_get_users_by_ids_with_valid_responses(mocker: MockerFixture, twitter: Twitter, response: Response) -> None:
    """
    正常にユーザーデータを取得できた場合、その値を返すこと
    """
    client_mock = mocker.MagicMock()
    client_mock.get_user = mocker.Mock(return_value=response)
    mocker.patch.object(twitter, "_Twitter__client", client_mock)

    usera = User({"id": 1, "name": "ユーザーA", "username": "usera"})
    user_ids = [1, 1]
    assert twitter.get_users_by_ids(user_ids) == [usera, usera]


def test_get_users_by_ids_with_res_errors(mocker: MockerFixture, twitter: Twitter, error_response: Response) -> None:
    """
    ユーザーデータ取得時にTwitterRequestError例外が発生した場合、そのまま例外をraiseすること
    """
    client_mock = mocker.MagicMock()
    client_mock.get_user = mocker.Mock(return_value=error_response)
    mocker.patch.object(twitter, "_Twitter__client", client_mock)

    with pytest.raises(TwitterRequestError):
        _ = twitter.get_users_by_ids([1, 1])


def test_get_users_with_valid_responses(mocker: MockerFixture, twitter: Twitter, response: Response) -> None:
    """
    正常にユーザーデータを取得できた場合、その値を返すこと
    """
    client_mock = mocker.MagicMock()
    client_mock.get_user = mocker.Mock(return_value=response)
    mocker.patch.object(twitter, "_Twitter__client", client_mock)

    usera = User({"id": 1, "name": "ユーザーA", "username": "usera"})
    user_ids = ["usera", "usera"]
    assert twitter.get_users(user_ids) == [usera, usera]


def test_get_users_with_res_errors(mocker: MockerFixture, twitter: Twitter, error_response: Response) -> None:
    """
    ユーザーデータ取得時にTwitterRequestError例外が発生した場合、そのまま例外をraiseすること
    """
    client_mock = mocker.MagicMock()
    client_mock.get_user = mocker.Mock(return_value=error_response)
    mocker.patch.object(twitter, "_Twitter__client", client_mock)

    with pytest.raises(TwitterRequestError):
        _ = twitter.get_users(["usera", "usera"])
