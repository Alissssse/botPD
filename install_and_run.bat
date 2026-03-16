@echo off
echo Установка зависимостей...
python -m pip install python-telegram-bot==20.7 python-dotenv==1.0.0
echo.
echo Запуск бота...
python bot.py
pause


