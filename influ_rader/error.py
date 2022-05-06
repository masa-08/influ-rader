class AppError(Exception):
    """全ての例外クラスのベース"""
    pass


class ConfigError(AppError):
    """Config関連の例外クラス"""
    pass


class TwitterError(AppError):
    """Twitter関連の例外クラス"""
    pass


class TwitterRequestError(TwitterError):
    """Twitter APIからエラーが返されたことを表す例外クラス"""
    pass
