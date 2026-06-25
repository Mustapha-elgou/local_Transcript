@echo off
chcp 65001 >nul
cls
echo ========================================
echo 🎙️ TRANSCRIPTION AUDIO SYSTÈME V2
echo ========================================
echo.
echo 🚀 Démarrage du serveur...
echo.
echo 📌 Instructions:
echo   1. Le serveur va démarrer
echo   2. Ouvrez http://localhost:5000 dans votre navigateur
echo   3. Lancez de l'audio dans Chrome/Edge
echo   4. Cliquez sur "Démarrer" dans l'interface
echo.
echo ⚠️  N'oubliez pas d'activer "Stereo Mix" dans Windows!
echo.
echo ========================================
echo.

REM Lance le serveur
python server_v2.py

REM Si le serveur s'arrête avec une erreur
if errorlevel 1 (
    echo.
    echo ❌ Erreur de démarrage du serveur!
    echo.
    echo Vérifiez que:
    echo 1. Toutes les dépendances sont installées (lancez install.bat)
    echo 2. Le port 5000 n'est pas déjà utilisé
    echo 3. Les fichiers config.py et transcription_manager.py existent
    echo.
)

pause