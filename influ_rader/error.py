class AppError(Exception):
    """全ての例外クラスのベース"""
    pass


class ConfigError(AppError):
    """Config関連の例外クラス"""
    pass


class ReadEnvError(ConfigError):
    """環境変数の読み込み例外クラス"""
    pass


class TwitterError(AppError):
    """Twitter関連の例外クラス"""
    pass


class TwitterRequestError(TwitterError):
    """Twitter APIからエラーが返されたことを表す例外クラス"""
    pass


class DbError(AppError):
    """Db関連の例外クラス"""
    pass


class DbInitializeError(DbError):
    """Db初期化時のエラーを表す例外クラス"""
    pass


class DbOperationError(DbError):
    """DBへのCRUD操作でエラーが発生したことを表す例外クラス"""
    pass
