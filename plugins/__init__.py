import importlib
import pkgutil
import asyncio
import logging
from pathlib import Path
from typing import Callable, List

logger = logging.getLogger(__name__)
PLUGINS_PATH = Path(__file__).parent
HANDLERS: List[Callable[[dict], asyncio.Future]] = []


def load_plugins() -> None:
    """Discover and load plugins from the plugins directory."""
    if not PLUGINS_PATH.exists():
        logger.warning("Plugins path %s does not exist", PLUGINS_PATH)
        return
    for info in pkgutil.iter_modules([str(PLUGINS_PATH)]):
        if info.name == "__init__":
            continue
        module_name = f"plugins.{info.name}"
        try:
            module = importlib.import_module(module_name)
        except Exception as exc:
            logger.error("Failed to import plugin %s: %s", module_name, exc)
            continue
        handler = getattr(module, "handle", None)
        if callable(handler):
            HANDLERS.append(handler)
            logger.info("Loaded plugin %s", module_name)


def dispatch_event(event: dict) -> None:
    """Send event to all registered plugin handlers."""
    for handler in HANDLERS:
        try:
            asyncio.create_task(handler(event))
        except Exception as exc:
            logger.error("Plugin handler error: %s", exc)
