@echo off
chcp 65001 >nul
echo ========================================
echo Установка зависимостей для бота
echo ========================================
echo.
python -m pip install --upgrade python-telegram-bot python-dotenv==1.0.0
echo.
echo ========================================
echo Установка завершена!
echo ========================================
pause

