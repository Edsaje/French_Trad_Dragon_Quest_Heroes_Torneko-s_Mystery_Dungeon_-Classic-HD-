# 🗡️ Dragon Quest Heroes: Torneko's Mystery Dungeon -Classic HD-
### 🇫🇷 Patch de Traduction Française Intégrale (PC / Steam / Steam Deck / Linux)

[![Version](https://img.shields.io/badge/Version-v1.2.0--Stable-brightgreen.svg)](https://github.com/Edsaje/French_Trad_Dragon_Quest_Heroes_Torneko-s_Mystery_Dungeon_-Classic-HD-/releases)
[![Statut](https://img.shields.io/badge/Statut-100%25%20Termin%C3%A9-success.svg)](https://github.com/Edsaje/French_Trad_Dragon_Quest_Heroes_Torneko-s_Mystery_Dungeon_-Classic-HD-)
[![Steam Deck](https://img.shields.io/badge/Steam%20Deck-Compatible%20100%25-success.svg)](https://github.com/Edsaje/French_Trad_Dragon_Quest_Heroes_Torneko-s_Mystery_Dungeon_-Classic-HD-)
[![Linux](https://img.shields.io/badge/Linux-Proton%20OK-brightgreen.svg)](https://github.com/Edsaje/French_Trad_Dragon_Quest_Heroes_Torneko-s_Mystery_Dungeon_-Classic-HD-)
[![Licence](https://img.shields.io/badge/Licence-Gratuit%20%2F%20Fan--Mod-green.svg)](LICENSE)
[![YouTube](https://img.shields.io/badge/YouTube-@Hibouxe-red.svg)](https://www.youtube.com/@Hibouxe)

Projet de **fan-traduction bénévole intégrale en français (100%)** pour le dungeon-crawler culte de Square Enix : ***Dragon Quest Heroes: Torneko's Mystery Dungeon -Classic HD-*** sur PC (Steam).

Le jeu officiel n'étant paru qu'en japonais et en anglais, ce patch permet à toute la communauté francophone de vivre l'aventure de Torneko entièrement en français, avec la nomenclature et le charme officiel de l'univers *Dragon Quest* !

---

## 🦉 Suivez le projet sur YouTube : Hibouxe !

Pour suivre le développement de la traduction, découvrir des vidéos de gameplay, des guides complets sur le jeu et participer aux retours de la communauté :

👉 **Rejoignez la chaîne YouTube :** [**youtube.com/@Hibouxe**](https://www.youtube.com/@Hibouxe)

---

## 📊 État d'avancement du projet (100% TERMINÉ)

| Élément | Progression | Statut |
| :--- | :---: | :--- |
| 🖥️ **Interface & Menus généraux** *(Écran-titre, options, commandes, HUD)* | **100%** | ✅ Terminé & Vérifié en jeu |
| 🗡️ **Objets & Équipements identifiés** *(Armes, boucliers, herbes, etc.)* | **100%** | ✅ Terminé & Vérifié en jeu |
| 🔮 **Objets non identifiés** *(Anneaux minéraux, herbes, parchemins, baguettes)* | **100%** | ✅ Terminé & Vérifié en jeu |
| 📜 **Descriptions détaillées des 160 objets** *(Effets, statistiques, astuces)* | **100%** | ✅ Terminé & Vérifié en jeu |
| 👾 **Bestiaire complet & Monstres** *(Nomenclature officielle Dragon Quest FR)* | **100%** | ✅ Terminé & Vérifié en jeu |
| ⚔️ **Journal de combat & Événements en donjon** *(294 messages et pièges)* | **100%** | ✅ Terminé & Vérifié en jeu |
| 💬 **Scénario, Histoire & Dialogues PNJ** *(544 répliques de village et donjon)* | **100%** | ✅ Terminé & Vérifié en jeu |
| 🏆 **Didacticiels complets & Registre des exploits** | **100%** | ✅ Terminé & Vérifié en jeu |

---

## 📝 Journal des modifications (Changelog)

### Version 1.2.0 (Outils autonomes, Mapping EN/JP & Packaging stable)
- **Module autonome `tools/radec_codec.py` :** Outil tout-en-un avec CLI pour décompresser, sérialiser (Gm::Variant), chiffrer et encoder (codec 6-bit) pour toute la communauté.
- **Cartographie complète des File ID EN ⟷ JP :** Documentation intégrale des 14 tables de données (voir `guides/RADEC_FILE_ID_MAP_EN_JP.md`).
- **Installateur v1.2.0 avec sauvegarde automatique :** `installer.bat` gère l'installation et la restauration de votre fichier d'origine en 1 clic.

### Version 1.1.0 (Correctif majeur & Finalisation lore)
- **Correction du freeze / softlock critique :** Résolution d'un dysfonctionnement binaire de balise dans les scènes d'agrandissement de la boutique.
- **Rétablissement du calcul de l'or :** Correction de l'évaluation des gains d'or sur les objets ramenés en boutique.
- **Harmonisation complète du Bestiaire :** Révision intégrale des 34 monstres selon la nomenclature officielle de Square Enix (*Ornithox, Prestidigitatueur, Maransac, Rochexplosif, Géant, Feutocopieur, Goule...*).
- **100% des dialogues fonctionnels en français :** L'ensemble des 544 répliques du jeu est désormais parfaitement stable.

---

## 📥 Téléchargement & Installation

### Option 1 : Installation automatique en 1-clic (Recommandé)
1. Téléchargez la dernière archive : [**TornekosMysteryDungeon-Windows_Patch_FR_v1.2.0.zip**](patch/TornekosMysteryDungeon-Windows_Patch_FR_v1.2.0.zip)
2. Décompressez l'archive sur votre ordinateur.
3. Lancez **`installer.bat`** et tapez `[1]` (le script détecte automatiquement votre jeu, sauvegarde vos fichiers originaux et installe le patch en 3 secondes).
4. Lancez le jeu via Steam en vous assurant que la langue est configurée sur **Anglais** dans les paramètres du jeu (le français s'affichera directement).

### Option 2 : Installation manuelle (30 secondes)
1. Téléchargez l'archive [**TornekosMysteryDungeon-Windows_Patch_FR_v1.2.0.zip**](patch/TornekosMysteryDungeon-Windows_Patch_FR_v1.2.0.zip).
2. Ouvrez votre bibliothèque Steam, faites un clic droit sur le jeu > **Gérer** > **Parcourir les fichiers locaux**.
3. Allez dans le répertoire :
   ```
   TornekosMysteryDungeon / Content / Paks /
   ```
4. *(Recommandé)* Renommez le fichier existant `TornekosMysteryDungeon-Windows.pak` en `TornekosMysteryDungeon-Windows.pak.backup`.
5. Copiez le fichier `TornekosMysteryDungeon-Windows.pak` extrait de l'archive dans ce dossier.
6. Lancez le jeu avec la langue réglée sur **Anglais**. Bon jeu !

### 🎮 Installation sur Steam Deck & Linux (SteamOS / Proton)
Le patch est **100% compatible Steam Deck et Linux** !
1. Sur Steam Deck, passez en **Mode Bureau** (*Bouton STEAM > Marche/Arrêt > Basculer vers le bureau*).
2. Téléchargez l'archive du patch et extrayez le fichier `TornekosMysteryDungeon-Windows.pak`.
3. Rendez-vous dans :
   ```
   TornekosMysteryDungeon / Content / Paks /
   ```
4. Remplacez le fichier `TornekosMysteryDungeon-Windows.pak`.
5. Repassez en **Mode Jeu** : Torneko se lance directement en français !

### Désinstallation
- Si vous avez utilisé `installer.bat`, lancez-le simplement et tapez `[2]` pour restaurer instantanément votre sauvegarde officielle.
- Ou via Steam : *Clic droit sur le jeu > Propriétés > Fichiers installés > Vérifier l'intégrité des fichiers du jeu.*

---

## ☕ Soutenir le projet bénévole

Ce mod est et demeurera **100% gratuit** pour tous les joueurs.

La rétro-ingénierie du moteur Radec de Square Enix, le décodage des binaires propriétaires, l'adaptation de la police et la traduction intégrale demandant de très nombreuses heures de travail bénévole, si vous souhaitez offrir un café ou encourager le travail réalisé :

👉 **Faire un don via PayPal :** [**paypal.me/Hibouxe**](https://paypal.me/Hibouxe) *(ou versement direct à `edsaje746@gmail.com`)*

---

## 🛠️ Informations techniques (Pour les moddeurs)

Ce patch repose sur un pipeline de reverse-engineering complet pour le moteur hybride Unreal Engine 5 / Radec :
- **Déchiffrement / Re-chiffrement AES-256-ECB** des index du conteneur PAK officiel V11 (`path_hash_seed: 0x6409933B`).
- **Outil autonome [`tools/radec_codec.py`](tools/radec_codec.py) :**
  - Classes `VariantReader` et `VariantWriter` pour parser et sérialiser l'AST binaire `Gm::Variant`.
  - Fonctions `unscramble` / `scramble` (cipher par File ID 32-bit).
  - Fonctions `decompress_radec` / `compress_and_scramble` (Zlib + Cipher).
  - Codec 6-bit `decode_radec` / `encode_radec` (chaînes préfixées par `|`).
  - Fonction `clean_retro_text` pour l'adaptation à la police rétro 1-octet sans glitch.
- **Guide complet pour les moddeurs internationaux :** Voir [`guides/STEAM_GUIDE_MODDING_TRANSLATION_EN.md`](guides/STEAM_GUIDE_MODDING_TRANSLATION_EN.md).
- Tous les scripts Python d'assemblage et de packaging sont disponibles dans le dossier [`tools/`](tools/).

---

## 📜 Crédits & Remerciements
- **Traduction & Rétro-ingénierie :** Hibouxe
- **Univers & Jeu original :** Square Enix / Chunsoft / Dragon Quest
