@echo off
chcp 65001 >nul
title Installation du Patch Francais - Dragon Quest Torneko
color 0B

echo =======================================================================
echo    Dragon Quest Heroes: Torneko's Mystery Dungeon -Classic HD-
echo             Patch de Traduction Francaise - Par Hibouxe
echo =======================================================================
echo.

set "PAK_NAME=TornekosMysteryDungeon-Windows.pak"
set "FOUND_PATH="

:: Detection automatique des dossiers Steam courants
for %%D in (
    "E:\SteamLibrary\steamapps\common\TornekosMysteryDungeon"
    "D:\SteamLibrary\steamapps\common\TornekosMysteryDungeon"
    "C:\Program Files (x86)\Steam\steamapps\common\TornekosMysteryDungeon"
    "C:\SteamLibrary\steamapps\common\TornekosMysteryDungeon"
    "F:\SteamLibrary\steamapps\common\TornekosMysteryDungeon"
    "G:\SteamLibrary\steamapps\common\TornekosMysteryDungeon"
) do (
    if exist "%%~D\TornekosMysteryDungeon\Content\Paks\%PAK_NAME%" (
        set "FOUND_PATH=%%~D\TornekosMysteryDungeon\Content\Paks"
        goto :found
    )
)

:ask_path
echo Impossible de detecter automatiquement le jeu.
echo.
set /p "USER_PATH=Veuillez glisser-deposer le dossier du jeu ou entrer le chemin : "
set "USER_PATH=%USER_PATH:"=%"

if exist "%USER_PATH%\TornekosMysteryDungeon\Content\Paks\%PAK_NAME%" (
    set "FOUND_PATH=%USER_PATH%\TornekosMysteryDungeon\Content\Paks"
    goto :found
)
if exist "%USER_PATH%\Content\Paks\%PAK_NAME%" (
    set "FOUND_PATH=%USER_PATH%\Content\Paks"
    goto :found
)
if exist "%USER_PATH%\%PAK_NAME%" (
    set "FOUND_PATH=%USER_PATH%"
    goto :found
)

echo [ERREUR] Chemin invalide. Le fichier %PAK_NAME% est introuvable.
echo.
pause
goto :ask_path

:found
echo Dossier du jeu detecte :
echo %FOUND_PATH%
echo.

:: Verifier la presence du nouveau pak
if not exist "%~dp0%PAK_NAME%" (
    if exist "%~dp0patch\%PAK_NAME%" (
        set "SRC_PAK=%~dp0patch\%PAK_NAME%"
    ) else (
        echo [ERREUR] Le fichier %PAK_NAME% a installer est introuvable dans ce dossier.
        echo Assurez-vous d'avoir extrait tout le contenu de l'archive ZIP.
        echo.
        pause
        exit /b 1
    )
) else (
    set "SRC_PAK=%~dp0%PAK_NAME%"
)

:: Sauvegarde automatique si pas encore faite
if not exist "%FOUND_PATH%\%PAK_NAME%.original_backup" (
    echo Creation d'une sauvegarde de secours de votre jeu d'origine...
    copy "%FOUND_PATH%\%PAK_NAME%" "%FOUND_PATH%\%PAK_NAME%.original_backup" >nul
    echo Sauvegarde creee : %PAK_NAME%.original_backup
)

echo.
echo Copie du patch francais en cours...
copy /y "%SRC_PAK%" "%FOUND_PATH%\%PAK_NAME%" >nul

if %ERRORLEVEL% equ 0 (
    echo.
    echo =======================================================================
    echo   [SUCCES] Le patch francais a ete installe avec succes !
    echo =======================================================================
    echo.
    echo Pensez a mettre la langue du jeu en ANGLAIS dans les options du jeu.
    echo Retrouvez-moi sur YouTube : @Hibouxe !
    echo.
) else (
    echo.
    echo [ERREUR] Echec lors de la copie. Verifiez que le jeu n'est pas lance.
    echo.
)

pause
