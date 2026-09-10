import os
import json
import struct
import zlib
import subprocess
import unicodedata

SCRATCH_DIR = r"C:\Users\quent\.gemini\antigravity-cli\brain\45f9af8b-81a5-42de-9c01-542f477f783b\scratch"
DECOMP_DIR = os.path.join(SCRATCH_DIR, "radec_decompressed")
MOD_STAGING = os.path.join(SCRATCH_DIR, "mod_staging")
REPAK_EXE = os.path.join(SCRATCH_DIR, "repak.exe")
GAME_PAKS_DIR = r"E:\SteamLibrary\steamapps\common\TornekosMysteryDungeon\TornekosMysteryDungeon\Content\Paks"

def clean_retro_text(s: str) -> str:
    """Normalize text to clean ASCII so that the game engine's utf8len and
    the 1-byte enSGOZ font atlas render every character without blanks or bugs."""
    has_var_tag = ('\x02)\x03\xeb\x0b\x03' in s)
    replacements = {
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'É': 'E', 'È': 'E', 'Ê': 'E', 'Ë': 'E',
        'à': 'a', 'â': 'a', 'ä': 'a',
        'À': 'A', 'Â': 'A', 'Ä': 'A',
        'ç': 'c', 'Ç': 'C',
        'î': 'i', 'ï': 'i',
        'Î': 'I', 'Ï': 'I',
        'ô': 'o', 'ö': 'o',
        'Ô': 'O', 'Ö': 'O',
        'ù': 'u', 'û': 'u', 'ü': 'u',
        'Ù': 'U', 'Û': 'U', 'Ü': 'U',
        '’': "'", '«': '"', '»': '"', '–': '-', '—': '-'
    }
    for k, v in replacements.items():
        s = s.replace(k, v)
    if has_var_tag:
        s = s.replace('\x02)\x03e\x0b\x03', '\x02)\x03\xeb\x0b\x03')
    return s

class VariantReader:
    def __init__(self, data):
        self.data = data
        self.pos = 0

    def read_byte(self):
        b = self.data[self.pos]
        self.pos += 1
        return b

    def read_count(self):
        b0 = self.read_byte()
        if b0 & 0x80:
            b1 = self.read_byte()
            return ((b1 << 7) | (b0 & 0x7F))
        return b0

    def read_str(self):
        length = self.read_count()
        s = self.data[self.pos : self.pos + length].decode('utf-8', errors='replace')
        self.pos += length
        return s

    def parse(self):
        t = self.read_byte()
        if t == 0: # Map
            count = self.read_count()
            return ('map', [(self.read_str(), self.parse()) for _ in range(count)])
        elif t == 1: # List
            count = self.read_count()
            return ('list', [self.parse() for _ in range(count)])
        elif t == 3: # Int
            b0 = self.read_byte()
            if b0 & 0x80:
                b1 = self.read_byte()
                return ('int', ((b1 << 7) | (b0 & 0x7F)))
            return ('int', b0)
        elif t == 8: # String
            return ('str', self.read_str())
        else:
            raise ValueError(f"Unknown variant type {t} at {hex(self.pos)}")

class VariantWriter:
    def __init__(self):
        self.buf = bytearray()

    def write_byte(self, b):
        self.buf.append(b & 0xFF)

    def write_count(self, n):
        if n >= 0x80:
            self.write_byte((n & 0x7F) | 0x80)
            self.write_byte((n >> 7) & 0xFF)
        else:
            self.write_byte(n)

    def write_str(self, s):
        raw = s.encode('utf-8')
        self.write_count(len(raw))
        self.buf.extend(raw)

    def write(self, val):
        t, data = val
        if t == 'map':
            self.write_byte(0)
            self.write_count(len(data))
            for k, v in data:
                self.write_str(k)
                self.write(v)
        elif t == 'list':
            self.write_byte(1)
            self.write_count(len(data))
            for item in data:
                self.write(item)
        elif t == 'int':
            self.write_byte(3)
            self.write_count(data)
        elif t == 'str':
            self.write_byte(8)
            self.write_str(data)

def scramble(data: bytes, key: int) -> bytes:
    buf = bytearray(data)
    esi = len(buf) & 0xFFFFFFFC
    ebx = (~key) & 0xFFFFFFFF
    if ebx != 0xFFFFFFFF:
        ebx_signed = ebx if ebx < 0x80000000 else ebx - 0x100000000
        eax = (ebx_signed >> 2) & 0x3F
        eax = (eax + 0x200) & 0xFFFFFFFC
        if esi > eax:
            esi = eax
    num_words = esi >> 2
    edi = 0
    for i in range(num_words):
        val = struct.unpack('<I', buf[i*4 : (i+1)*4])[0]
        ebx = (ebx ^ val) & 0xFFFFFFFF
        buf[i*4 : (i+1)*4] = struct.pack('<I', ebx)
        ecx = ebx & 3
        ebx = ((ebx << ecx) + edi) & 0xFFFFFFFF
        edi += 1
    return bytes(buf)

def compress_and_scramble(uncompressed_data: bytes, key: int) -> bytes:
    comp = zlib.compress(uncompressed_data, level=9)
    payload = struct.pack('<I', len(uncompressed_data)) + comp
    return scramble(payload, key)

# Calibrated UI translations: compact, elegant, fitting the retro layout boxes
FRENCH_UI = {
    "ui_yes": "Oui",
    "ui_no": "Non",
    "ui_dungeon_0": "Petit Donjon",
    "ui_dungeon_1": "Donjon Mystere",
    "ui_dungeon_2": "Grand Donjon",
    "ui_dungeon_3": "Sans Fin",
    "ui_dungeon_0s": "Petit Donjon",
    "ui_dungeon_1s": "Donjon",
    "ui_dungeon_2s": "Grand Donjon",
    "ui_dungeon_3s": "Sans Fin",
    "ui_main_cmd_0": "Objets",
    "ui_main_cmd_1": "Carte",
    "ui_main_cmd_2": "Au sol",
    "ui_main_cmd_3": "Divers",
    "ui_main_cmd_2a": "Escalier",
    "ui_item_equip": "Equiper",
    "ui_item_equip_off": "Oter",
    "ui_item_throw": "Lancer",
    "ui_item_put": "Poser",
    "ui_item_pick": "Prendre",
    "ui_item_swap": "Echanger",
    "ui_item_name": "Nommer",
    "ui_item_shoot": "Tirer",
    "ui_item_eat": "Manger",
    "ui_item_drink": "Boire",
    "ui_item_read": "Lire",
    "ui_item_swing": "Brandir",
    "ui_item_guess": "Deviner",
    "ui_item_under": "Au sol",
    "ui_down": "Descendre",
    "ui_down_cancel": "Rester",
    "ui_up": "Monter",
    "ui_up_cancel": "Rester",
    "ui_stat_deep": "Etage max",
    "ui_stat_atk": "Att. arme",
    "ui_stat_def": "Def. bouclier",
    "ui_stat_food": "Satiete",
    "ui_stat_pow": "Force",
    "ui_stat_exp": "Experience",
    "ui_sys_abort": "Abandonner",
    "ui_sys_config": "Parametres",
    "ui_sys_save": "Quitter",
    "ui_start_begin": "Nouvelle aventure",
    "ui_start_delete": "Effacer aventure",
    "ui_start_continue": "Continuer",
    "ui_start_rename": "Renommer village",
    "ui_start_highscore": "Meilleurs scores",
    "ui_start_quit": "Quitter",
    "ui_house_storage": "Entrepot",
    "ui_house_storage_sell": "Vendre",
    "ui_house_carry_info": "Inventaire",
    "ui_house_storage_info": "Vers entrepot",
    "ui_house_achievement": "Succes",
    "ui_house_license": "Licences",
    "ui_house_privacy_policy": "Confidentialite",
    "ui_house_credit": "Credits",
    "ui_house_title": "Ecran titre",
    "ui_title_start": "<a(blink)>Appuyez sur une touche",
    "ui_rank_hiscore": "Meilleurs scores",
    "ui_key_kata": "Katakana",
    "ui_key_kana": "Hiragana",
    "ui_key_eisuu": "ABC123",
    "ui_key_space": "Espace",
    "ui_key_back": "Retour",
    "ui_key_enter": "Valider",
    "ui_config_graphics": "Affichage",
    "ui_config_sound": "Audio",
    "ui_config_key_binding_controller": "Manette",
    "ui_config_key_binding_keyboard": "Clavier",
    "ui_config_key_binding_mouse": "Souris",
    "ui_config_key_binding_gamepad": "Manette",
    "ui_config_key_binding_virtualpad": "Manette virtuelle",
    "ui_config_key_binding_1": "Attaque / Action",
    "ui_config_key_binding_2": "Annuler / Courir",
    "ui_config_key_binding_3": "Pivoter / Trier",
    "ui_config_key_binding_4": "Menu",
    "ui_config_key_binding_5": "Tirer fleche",
    "ui_config_key_binding_6": "Diagonale fixe",
    "ui_config_key_binding_7": "Carte",
    "ui_config_key_binding_8": "Sur place",
    "ui_config_key_binding_9": "Haut",
    "ui_config_key_binding_10": "Gauche",
    "ui_config_key_binding_11": "Bas",
    "ui_config_key_binding_12": "Droite",
    "ui_config_key_binding_13": "Souris",
    "ui_config_key_binding_14": "Manette",
    "ui_config_key_binding_15": "Arriere-plan",
    "ui_config_game_balance": "Equilibrage",
    "ui_config_game_system": "Systeme de jeu",
    "ui_config_lang": "Langue",
    "ui_config_font": "Police",
    "ui_config_log": "Lignes journal",
    "ui_config_map_anchor": "Position mini-carte",
    "ui_config_screen_vertical_value_0": "Horizontal",
    "ui_config_screen_vertical_value_1": "Vertical",
    "ui_config_window_mode": "Affichage",
    "ui_config_font_normal": "Normal",
    "ui_config_vol": "Volume",
    "ui_config_se_vol": "Bruitages",
    "ui_config_bgm_vol": "Musique",
    "ui_config_sound_background": "Son en fond",
    "ui_config_framerate": "Images/sec.",
    "ui_config_grid": "Grille",
    "ui_config_dust": "Effets meteo",
    "ui_config_food": "Apparition pain",
    "ui_config_item": "Apparition objets",
    "ui_config_monster_house": "Repaires monstres",
    "ui_config_enemy": "Apparition monstres",
    "ui_config_gold": "Gain d'or",
    "ui_config_exp": "Gain experience",
    "ui_config_trap": "Apparition pieges",
    "ui_config_rate_none": "x0.0",
    "ui_config_rate_low": "x0.5",
    "ui_config_rate_normal": "x1.0",
    "ui_config_rate_up": "x1.5",
    "ui_config_rate_double": "x2.0",
    "ui_config_on": "Oui",
    "ui_config_off": "Non",
    "ui_config_default": "Par defaut",
    "ui_record_play": "Historique",
    "ui_record_note_castle": "Conseils chateau",
    "ui_record_note_store": "Conseils boutique",
    "ui_record_play_total_time": "Temps de jeu :",
    "ui_record_play_try": "Visites donjon :",
    "ui_record_play_success": "Retours reussis :",
    "ui_record_play_kill": "Monstres vaincus :",
    "ui_record_play_gold": "Total or gagne :",
    "ui_config_anchor_0": "Haut-Gauche",
    "ui_config_anchor_1": "Haut",
    "ui_config_anchor_2": "Haut-Droite",
    "ui_config_anchor_3": "Gauche",
    "ui_config_anchor_4": "Centre",
    "ui_config_anchor_5": "Droite",
    "ui_config_anchor_6": "Bas-Gauche",
    "ui_config_anchor_7": "Bas",
    "ui_config_anchor_8": "Bas-Droite",
    "ui_config_window_mode_0": "Fenetre",
    "ui_config_window_mode_1": "Plein ecran",
    "ui_config_window_mode_2": "Plein ecran sans bord",
    "ui_hiscore_none": "Aucun record pour l'instant.",
    "ui_config_map_type": "Mode mini-carte",
    "ui_start_replay": "Revoir",
    "ui_config_rbutton_0": "Appuyer",
    "ui_config_rbutton_1": "Maintenir",
    "ui_config_rbutton_2": "Les deux",
    "ui_config_rbutton_type": "Diagonale fixe",
    "ui_config_dialog_equip_show": "Voir changements",
    "ui_achievement_count_title": "ACCOMPLI",
    "ui_record_drop_rate_0": "Jamais",
    "ui_record_drop_rate_1": "Rarement",
    "ui_record_drop_rate_2": "Une fois sur 6",
    "ui_record_drop_rate_3": "Parfois",
    "ui_record_drop_rate_4": "Frequemment",
    "ui_record_drop_rate_5": "Or garanti",
    "ui_record_drop_rate_6": "Graines de croissance",
    "ui_record_drop_rate_7": "Toujours",
    "ui_ending_fin": "Fin",
    "ui_change": "Casse",
    "ui_reflect": "Appliquer",
    "ui_prev_page": "Precedent",
    "ui_next_page": "Suivant",
    "ui_change_detail": "Details",
    "ui_organize": "Trier",
    "ui_platform": "Plateforme stream",
    "ui_streaming_1": "Connexion",
    "ui_streaming_2": "Verification app",
    "ui_streaming_3": "Streaming",
    "ui_streaming_4": "Desactive",
    "ui_streaming_5": "Active",
    "ui_streaming_6": "Reglages stream",
    "ui_streaming_8": "Demarrer",
    "ui_streaming_9": "Confirmer",
    "ui_streaming_10": "Affichage stream",
    "ui_streaming_12": "Dedie",
    "ui_streaming_13": "Frequence events",
    "ui_streaming_14": "Frequente",
    "ui_streaming_15": "Occasionnelle",
    "ui_streaming_16": "Rare",
    "ui_streaming_17": "Choix event",
    "ui_streaming_18": "Joueur",
    "ui_streaming_19": "Aleatoire",
    "ui_streaming_20": "Vote public",
    "ui_streaming_21": "Spectateur",
    "ui_streaming_22": "Premier com.",
    "ui_streaming_23": "Mot magique",
    "ui_streaming_24": "Par defaut",
    "ui_streaming_26": "Statut stream",
    "ui_streaming_27": "Mode stream",
    "ui_streaming_28": "Hors ligne",
    "ui_floorevent_lucky": "Brise joyeuse",
    "ui_floorevent_hunter": "Arome inquietant",
    "ui_floorevent_something_happens": "Abracadabra",
    "ui_floorevent_pinch": "Chant du destin",
    "ui_floorevent_teleport": "Vents du changement",
    "ui_floorevent_light": "Brume legere",
    "ui_config_key": "Commandes",
    "ui_dungeon_result_title": "Resultats",
    "ui_dungeon_result_score": "Score",
    "ui_movie_skip": "Passer",
    "ui_record_play2": "Stats generales",
    "ui_streaming_29": "Streameur",
    "ui_streaming_30": "Modifier",
    "ui_menu_sp": "Menu",
    "ui_streaming_items": "Inventaire",
    "ui_title_start_sp": "<a(blink)>Touchez pour commencer",
    "ui_cloud_sp": "Sauvegarde cloud",
    "ui_cloud_sp2": "Verification...",
    "ui_loading": "Chargement...",
    "ui_cloud_sp3": "Sauver sur cloud",
    "ui_cloud_sp4": "Charger du cloud",
    "ui_cloud_sp5": "Donnees locales",
    "ui_cloud_sp6": "Donnees cloud",
    "ui_item_guess_sp": "Deviner",
    "ui_item_list_sp": "Objets",
    "ui_config_key_binding_controller2": "Manette sans fil",
    "ui_config_graphics_resolution": "Resolution",
    "ui_config_graphics_resolution2": "Resolution actuelle",
    "ui_config_key_binding_3_virtualpad": "Pivoter"
}

ITEM_TRANSLATIONS = {
    "Oaken Club": ("massue de chene", "Massue de chene", "massues de chene", "Massues de chene"),
    "Gold Sword": ("epee d'or", "Epee d'or", "epees d'or", "Epees d'or"),
    "Copper Sword": ("epee de cuivre", "Epee de cuivre", "epees de cuivre", "Epees de cuivre"),
    "Iron Axe": ("hache de fer", "Hache de fer", "haches de fer", "Haches de fer"),
    "Dragonsbane": ("tueuse de dragon", "Tueuse de dragon", "tueuses de dragon", "Tueuses de dragon"),
    "Liquid Metal Sword": ("epee de mercure", "Epee de mercure", "epees de mercure", "Epees de mercure"),
    "Astraea's Abacus": ("boulier d'Astree", "Boulier d'Astree", "bouliers d'Astree", "Bouliers d'Astree"),
    "Leather Shield": ("bouclier de cuir", "Bouclier de cuir", "boucliers de cuir", "Boucliers de cuir"),
    "Bronze Shield": ("bouclier de bronze", "Bouclier de bronze", "boucliers de bronze", "Boucliers de bronze"),
    "Scale Shield": ("bouclier d'ecailles", "Bouclier d'ecailles", "boucliers d'ecailles", "Boucliers d'ecailles"),
    "Silver Shield": ("bouclier d'argent", "Bouclier d'argent", "boucliers d'argent", "Boucliers d'argent"),
    "Steel Shield": ("bouclier d'acier", "Bouclier d'acier", "boucliers d'acier", "Boucliers d'acier"),
    "Dragon Shield": ("bouclier du dragon", "Bouclier du dragon", "boucliers du dragon", "Boucliers du dragon"),
    "Liquid Metal Shield": ("bouclier de mercure", "Bouclier de mercure", "boucliers de mercure", "Boucliers de mercure"),
    "Strength Ring": ("bague de force", "Bague de force", "bagues de force", "Bagues de force"),
    "Antidotal Ring": ("bague d'antidote", "Bague d'antidote", "bagues d'antidote", "Bagues d'antidote"),
    "Restless Ring": ("bague d'eveil", "Bague d'eveil", "bagues d'eveil", "Bagues d'eveil"),
    "Zoom Ring": ("bague de teleport", "Bague de teleport", "bagues de teleport", "Bagues de teleport"),
    "Sustaining Ring": ("bague de satiete", "Bague de satiete", "bagues de satiete", "Bagues de satiete"),
    "Sneaky Ring": ("bague de discretion", "Bague de discretion", "bagues de discretion", "Bagues de discretion"),
    "Profiteer Ring": ("bague de fortune", "Bague de fortune", "bagues de fortune", "Bagues de fortune"),
    "Revealing Ring": ("bague de clairvoyance", "Bague de clairvoyance", "bagues de clairvoyance", "Bagues de clairvoyance"),
    "Hanker Ring": ("bague de voracite", "Bague de voracite", "bagues de voracite", "Bagues de voracite"),
    "Safety Ring": ("bague de surete", "Bague de surete", "bagues de surete", "Bagues de surete"),
    "Puppeteer Ring": ("bague de marionnette", "Bague de marionnette", "bagues de marionnette", "Bagues de marionnette"),
    "Cock-a-Doodle-Doo Ring": ("bague du coq", "Bague du coq", "bagues du coq", "Bagues du coq"),
    "Wooden Arrow": ("fleche de bois", "Fleche de bois", "fleches de bois", "Fleches de bois"),
    "Iron Arrow": ("fleche de fer", "Fleche de fer", "fleches de fer", "Fleches de fer"),
    "Silver Arrow": ("fleche d'argent", "Fleche d'argent", "fleches d'argent", "Fleches d'argent"),
    "Little Loaf": ("petit pain", "Petit pain", "petits pains", "Petits pains"),
    "Large Loaf": ("grand pain", "Grand pain", "grands pains", "Grands pains"),
    "Mouldy Loaf": ("pain moisi", "Pain moisi", "pains moisis", "Pains moisis"),
    "Medicinal Herb": ("herbe medicinale", "Herbe medicinale", "herbes medicinales", "Herbes medicinales"),
    "Mega Medicinal Herb": ("herbe curative", "Herbe curative", "herbes curatives", "Herbes curatives"),
    "Antidotal Herb": ("herbe d'antidote", "Herbe d'antidote", "herbes d'antidote", "Herbes d'antidote"),
    "Seed of Strength": ("graine de force", "Graine de force", "graines de force", "Graines de force"),
    "Seed of Growth": ("graine de croissance", "Graine de croissance", "graines de croissance", "Graines de croissance"),
    "Seed of Agility": ("graine d'agilite", "Graine d'agilite", "graines d'agilite", "Graines d'agilite"),
    "Eye-Opening Herb": ("herbe de lucidite", "Herbe de lucidite", "herbes de lucidite", "Herbes de lucidite"),
    "Poison Herb": ("herbe toxique", "Herbe toxique", "herbes toxiques", "Herbes toxiques"),
    "Blinding Herb": ("herbe aveuglante", "Herbe aveuglante", "herbes aveuglantes", "Herbes aveuglantes"),
    "Hallucinatory Herb": ("herbe d'illusion", "Herbe d'illusion", "herbes d'illusion", "Herbes d'illusion"),
    "Fuddle Herb": ("herbe de confusion", "Herbe de confusion", "herbes de confusion", "Herbes de confusion"),
    "Snooze Herb": ("herbe de sommeil", "Herbe de sommeil", "herbes de sommeil", "Herbes de sommeil"),
    "Zoom Herb": ("herbe de teleport", "Herbe de teleport", "herbes de teleport", "Herbes de teleport"),
    "Red-Hot Herb": ("herbe brulante", "Herbe brulante", "herbes brulantes", "Herbes brulantes"),
    "Oomph Scroll": ("parch. Decuplo", "Parch. Decuplo", "parchemins Decuplo", "Parchemins Decuplo"),
    "Buff Scroll": ("parch. Megaprotection", "Parch. Megaprotection", "parchemins Megaprotection", "Parchemins Megaprotection"),
    "Plating Scroll": ("parch. de placage", "Parch. de placage", "parchemins de placage", "Parchemins de placage"),
    "Sheen Scroll": ("parch. d'eclat", "Parch. d'eclat", "parchemins d'eclat", "Parchemins d'eclat"),
    "Peep Scroll": ("parch. d'inspection", "Parch. d'inspection", "parchemins d'inspection", "Parchemins d'inspection"),
    "Glow Scroll": ("parch. lumineux", "Parch. lumineux", "parchemins lumineux", "Parchemins lumineux"),
    "Stupefying Scroll": ("parch. de stupeur", "Parch. de stupeur", "parchemins de stupeur", "Parchemins de stupeur"),
    "Sanctuary Scroll": ("parch. sanctuaire", "Parch. sanctuaire", "parchemins sanctuaire", "Parchemins sanctuaire"),
    "Dungeon Conqueror's Certificate": ("certif. de conquete", "Certif. de conquete", "certificats de conquete", "Certificats de conquete"),
    "Dungeon Plunderer's Diploma": ("diplome de pillard", "Diplome de pillard", "diplomes de pillard", "Diplomes de pillard"),
    "See-All Scroll": ("parch. d'omniscience", "Parch. d'omniscience", "parchemins d'omniscience", "Parchemins d'omniscience"),
    "Hear-All Scroll": ("parch. d'ouie fine", "Parch. d'ouie fine", "parchemins d'ouie fine", "Parchemins d'ouie fine"),
    "Bread Scroll": ("parch. du boulanger", "Parch. du boulanger", "parchemins du boulanger", "Parchemins du boulanger"),
    "Wanderful Scroll": ("parch. vagabond", "Parch. vagabond", "parchemins vagabonds", "Parchemins vagabonds"),
    "Bang Scroll": ("parch. Bang", "Parch. Bang", "parchemins Bang", "Parchemins Bang"),
    "Gobstopping Scroll": ("parch. de silence", "Parch. de silence", "parchemins de silence", "Parchemins de silence"),
    "Sands of Time Scroll": ("parch. Sables du temps", "Parch. Sables du temps", "parchemins Sables du temps", "Parchemins Sables du temps"),
    "Pratfall Scroll": ("parch. de chute", "Parch. de chute", "parchemins de chute", "Parchemins de chute"),
    "Hocus Pocus Scroll": ("parch. Aleatoire", "Parch. Aleatoire", "parchemins Aleatoire", "Parchemins Aleatoire"),
    "Evac Scroll": ("parch. Evacuation", "Parch. Evacuation", "parchemins Evacuation", "Parchemins Evacuation"),
    "Lightning Staff": ("baton d'eclair", "Baton d'eclair", "batons d'eclair", "Batons d'eclair"),
    "Deceleratle Wand": ("baguette d'entrave", "Baguette d'entrave", "baguettes d'entrave", "Baguettes d'entrave"),
    "Snooze Wand": ("baguette de sommeil", "Baguette de sommeil", "baguettes de sommeil", "Baguettes de sommeil"),
    "Fuddle Wand": ("baguette de confusion", "Baguette de confusion", "baguettes de confusion", "Baguettes de confusion"),
    "Sealing Stave": ("baton de sceau", "Baton de sceau", "batons de sceau", "Batons de sceau"),
    "Bazoom Wand": ("baguette d'ejection", "Baguette d'ejection", "baguettes d'ejection", "Baguettes d'ejection"),
    "Mod Rod": ("baton de mutation", "Baton de mutation", "batons de mutation", "Batons de mutation"),
    "Acceleratle Wand": ("baguette d'acceleration", "Baguette d'acceleration", "baguettes d'acceleration", "Baguettes d'acceleration"),
    "Fade Wand": ("baguette d'invisibilite", "Baguette d'invisibilite", "baguettes d'invisibilite", "Baguettes d'invisibilite"),
    "Walking Stick": ("baton de marche", "Baton de marche", "batons de marche", "Batons de marche"),
    "Copy Cane": ("canne de copie", "Canne de copie", "cannes de copie", "Cannes de copie"),
    "Whack Wand": ("baguette de mort", "Baguette de mort", "baguettes de mort", "Baguettes de mort"),
    "Two-Ended Truncheon": ("matraque double", "Matraque double", "matraques doubles", "Matraques doubles"),
    "Sacrificial Shillelagh": ("gourdin sacrifice", "Gourdin sacrifice", "gourdins sacrifice", "Gourdins sacrifice"),
    "Gold Coin": ("piece d'or", "Piece d'or", "pieces d'or", "Pieces d'or"),
    "Steel Strongbox": ("coffre d'acier", "Coffre d'acier", "coffres d'acier", "Coffres d'acier"),
    "Crown Jewels": ("joyaux royaux", "Joyaux royaux", "joyaux royaux", "Joyaux royaux"),
    "Chest of Cheer": ("coffre d'allegresse", "Coffre d'allegresse", "coffres d'allegresse", "Coffres d'allegresse"),
    "Strange Box": ("boite etrange", "Boite etrange", "boites etranges", "Boites etranges"),
    "Trap Arrow": ("fleche piege", "Fleche piege", "fleches pieges", "Fleches pieges"),
    "Dragon's Breath": ("souffle du dragon", "Souffle du dragon", "souffles du dragon", "Souffles du dragon"),
    "Kazapple Scroll": ("parch. Megafoudre", "Parch. Megafoudre", "parchemins Megafoudre", "Parchemins Megafoudre"),
    "Box of Multiple Miracles": ("boite a miracles", "Boite a miracles", "boites a miracles", "Boites a miracles")
}

def translate_ui():
    src_bin = os.path.join(DECOMP_DIR, "287453834.bin")
    with open(src_bin, 'rb') as fp:
        raw_bin = fp.read()

    reader = VariantReader(raw_bin)
    tree_type, root_entries = reader.parse()

    translated_count = 0
    for root_k, root_v in root_entries:
        if root_k == "rows":
            rows_type, rows_entries = root_v
            for i, (row_key, row_val) in enumerate(rows_entries):
                if row_key in FRENCH_UI:
                    french_text = clean_retro_text(FRENCH_UI[row_key])
                    list_type, list_items = row_val
                    # IMPORTANT: Do NOT alter orig_px! The engine uses it as the layout box width!
                    list_items[0] = ('str', french_text)
                    translated_count += 1

    print(f"UI: Applied {translated_count} French translations.")
    writer = VariantWriter()
    writer.write((tree_type, root_entries))
    new_bin = bytes(writer.buf)

    dest_dir = os.path.join(MOD_STAGING, "TornekosMysteryDungeon", "Content", "Anya", "Radec")
    os.makedirs(dest_dir, exist_ok=True)
    with open(os.path.join(dest_dir, "287453834"), 'wb') as fp:
        fp.write(compress_and_scramble(new_bin, 287453834))

def translate_items():
    src_bin = os.path.join(DECOMP_DIR, "1290896954.bin")
    with open(src_bin, 'rb') as fp:
        raw_bin = fp.read()

    reader = VariantReader(raw_bin)
    tree_type, root_entries = reader.parse()

    item_count = 0
    for root_k, root_v in root_entries:
        if root_k == "rows":
            rows_type, rows = root_v
            for row in rows:
                items = row[1]
                eng_name = items[8][1]
                if eng_name in ITEM_TRANSLATIONS:
                    fr_sgl, fr_sgg, fr_plr, fr_plg = ITEM_TRANSLATIONS[eng_name]
                    items[0] = ('str', clean_retro_text(fr_sgl))
                    items[2] = ('str', clean_retro_text(fr_plr))
                    items[8] = ('str', clean_retro_text(fr_sgg))
                    item_count += 1

    print(f"Items: Applied {item_count} French item translations.")
    writer = VariantWriter()
    writer.write((tree_type, root_entries))
    new_bin = bytes(writer.buf)

    dest_dir = os.path.join(MOD_STAGING, "TornekosMysteryDungeon", "Content", "Anya", "Radec")
    os.makedirs(dest_dir, exist_ok=True)
    with open(os.path.join(dest_dir, "1290896954"), 'wb') as fp:
        fp.write(compress_and_scramble(new_bin, 1290896954))

def main():
    translate_ui()
    translate_items()
    print("Translation files prepared in mod_staging.")

if __name__ == "__main__":
    main()
