@echo off
chcp 65001 >nul
title Installation du Patch Francais - Dragon Quest Torneko
color 0B

echo =======================================================================
echo    Dragon Quest Heroes: Torneko's Mystery Dungeon -Classic HD-
echo       Patch de Traduction Francaise v1.2.0 - Par Hibouxe
echo =======================================================================
echo.

set "PAK_FILE=HibouxeDonjonMystere_FR_P.pak"
set "UTOC_FILE=HibouxeDonjonMystere_FR_P.utoc"
set "UCAS_FILE=HibouxeDonjonMystere_FR_P.ucas"
set "FOUND_PATH="

:: Detection automatique des dossiers Steam courants
for %%D in (
    "C:\Program Files (x86)\Steam\steamapps\common\TornekosMysteryDungeon"
    "D:\SteamLibrary\steamapps\common\TornekosMysteryDungeon"
    "E:\SteamLibrary\steamapps\common\TornekosMysteryDungeon"
    "F:\SteamLibrary\steamapps\common\TornekosMysteryDungeon"
    "G:\SteamLibrary\steamapps\common\TornekosMysteryDungeon"
) do (
    if exist "%%~D\TornekosMysteryDungeon\Content\Paks\TornekosMysteryDungeon-Windows.pak" (
        set "FOUND_PATH=%%~D\TornekosMysteryDungeon\Content\Paks"
        goto :menu
    )
)

:ask_path
echo Impossible de detecter automatiquement le jeu Torneko.
echo.
set /p "USER_PATH=Veuillez glisser-deposer le dossier du jeu ou entrer le chemin : "
set "USER_PATH=%USER_PATH:"=%"

if exist "%USER_PATH%\TornekosMysteryDungeon\Content\Paks\TornekosMysteryDungeon-Windows.pak" (
    set "FOUND_PATH=%USER_PATH%\TornekosMysteryDungeon\Content\Paks"
    goto :menu
)
if exist "%USER_PATH%\Content\Paks\TornekosMysteryDungeon-Windows.pak" (
    set "FOUND_PATH=%USER_PATH%\Content\Paks"
    goto :menu
)
if exist "%USER_PATH%\TornekosMysteryDungeon-Windows.pak" (
    set "FOUND_PATH=%USER_PATH%"
    goto :menu
)

echo [ERREUR] Dossier invalide. Le fichier TornekosMysteryDungeon-Windows.pak est introuvable.
echo.
pause
goto :ask_path

:menu
cls
echo =======================================================================
echo    Dragon Quest Heroes: Torneko's Mystery Dungeon -Classic HD-
echo       Patch de Traduction Francaise v1.2.0 - Par Hibouxe
echo =======================================================================
echo.
echo Dossier du jeu detecte :
echo %FOUND_PATH%
echo.
echo Que souhaitez-vous faire ?
echo   [1] Installer le patch francais (Non-destructif, conserve vos fichiers)
echo   [2] Desinstaller le patch francais
echo   [3] Quitter
echo.
set /p "CHOICE=Votre choix (1/2/3) : "

if "%CHOICE%"=="1" goto :install
if "%CHOICE%"=="2" goto :uninstall
if "%CHOICE%"=="3" exit /b 0
goto :menu

:install
if not exist "%~dp0%PAK_FILE%" (
    echo [ERREUR] Le fichier %PAK_FILE% est introuvable dans ce dossier.
    echo Assurez-vous d'avoir bien extrait tous les fichiers de l'archive ZIP.
    pause
    exit /b 1
)

echo.
echo Copie des fichiers patch en cours...
copy /y "%~dp0%PAK_FILE%" "%FOUND_PATH%\%PAK_FILE%" >nul
copy /y "%~dp0%UTOC_FILE%" "%FOUND_PATH%\%UTOC_FILE%" >nul
copy /y "%~dp0%UCAS_FILE%" "%FOUND_PATH%\%UCAS_FILE%" >nul

if %ERRORLEVEL% equ 0 (
    echo.
    echo =======================================================================
    echo   [SUCCES] Le patch francais v1.2.0 a ete installe avec succes !
    echo =======================================================================
    echo.
    echo Ce patch est 100%% non-destructif : votre fichier officiel original
    echo TornekosMysteryDungeon-Windows.pak est reste totalement intact.
    echo.
    echo Pensez a mettre la langue du jeu en ANGLAIS dans les options du jeu.
    echo Retrouvez mes guides et projets sur YouTube : @Hibouxe !
    echo.
) else (
    echo [ERREUR] Impossible de copier les fichiers. Essayez en mode administrateur.
)
pause
exit /b 0

:uninstall
echo.
echo Suppression des fichiers patch...
if exist "%FOUND_PATH%\%PAK_FILE%" del /f /q "%FOUND_PATH%\%PAK_FILE%"
if exist "%FOUND_PATH%\%UTOC_FILE%" del /f /q "%FOUND_PATH%\%UTOC_FILE%"
if exist "%FOUND_PATH%\%UCAS_FILE%" del /f /q "%FOUND_PATH%\%UCAS_FILE%"

:: Si l'utilisateur avait une ancienne sauvegarde de pak v1.1.0, on la restaure
if exist "%FOUND_PATH%\TornekosMysteryDungeon-Windows.pak.original_backup" (
    copy /y "%FOUND_PATH%\TornekosMysteryDungeon-Windows.pak.original_backup" "%FOUND_PATH%\TornekosMysteryDungeon-Windows.pak" >nul
    del /f /q "%FOUND_PATH%\TornekosMysteryDungeon-Windows.pak.original_backup"
    echo Fichier original pre-v1.2 restaure.
)

echo.
echo [OK] Le patch francais a ete retire.
echo Votre jeu est maintenant a 100%% en version officielle d'origine !
echo.
pause
exit /b 0
