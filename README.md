# fiorentin0-ODstat

Простой Telegram-бот, который предоставляет различную информацию о игроках и командах ЧГК.

Ссылка на pythonanywhere: https://www.pythonanywhere.com/user/fiorentin0/files/home/fiorentin0/run_bot.py?edit

## Что бот умеет

Находить лучшие турниры игрока/команды,
графически отображать активность игрока/команды,
находить количество сыгранных игр за каждую команду,
а также смотреть рейтинг команд в которых игрок принимал участие

## Зависимости

Вначале создайте `venv`

```commandline
python -m venv venv
```

потом установите зависимости

```commandline
pip install -r requirements.txt
```

## Запуск

```commandline
env BOT_TOKEN=<token> python run_bot.py
```

# Детали реализации

Для запросов на сайт (`rating.chgk.info`) используется библиотека `aiohttp`.
Результат запросов парсится с помощью `beautifulsoup4`. Графики строятся через `matplotlib`.
функциональность бота реализованная через библиотеку `aiogram`.
