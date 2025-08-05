
# 🚀 Полное руководство по развертыванию на VPS

## 🎯 Выбор VPS провайдера

### Рекомендуемые провайдеры в России:
- **REG.RU** - надежно, российская юрисдикция
- **Selectel** - хорошее соотношение цена/качество  
- **Yandex.Cloud** - современная платформа
- **VK Cloud** - быстрый SSD
- **Timeweb** - популярный у разработчиков

### Рекомендуемые характеристики:
```
🔹 Минимальная конфигурация:
   - 1 vCPU
   - 1 GB RAM  
   - 10 GB SSD
   - Ubuntu 20.04/22.04

🔹 Рекомендуемая конфигурация:
   - 2 vCPU
   - 2 GB RAM
   - 20 GB SSD
   - Ubuntu 22.04 LTS
```

## 📋 Пошаговое развертывание

### Шаг 1: Подготовка сервера

```bash
# Подключаемся по SSH
ssh root@your-server-ip

# Обновляем систему
apt update && apt upgrade -y

# Устанавливаем необходимые пакеты
apt install -y python3 python3-pip python3-venv git htop curl wget unzip

# Создаем пользователя для приложения
adduser botuser
usermod -aG sudo botuser

# Переключаемся на нового пользователя
su - botuser
```

### Шаг 2: Загрузка и установка бота

```bash
# Загружаем архив проекта
wget https://github.com/your-repo/autoresponder-bot/archive/main.zip
# или загружаем через scp:
# scp autoresponder-bot-complete.zip botuser@your-server:/home/botuser/

# Распаковываем
unzip autoresponder-bot-complete.zip
cd autoresponder-bot

# Запускаем автоматическую установку
chmod +x install.sh
./install.sh
```

### Шаг 3: Настройка конфигурации

```bash
# Копируем пример конфигурации
cp config_example.env .env

# Редактируем конфигурацию
nano .env
```

**Пример заполнения .env:**
```env
# Telegram Bot (обязательно)
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# Email настройки (обязательно)
EMAIL_IMAP_SERVER=imap.gmail.com
EMAIL_USERNAME=your-company@gmail.com  
EMAIL_PASSWORD=your-app-password

# WhatsApp API (рекомендуется Green API)
WHATSAPP_API_URL=https://api.green-api.com/waInstance1234567890/sendMessage/abc123def456
WHATSAPP_TOKEN=your-green-api-token

# Дополнительные настройки
DEBUG=false
CHECK_INTERVAL=60

# Telegram User API (опционально, для личного аккаунта)
# TELEGRAM_API_ID=1234567
# TELEGRAM_API_HASH=abcdef123456789
# TELEGRAM_PHONE_NUMBER=+7900123456
```

### Шаг 4: Получение необходимых токенов

#### 🤖 Telegram Bot Token:
1. Найдите @BotFather в Telegram
2. Отправьте `/newbot`
3. Следуйте инструкциям
4. Получите токен вида: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

#### 📧 Email App Password (Gmail):
1. Включите двухфакторную аутентификацию
2. Перейдите в "Аккаунт Google" → "Безопасность"
3. Выберите "Пароли приложений"
4. Создайте пароль для "Другое приложение"

#### 📱 WhatsApp API (Green API):
1. Зарегистрируйтесь на [green-api.com](https://green-api.com)
2. Создайте инстанс
3. Получите Instance ID и API Token
4. Авторизуйте WhatsApp через QR-код

### Шаг 5: Запуск и тестирование

```bash
# Тестовый запуск
source venv/bin/activate
python autoresponder_bot.py

# Если все работает, останавливаем (Ctrl+C) и запускаем как сервис
sudo systemctl start autoresponder-bot
sudo systemctl enable autoresponder-bot

# Проверяем статус
sudo systemctl status autoresponder-bot
```

## 🔧 Настройка Flexbe Webhook

### В панели Flexbe:
1. Перейдите в "Настройки" → "API"
2. Добавьте Webhook: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/sendMessage`
3. Или настройте отправку на email, который мониторит бот

### Альтернативный способ - прямой webhook:
Можно настроить простой HTTP сервер для приема webhook'ов от Flexbe:

```python
from flask import Flask, request
import requests

app = Flask(__name__)

@app.route('/webhook/flexbe', methods=['POST'])  
def flexbe_webhook():
    data = request.json
    # Отправляем данные боту в Telegram
    bot_token = "YOUR_BOT_TOKEN"
    chat_id = "YOUR_CHAT_ID"  

    message = f"Новая заявка с Flexbe: {data}"

    requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", {
        'chat_id': chat_id,
        'text': message
    })

    return "OK"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## 🔒 Настройка безопасности

### Файрвол:
```bash
# Настраиваем UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### SSL сертификат (при необходимости):
```bash
# Устанавливаем Certbot
sudo apt install snapd
sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot

# Получаем сертификат
sudo certbot certonly --standalone -d your-domain.com
```

### Защита конфигурации:
```bash
# Ограничиваем доступ к .env файлу
chmod 600 .env
chown botuser:botuser .env
```

## 📊 Мониторинг и логи

### Просмотр логов:
```bash
# Логи systemd
sudo journalctl -u autoresponder-bot -f

# Логи приложения
tail -f ~/autoresponder-bot/bot.log

# Логи с фильтрацией ошибок
sudo journalctl -u autoresponder-bot -p err
```

### Настройка ротации логов:
```bash
sudo nano /etc/logrotate.d/autoresponder-bot
```

Содержимое файла:
```
/home/botuser/autoresponder-bot/bot.log {
    daily
    missingok
    rotate 30
    compress  
    notifempty
    create 644 botuser botuser
}
```

## 🚨 Мониторинг и алерты

### Простой мониторинг доступности:
```bash
#!/bin/bash
# check_bot.sh

SERVICE="autoresponder-bot"
if ! systemctl is-active --quiet $SERVICE; then
    echo "Сервис $SERVICE не работает!" | mail -s "Alert: Bot Down" admin@company.com
    systemctl restart $SERVICE
fi
```

Добавляем в crontab:
```bash
crontab -e
# Проверяем каждые 5 минут
*/5 * * * * /home/botuser/check_bot.sh
```

## 📈 Масштабирование

### Для высоких нагрузок:

#### 1. Используйте Docker:
```bash
# Собираем образ
docker build -t autoresponder-bot .

# Запускаем контейнер
docker-compose up -d
```

#### 2. Настройте Load Balancer:
```nginx
# /etc/nginx/sites-available/bot
upstream bot_servers {
    server 127.0.0.1:5000;
    server 127.0.0.1:5001;
}

server {
    listen 80;
    server_name your-domain.com;

    location /webhook {
        proxy_pass http://bot_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 3. Используйте Redis для очередей:
```python
import redis
import json

r = redis.Redis(host='localhost', port=6379, db=0)

# Добавляем задачу в очередь
def add_task(task_data):
    r.lpush('bot_tasks', json.dumps(task_data))

# Обрабатываем задачи из очереди  
def process_tasks():
    while True:
        task = r.brpop('bot_tasks', timeout=1)
        if task:
            task_data = json.loads(task[1])
            # Обрабатываем задачу
```

## 💰 Оценка стоимости

### Ежемесячные расходы:

**VPS (минимальная конфигурация):**
- REG.RU: ~300₽/мес
- Selectel: ~350₽/мес  
- Yandex.Cloud: ~400₽/мес

**API сервисы:**
- Telegram Bot API: бесплатно
- WhatsApp Green API: от 1000₽/мес (зависит от объема)
- Email: бесплатно (если свой домен)

**Итого: от 1300₽/мес**

### Экономия:
При обработке 100+ заявок в день бот окупается за счет:
- Экономии времени менеджеров (50+ часов/мес)
- Мгновенных ответов клиентам (увеличение конверсии)
- Работы 24/7 без выходных

## ⚡ Оптимизация производительности

### Настройки для высокой нагрузки:

```python
# В autoresponder_bot.py
import asyncio
import aiohttp

class OptimizedBot:
    def __init__(self):
        self.session = aiohttp.ClientSession()
        self.email_check_interval = 30  # Проверяем чаще
        self.batch_size = 10  # Обрабатываем пакетами

    async def send_messages_batch(self, messages):
        tasks = []
        for msg in messages:
            task = self.send_message_async(msg)
            tasks.append(task)

        await asyncio.gather(*tasks)
```

### Кеширование и оптимизация:
```python
import functools
import time

@functools.lru_cache(maxsize=1000)
def format_phone_number(phone):
    # Кешируем форматирование номеров
    return clean_phone(phone)

# Ограничиваем частоту запросов к API
class RateLimiter:
    def __init__(self, max_calls=30, period=60):
        self.max_calls = max_calls
        self.period = period
        self.calls = []

    def wait_if_needed(self):
        now = time.time()
        # Убираем старые вызовы
        self.calls = [call for call in self.calls if now - call < self.period]

        if len(self.calls) >= self.max_calls:
            sleep_time = self.period - (now - self.calls[0])
            time.sleep(sleep_time)

        self.calls.append(now)
```

## 🔄 Резервное копирование

### Автоматический бэкап:
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/autoresponder-bot"
SOURCE_DIR="/home/botuser/autoresponder-bot"
DATE=$(date +%Y%m%d_%H%M%S)

# Создаем резервную копию
mkdir -p $BACKUP_DIR
tar -czf "$BACKUP_DIR/backup_$DATE.tar.gz"     -C $SOURCE_DIR     .env bot.log data/

# Удаляем старые бэкапы (старше 30 дней)
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +30 -delete

echo "Backup completed: backup_$DATE.tar.gz"
```

Добавляем в crontab:
```bash
# Бэкап каждый день в 3:00
0 3 * * * /home/botuser/backup.sh
```

## 🆘 Troubleshooting

### Частые проблемы и решения:

#### Бот не отвечает:
```bash
# Проверяем статус сервиса
sudo systemctl status autoresponder-bot

# Проверяем логи
sudo journalctl -u autoresponder-bot -n 50

# Проверяем процессы
ps aux | grep python

# Перезапускаем
sudo systemctl restart autoresponder-bot
```

#### Проблемы с памятью:
```bash
# Проверяем использование памяти
free -h
htop

# Если нужно - увеличиваем swap
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Добавляем в /etc/fstab для постоянного использования
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

#### Email не работает:
```bash
# Тестируем подключение к IMAP
python3 -c "
import imaplib
imap = imaplib.IMAP4_SSL('imap.gmail.com')
imap.login('your-email@gmail.com', 'your-app-password')
print('Email connection OK')
imap.logout()
"
```

#### WhatsApp API ошибки:
```bash
# Проверяем доступность API
curl -X GET "https://api.green-api.com/waInstance{instance}/getStateInstance/{token}"

# Тестируем отправку сообщения
curl -X POST "https://api.green-api.com/waInstance{instance}/sendMessage/{token}" -H "Content-Type: application/json" -d '{"chatId":"79001234567@c.us","message":"Test"}'
```

Этот гайд поможет вам полностью развернуть и настроить бота на VPS сервере! 🚀
