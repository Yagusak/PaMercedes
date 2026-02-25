# PaMercedes

Парсер раздела форума `benzclub.ru` 

## Что в репозитории

- `forum_parser.py` - парсинг тем форума по страницам.
- `save_cookies.py` - опциональное сохранение cookies после ручного входа.
- `requirements.txt` - зависимости Python.

## Установка

```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
```

## 1) Сохранить cookies (опционально)

Нужно только если форум требует авторизацию для полного просмотра.

```bash
python save_cookies.py --output benzclub_cookies.pkl
```

Откроется браузер: войдите в аккаунт вручную и нажмите Enter в терминале.

## 2) Запустить парсер

```bash
python forum_parser.py --forum-id 40 --pages 10 --cookies benzclub_cookies.pkl
```

Если cookies не нужны:

```bash
python forum_parser.py --forum-id 40 --pages 10
```

## Параметры `forum_parser.py`

- `--forum-id` - ID раздела форума (по умолчанию `40`).
- `--pages` - сколько страниц парсить (по умолчанию `3`).
- `--delay` - задержка между страницами в секундах (по умолчанию `1.5`).
- `--headless` - запуск браузера без окна.
- `--cookies` - путь к `.pkl` файлу cookies.
- `--output-csv` - путь к CSV (по умолчанию `topics.csv`).
- `--output-json` - путь к JSON (по умолчанию `topics.json`).

## Выходные данные

- `topics.csv`
- `topics.json`

Поля: `title`, `url`, `replies`, `views`, `last_post`.

## Важно

- В репозитории нет API-ключей, логинов, cookie-файлов и локальных персональных путей.
- Не коммитьте `benzclub_cookies.pkl` и результаты выгрузки.
