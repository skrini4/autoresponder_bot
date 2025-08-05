#!/bin/bash
# Скрипт установки бота автоответчика

echo "🚀 Установка бота автоответчика..."

# Обновляем систему
sudo apt update && sudo apt upgrade -y

# Устанавливаем Python 3 и pip
sudo apt install python3 python3-pip python3-venv -y

# Создаем виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements.txt

# Создаем systemd сервис
sudo tee /etc/systemd/system/autoresponder-bot.service > /dev/null <<EOF
[Unit]
Description=AutoResponder Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python autoresponder_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Перезагружаем systemd
sudo systemctl daemon-reload

echo "✅ Установка завершена!"
echo ""
echo "📝 Что нужно сделать дальше:"
echo "1. Скопируйте config_example.env в .env: cp config_example.env .env"
echo "2. Отредактируйте .env файл с вашими токенами и настройками"
echo "3. Запустите бота: sudo systemctl start autoresponder-bot"
echo "4. Включите автозапуск: sudo systemctl enable autoresponder-bot"
echo ""
echo "🔍 Проверить статус: sudo systemctl status autoresponder-bot"
echo "📋 Посмотреть логи: sudo journalctl -u autoresponder-bot -f"
