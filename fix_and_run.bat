@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo Обновление библиотеки для Python 3.13
echo ========================================
echo.
python -m pip install --upgrade python-telegram-bot python-dotenv==1.0.0
echo.
echo ========================================
echo Запуск бота...
echo ========================================
echo.
python bot.py
pause


