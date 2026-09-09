# 🗡️ Dragon Quest Heroes: Torneko's Mystery Dungeon -Classic HD-
### 🇫🇷 Patch de Traduction Française Intégrale (PC / Steam)

[![Version](https://img.shields.io/badge/Version-v0.5--Beta-blue.svg)](https://github.com/Edsaje/French_Trad_Dragon_Quest_Heroes_Torneko-s_Mystery_Dungeon_-Classic-HD-/releases)
[![Statut](https://img.shields.io/badge/Statut-Work%20In%20Progress%20(WIP)-orange.svg)](https://github.com/Edsaje/French_Trad_Dragon_Quest_Heroes_Torneko-s_Mystery_Dungeon_-Classic-HD-)
[![Licence](https://img.shields.io/badge/Licence-Gratuit%20%2F%20Fan--Mod-green.svg)](LICENSE)
[![YouTube](https://img.shields.io/badge/YouTube-@Hibouxe-red.svg)](https://www.youtube.com/@Hibouxe)

Projet de **fan-traduction bénévole intégrale en français** pour le dungeon-crawler légendaire de Square Enix : ***Dragon Quest Heroes: Torneko's Mystery Dungeon -Classic HD-*** sur PC (Steam).

Le jeu officiel n'étant paru qu'en japonais et en anglais, ce patch permet à toute la communauté francophone de profiter pleinement du titre dans la langue de Molière, avec la terminologie officielle de la série *Dragon Quest* !

---

## 🦉 Suivez le projet sur YouTube : Hibouxe !

Pour suivre le développement de la traduction, découvrir des vidéos de gameplay, des guides complets sur le jeu et participer aux retours de la communauté :

👉 **Rejoignez la chaîne YouTube :** [**youtube.com/@Hibouxe**](https://www.youtube.com/@Hibouxe)

---

## 📊 État d'avancement du projet

| Élément | Progression | Statut |
| :--- | :---: | :--- |
| 🖥️ **Interface & Menus généraux** *(Écran-titre, options, commandes)* | **100%** | ✅ Terminé & Vérifié en jeu |
| 🗡️ **Base de données des 90 objets** *(Épées, boucliers, herbes, parchemins, baguettes)* | **100%** | ✅ Terminé & Vérifié en jeu |
| 📜 **Descriptions des objets & Guides d'astuces** | **0%** | ⏳ En cours d'écriture |
| ⚔️ **Journal de combat & Événements en donjon** | **0%** | ⏳ Prévu Étape 2 |
| 💬 **Scénario, Cinématiques & Dialogues PNJ** | **0%** | ⏳ Prévu Étape 3 |

---

## 📥 Téléchargement & Installation

### Option 1 : Installation automatique en 1-clic (Recommandé)
1. Téléchargez la dernière archive : [**TornekosMysteryDungeon-Windows_Patch_FR_v0.5_Beta.zip**](patch/TornekosMysteryDungeon-Windows_Patch_FR_v0.5_Beta.zip)
2. Décompressez l'archive sur votre ordinateur.
3. Lancez le fichier **`installer.bat`** (il détecte automatiquement votre jeu, sauvegarde vos fichiers originaux et installe le patch en 5 secondes).
4. Lancez le jeu via Steam en vous assurant que la langue est configurée sur **Anglais** dans les paramètres du jeu.

### Option 2 : Installation manuelle (30 secondes)
1. Téléchargez le fichier de patch `TornekosMysteryDungeon-Windows.pak` (situé dans le dossier `patch/`).
2. Ouvrez votre bibliothèque Steam, faites un clic droit sur le jeu > **Gérer** > **Parcourir les fichiers locaux**.
3. Allez dans le répertoire :
   ```
   TornekosMysteryDungeon / Content / Paks /
   ```
4. *(Recommandé)* Renommez le fichier existant `TornekosMysteryDungeon-Windows.pak` en `TornekosMysteryDungeon-Windows.pak.backup`.
5. Collez le fichier `TornekosMysteryDungeon-Windows.pak` téléchargé dans ce dossier.
6. Lancez le jeu avec la langue réglée sur **Anglais**. Bon jeu !

### Désinstallation
Pour revenir à la version anglaise ou japonaise officielle, supprimez simplement `TornekosMysteryDungeon-Windows.pak` et restaurez votre backup, ou faites :
*Steam > Clic droit sur le jeu > Propriétés > Fichiers installés > Vérifier l'intégrité des fichiers du jeu.*

---

## ☕ Soutenir le projet bénévole

Ce mod est et demeurera **100% gratuit** pour tous les joueurs.

La rétro-ingénierie du moteur Radec de Square Enix, le décodage des binaires propriétaires, l'adaptation de la police et la traduction demandant des dizaines d'heures de travail bénévole, si vous souhaitez offrir un café ou encourager les prochaines mises à jour :

👉 **Faire un don via PayPal :** [**Cliquez ici pour faire un don PayPal**](https://www.paypal.com/donate/?business=edsaje746@gmail.com&currency_code=EUR) *(ou versement direct à `edsaje746@gmail.com`)*

---

## 🛠️ Informations techniques (Pour les moddeurs)

Ce patch repose sur un pipeline de reverse-engineering conçu pour le moteur hybride Unreal Engine 5 / Radec :
- **Déchiffrement / Re-chiffrement AES-256-ECB** des index du conteneur PAK officiel V11 (`path_hash_seed: 0x6409933B`).
- **Décodeur / Encodeur binaire Square Enix Variant (`Gm::Variant`)** pour les tables de données Radec (`Content/Anya/Radec/`).
- **Gestionnaire d'encodage XOR dynamique** et compression zlib native.
- Tous les scripts Python du pipeline sont mis à disposition dans le dossier [`tools/`](tools/).

---

## 📜 Crédits & Remerciements
- **Traduction & Rétro-ingénierie :** Hibouxe
- **Univers & Jeu original :** Square Enix / Chunsoft / Dragon Quest
