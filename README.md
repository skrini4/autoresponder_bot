# Бот Автоответчик для Строительной Компании "Срубим"

Автоматический бот для обработки заявок из различных источников:
- 📧 Email
- 📱 Telegram 
- 🌐 Flexbe (веб-сайт)

## 🚀 Возможности

- ✅ Автоматическая обработка заявок из всех источников
- ✅ Определение типа объекта (дом/баня)
- ✅ Выбор способа связи (WhatsApp/Telegram)
- ✅ Персонализированные ответы
- ✅ Фильтрация заявок (пропуск "озвучить по телефону")
- ✅ Отправка сообщений с личных аккаунтов
- ✅ Логирование всех операций

## 📋 Требования

- Python 3.8+
- Ubuntu/Debian сервер (рекомендуется)
- Telegram Bot Token
- API ключи для WhatsApp
- Email аккаунт с IMAP

## 🛠 Установка на VPS

### Быстрая установка
```bash
# Загрузите архив на сервер
wget https://your-server.com/autoresponder-bot.zip
unzip autoresponder-bot.zip
cd autoresponder-bot

# Запустите автоматическую установку
chmod +x install.sh
./install.sh
```

### Ручная установка

1. **Подготовка системы:**
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv git -y
```

2. **Создание проекта:**
```bash
git clone <repository-url> autoresponder-bot
cd autoresponder-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Настройка конфигурации:**
```bash
cp config_example.env .env
nano .env
```

4. **Заполните .env файл:**
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
EMAIL_IMAP_SERVER=imap.gmail.com
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
WHATSAPP_API_URL=https://api.green-api.com/...
WHATSAPP_TOKEN=your_whatsapp_token
```

## 🔧 Настройка сервисов

### Telegram Bot
1. Найдите @BotFather в Telegram
2. Создайте нового бота: `/newbot`
3. Получите токен и добавьте в .env

### WhatsApp API
Рекомендуемые сервисы:
- [Green API](https://green-api.com) - стабильный и надежный
- [Whapi.Cloud](https://whapi.cloud) - современный интерфейс
- [Chat API](https://chat-api.com) - проверенное решение

### Email настройка
Для Gmail:
1. Включите 2FA
2. Создайте пароль приложения
3. Используйте imap.gmail.com

## 🎯 Запуск

### Разовый запуск (для тестирования)
```bash
source venv/bin/activate
python autoresponder_bot.py
```

### Запуск как сервис
```bash
sudo systemctl start autoresponder-bot
sudo systemctl enable autoresponder-bot
```

### Управление сервисом
```bash
# Статус
sudo systemctl status autoresponder-bot

# Перезапуск
sudo systemctl restart autoresponder-bot

# Остановка
sudo systemctl stop autoresponder-bot

# Логи
sudo journalctl -u autoresponder-bot -f
```

## 📊 Мониторинг

### Проверка логов
```bash
# Последние 50 строк
sudo journalctl -u autoresponder-bot -n 50

# В реальном времени
sudo journalctl -u autoresponder-bot -f

# Ошибки
sudo journalctl -u autoresponder-bot -p err
```

## 🔒 Безопасность

### Настройка файрвола
```bash
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### Защита конфигурации
```bash
chmod 600 .env
chown $USER:$USER .env
```

## 🚨 Важные замечания

⚠️ **Отправка с личных аккаунтов WhatsApp/Telegram может привести к блокировке!**

Рекомендации:
- Используйте официальные Business API
- Не превышайте лимиты отправки
- Тестируйте на небольших объемах
- Следите за обновлениями политик мессенджеров

## 🆘 Поддержка

### Частые проблемы

**Бот не отвечает:**
- Проверьте токены в .env
- Убедитесь что сервис запущен
- Посмотрите логи

**Ошибки с email:**
- Проверьте настройки IMAP
- Убедитесь в правильности пароля приложения
- Проверьте подключение к интернету

**Проблемы с WhatsApp:**
- Убедитесь что API сервис работает
- Проверьте формат номеров телефонов
- Проверьте лимиты API

### Логи и отладка
```bash
# Включить подробные логи
export DEBUG=1

# Проверить соединение
ping api.telegram.org
ping imap.gmail.com
```

## 📈 Масштабирование

### Для больших нагрузок:
- Используйте Redis для очередей
- Настройте балансировку нагрузки
- Добавьте мониторинг (Prometheus + Grafana)
- Настройте бэкапы конфигурации

### Рекомендуемые характеристики VPS:
- **Минимум:** 1 CPU, 1GB RAM, 10GB SSD
- **Рекомендуемо:** 2 CPU, 2GB RAM, 20GB SSD
- **Для больших объемов:** 4 CPU, 4GB RAM, 50GB SSD

## 📄 Лицензия

MIT License - используйте свободно для коммерческих проектов.

## 🤝 Поддержка проекта

Если проект помог вашему бизнесу, будем рады обратной связи!
