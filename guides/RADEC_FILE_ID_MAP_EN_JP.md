# Dragon Quest Heroes: Torneko's Mystery Dungeon -Classic HD-
## Radec Binary File ID Mapping: English ⟷ Japanese

This document provides the complete reverse-engineered mapping between **English** and **Japanese** binary database tables in Square Enix's Radec engine (`Content/Anya/Radec/`).

All files use the proprietary **Gm::Variant AST** serialization, **File ID bitwise scramble cipher**, and **Zlib compression**, decoded via [`tools/radec_codec.py`](https://github.com/Edsaje/French_Trad_Dragon_Quest_Heroes_Torneko-s_Mystery_Dungeon_-Classic-HD-/blob/main/tools/radec_codec.py).

---

### Complete File ID Mapping Table

| Content / Database Description | English File ID | Japanese File ID | Entries | Notes & Samples |
| :--- | :---: | :---: | :---: | :--- |
| **Items & Equipment Database** | `1290896954` | `1255572860` | 160 items | Weapons, Shields, Herbs, Scrolls, Rings (e.g. `こん棒`, `銅の剣`, `はぐれメタルの剣`, `薬草`...) |
| **Item Descriptions & Lore** | `1362871123` | `1557199733` | 160 items | Detailed lore & tactical tips for all 160 items |
| **Item Category Headers** | `1537184055` | `2142944893` | 8 categories | `武器` (Weapons), `盾` (Shields), `指輪` (Rings), `飛び道具` (Projectiles), `食糧` (Food), `草` (Herbs), `巻物` (Scrolls), `杖` (Staves) |
| **Monster Directory & Bestiary Names** | `860534025` | `2071660299` | 34 species | Official monster names (e.g. `スライム`, `ドラキー`, `ゴースト`, `ももんじゃ`, `まどうし`...) |
| **Monster Lore Descriptions** | `1762117298` | `917308820` | 34 species | Monster bestiary background lore |
| **Story, NPCs & Cutscenes Dialogues** | `353109016` | `247540702` | 544 entries | Main storyline, village dialogues, ending, and cutscenes |
| **Dungeon Messages & Combat Log** | `568064241` | `37267031` | 294 events | Battle logs, trap activations, status conditions, stairs |
| **General UI & Menu Options** | `287453834` | `332245516` | 252 strings | UI actions (`はい`/`いいえ`, `どうぐ`, `あしもと`, dungeon selection, settings) |
| **HUD Dynamic Labels** | `955749668` | `242190762` | 88 labels | Floor (`階`), Level (`Lv`), Health (`HP`), Gold (`G`), Shield Power labels |
| **System Confirmation Popups** | `464627131` | `1338011025` | 29 prompts | Save confirmation, Suspend adventure, Game Over retry popups |
| **Achievement Titles** | `1530265350` | `1273666140` | 31 feats | Achievement names (e.g. `初めての不思議のダンジョン`, `王の試練`...) |
| **Achievement Descriptions** | `1980620336` | `382436806` | 34 records | Unlock criteria descriptions |
| **Gamepad / Keyboard Tutorial Prompts** | `801856052` | `1076805126` | 14 prompts | Button mapping tutorials & movement prompts |
| **Debug Menu & Location Names** | `8513248` | *(shared / debug)* | 116 strings | Internal debug options, room names (`Dungeon`, `Shop`, `Castle`...) |

---

### Quick Technical Reference

#### 1. Decompressing & Unscrambling
Every file on disk is obfuscated using a bitwise cipher keyed to its numeric **File ID**, then compressed with standard zlib:
```python
from tools.radec_codec import decompress_radec, compress_and_scramble

# Example: Decompressing Japanese item database
with open("1255572860", "rb") as f:
    raw_ast_bytes = decompress_radec(f.read(), 1255572860)
```

#### 2. 6-Bit String Codec
Strings prefixed with `|` use a proprietary 6-bit packed encoding (3 raw bytes mapped to 4 printable ASCII characters):
```python
from tools.radec_codec import decode_radec, encode_radec

# Decodes to UTF-8 bytes:
raw_bytes = decode_radec("|...")
text = raw_bytes.decode('utf-8')
```

#### 3. AST Parsing & Serializing
```python
from tools.radec_codec import VariantReader, VariantWriter

reader = VariantReader(raw_ast_bytes)
ast_tree = reader.parse()

# Re-serialize back to identical binary structure
writer = VariantWriter()
writer.write(ast_tree)
new_binary = bytes(writer.buf)
```

#### 4. Packaging as a Lightweight Patch (`_P.pak`)
When translating either language, you do **not** need to touch IoStore (`.utoc` / `.ucas`). Radec files are loose files inside the legacy PAK container. Repacking into a `_P.pak` (e.g. `TornekosMysteryDungeon-Windows_P.pak`) mounts with higher priority over the base 112 MB file:
```bash
python tools/build_patch_pak.py
```
This produces a standalone patch of only **~100 KB**.

---
*Created by Hibouxe (https://github.com/Edsaje/French_Trad_Dragon_Quest_Heroes_Torneko-s_Mystery_Dungeon_-Classic-HD-)*
