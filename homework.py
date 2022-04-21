from dotenv import load_dotenv
import logging
import os
import requests
import sys
import time
import telegram

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)
formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(message)s'
)
handler.setFormatter(formatter)


def send_message(bot, message):
    """Отправка сообщения в Telegram-чат."""
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message
        )
        logger.info(f'Бот отправил сообщение: {message}')
    except telegram.error.TelegramError:
        logger.error('Ошибка отправки сообщения в Telegram-чат!')


def get_api_answer(current_timestamp):
    """Получаем ответ от API Практикума."""
    timestamp = current_timestamp
    params = {'from_date': timestamp}
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if response.status_code != 200:
        error = (
            f'Сбой в работе программы: Эндпоинт {ENDPOINT} недоступен. '
            f'Код ответа API: {response.status_code}'
        )
        raise Exception(error)
    return response.json()


def check_response(response):
    """Проверка ответа от API на корректность."""
    if not isinstance(response, dict):
        error = 'Некорректный ответ от API - ожидался словарь'
        raise TypeError(error)
    if 'homeworks' not in response.keys():
        error = (
            'Некорректный ответ от API - '
            'в словаре отсутствует ключ "homeworks"'
        )
        raise KeyError(error)
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        error = (
            'Некорректный ответ от API - '
            '"homeworks" должен иметь тип list'
        )
        raise TypeError(error)
    return homeworks


def parse_status(homework):
    """Получаем статус последней домашней работы."""
    if 'homework_name' not in homework.keys():
        error = (
            'Некорректный ответ от API - '
            'в словаре отсутствует ключ "homework_name"'
        )
        raise KeyError(error)
    homework_name = homework["homework_name"]
    if 'status' not in homework.keys():
        error = (
            'Некорректный ответ от API - '
            'в словаре отсутствует ключ "status"'
        )
        raise KeyError(error)
    homework_status = homework["status"]
    if homework_status not in HOMEWORK_STATUSES.keys():
        error = (
            'Некорректный ответ от API - '
            'недокументированный статус домашней работы'
        )
        raise KeyError(error)
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка доступности переменных окружения."""
    return PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID


def main():
    """Основная логика работы бота."""
    if check_tokens():
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
    else:
        logger.critical('Отсутствует обязательная переменная окружения')
        raise SystemExit('Программа принудительно остановлена.')
    current_timestamp = int(time.time()) - 2629743
    previous_message = ''
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if len(homeworks) > 0:
                message = parse_status(homeworks[0])
                send_message(bot, message)
            else:
                logger.debug('В ответе отсутствует новый статус')
            current_timestamp = response.get('current_date')
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            if message != previous_message:
                send_message(bot, message)
                previous_message = message
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
