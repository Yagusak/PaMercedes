# PaMercedes

Парсер тем форума `benzclub.ru` на Python + Selenium с опциональным GPT-фильтром по техническим проблемам.

## Паспорт проекта

- Название: `PaMercedes`
- Тип: CLI-утилита для сбора и фильтрации тем форума
- Язык: `Python 3.10+`
- Источник: страницы `forumdisplay.php?f=<forum_id>&page=<n>`
- Основной результат: список тем с полями `title`, `url`, `replies`, `views`, `last_post`
- Форматы вывода: `CSV` и `JSON`
- Дополнительно: GPT-классификация тем (`Да/Нет`) по признаку технической неисправности

## Назначение

Проект автоматизирует сбор тем выбранного раздела Mercedes Club.
После парсинга можно включить GPT-фильтр, который оставляет только технические проблемы
(поломки, ошибки, ремонты, отказы систем и т.д.).

## Состав репозитория

- `forum_parser.py` - парсинг страниц + опциональная GPT-фильтрация.
- `save_cookies.py` - сохранение cookies после ручного входа.
- `requirements.txt` - зависимости проекта.
- `.env.example` - пример переменной окружения для OpenAI.
- `.gitignore` - исключения для временных файлов и результатов выгрузки.

## Как работает `forum_parser.py`

1. Принимает параметры CLI (ID раздела, число страниц, задержки, пути output).
2. Поднимает Chrome WebDriver через `webdriver-manager`.
3. Если задан `--cookies`, применяет cookies перед обходом страниц.
4. Переходит по страницам раздела и извлекает темы через `BeautifulSoup`.
5. Сохраняет полный набор тем в `topics.csv` и `topics.json`.
6. Если включен `--use-gpt-filter`, отправляет заголовки тем в OpenAI и сохраняет отфильтрованный набор в отдельные файлы.

## Логика извлечения полей

- `title`: текст ссылки темы (`a[id^=thread_title_]`).
- `url`: абсолютный URL темы.
- `replies`: число ответов из блока `who posted`.
- `views`: максимальное числовое значение в целевых ячейках статистики.
- `last_post`: дата последнего поста в формате `YYYY-MM-DDTHH:MM`.

## Установка

```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
```

## Настройка OpenAI (для GPT-фильтра)

Вариант 1, переменная окружения:

```bash
set OPENAI_API_KEY=your_openai_api_key
```

Вариант 2, файл `.env` рядом со скриптом:

```env
OPENAI_API_KEY=your_openai_api_key
```

## Быстрый старт

### 1) Сохранить cookies (опционально)

```bash
python save_cookies.py --output benzclub_cookies.pkl
```

### 2) Базовый парсинг без GPT

```bash
python forum_parser.py --forum-id 40 --pages 10 --cookies benzclub_cookies.pkl
```

### 3) Парсинг + GPT-фильтр

```bash
python forum_parser.py --forum-id 40 --pages 10 --use-gpt-filter --gpt-model gpt-4o-mini
```

## Параметры `forum_parser.py`

- `--forum-id`: ID раздела форума (по умолчанию `40`).
- `--pages`: число страниц для обхода (по умолчанию `3`).
- `--delay`: задержка между загрузками страниц (по умолчанию `1.5`).
- `--headless`: запуск браузера без окна.
- `--cookies`: путь к `.pkl` cookies.
- `--output-csv`: путь к CSV с полным набором (по умолчанию `topics.csv`).
- `--output-json`: путь к JSON с полным набором (по умолчанию `topics.json`).
- `--use-gpt-filter`: включить GPT-фильтрацию.
- `--gpt-model`: модель OpenAI для фильтра (по умолчанию `gpt-4o-mini`).
- `--gpt-delay`: задержка между GPT-запросами (по умолчанию `0.0`).
- `--gpt-output-csv`: CSV для отфильтрованных тем (по умолчанию `topics_gpt_filtered.csv`).
- `--gpt-output-json`: JSON для отфильтрованных тем (по умолчанию `topics_gpt_filtered.json`).

## Выходные файлы

Всегда создаются:

- `topics.csv`
- `topics.json`

При `--use-gpt-filter` дополнительно:

- `topics_gpt_filtered.csv`
- `topics_gpt_filtered.json`

## Ограничения

- При изменении HTML форума может потребоваться корректировка CSS-селекторов.
- GPT-фильтр использует внешнее API, зависит от сети и тарифа OpenAI.
- При ошибке GPT-запроса тема временно сохраняется (fail-open), чтобы не потерять данные.
