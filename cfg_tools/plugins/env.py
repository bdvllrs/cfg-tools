import os


def env_plugin(
    keys: str,
    _,
) -> str:
    key, _, default = keys.partition(",")
    return os.getenv(key, default)
