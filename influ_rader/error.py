class AppError(Exception):
    """全ての例外クラスのベース"""


class ConfigError(AppError):
    """Config関連の例外クラス"""


class ReadEnvError(ConfigError):
    """環境変数の読み込み例外クラス"""


class TwitterError(AppError):
    """Twitter関連の例外クラス"""


class TwitterRequestError(TwitterError):
    """Twitter APIからエラーが返されたことを表す例外クラス"""


class DbError(AppError):
    """Db関連の例外クラス"""


class DbInitializeError(DbError):
    """Db初期化時のエラーを表す例外クラス"""


class DbOperationError(DbError):
    """DBへのCRUD操作でエラーが発生したことを表す例外クラス"""


class BotError(AppError):
    """Bot関連の例外クラス"""
