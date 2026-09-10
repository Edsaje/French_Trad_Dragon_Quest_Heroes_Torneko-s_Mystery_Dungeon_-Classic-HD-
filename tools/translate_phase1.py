import os
import struct
import zlib
from build_french_mod import (
    clean_retro_text,
    scramble,
    compress_and_scramble,
    VariantReader,
    VariantWriter,
    SCRATCH_DIR,
    DECOMP_DIR,
    MOD_STAGING
)

def decode_radec(s: str) -> bytes:
    if not s.startswith('|'):
        return s.encode('latin1')
    data = s[1:]
    rdi = int(len(data) * 3 * 0.25)
    out = bytearray()
    for i in range(rdi):
        b = ord(data[i])
        if b == 0x7A: b = 0x5C
        out.append((b - 0x28) & 0xFF)
    rem = data[rdi:]
    rdx = 0
    for ch in rem:
        b = ord(ch)
        if b == 0x7A: b = 0x5C
        v = (b - 0x28) & 0xFF
        if rdx < len(out):     out[rdx]     |= ((v & 0x30) << 2) & 0xFF
        if rdx + 1 < len(out): out[rdx + 1] |= ((v & 0x0C) << 4) & 0xFF
        if rdx + 2 < len(out): out[rdx + 2] |= ((v & 0x03) << 6) & 0xFF
        rdx += 3
    return bytes(out)

def encode_radec(raw: bytes) -> str:
    part1, part2 = [], []
    for i in range(0, len(raw), 3):
        chunk = raw[i:i+3]
        b0 = chunk[0]
        b1 = chunk[1] if len(chunk) > 1 else 0
        b2 = chunk[2] if len(chunk) > 2 else 0
        for b in chunk:
            c = (b & 0x3F) + 0x28
            if c == 0x5C: c = 0x7A
            part1.append(chr(c))
        t0 = (b0 >> 6) & 0x03
        t1 = (b1 >> 6) & 0x03
        t2 = (b2 >> 6) & 0x03
        c2 = ((t0 << 4) | (t1 << 2) | t2) + 0x28
        if c2 == 0x5C: c2 = 0x7A
        part2.append(chr(c2))
    return '|' + ''.join(part1) + ''.join(part2)

def stage_file(file_id: str, new_bin: bytes):
    dest_dir = os.path.join(MOD_STAGING, "TornekosMysteryDungeon", "Content", "Anya", "Radec")
    os.makedirs(dest_dir, exist_ok=True)
    out_path = os.path.join(dest_dir, file_id)
    with open(out_path, 'wb') as fp:
        fp.write(compress_and_scramble(new_bin, int(file_id)))
    print(f"Staged {file_id}: {len(new_bin)} bytes -> {out_path}")

# =========================================================================
# 1. ITEM CATEGORIES (1537184055.bin)
# =========================================================================
CATEGORIES_FR = [
    "Arme",
    "Bouclier",
    "Anneau",
    "Projectile",
    "Nourriture",
    "Herbe",
    "Parchemin",
    "Baguette"
]

def translate_categories():
    src_bin = os.path.join(DECOMP_DIR, "1537184055.bin")
    with open(src_bin, 'rb') as fp:
        tree = VariantReader(fp.read()).parse()
    rows = dict(tree[1])['rows'][1]
    for i, cat in enumerate(CATEGORIES_FR):
        rows[i][1][0] = ('str', clean_retro_text(cat))
    writer = VariantWriter()
    writer.write(tree)
    stage_file("1537184055", bytes(writer.buf))

# =========================================================================
# 2. CONTROLS (801856052.bin)
# =========================================================================
CONTROLS_FR = {
    0: b"Utilisez \x02)\x03\xeb'\x03 pour vous deplacer dans 8 directions.\x02\x10\x01\x03Appuyez sur \x02)\x03\xeb\x1f\x03 pour attaquer.",
    1: b"Maintenez \x02)\x03\xeb$\x03 et utilisez \x02)\x03\xeb'\x03 pour aller en diagonale.",
    2: b"Utilisez \x02)\x03\xeb!\x03 pour ouvrir le menu.\x02\x10\x01\x03\x02)\x03\xeb\x1f\x03 pour valider et \x02)\x03\xeb \x03 pour annuler.",
    3: b"Maintenez \x02)\x03\xeb \x03 pour courir.\x02\x10\x01\x03Maintenez \x02)\x03\xeb \x03 et \x02)\x03\xeb\x1f\x03 pour guerir sur place.",
    4: b"Maintenez \x02)\x03\xeb\"\x03 et \x02)\x03\xeb'\x03 pour pivoter sans bouger.",
    5: b"Maintenez \x02)\x03\xeb(\x03 pour afficher uniquement la carte.",
    6: b"Appuyez sur \x02)\x03\xeb#\x03 pour tirer une fleche.\x02\x10\x01\x03Appuyez sur \x02)\x03\xeb\"\x03 pour ranger le sac."
}

def translate_controls():
    src_bin = os.path.join(DECOMP_DIR, "801856052.bin")
    with open(src_bin, 'rb') as fp:
        tree = VariantReader(fp.read()).parse()
    rows = dict(tree[1])['rows'][1]
    for idx, raw_fr in CONTROLS_FR.items():
        clean_bytes = raw_fr
        rows[idx][1][0] = ('str', encode_radec(clean_bytes))
    writer = VariantWriter()
    writer.write(tree)
    stage_file("801856052", bytes(writer.buf))

# =========================================================================
# 3. SYSTEM PROMPTS (464627131.bin)
# =========================================================================
PROMPTS_FR = {
    "ask_save": b"Votre aventure va etre suspendue. La prochaine fois que vous choisirez 'Continuer', vous reprendrez ici. Voulez-vous continuer ?",
    "ask_abort": b"Fuir le donjon ? Tous les objets actuellement dans votre sac seront perdus.",
    "ask_load": b"Reprendre votre aventure ?",
    "ask_remove": b"Voulez-vous vraiment abandonner \x02)\x03\xea\x02\x03?",
    "ask_retry": b"Recommencer ce donjon avec un gros pain dans votre sac ? Choisissez 'Non' pour remonter a la surface.",
    "ask_change": b"Les changements prendront effet a votre prochaine entree dans le donjon. Certains reglages ne s'appliquent pas aux repaires de monstres. Voulez-vous continuer ?\x02\x10\x01\x03",
    "ask_restore": b"Des ajustements d'equilibrage ont ete appliques. Annuler ces modifications et reprendre l'aventure ?",
    "ask_load_caution": b"Si l'equilibrage est modifie, vous ne pourrez pas revoir les replays du donjon. Certaines donnees ne figureront pas dans les meilleurs scores et succes. Continuer ?",
    "ask_sp_setting_caution": b"Les parametres d'affichage ont ete modifies. Vous allez revenir au menu titre. Vous pourrez choisir 'Continuer'. Continuer ?",
    "ask_5050": b"Reduire les options de moitie ? Il vous reste \x02 \x03\xe8\x02\x03 \x02\x08\x14\xe4\xe8\x02\x02\xff\x04util.\xff\x05utils.\x03.",
    "ask_streaming_start": b"Certains parametres ne sont pas compatibles avec la diffusion. Voulez-vous continuer avec ces parametres ?",
    "ask_streaming_load": b"Un donjon special pour le streaming va etre charge. Reprendre la diffusion ?\x02\x10\x01\x03\x02\x10\x01\x03Choisissez 'Non' pour charger le donjon sans les fonctions de streaming.",
    "ask_streaming_setting": b"Modifier les parametres pour lancer la diffusion ?",
    "ask_streaming_end": b"Quitter le mode streaming ? Si vous choisissez 'Oui', vous reviendrez en mode hors-ligne et les fonctions seront limitees.",
    "ask_streaming_terms_1": b"Voulez-vous continuer ?",
    "ask_streaming_terms_2": b"Acceptez-vous les conditions d'utilisation du streaming ?",
    "ask_streaming_info_1": b"Impossible de se connecter au reseau. Reessayer ?",
    "ask_streaming_info_2": b"Vous etes actuellement connecte a un compte. Continuer avec ce compte ? Si vous choisissez 'Non', vous serez deconnecte.",
    "ask_equip_unidentified": b"Pour l'equipement \x02\x13\x03\xe8\x02\x03non identifie\x02\x13\x05\xf6\xff\xff\xff\x03, seules les valeurs de base sont affichees sans les bonus (+/-). Voulez-vous l'equiper ?",
    "ask_equip_identified": b"Equiper cet objet ?",
    "ask_lang_setting": b"Quelle langue souhaitez-vous utiliser ?",
    "ask_streaming_change": b"Passer en mode streaming ?",
    "ask_streaming_terms_3": b"Une version beta d'un donjon participatif pour le streaming est disponible. Veuillez lire les regles sur le site officiel (https://www.dragonquest.jp/guideline/torneko_re) avant d'y acceder. Choisir 'Oui' indique que vous acceptez ces regles.",
    "ask_lang_setting_caution": b"La langue a ete modifiee. Vous allez revenir au menu titre. Vous pourrez choisir 'Continuer' pour reprendre l'aventure. Voulez-vous continuer ?"
}

def translate_system_prompts():
    src_bin = os.path.join(DECOMP_DIR, "464627131.bin")
    with open(src_bin, 'rb') as fp:
        tree = VariantReader(fp.read()).parse()
    rows = dict(dict(tree[1])['rows'][1])
    for k, raw_fr in PROMPTS_FR.items():
        if k in rows:
            clean_bytes = raw_fr
            rows[k][1][0] = ('str', encode_radec(clean_bytes))
    writer = VariantWriter()
    writer.write(tree)
    stage_file("464627131", bytes(writer.buf))

# =========================================================================
# 4. RECORDS / ACHIEVEMENTS (1980620336.bin)
# =========================================================================
RECORDS_FR = [
    "Obtenu pour avoir explore le Petit Donjon Mystere pour la premiere fois.",
    "Obtenu pour avoir recupere les joyaux de la couronne.",
    "Obtenu pour avoir obtenu le Diplome de pilleur de donjon.",
    "Obtenu pour avoir obtenu le Certificat de conquereur de donjon.",
    "Obtenu pour avoir obtenu toutes les armes.",
    "Obtenu pour avoir obtenu tous les boucliers.",
    "Obtenu pour avoir obtenu tous les anneaux.",
    "Obtenu pour avoir obtenu toutes les fleches.",
    "Obtenu pour avoir obtenu tous les types de nourriture.",
    "Obtenu pour avoir obtenu toutes les baguettes.",
    "Obtenu pour avoir obtenu toutes les herbes et graines.",
    "Obtenu pour avoir obtenu tous les parchemins.",
    "Obtenu pour avoir rencontre tous les monstres.",
    "Obtenu pour avoir ouvert votre magasin.",
    "Obtenu pour avoir agrandi votre magasin 4 fois.",
    "Obtenu pour avoir agrandi votre magasin 8 fois.",
    "Obtenu pour avoir agrandi votre magasin 9 fois.",
    "Obtenu pour avoir effectue 10 explorations de donjon.",
    "Obtenu pour avoir effectue 50 explorations de donjon.",
    "Obtenu pour avoir effectue 100 explorations de donjon.",
    "Obtenu pour avoir effectue 1000 explorations de donjon.",
    "Obtenu pour avoir amasse 1000 pieces d'or.",
    "Obtenu pour avoir amasse un million de pieces d'or.",
    "Obtenu pour avoir amasse 10 millions de pieces d'or.",
    "Obtenu pour avoir amasse 150 millions de pieces d'or.",
    "Obtenu pour avoir amasse 300 millions de pieces d'or.",
    "Obtenu pour avoir cree un journal d'aventure.",
    "Obtenu pour avoir vaincu un monstre.",
    "Obtenu pour avoir gagne un niveau pour la premiere fois.",
    "Obtenu pour avoir accompli tous les succes.",
    "Obtenu pour avoir recupere les joyaux de la couronne (reglages par defaut).",
    "Obtenu pour le Diplome de pilleur de donjon (reglages par defaut).",
    "Obtenu pour le Certificat de conquereur de donjon (reglages par defaut)."
]

def translate_records():
    src_bin = os.path.join(DECOMP_DIR, "1980620336.bin")
    with open(src_bin, 'rb') as fp:
        tree = VariantReader(fp.read()).parse()
    rows = dict(tree[1])['rows'][1]
    for i, rec in enumerate(RECORDS_FR):
        clean_bytes = clean_retro_text(rec).encode('latin1')
        rows[i][1][0] = ('str', encode_radec(clean_bytes))
    writer = VariantWriter()
    writer.write(tree)
    stage_file("1980620336", bytes(writer.buf))

# =========================================================================
# 5. HUD VALUES (955749668.bin)
# =========================================================================
HUD_FR = {
    "ui_value_floor": b"\x02\x13\x03\xe9\x02\x03Etage\x02\x13\x05\xf6\xff\xff\xff\x03 \x02 \x03\xe9\x0c\x03",
    "ui_value_lv": b"\x02\x13\x03\xe9\x02\x03Niv. \x02\x13\x03\xe9\x03\x03\x02 \x03\xe9\r\x03",
    "ui_value_hp": b"\x02\x13\x03\xe9\x02\x03PV\x02\x13\x03\xe9\x05\x03 \x02 \x03\xe9\x0e\x03/\x02 \x03\xe9\x0f\x03",
    "ui_value_gold": b"\x02 \x03\xe9\x10\x03 \x02\x13\x03\xe9\x02\x03PO",
    "ui_value_food_label": b"\x02\x13\x03\xe9\x02\x03Satiete",
    "ui_value_under": b"Etage \x02 \x03\xe8\x02\x03",
    "ui_value_eq_atk": b"Attaque arme\x02\x13\x03\xe8\x02\x03",
    "ui_value_eq_def": b"Defense bouclier\x02\x13\x03\xe8\x02\x03",
    "ui_value_eq_atk_pow": b"Attaque arme\x02\x13\x03\xe8\x02\x03 \x02 \x03\xe8\x03\x03",
    "ui_value_eq_atk_pow_q": b"\x02\x13\x03\xe8\x02\x03Attaque arme \x02 \x03\xe8\x03\x03",
    "ui_value_eq_def_pow": b"Defense bouclier\x02\x13\x03\xe8\x02\x03 \x02 \x03\xe8\x03\x03",
    "ui_value_eq_def_pow_q": b"\x02\x13\x03\xe8\x02\x03Defense bouclier \x02 \x03\xe8\x03\x03",
    "ui_value_itemlist_u": b"[Au sol] \x02\x13\x03\xe8\x05\x03\x021\x11\xff\nitem_noun\x01\xe8\x02\x01\x02\x03\x02)\x03\xea\x04\x03\x02\x08\x11\xe1\xe8\x03\x02\xff\t x\x02 \x03\xe8\x03\x03\xff\x01\x03",
    "ui_value_itemlist_select": b"[Equipe] \x02\x13\x03\xe8\x05\x03\x021\x11\xff\nitem_noun\x01\xe8\x02\x01\x02\x03\x02)\x03\xea\x04\x03\x02\x08\x11\xe1\xe8\x03\x02\xff\t x\x02 \x03\xe8\x03\x03\xff\x01\x03",
    "ui_value_itemlist_u_select": b"[Equipe] [Au sol] \x02\x13\x03\xe8\x05\x03\x021\x11\xff\nitem_noun\x01\xe8\x02\x01\x02\x03\x02)\x03\xea\x04\x03\x02\x08\x11\xe1\xe8\x03\x02\xff\t x\x02 \x03\xe8\x03\x03\xff\x01\x03",
    "ui_value_guess1": b"\x02\x10\x01\x03Peut-etre \x021\x11\xff\nitem_noun\x01\xe8\x02\x02\x02\x03 ?",
    "ui_value_guess2": b"\x02\x10\x01\x03Peut-etre \x021\x11\xff\nitem_noun\x01\xe8\x02\x02\x02\x03 ou \x021\x11\xff\nitem_noun\x01\xe8\x03\x02\x02\x03 ?",
    "ui_value_guess3": b"\x02\x10\x01\x03Peut-etre \x021\x11\xff\nitem_noun\x01\xe8\x02\x02\x02\x03, \x021\x11\xff\nitem_noun\x01\xe8\x03\x02\x02\x03 ou \x021\x11\xff\nitem_noun\x01\xe8\x04\x02\x02\x03 ?",
    "ui_value_guess4": b"\x02\x10\x01\x03Peut-etre \x021\x11\xff\nitem_noun\x01\xe8\x02\x02\x02\x03, \x021\x11\xff\nitem_noun\x01\xe8\x03\x02\x02\x03, \x021\x11\xff\nitem_noun\x01\xe8\x04\x02\x02\x03 ou meme...",
    "ui_value_file": b"\x02 \x03\xe8\x02\x03: Journal \x02 \x03\xe8\x02\x03",
    "ui_value_save_town": b"Au magasin",
    "ui_value_save_castle": b"Au chateau",
    "ui_value_save_result": b"Sur le retour",
    "ui_value_save_count": b"\x02\"\x06\xe8\x02\xff\x02,\x03 \x02\x08\x16\xe4\xe8\x02\x02\xff\x07Visite\xff\x08Visites\x03",
    "ui_value_note_king": b"Conseil du Roi \x02 \x03\xe8\x02\x03",
    "ui_value_note_sol1": b"Conseil sentinelle \x02 \x03\xe8\x02\x03",
    "ui_value_note_sol2": b"Conseil du garde \x02 \x03\xe8\x02\x03",
    "ui_value_note_trainer": b"Conseil du vassal \x02 \x03\xe8\x02\x03",
    "ui_value_note_minister": b"Conseil ministre \x02 \x03\xe8\x02\x03",
    "ui_value_note_prince": b"Conseil du prince \x02 \x03\xe8\x02\x03",
    "ui_value_note_village": b"Conseil village \x02 \x03\xe8\x02\x03",
    "ui_value_record_floor": b"Etage \x02 \x03\xe8\x02\x03",
    "ui_value_house_carry_count": b"Objets (\x02 \x03\xe8\x02\x03/\x02 \x03\xe8\x03\x03)",
    "ui_value_house_storage_count": b"Entrepot (\x02 \x03\xe8\x02\x03/\x02 \x03\xe8\x03\x03)",
    "ui_value_house_store_info": b"Prix de vente (\x02 \x03\xe8\x02\x03 \x02\x08\x14\xe4\xe8\x02\x02\xff\x06Objet\xff\x07Objets\x03)",
    "ui_value_action_npc": b"\x02)\x03\xeb\x1f\x03 Parler",
    "ui_value_action_object": b"\x02)\x03\xeb\x1f\x03 Examiner",
    "ui_value_action_door": b"\x02)\x03\xeb\x1f\x03 Ouvrir",
    "ui_value_record_hp": b"PV: \x02 \x03\xe8\x02\x03",
    "ui_value_record_attack": b"Attaque: \x02 \x03\xe8\x02\x03",
    "ui_value_record_defense": b"Defense: \x02 \x03\xe8\x02\x03",
    "ui_value_record_exp": b"Experience: \x02 \x03\xe8\x02\x03",
    "ui_value_record_drop_rate": b"Objets laisses",
    "ui_value_record_appear": b"Habitat",
    "ui_value_record_appear_0": b"Petit Donjon:\x02\x1d\x01\x03",
    "ui_value_record_appear_1": b"Donjon:\x02\x1d\x01\x03",
    "ui_value_record_appear_section": b"Etages \x02 \x03\xe8\x02\x03 - \x02 \x03\xe8\x03\x03",
    "ui_value_record_enemy": b"Bestiaire",
    "ui_value_record_item": b"Catalogue d'objets",
    "ui_value_result_turn": b"(\x02 \x03\xe8\x02\x03 \x02\x08\x12\xe4\xe8\x02\x02\xff\x05Tour\xff\x06Tours\x03)",
    "ui_value_record_dungeon_0": b"Petit Donjon Mystere:",
    "ui_value_record_dungeon_1": b"Donjon Mystere:",
    "ui_value_record_dungeon_2": b"Grand Donjon Mystere:",
    "ui_value_playtime_for_streaming": b"(Temps de jeu: \x02 \x03\xe8\x02\x03:\x02$\x03\xe8\x03\x03:\x02$\x03\xe8\x04\x03)",
    "ui_value_result_turn2": b"\x02 \x03\xe8\x02\x03 Tour(s)",
    "ui_value_cloud_saves": b"Et \x02 \x03\xe8\x02\x03 autre(s) sauvegarde(s)"
}

def translate_hud_values():
    src_bin = os.path.join(DECOMP_DIR, "955749668.bin")
    with open(src_bin, 'rb') as fp:
        tree = VariantReader(fp.read()).parse()
    rows = dict(dict(tree[1])['rows'][1])
    for k, raw_fr in HUD_FR.items():
        if k in rows:
            clean_bytes = raw_fr
            rows[k][1][0] = ('str', encode_radec(clean_bytes))
    writer = VariantWriter()
    writer.write(tree)
    stage_file("955749668", bytes(writer.buf))

def main():
    print("Translating Phase 1 files...")
    translate_categories()
    translate_controls()
    translate_system_prompts()
    translate_records()
    translate_hud_values()
    print("Phase 1 complete!")

if __name__ == "__main__":
    main()
