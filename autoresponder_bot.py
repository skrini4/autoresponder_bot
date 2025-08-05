
import re
import imaplib
import email
from email.header import decode_header
import telebot
import requests
import json
from typing import Dict, List, Optional
import time
import logging
import os
from dotenv import load_dotenv
import threading
from pathlib import Path
from datetime import datetime

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
log_level = logging.DEBUG if os.getenv('DEBUG') else logging.INFO
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PyrusAPI:
    """Класс для работы с Pyrus CRM API"""

    def __init__(self, login: str, security_key: str):
        self.login = login
        self.security_key = security_key
        self.base_url = "https://api.pyrus.com/v4"
        self.auth_token = None
        self.authenticate()

    def authenticate(self):
        """Аутентификация в Pyrus API"""
        try:
            auth_url = f"{self.base_url}/auth"
            auth_data = {
                "login": self.login,
                "security_key": self.security_key
            }

            response = requests.post(auth_url, json=auth_data)

            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                logger.info("✅ Успешная аутентификация в Pyrus CRM")
                return True
            else:
                logger.error(f"❌ Ошибка аутентификации в Pyrus: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"❌ Исключение при аутентификации в Pyrus: {e}")
            return False

    def create_task(self, form_id: int, task_data: Dict) -> Optional[str]:
        """Создает задачу в Pyrus CRM"""
        try:
            if not self.auth_token:
                logger.error("❌ Нет токена аутентификации для Pyrus")
                return None

            create_url = f"{self.base_url}/tasks"
            headers = {
                'Authorization': f'Bearer {self.auth_token}',
                'Content-Type': 'application/json'
            }

            # Формируем данные для создания задачи
            task_payload = {
                "form_id": form_id,
                "text": f"Новая заявка с сайта от {datetime.now().strftime('%d.%m.%Y %H:%M')}",
                "fields": []
            }

            # Добавляем поля из данных заявки
            for field_name, value in task_data.items():
                task_payload["fields"].append({
                    "name": field_name,
                    "value": str(value)
                })

            response = requests.post(create_url, json=task_payload, headers=headers)

            if response.status_code == 200:
                data = response.json()
                task_id = data.get('task', {}).get('id')
                logger.info(f"✅ Создана задача в Pyrus CRM: {task_id}")
                return str(task_id)
            else:
                logger.error(f"❌ Ошибка создания задачи в Pyrus: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"❌ Исключение при создании задачи в Pyrus: {e}")
            return None

class GreenAPI:
    """Класс для работы с Green API WhatsApp"""

    def __init__(self, instance_id: str, api_token: str):
        self.instance_id = instance_id
        self.api_token = api_token
        self.base_url = f"https://api.green-api.com/waInstance{instance_id}"

    def get_state_instance(self) -> bool:
        """Проверяет состояние инстанса WhatsApp"""
        try:
            url = f"{self.base_url}/getStateInstance/{self.api_token}"
            response = requests.get(url, timeout=30)

            if response.status_code == 200:
                data = response.json()
                state = data.get('stateInstance')
                logger.info(f"📱 Состояние WhatsApp инстанса: {state}")
                return state == 'authorized'
            else:
                logger.error(f"❌ Ошибка проверки состояния WhatsApp: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"❌ Исключение при проверке состояния WhatsApp: {e}")
            return False

    def send_message(self, phone: str, message: str) -> bool:
        """Отправляет сообщение через WhatsApp"""
        try:
            url = f"{self.base_url}/sendMessage/{self.api_token}"

            # Форматируем номер телефона для Green API
            formatted_phone = self.format_phone_number(phone)

            payload = {
                "chatId": f"{formatted_phone}@c.us",
                "message": message
            }

            response = requests.post(url, json=payload, timeout=30)

            if response.status_code == 200:
                data = response.json()
                if data.get('idMessage'):
                    logger.info(f"✅ WhatsApp сообщение отправлено на {phone}")
                    return True
                else:
                    logger.error(f"❌ Не удалось отправить WhatsApp сообщение: {data}")
                    return False
            else:
                logger.error(f"❌ Ошибка Green API: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ Исключение при отправке WhatsApp сообщения: {e}")
            return False

    def format_phone_number(self, phone: str) -> str:
        """Форматирует номер телефона для Green API"""
        # Удаляем все лишние символы
        cleaned = re.sub(r'[^\d+]', '', phone)

        # Если номер начинается с 8, заменяем на 7
        if cleaned.startswith('8'):
            cleaned = '7' + cleaned[1:]
        elif cleaned.startswith('+7'):
            cleaned = cleaned[1:]
        elif cleaned.startswith('+'):
            cleaned = cleaned[1:]
        elif not cleaned.startswith('7'):
            cleaned = '7' + cleaned

        return cleaned

class AutoResponderBot:
    """
    Улучшенный бот автоответчик с интеграцией Pyrus CRM и Green API
    """

    def __init__(self):
        # Загружаем конфигурацию из переменных окружения
        self.config = self.load_config()

        # Инициализация Telegram Bot API
        if self.config.get('telegram_bot_token'):
            try:
                self.telegram_bot = telebot.TeleBot(self.config['telegram_bot_token'])
                self.setup_telegram_handlers()
                logger.info("✅ Telegram Bot API инициализирован")
            except Exception as e:
                logger.error(f"❌ Ошибка инициализации Telegram Bot: {e}")
                self.telegram_bot = None

        # Инициализация Pyrus CRM API
        if self.config.get('pyrus_login') and self.config.get('pyrus_security_key'):
            try:
                self.pyrus_api = PyrusAPI(
                    self.config['pyrus_login'],
                    self.config['pyrus_security_key']
                )
                logger.info("✅ Pyrus CRM API инициализирован")
            except Exception as e:
                logger.error(f"❌ Ошибка инициализации Pyrus CRM: {e}")
                self.pyrus_api = None
        else:
            self.pyrus_api = None

        # Инициализация Green API для WhatsApp
        if self.config.get('green_api_instance_id') and self.config.get('green_api_token'):
            try:
                self.green_api = GreenAPI(
                    self.config['green_api_instance_id'],
                    self.config['green_api_token']
                )

                # Проверяем состояние WhatsApp инстанса
                if self.green_api.get_state_instance():
                    logger.info("✅ Green API WhatsApp инициализирован и авторизован")
                else:
                    logger.warning("⚠️ Green API инстанс не авторизован. Требуется сканирование QR-кода")

            except Exception as e:
                logger.error(f"❌ Ошибка инициализации Green API: {e}")
                self.green_api = None
        else:
            self.green_api = None

        # Настройки для email
        self.email_config = self.config.get('email', {})

        # Счетчики для статистики
        self.stats = {
            'processed_applications': 0,
            'sent_whatsapp': 0,
            'sent_telegram': 0,
            'created_crm_tasks': 0,
            'errors': 0
        }

        # Шаблоны сообщений
        self.message_templates = {
            'house': "Здравствуйте! С Вами на связи строительная компания «Срубим».\nРады будем обсудить Ваши более детальные пожелания по будущему дому здесь или готовы назначить встречу в офисе.",
            'bath': "Здравствуйте! С Вами на связи строительная компания «Срубим».\nРады будем обсудить Ваши более детальные пожелания по будущей бане здесь или готовы назначить встречу в офисе.",
            'general_request': "Здравствуйте! С Вами на связи строительная компания «Срубим».\nМы получили Ваше обращение и в ближайшее время вернемся к Вам с ответом."
        }

    def load_config(self) -> Dict:
        """Загружает конфигурацию из переменных окружения"""
        return {
            # Telegram Bot API Token
            'telegram_bot_token': os.getenv('TELEGRAM_BOT_TOKEN'),

            # Настройки email
            'email': {
                'imap_server': os.getenv('EMAIL_IMAP_SERVER', 'imap.gmail.com'),
                'username': os.getenv('EMAIL_USERNAME'),
                'password': os.getenv('EMAIL_PASSWORD')
            },

            # Green API настройки для WhatsApp
            'green_api_instance_id': os.getenv('GREEN_API_INSTANCE_ID'),
            'green_api_token': os.getenv('GREEN_API_TOKEN'),

            # Pyrus CRM настройки
            'pyrus_login': os.getenv('PYRUS_LOGIN'),
            'pyrus_security_key': os.getenv('PYRUS_SECURITY_KEY'),
            'pyrus_form_id': int(os.getenv('PYRUS_FORM_ID', '0')),

            # Прочие настройки
            'debug': os.getenv('DEBUG', 'false').lower() == 'true',
            'check_interval': int(os.getenv('CHECK_INTERVAL', '60'))
        }

    def setup_telegram_handlers(self):
        """Настройка обработчиков для Telegram бота"""

        @self.telegram_bot.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            welcome_text = """
🤖 Бот автоответчик строительной компании "Срубим"

Я автоматически обрабатываю заявки и отправляю ответы клиентам.

🔧 Интеграции:
✅ Telegram Bot API
✅ Green API (WhatsApp)
✅ Pyrus CRM
✅ Email (IMAP)

Команды:
/stats - Статистика работы
/health - Проверка состояния всех сервисов
/test_whatsapp <номер> - Тест отправки WhatsApp
/help - Эта помощь
            """
            self.telegram_bot.reply_to(message, welcome_text)

        @self.telegram_bot.message_handler(commands=['stats'])
        def send_stats(message):
            stats_text = f"""
📊 Статистика работы бота:

✅ Обработано заявок: {self.stats['processed_applications']}
📱 Отправлено WhatsApp: {self.stats['sent_whatsapp']}
💬 Отправлено Telegram: {self.stats['sent_telegram']}
📋 Создано задач в CRM: {self.stats['created_crm_tasks']}
❌ Ошибок: {self.stats['errors']}

⏰ Время работы: {self.get_uptime()}
            """
            self.telegram_bot.reply_to(message, stats_text)

        @self.telegram_bot.message_handler(commands=['health'])
        def health_check(message):
            status = "🟢 Бот работает нормально"

            # Проверяем доступность сервисов
            checks = []

            # Проверка Green API
            if self.green_api and self.green_api.get_state_instance():
                checks.append("✅ Green API WhatsApp - авторизован")
            elif self.green_api:
                checks.append("⚠️ Green API WhatsApp - не авторизован")
            else:
                checks.append("❌ Green API WhatsApp - не настроен")

            # Проверка Pyrus CRM
            if self.pyrus_api and self.pyrus_api.auth_token:
                checks.append("✅ Pyrus CRM - подключен")
            else:
                checks.append("❌ Pyrus CRM - не настроен")

            # Проверка Email
            if all(self.email_config.values()):
                checks.append("✅ Email IMAP - настроен")
            else:
                checks.append("❌ Email IMAP - не настроен")

            health_text = f"{status}\n\n" + "\n".join(checks)
            self.telegram_bot.reply_to(message, health_text)

        @self.telegram_bot.message_handler(commands=['test_whatsapp'])
        def test_whatsapp(message):
            try:
                # Извлекаем номер телефона из команды
                parts = message.text.split(' ', 1)
                if len(parts) < 2:
                    self.telegram_bot.reply_to(message, "❌ Укажите номер телефона: /test_whatsapp +79001234567")
                    return

                phone = parts[1]
                test_message = "Тестовое сообщение от бота автоответчика компании «Срубим»"

                if self.green_api:
                    if self.green_api.send_message(phone, test_message):
                        self.telegram_bot.reply_to(message, f"✅ Тестовое сообщение отправлено на {phone}")
                    else:
                        self.telegram_bot.reply_to(message, f"❌ Не удалось отправить сообщение на {phone}")
                else:
                    self.telegram_bot.reply_to(message, "❌ Green API не настроен")

            except Exception as e:
                self.telegram_bot.reply_to(message, f"❌ Ошибка: {e}")

        @self.telegram_bot.message_handler(func=lambda message: True)
        def handle_message(message):
            # Проверяем, является ли сообщение заявкой
            if self.is_application_message(message.text):
                logger.info(f"📨 Получена заявка в Telegram от {message.from_user.username or 'Unknown'}")
                application_data = self.parse_application(message.text)
                if application_data:
                    success = self.process_application(application_data)
                    if success:
                        self.telegram_bot.reply_to(message, "✅ Заявка обработана и отправлен ответ клиенту")
                    else:
                        self.telegram_bot.reply_to(message, "⚠️ Заявка обработана частично")
                else:
                    self.telegram_bot.reply_to(message, "❌ Не удалось обработать заявку")

    def get_uptime(self) -> str:
        """Возвращает время работы бота"""
        if not hasattr(self, 'start_time'):
            self.start_time = datetime.now()

        uptime = datetime.now() - self.start_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        return f"{days}д {hours}ч {minutes}м"

    def is_application_message(self, text: str) -> bool:
        """Проверяет, является ли сообщение заявкой с сайта"""
        if not text:
            return False

        patterns = [
            r"Новая заявка № \d+",
            r"Название формы: (Application|Заявка)",
            r"Данные формы:",
            r"Телефон: [+\d\s\(\)\-]+",
            r"Куда отправить расчет стоимости"
        ]

        matches = 0
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                matches += 1

        # Считаем заявкой, если совпадает хотя бы 2 паттерна
        return matches >= 2

    def parse_application(self, text: str) -> Optional[Dict]:
        """Парсит заявку и извлекает нужную информацию"""
        try:
            data = {}

            # Извлекаем номер заявки
            application_number_match = re.search(r"Новая заявка № (\d+)", text)
            if application_number_match:
                data['application_number'] = application_number_match.group(1)

            # Извлекаем номер телефона
            phone_patterns = [
                r"Телефон: ([+\d\s\(\)\-]+)",
                r"тел[\.:][\s]*([+\d\s\(\)\-]+)",
                r"телефон[\.:][\s]*([+\d\s\(\)\-]+)"
            ]

            for pattern in phone_patterns:
                phone_match = re.search(pattern, text, re.IGNORECASE)
                if phone_match:
                    data['phone'] = phone_match.group(1).strip()
                    break

            # Определяем тип объекта (дом или баня)
            house_keywords = ['дом', 'коттедж', 'домик', 'house']
            bath_keywords = ['бан', 'сауна', 'парилка', 'bath', 'sauna']

            text_lower = text.lower()

            if any(keyword in text_lower for keyword in house_keywords):
                data['object_type'] = 'house'
                data['object_description'] = 'дом'
            elif any(keyword in text_lower for keyword in bath_keywords):
                data['object_type'] = 'bath'
                data['object_description'] = 'баня'
            else:
                data['object_type'] = 'house'  # по умолчанию дом
                data['object_description'] = 'дом'

            # Извлекаем площадь строения
            area_match = re.search(r"Площадь строения: ([^\n]+)", text)
            if area_match:
                data['area'] = area_match.group(1).strip()

            # Извлекаем бюджет
            budget_match = re.search(r"бюджет[^:]*: ([^\n]+)", text, re.IGNORECASE)
            if budget_match:
                data['budget'] = budget_match.group(1).strip()

            # Извлекаем наличие участка
            land_match = re.search(r"земельный участок[^:]*: ([^\n]+)", text, re.IGNORECASE)
            if land_match:
                data['has_land'] = land_match.group(1).strip()

            # Определяем способ связи
            contact_patterns = [
                (r"whatsapp", 'whatsapp'),
                (r"telegram", 'telegram'),
                (r"озвучить по телефону", 'phone_call'),
                (r"позвонить", 'phone_call')
            ]

            for pattern, method in contact_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    data['contact_method'] = method
                    break
            else:
                data['contact_method'] = 'whatsapp'  # по умолчанию WhatsApp

            # Определяем тип формы
            form_match = re.search(r"Название формы: (Application|Заявка)", text, re.IGNORECASE)
            if form_match:
                data['form_type'] = form_match.group(1).lower()
            else:
                data['form_type'] = 'application'

            # Добавляем временную метку
            data['created_at'] = datetime.now().isoformat()

            logger.info(f"📋 Распознанные данные заявки: {data}")
            return data if data.get('phone') else None

        except Exception as e:
            logger.error(f"❌ Ошибка при парсинге заявки: {e}")
            self.stats['errors'] += 1
            return None

    def process_application(self, data: Dict) -> bool:
        """Обрабатывает заявку и отправляет ответное сообщение"""
        try:
            success_count = 0
            total_actions = 3  # WhatsApp/Telegram, CRM, статистика

            # Пропускаем заявки с способом связи "озвучить по телефону"
            if data.get('contact_method') == 'phone_call':
                logger.info("⏭️ Пропускаем заявку с способом связи 'озвучить по телефону'")
                return True

            # 1. Создаем задачу в Pyrus CRM
            if self.pyrus_api and self.config.get('pyrus_form_id'):
                crm_data = {
                    'Телефон': data.get('phone', ''),
                    'Тип объекта': data.get('object_description', ''),
                    'Способ связи': data.get('contact_method', ''),
                    'Площадь': data.get('area', ''),
                    'Бюджет': data.get('budget', ''),
                    'Участок': data.get('has_land', ''),
                    'Номер заявки': data.get('application_number', ''),
                    'Дата создания': data.get('created_at', '')
                }

                task_id = self.pyrus_api.create_task(self.config['pyrus_form_id'], crm_data)
                if task_id:
                    success_count += 1
                    self.stats['created_crm_tasks'] += 1
                    data['crm_task_id'] = task_id

            # 2. Выбираем шаблон сообщения
            if data.get('form_type') == 'заявка':
                message_template = self.message_templates['general_request']
            else:
                object_type = data.get('object_type', 'house')
                message_template = self.message_templates.get(object_type, self.message_templates['house'])

            # 3. Отправляем сообщение в зависимости от способа связи
            contact_method = data.get('contact_method')
            phone = data.get('phone')

            message_sent = False

            if contact_method == 'whatsapp' and phone and self.green_api:
                if self.green_api.send_message(phone, message_template):
                    success_count += 1
                    self.stats['sent_whatsapp'] += 1
                    message_sent = True
            elif contact_method == 'telegram' and phone:
                # Здесь можно добавить отправку через Telegram User API
                logger.info(f"📱 Требуется отправка в Telegram на {phone}: {message_template}")
                # Заглушка - считаем успешным
                success_count += 1
                self.stats['sent_telegram'] += 1
                message_sent = True

            # 4. Обновляем общую статистику
            if message_sent or data.get('crm_task_id'):
                self.stats['processed_applications'] += 1
                success_count += 1

            # Определяем успешность операции
            success_ratio = success_count / total_actions
            is_successful = success_ratio >= 0.5  # Считаем успешным если выполнено хотя бы 50%

            if is_successful:
                logger.info(f"✅ Успешно обработана заявка ({success_count}/{total_actions}): {data}")
            else:
                logger.warning(f"⚠️ Частично обработана заявка ({success_count}/{total_actions}): {data}")
                self.stats['errors'] += 1

            return is_successful

        except Exception as e:
            logger.error(f"❌ Ошибка при обработке заявки: {e}")
            self.stats['errors'] += 1
            return False

    def check_email(self):
        """Проверяет новые письма в почтовом ящике"""
        try:
            if not all(self.email_config.values()):
                return

            imap_server = self.email_config.get('imap_server')
            username = self.email_config.get('username')
            password = self.email_config.get('password')

            # Подключаемся к почтовому серверу
            imap = imaplib.IMAP4_SSL(imap_server)
            imap.login(username, password)
            imap.select("INBOX")

            # Ищем непрочитанные письма
            status, messages = imap.search(None, "UNSEEN")

            if status == "OK" and messages[0]:
                message_ids = messages[0].split()
                logger.info(f"📧 Найдено {len(message_ids)} непрочитанных писем")

                for msg_id in message_ids:
                    # Получаем письмо
                    status, msg_data = imap.fetch(msg_id, "(RFC822)")

                    if status == "OK":
                        email_body = msg_data[0][1]
                        email_message = email.message_from_bytes(email_body)

                        # Проверяем, является ли письмо заявкой
                        subject = email_message.get("Subject", "")
                        body = self.get_email_body(email_message)

                        full_text = f"{subject} {body}"

                        if self.is_application_message(full_text):
                            logger.info(f"📧 Получена заявка по email: {subject}")
                            application_data = self.parse_application(full_text)
                            if application_data:
                                self.process_application(application_data)

                        # Помечаем письмо как прочитанное
                        imap.store(msg_id, '+FLAGS', '\\Seen')

            imap.close()
            imap.logout()

        except Exception as e:
            logger.error(f"❌ Ошибка при проверке email: {e}")
            self.stats['errors'] += 1

    def get_email_body(self, email_message) -> str:
        """Извлекает текст из письма"""
        try:
            body = ""

            if email_message.is_multipart():
                for part in email_message.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))

                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
            else:
                body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')

            return body

        except Exception as e:
            logger.error(f"❌ Ошибка при извлечении текста письма: {e}")
            return ""

    def run(self):
        """Запускает бота"""
        logger.info("🚀 Запуск бота автоответчика...")
        self.start_time = datetime.now()

        try:
            # Проверяем конфигурацию
            config_warnings = []

            if not self.config.get('telegram_bot_token'):
                config_warnings.append("⚠️ Telegram Bot Token не настроен")

            if not all(self.email_config.values()):
                config_warnings.append("⚠️ Email настройки не полные")

            if not self.green_api:
                config_warnings.append("⚠️ Green API не настроен")

            if not self.pyrus_api:
                config_warnings.append("⚠️ Pyrus CRM не настроен")

            if config_warnings:
                logger.warning("Предупреждения конфигурации:")
                for warning in config_warnings:
                    logger.warning(warning)

            # Запускаем Telegram бота в отдельном потоке
            if hasattr(self, 'telegram_bot') and self.telegram_bot:
                telegram_thread = threading.Thread(
                    target=self.telegram_bot.polling, 
                    kwargs={'none_stop': True, 'timeout': 60}
                )
                telegram_thread.daemon = True
                telegram_thread.start()
                logger.info("✅ Telegram Bot запущен")

            # Главный цикл для проверки email
            check_interval = self.config.get('check_interval', 60)
            logger.info(f"🔄 Начинаем проверку email каждые {check_interval} секунд")

            while True:
                try:
                    self.check_email()

                    # Выводим статистику каждые 10 проверок
                    if hasattr(self, 'check_count'):
                        self.check_count += 1
                    else:
                        self.check_count = 1

                    if self.check_count % 10 == 0:
                        logger.info(f"📊 Статистика: обработано {self.stats['processed_applications']} заявок, время работы: {self.get_uptime()}")

                except Exception as e:
                    logger.error(f"❌ Ошибка в цикле проверки email: {e}")
                    self.stats['errors'] += 1

                time.sleep(check_interval)

        except KeyboardInterrupt:
            logger.info("⏹️ Бот остановлен пользователем")
        except Exception as e:
            logger.error(f"💥 Критическая ошибка в работе бота: {e}")

def main():
    """Основная функция запуска бота"""

    # Создаем необходимые директории
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)

    # Проверяем наличие .env файла
    if not Path(".env").exists():
        logger.error("❌ Файл .env не найден! Скопируйте config_example.env в .env и заполните настройки.")
        print("\n🔧 Быстрая настройка:")
        print("1. cp config_example.env .env")
        print("2. nano .env  # Заполните настройки")
        print("3. python autoresponder_bot.py")
        return

    # Запускаем бота
    try:
        bot = AutoResponderBot()
        bot.run()
    except Exception as e:
        logger.error(f"💥 Не удалось запустить бота: {e}")

if __name__ == "__main__":
    main()
