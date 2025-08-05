
# 📖 Полное руководство по установке и настройке бота автоответчика

## 🎯 Назначение проекта

Бот автоответчик для строительной компании "Срубим" автоматически:
- 📧 Обрабатывает заявки из email
- 📱 Принимает заявки через Telegram  
- 🌐 Работает с веб-формами Flexbe
- 💬 Отправляет ответы в WhatsApp через Green API
- 📋 Создает задачи в Pyrus CRM
- 🔄 Работает 24/7 без перерывов

## 📋 Содержание

1. [Требования к системе](#требования-к-системе)
2. [Получение API ключей](#получение-api-ключей)
3. [Установка на VPS](#установка-на-vps)
4. [Настройка конфигурации](#настройка-конфигурации)  
5. [Запуск и тестирование](#запуск-и-тестирование)
6. [Мониторинг и логи](#мониторинг-и-логи)
7. [Troubleshooting](#troubleshooting)
8. [Масштабирование](#масштабирование)

---

## 🔧 Требования к системе

### Минимальные требования VPS:
- **ОС:** Ubuntu 20.04+ / Debian 10+ / CentOS 8+
- **RAM:** 1 GB (рекомендуется 2 GB)
- **CPU:** 1 vCPU (рекомендуется 2 vCPU)  
- **Диск:** 10 GB SSD (рекомендуется 20 GB)
- **Сеть:** постоянное подключение к интернету

### Программные требования:
- Python 3.8+
- pip (менеджер пакетов Python)
- systemd (для работы как сервис)
- git (для клонирования репозитория)

---

## 🔑 Получение API ключей

### 1. Telegram Bot Token

**Создание бота в Telegram:**

1. Найдите @BotFather в Telegram
2. Отправьте команду `/newbot`
3. Придумайте имя для бота: `Срубим Автоответчик`
4. Придумайте username: `srubim_autoresponder_bot`
5. Получите токен вида: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

**Настройка бота:**
```
/setdescription - Автоматический обработчик заявок компании Срубим
/setabouttext - Бот обрабатывает заявки и отправляет ответы клиентам
/setuserpic - Загрузите логотип компании
```

### 2. Green API (WhatsApp)

**Регистрация и настройка:**

1. Перейдите на [green-api.com](https://green-api.com)
2. Зарегистрируйтесь и войдите в личный кабинет
3. Создайте новый инстанс:
   - Выберите тариф (есть бесплатный "Разработчик")
   - Получите **Instance ID** (например: `1101000001`)
   - Получите **API Token** (например: `d75b3a66374942c5b3c019c698abc2067e151558acbd412345`)

**Авторизация WhatsApp:**

1. В личном кабинете Green API перейдите к своему инстансу
2. Нажмите "Привязать аккаунт"
3. Откройте WhatsApp на телефоне
4. Перейдите в Настройки → Связанные устройства
5. Нажмите "Привязать устройство"
6. Отсканируйте QR-код на сайте Green API

⚠️ **Важно:** Используйте отдельный номер WhatsApp для бизнеса!

### 3. Pyrus CRM

**Настройка API доступа:**

1. Войдите в ваш аккаунт [Pyrus.com](https://pyrus.com)
2. Перейдите в Настройки → API
3. Создайте API ключ:
   - **Login:** ваш email в Pyrus
   - **Security Key:** сгенерированный ключ
4. Найдите ID формы для заявок:
   - Откройте нужную форму
   - В URL найдите число после `/forms/` - это Form ID

**Создание формы для заявок (если нет):**

1. Создайте новую форму: "Заявки с сайта"
2. Добавьте поля:
   - Телефон (текст)
   - Тип объекта (текст)
   - Способ связи (текст)  
   - Площадь (текст)
   - Бюджет (текст)
   - Участок (текст)
   - Номер заявки (текст)
   - Дата создания (дата/время)

### 4. Email настройки

**Для Gmail:**

1. Включите двухфакторную аутентификацию
2. Перейдите в настройки Google аккаунта
3. Безопасность → Пароли приложений  
4. Создайте пароль для "Другое приложение"
5. Используйте этот пароль в настройках бота

**Для других почтовых сервисов:**
- **Yandex:** imap.yandex.ru, порт 993
- **Mail.ru:** imap.mail.ru, порт 993
- **Rambler:** imap.rambler.ru, порт 993

---

## 🚀 Установка на VPS

### Метод 1: Автоматическая установка

```bash
# Подключитесь к серверу
ssh root@your-server-ip

# Загрузите проект
wget https://github.com/your-repo/autoresponder-bot/releases/latest/download/autoresponder-bot-complete.zip
unzip autoresponder-bot-complete.zip
cd autoresponder-bot

# Запустите автоматическую установку
chmod +x install.sh
./install.sh
```

### Метод 2: Ручная установка

```bash
# 1. Обновление системы
sudo apt update && sudo apt upgrade -y

# 2. Установка Python и зависимостей
sudo apt install python3 python3-pip python3-venv git htop curl wget unzip -y

# 3. Создание пользователя для бота
sudo adduser botuser
sudo usermod -aG sudo botuser
su - botuser

# 4. Клонирование проекта
git clone https://github.com/your-repo/autoresponder-bot.git
cd autoresponder-bot

# 5. Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# 6. Установка зависимостей Python
pip install --upgrade pip
pip install -r requirements.txt

# 7. Настройка конфигурации
cp config_example.env .env
nano .env  # Заполните настройки

# 8. Создание systemd сервиса
sudo nano /etc/systemd/system/autoresponder-bot.service
```

**Содержимое файла сервиса:**
```ini
[Unit]
Description=AutoResponder Bot for Srubim Company
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/home/botuser/autoresponder-bot
Environment=PATH=/home/botuser/autoresponder-bot/venv/bin
ExecStart=/home/botuser/autoresponder-bot/venv/bin/python autoresponder_bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

```bash
# 9. Активация сервиса
sudo systemctl daemon-reload
sudo systemctl enable autoresponder-bot
```

---

## ⚙️ Настройка конфигурации

### Редактирование .env файла

```bash
nano .env
```

**Пример заполненного .env файла:**

```env
# Telegram Bot API
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# Email настройки
EMAIL_IMAP_SERVER=imap.gmail.com
EMAIL_USERNAME=company@gmail.com
EMAIL_PASSWORD=abcd1234efgh5678

# Green API (WhatsApp)
GREEN_API_INSTANCE_ID=1101000001
GREEN_API_TOKEN=d75b3a66374942c5b3c019c698abc2067e151558acbd412345

# Pyrus CRM
PYRUS_LOGIN=manager@company.com
PYRUS_SECURITY_KEY=aAbBcCdDeEfFgGhHiIjJkK1234567890
PYRUS_FORM_ID=12345

# Дополнительные настройки
DEBUG=false
CHECK_INTERVAL=60
```

### Проверка конфигурации

```bash
# Проверка синтаксиса .env файла
python3 -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('✅ Конфигурация загружена успешно')
print(f'Telegram Bot: {"✅" if os.getenv("TELEGRAM_BOT_TOKEN") else "❌"}')
print(f'Green API: {"✅" if os.getenv("GREEN_API_INSTANCE_ID") else "❌"}')
print(f'Pyrus CRM: {"✅" if os.getenv("PYRUS_LOGIN") else "❌"}')
print(f'Email: {"✅" if os.getenv("EMAIL_USERNAME") else "❌"}')
"
```

---

## 🎬 Запуск и тестирование

### Первый запуск (тестовый режим)

```bash
# Активируем виртуальное окружение
cd /home/botuser/autoresponder-bot
source venv/bin/activate

# Включаем режим отладки
export DEBUG=true

# Запускаем бота
python autoresponder_bot.py
```

**Что должно произойти:**
```
2024-08-04 16:00:01 - INFO - 🚀 Запуск бота автоответчика...
2024-08-04 16:00:02 - INFO - ✅ Telegram Bot API инициализирован
2024-08-04 16:00:03 - INFO - ✅ Pyrus CRM API инициализирован
2024-08-04 16:00:04 - INFO - ✅ Green API WhatsApp инициализирован и авторизован
2024-08-04 16:00:05 - INFO - ✅ Telegram Bot запущен
2024-08-04 16:00:06 - INFO - 🔄 Начинаем проверку email каждые 60 секунд
```

### Тестирование функций

**1. Тест Telegram бота:**
- Найдите вашего бота в Telegram
- Отправьте `/start`
- Отправьте `/health` для проверки состояния

**2. Тест WhatsApp:**
- В чате с ботом отправьте: `/test_whatsapp +79001234567`
- Проверьте, пришло ли сообщение на указанный номер

**3. Тест обработки заявки:**
Отправьте боту тестовое сообщение:
```
Новая заявка № 123 со страницы sk.srubim.su/

Название формы: Application

Данные формы:
Телефон: +7 (900) 123-45-67
Какой дом или баню хотите построить?: Большую баню
Площадь строения: 10-50 м²
У вас есть земельный участок?: Да
В какой бюджет планируете уложиться?: До 500 000 руб
Куда отправить расчет стоимости?: WhatsApp
```

### Запуск как сервис

Если тестирование прошло успешно:

```bash
# Останавливаем тестовый режим (Ctrl+C)

# Запускаем как сервис
sudo systemctl start autoresponder-bot

# Проверяем статус
sudo systemctl status autoresponder-bot

# Включаем автозапуск
sudo systemctl enable autoresponder-bot
```

---

## 📊 Мониторинг и логи

### Команды для мониторинга

```bash
# Статус сервиса
sudo systemctl status autoresponder-bot

# Логи в реальном времени
sudo journalctl -u autoresponder-bot -f

# Последние 50 строк логов
sudo journalctl -u autoresponder-bot -n 50

# Логи с ошибками
sudo journalctl -u autoresponder-bot -p err

# Логи за последний час
sudo journalctl -u autoresponder-bot --since "1 hour ago"

# Логи файла приложения
tail -f /home/botuser/autoresponder-bot/bot.log
```

### Настройка ротации логов

```bash
# Создаем конфигурацию ротации
sudo nano /etc/logrotate.d/autoresponder-bot
```

```bash
/home/botuser/autoresponder-bot/bot.log {
    daily
    missingok
    rotate 30
    compress
    notifempty
    create 644 botuser botuser
    postrotate
        systemctl reload autoresponder-bot
    endscript
}
```

### Мониторинг производительности

```bash
# Использование ресурсов
htop

# Статистика процесса
ps aux | grep python

# Использование диска
df -h

# Использование памяти
free -h

# Сетевые соединения
netstat -tulpn | grep python
```

---

## 🚨 Troubleshooting

### Частые проблемы и решения

#### 1. Бот не запускается

**Проблема:** `ModuleNotFoundError: No module named 'telebot'`

**Решение:**
```bash
cd /home/botuser/autoresponder-bot
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. Ошибка аутентификации Telegram

**Проблема:** `Unauthorized: bot token is invalid`

**Решение:**
1. Проверьте токен в .env файле
2. Убедитесь, что токен получен от @BotFather
3. Проверьте отсутствие пробелов в токене

#### 3. WhatsApp не авторизован

**Проблема:** `Green API инстанс не авторизован`

**Решение:**
1. Войдите в личный кабинет Green API
2. Перейдите к своему инстансу  
3. Повторно отсканируйте QR-код
4. Проверьте статус: `/health` в боте

#### 4. Email не работает

**Проблема:** `Authentication failed`

**Решение для Gmail:**
```bash
# Проверка подключения
python3 -c "
import imaplib
try:
    imap = imaplib.IMAP4_SSL('imap.gmail.com')
    imap.login('your-email@gmail.com', 'your-app-password') 
    print('✅ Email подключение работает')
    imap.logout()
except Exception as e:
    print(f'❌ Ошибка: {e}')
"
```

1. Убедитесь, что включена 2FA
2. Используйте пароль приложения, не основной пароль
3. Проверьте настройки IMAP в Gmail

#### 5. Pyrus CRM ошибки

**Проблема:** `Ошибка аутентификации в Pyrus`

**Решение:**
1. Проверьте login и security_key в Pyrus
2. Убедитесь, что API доступ включен
3. Проверьте правильность Form ID

#### 6. Высокое использование памяти

**Решение:**
```bash
# Перезапуск сервиса
sudo systemctl restart autoresponder-bot

# Очистка логов
sudo journalctl --vacuum-time=7d

# Добавление swap если нужно
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Диагностические команды

```bash
# Полная диагностика системы
#!/bin/bash
echo "=== ДИАГНОСТИКА AUTORESPONDER BOT ==="

echo "1. Статус сервиса:"
sudo systemctl status autoresponder-bot --no-pager

echo -e "
2. Процессы Python:"
ps aux | grep python

echo -e "
3. Использование памяти:"
free -h

echo -e "
4. Использование диска:"
df -h

echo -e "
5. Последние логи (10 строк):"
sudo journalctl -u autoresponder-bot -n 10 --no-pager

echo -e "
6. Проверка портов:"
netstat -tulpn | grep python

echo -e "
7. Версия Python:"
python3 --version

echo -e "
8. Проверка .env файла:"
ls -la /home/botuser/autoresponder-bot/.env
```

---

## 📈 Масштабирование

### Для высоких нагрузок

#### 1. Оптимизация конфигурации

```env
# Уменьшаем интервал проверки email
CHECK_INTERVAL=30

# Включаем debug только при необходимости
DEBUG=false
```

#### 2. Использование Docker

```bash
# Сборка образа
docker build -t autoresponder-bot .

# Запуск контейнера
docker run -d   --name autoresponder-bot   --restart unless-stopped   --env-file .env   -v $(pwd)/logs:/app/logs   -v $(pwd)/data:/app/data   autoresponder-bot
```

#### 3. Настройка балансировки нагрузки

```nginx
# /etc/nginx/sites-available/autoresponder
upstream bot_servers {
    server 127.0.0.1:5000;
    server 127.0.0.1:5001;
}

server {
    listen 80;
    server_name bot.company.com;

    location /webhook {
        proxy_pass http://bot_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 4. Мониторинг с Prometheus

```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

---

## 🔒 Безопасность

### Настройка файрвола

```bash
# Установка UFW
sudo ufw --version || sudo apt install ufw

# Базовые правила
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Разрешаем SSH
sudo ufw allow ssh

# Разрешаем HTTP/HTTPS (если нужно)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Активируем файрвол
sudo ufw enable

# Проверяем статус
sudo ufw status
```

### Защита конфигурации

```bash
# Ограничиваем доступ к .env
chmod 600 .env
chown botuser:botuser .env

# Создаем бэкап конфигурации
cp .env .env.backup
chmod 600 .env.backup
```

### SSL сертификат (при необходимости)

```bash
# Установка Certbot
sudo snap install --classic certbot

# Получение сертификата
sudo certbot certonly --standalone -d your-domain.com

# Автообновление
sudo crontab -e
# Добавить: 0 12 * * * /usr/bin/certbot renew --quiet
```

---

## 📋 Чеклист перед продакшном

### ✅ Предварительная проверка

- [ ] Все API ключи получены и проверены
- [ ] .env файл заполнен и защищен
- [ ] Бот успешно запускается в тестовом режиме
- [ ] Тест отправки WhatsApp сообщений прошел
- [ ] Создание задач в Pyrus CRM работает
- [ ] Email мониторинг функционирует
- [ ] Логирование настроено
- [ ] Мониторинг ресурсов настроен

### ✅ Продакшн настройки

- [ ] DEBUG=false в .env
- [ ] Systemd сервис создан и активирован
- [ ] Автозапуск при перезагрузке включен
- [ ] Ротация логов настроена
- [ ] Файрвол настроен
- [ ] Бэкапы конфигурации созданы
- [ ] Мониторинг настроен

### ✅ Тестирование в продакшне

- [ ] Отправка тестовой заявки через все каналы
- [ ] Проверка создания задач в CRM
- [ ] Проверка отправки WhatsApp сообщений
- [ ] Мониторинг логов в течение часа
- [ ] Проверка работы после перезагрузки сервера

---

## 📞 Поддержка

### Контакты для получения помощи

- 🐛 **Баги и ошибки:** создайте issue в GitHub
- 💬 **Вопросы по настройке:** Telegram @support
- 📧 **Коммерческие вопросы:** support@company.com

### Полезные ссылки

- [Green API документация](https://green-api.com/docs/)
- [Pyrus API документация](https://pyrus.com/ru/help/api)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Python-telegram-bot документация](https://python-telegram-bot.readthedocs.io/)

---

## 📄 Приложения

### A. Примеры сообщений заявок

**Flexbe форма "Application":**
```
Новая заявка № 123 со страницы sk.srubim.su/

Название формы: Application

Данные формы:
Телефон: +7 (900) 123-45-67
Какой дом или баню хотите построить?: Большую баню
Площадь строения: 10-50 м²
У вас есть земельный участок?: Да
В какой бюджет планируете уложиться?: До 500 000 руб
Какие средства планируете использовать для покупки?: Собственные средства
Куда отправить расчет стоимости?: WhatsApp
Я соглашаюсь с условиями политики обработки персональных данных: Да
```

**Flexbe форма "Заявка":**
```
Новая заявка № 124 со страницы sk.srubim.su/contact

Название формы: Заявка

Данные формы:
Телефон: +7 (900) 987-65-43
Сообщение: Хочу построить дом из бруса
```

### B. Структура логов

```
2024-08-04 16:00:01,123 - autoresponder_bot - INFO - 🚀 Запуск бота автоответчика...
2024-08-04 16:00:02,456 - autoresponder_bot - INFO - ✅ Telegram Bot API инициализирован
2024-08-04 16:00:03,789 - autoresponder_bot - INFO - 📨 Получена заявка в Telegram от user123
2024-08-04 16:00:04,012 - autoresponder_bot - INFO - 📋 Распознанные данные заявки: {'phone': '+79001234567', 'object_type': 'bath', 'contact_method': 'whatsapp'}
2024-08-04 16:00:05,345 - autoresponder_bot - INFO - ✅ Создана задача в Pyrus CRM: 98765
2024-08-04 16:00:06,678 - autoresponder_bot - INFO - ✅ WhatsApp сообщение отправлено на +79001234567
2024-08-04 16:00:07,901 - autoresponder_bot - INFO - ✅ Успешно обработана заявка (3/3): {'phone': '+79001234567', 'crm_task_id': '98765'}
```

### C. Команды для быстрого управления

```bash
# Алиасы для удобства (добавить в ~/.bashrc)
alias bot-start='sudo systemctl start autoresponder-bot'
alias bot-stop='sudo systemctl stop autoresponder-bot'  
alias bot-restart='sudo systemctl restart autoresponder-bot'
alias bot-status='sudo systemctl status autoresponder-bot'
alias bot-logs='sudo journalctl -u autoresponder-bot -f'
alias bot-errors='sudo journalctl -u autoresponder-bot -p err'

# Скрипт быстрой диагностики
#!/bin/bash
# save as bot-health.sh
echo "🔍 Проверка состояния бота..."
sudo systemctl is-active autoresponder-bot && echo "✅ Сервис активен" || echo "❌ Сервис не активен"
pgrep -f autoresponder_bot.py > /dev/null && echo "✅ Процесс запущен" || echo "❌ Процесс не найден"
curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe" | grep -q '"ok":true' && echo "✅ Telegram API доступен" || echo "❌ Telegram API недоступен"
```

---

**Это руководство содержит всю необходимую информацию для успешного развертывания и эксплуатации бота автоответчика. При возникновении вопросов обращайтесь к разделу Troubleshooting или в службу поддержки.**

---

*Последнее обновление: 4 августа 2024*
*Версия документации: 1.0*
