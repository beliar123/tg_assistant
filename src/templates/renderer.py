import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

_TEMPLATES_DIR = Path(__file__).parent

# autoescape включён для всех расширений кроме .md (Telegram MarkdownV2).
# HTML-шаблоны (например reminder_email.html) экранируются автоматически —
# не добавляйте фильтр | safe к пользовательским данным.
_env = Environment(
    loader=FileSystemLoader(_TEMPLATES_DIR),
    autoescape=select_autoescape(disabled_extensions=("md",)),
    trim_blocks=True,
    lstrip_blocks=True,
)


def render(template_name: str, **context: object) -> str:
    """Рендерит шаблон и возвращает готовую строку для отправки."""
    template = _env.get_template(template_name)
    return template.render(**context).strip()