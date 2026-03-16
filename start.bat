@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo Запуск бота Simple Physics
echo ========================================
echo.
echo Проверка зависимостей...
python -c "import telegram" 2>nul
if errorlevel 1 (
    echo Установка зависимостей...
    python -m pip install --upgrade python-telegram-bot python-dotenv==1.0.0
    if errorlevel 1 (
        echo ОШИБКА: Не удалось установить зависимости!
        pause
        exit /b 1
    )
)
echo.
echo Запуск бота...
echo.
python bot.py
if errorlevel 1 (
    echo.
    echo ОШИБКА: Бот завершился с ошибкой!
    pause
)
pause
