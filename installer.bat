@echo off
chcp 65001 >nul
title Installation du Patch Francais - Dragon Quest Torneko
color 0B

echo =======================================================================
echo    Dragon Quest Heroes: Torneko's Mystery Dungeon -Classic HD-
echo        Patch de Traduction Francaise Integrale (100%) - Par Hibouxe
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
        goto :menu
    )
)

:ask_path
echo Impossible de detecter automatiquement le jeu.
echo.
set /p "USER_PATH=Veuillez glisser-deposer le dossier du jeu ou entrer le chemin : "
set "USER_PATH=%USER_PATH:"=%"

if exist "%USER_PATH%\TornekosMysteryDungeon\Content\Paks\%PAK_NAME%" (
    set "FOUND_PATH=%USER_PATH%\TornekosMysteryDungeon\Content\Paks"
    goto :menu
)
if exist "%USER_PATH%\Content\Paks\%PAK_NAME%" (
    set "FOUND_PATH=%USER_PATH%\Content\Paks"
    goto :menu
)
if exist "%USER_PATH%\%PAK_NAME%" (
    set "FOUND_PATH=%USER_PATH%"
    goto :menu
)

echo [ERREUR] Dossier invalide. Le fichier %PAK_NAME% est introuvable.
echo.
pause
goto :ask_path

:menu
echo Dossier du jeu detecte :
echo %FOUND_PATH%
echo.
echo Que souhaitez-vous faire ?
echo   [1] Installer le patch francais (Sauvegarde automatique incluse)
echo   [2] Desinstaller le patch (Restaurer la version officielle d'origine)
echo   [3] Quitter
echo.
set /p "CHOICE=Votre choix (1/2/3) : "

if "%CHOICE%"=="1" goto :install
if "%CHOICE%"=="2" goto :uninstall
if "%CHOICE%"=="3" exit /b 0
goto :menu

:install
if exist "%~dp0%PAK_NAME%" (
    set "SRC_PAK=%~dp0%PAK_NAME%"
) else if exist "%~dp0patch\%PAK_NAME%" (
    set "SRC_PAK=%~dp0patch\%PAK_NAME%"
) else (
    echo [ERREUR] Le fichier %PAK_NAME% est introuvable dans ce dossier.
    echo Assurez-vous d'avoir bien extrait tout le contenu de l'archive ZIP.
    pause
    exit /b 1
)

:: Sauvegarde automatique du fichier d'origine avant tout ecrasement
if not exist "%FOUND_PATH%\%PAK_NAME%.original_backup" (
    echo Creation d'une sauvegarde de secours de votre fichier d'origine...
    copy "%FOUND_PATH%\%PAK_NAME%" "%FOUND_PATH%\%PAK_NAME%.original_backup" >nul
    echo [OK] Sauvegarde creee : %PAK_NAME%.original_backup
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
if exist "%FOUND_PATH%\%PAK_NAME%.original_backup" (
    copy /y "%FOUND_PATH%\%PAK_NAME%.original_backup" "%FOUND_PATH%\%PAK_NAME%" >nul
    echo.
    echo [OK] Fichier d'origine restaure avec succes !
    echo Votre jeu est maintenant 100%% en version officielle.
) else (
    echo.
    echo [INFO] Aucune sauvegarde locale trouvee.
    echo Pour restaurer les fichiers officiels via Steam :
    echo Clic droit sur le jeu > Proprietes > Fichiers installes > Verifier l'integrite.
)
echo.
pause
exit /b 0
