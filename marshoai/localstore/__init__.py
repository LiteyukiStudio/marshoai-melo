# 对nonebot-plugin-localstore的简单重新实现
from pathlib import Path
from typing import Callable, Optional
from typing_extensions import ParamSpec


from ..config import Config
from .source import user_data_dir, user_cache_dir, user_config_dir

plugin_config = Config()

P = ParamSpec("P")

APP_NAME = "melobot"
BASE_CACHE_DIR = (
    user_cache_dir(APP_NAME).resolve()
    if plugin_config.localstore_cache_dir is None
    else plugin_config.localstore_cache_dir.resolve()
)
BASE_CONFIG_DIR = (
    user_config_dir(APP_NAME).resolve()
    if plugin_config.localstore_config_dir is None
    else plugin_config.localstore_config_dir.resolve()
)
BASE_DATA_DIR = (
    user_data_dir(APP_NAME).resolve()
    if plugin_config.localstore_data_dir is None
    else plugin_config.localstore_data_dir.resolve()
)


def _ensure_dir(path: Path) -> None:
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    elif not path.is_dir():
        raise RuntimeError(f"{path} is not a directory")


def _auto_create_dir(func: Callable[P, Path]) -> Callable[P, Path]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Path:
        path = func(*args, **kwargs)
        _ensure_dir(path)
        return path

    return wrapper


@_auto_create_dir
def get_cache_dir(plugin_name: Optional[str]) -> Path:
    return BASE_CACHE_DIR / plugin_name if plugin_name else BASE_CACHE_DIR


def get_cache_file(plugin_name: Optional[str], filename: str) -> Path:
    return get_cache_dir(plugin_name) / filename


@_auto_create_dir
def get_config_dir(plugin_name: Optional[str]) -> Path:
    return BASE_CONFIG_DIR / plugin_name if plugin_name else BASE_CONFIG_DIR


def get_config_file(plugin_name: Optional[str], filename: str) -> Path:
    return get_config_dir(plugin_name) / filename


@_auto_create_dir
def get_data_dir(plugin_name: Optional[str]) -> Path:
    return BASE_DATA_DIR / plugin_name if plugin_name else BASE_DATA_DIR


def get_data_file(plugin_name: Optional[str], filename: str) -> Path:
    return get_data_dir(plugin_name) / filename


class PluginStore():
    def __init__(self, name: str):
        self.name = name

    def _get_plugin_path(self, base_dir: Path, plugin: str) -> Path:
        return base_dir.joinpath(plugin)


    @_auto_create_dir
    def get_plugin_cache_dir(self) -> Path:
        plugin = self.name
        return self._get_plugin_path(BASE_CACHE_DIR, plugin)


    def get_plugin_cache_file(self, filename: str) -> Path:
        return self.get_plugin_cache_dir() / filename


    @_auto_create_dir
    def get_plugin_config_dir(self) -> Path:
        plugin = self.name
        return self._get_plugin_path(BASE_CONFIG_DIR, plugin)


    def get_plugin_config_file(self, filename: str) -> Path:
        return self.get_plugin_config_dir() / filename


    @_auto_create_dir
    def get_plugin_data_dir(self) -> Path:
        plugin = self.name
        return self._get_plugin_path(BASE_DATA_DIR, plugin)


    def get_plugin_data_file(self, filename: str) -> Path:
        return self.get_plugin_data_dir() / filename
