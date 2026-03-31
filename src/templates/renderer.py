import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

_TEMPLATES_DIR = Path(__file__).parent

_env = Environment(
    loader=FileSystemLoader(_TEMPLATES_DIR),
    autoescape=select_autoescape(disabled_extensions=("md",)),
    trim_blocks=True,
    lstrip_blocks=True,
)

# Символы, которые нужно экранировать в Telegram MarkdownV2
_MD_SPECIAL = re.compile(r"([_*\[\]()~`>#+\-=|{}.!\\])")


def _escape_md(value: object) -> str:
    """Экранирует спецсимволы MarkdownV2 для пользовательских данных."""
    return _MD_SPECIAL.sub(r"\\\1", str(value))


_env.filters["escape_md"] = _escape_md


def render(template_name: str, **context: object) -> str:
    """Рендерит шаблон и возвращает готовую строку для отправки в Telegram."""
    template = _env.get_template(template_name)
    return template.render(**context).strip()