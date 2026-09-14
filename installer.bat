@echo off
chcp 65001 >nul
title Patch Français v1.2.0 - Dragon Quest Torneko (Mod Patch)
color 0B

echo =======================================================================
echo    Dragon Quest Heroes: Torneko's Mystery Dungeon -Classic HD-
echo       Patch de Traduction Francaise v1.2.0 (Patch _P.pak) - Par Hibouxe
echo =======================================================================
echo.

set "BASE_PAK=TornekosMysteryDungeon-Windows.pak"
set "PATCH_PAK=TornekosMysteryDungeon-Windows_P.pak"
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
    if exist "%%~D\TornekosMysteryDungeon\Content\Paks\%BASE_PAK%" (
        set "FOUND_PATH=%%~D\TornekosMysteryDungeon\Content\Paks"
        goto :menu
    )
)

:ask_path
echo Impossible de detecter automatiquement le jeu.
echo.
set /p "USER_PATH=Veuillez glisser-deposer le dossier du jeu ou entrer le chemin : "
set "USER_PATH=%USER_PATH:"=%"

if exist "%USER_PATH%\TornekosMysteryDungeon\Content\Paks\%BASE_PAK%" (
    set "FOUND_PATH=%USER_PATH%\TornekosMysteryDungeon\Content\Paks"
    goto :menu
)
if exist "%USER_PATH%\Content\Paks\%BASE_PAK%" (
    set "FOUND_PATH=%USER_PATH%\Content\Paks"
    goto :menu
)
if exist "%USER_PATH%\%BASE_PAK%" (
    set "FOUND_PATH=%USER_PATH%"
    goto :menu
)

echo [ERREUR] Dossier invalide. Le fichier %BASE_PAK% est introuvable.
echo.
pause
goto :ask_path

:menu
echo Dossier du jeu detecte :
echo %FOUND_PATH%
echo.
echo Que souhaitez-vous faire ?
echo   [1] Installer le patch francais v1.2.0
echo   [2] Desinstaller le patch francais (revenir a la version officielle)
echo   [3] Quitter
echo.
set /p "CHOICE=Votre choix (1/2/3) : "

if "%CHOICE%"=="1" goto :install
if "%CHOICE%"=="2" goto :uninstall
if "%CHOICE%"=="3" exit /b 0
goto :menu

:install
:: Source du patch
if exist "%~dp0%PATCH_PAK%" (
    set "SRC_PAK=%~dp0%PATCH_PAK%"
) else if exist "%~dp0patch\%PATCH_PAK%" (
    set "SRC_PAK=%~dp0patch\%PATCH_PAK%"
) else (
    echo [ERREUR] Le fichier %PATCH_PAK% est introuvable.
    echo Assurez-vous d'avoir bien extrait tout le contenu de l'archive ZIP.
    pause
    exit /b 1
)

:: Si l'utilisateur avait une sauvegarde v1.1.0 et que son pak de base etait modifie, on restaure le pak d'origine
if exist "%FOUND_PATH%\%BASE_PAK%.original_backup" (
    echo Une sauvegarde de votre fichier original pre-v1.2 a ete detectee.
    echo Restauration du fichier de base propre...
    copy /y "%FOUND_PATH%\%BASE_PAK%.original_backup" "%FOUND_PATH%\%BASE_PAK%" >nul
)

echo.
echo Installation du fichier patch (%PATCH_PAK%)...
copy /y "%SRC_PAK%" "%FOUND_PATH%\%PATCH_PAK%" >nul

if %ERRORLEVEL% equ 0 (
    echo.
    echo =======================================================================
    echo   [SUCCES] Le patch francais v1.2.0 a ete installe avec succes !
    echo =======================================================================
    echo.
    echo Le patch fonctionne de maniere non-destructive sans toucher aux fichiers
    echo officiels du jeu.
    echo.
    echo IMPORTANT : Mettez la langue du jeu en ANGLAIS dans les options.
    echo Retrouvez mes guides et projets sur YouTube : @Hibouxe !
    echo.
) else (
    echo.
    echo [ERREUR] Echec lors de la copie. Verifiez que le jeu est ferme.
    echo.
)
pause
exit /b 0

:uninstall
if exist "%FOUND_PATH%\%PATCH_PAK%" (
    del /f /q "%FOUND_PATH%\%PATCH_PAK%"
    echo.
    echo [OK] Le fichier patch %PATCH_PAK% a ete supprime.
    echo Votre jeu est maintenant 100%% en version officielle d'origine !
) else (
    echo.
    echo Le patch francais n'etait pas installe dans ce dossier.
)
if exist "%FOUND_PATH%\%BASE_PAK%.original_backup" (
    copy /y "%FOUND_PATH%\%BASE_PAK%.original_backup" "%FOUND_PATH%\%BASE_PAK%" >nul
    echo Fichier de base restaure a partir de la sauvegarde d'origine.
)
echo.
pause
exit /b 0
