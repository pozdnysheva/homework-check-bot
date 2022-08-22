## Telegram-бот
Этот бот:
- раз в 10 минут опрашивает API сервиса Практикум.Домашка и проверяет статус отправленной на ревью домашней работы;
- при обновлении статуса анализирует ответ API и отправляет пользователю соответствующее уведомление в Telegram;
- логирует свою работу и сообщает о важных проблемах сообщением в Telegram.

## Технологии:
- Python 3.7
- Библиотека python-telegram-bot

## Как запустить проект

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/pozdnysheva/homework-check-bot.git
```

Cоздать и активировать виртуальное окружение:

```
python -m venv env
```

```
source venv/Scripts/activate
```

Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```
Создайте чат-бота Телеграм

Создайте в директории файл .env и поместите туда необходимые токены в формате PRAKTIKUM_TOKEN = 'ххххххххх', TELEGRAM_TOKEN = 'ххххххххххх', TELEGRAM_CHAT_ID = 'ххххххххххх'

Запустить проект:

```
python homework.py
```
