[h1]Modding & Localization Guide: How to Translate Dragon Quest Heroes: Torneko's Mystery Dungeon -Classic HD-[/h1]

[b]A complete technical walkthrough on reverse-engineering, extracting, translating, and repacking Square Enix's Radec engine for any language (Spanish, German, Italian, etc.).[/b]

---

[h2]Introduction & Purpose[/h2]
When Square Enix released [i]Dragon Quest Heroes: Torneko's Mystery Dungeon -Classic HD-[/i] on Steam, the game was only made available in [b]Japanese and English[/b]. 

To bring the game to the French community, we reverse-engineered the engine, decoded its proprietary binary file formats, and developed an automated open-source translation pipeline. 

This guide is designed for modders and translators who want to localize Torneko into their own language. Everything you need—tools, file specifications, encryption keys, and pitfalls to avoid—is documented below.

[b]Open-Source Repository & Python Tools:[/b]
[url=https://github.com/Edsaje/French_Trad_Dragon_Quest_Heroes_Torneko-s_Mystery_Dungeon_-Classic-HD-]GitHub: Torneko Localization Pipeline[/url]

---

[h2]1. Architecture Overview & Prerequisites[/h2]

The game uses a hybrid architecture:
[list]
[*] [b]Engine Wrapper:[/b] Unreal Engine (Windows x64).
[*] [b]Core Game Data:[/b] Custom proprietary Chunsoft/Square Enix engine named [b]Radec[/b].
[*] [b]Archive Container:[/b] Unreal PAK file format version [b]V11[/b] encrypted with [b]AES-256-ECB[/b].
[/list]

[h3]Prerequisites:[/h3]
[list]
[*] [b]Python 3.10+[/b] (with [code]cryptography[/code] installed: [code]pip install cryptography[/code]).
[*] [b]repak[/b] (an open-source CLI tool for Unreal Engine PAK archives).
[*] [b]Torneko AES-256 Encryption Key:[/b]
[code]0xC71FCA6F12BDD06334324F18A52199BDC45A03F23B0935D5641CA4E130449F8F[/code]
[*] [b]Unreal Path Hash Seed (Fnv64):[/b]
[code]0x6409933B (Decimal: 1678349115)[/code]
[/list]

---

[h2]2. Unpacking the Game PAK[/h2]

The game's assets reside in:
[code]TornekosMysteryDungeon/Content/Paks/TornekosMysteryDungeon-Windows.pak[/code]

To extract the archive using [code]repak[/code]:
[code]
repak.exe --aes-key 0xC71FCA6F12BDD06334324F18A52199BDC45A03F23B0935D5641CA4E130449F8F unpack -o extracted_pak TornekosMysteryDungeon-Windows.pak
[/code]

All text and game database tables are located in:
[code]extracted_pak/TornekosMysteryDungeon/Content/Anya/Radec/[/code]

Notice that the files do not have filenames—they are named using [b]numeric 32-bit hash identifiers[/b].

---

[h2]3. Radec File ID Map (What each file contains)[/h2]

Here is the complete mapping of all text and data tables in the game:

[table]
[tr]
[th]File ID[/th]
[th]Content Description[/th]
[th]Size / Entries[/th]
[/tr]
[tr]
[td][b]353109016[/b][/td]
[td]Story Dialogues, Cutscenes, NPC interactions[/td]
[td]544 dialogue entries[/td]
[/tr]
[tr]
[td][b]287453834[/b][/td]
[td]General UI, Menu options, Button prompts[/td]
[td]Main interface strings[/td]
[/tr]
[tr]
[td][b]1290896954[/b][/td]
[td]Items & Equipment Database (Weapons, Shields, Herbs, Rings)[/td]
[td]160 item records[/td]
[/tr]
[tr]
[td][b]860534025[/b][/td]
[td]Monster Directory & Bestiary Names[/td]
[td]34 monster species[/td]
[/tr]
[tr]
[td][b]1362871123[/b][/td]
[td]Detailed Item Descriptions & Lore[/td]
[td]All 160 items described[/td]
[/tr]
[tr]
[td][b]568064241[/b][/td]
[td]Dungeon Messages, Combat Log, Status Effects, Traps[/td]
[td]294 dungeon events[/td]
[/tr]
[tr]
[td][b]955749668[/b][/td]
[td]HUD Dynamic Values (Gold, Floor, HP, Stats labels)[/td]
[td]On-screen labels[/td]
[/tr]
[tr]
[td][b]464627131[/b][/td]
[td]System Prompts & Confirmation Popups (Save, Quit, Settings)[/td]
[td]System dialogues[/td]
[/tr]
[tr]
[td][b]1980620336[/b][/td]
[td]Records, Feats & Achievements Descriptions[/td]
[td]33 achievement records[/td]
[/tr]
[tr]
[td][b]1537184055[/b][/td]
[td]Item Category Headers (Swords, Shields, Herbs, Scrolls)[/td]
[td]Inventory categories[/td]
[/tr]
[tr]
[td][b]801856052[/b][/td]
[td]Gamepad / Keyboard Controls & Remapping Labels[/td]
[td]Control layout[/td]
[/tr]
[/table]

---

[h2]4. Understanding the Binary Format (Gm::Variant & Scramble)[/h2]

Each Radec file uses a two-layer protection and serialization structure:

[h3]Layer A: Bitwise Scramble + Zlib Compression[/h3]
The raw file on disk is obfuscated with a bitwise cipher keyed to its [b]File ID[/b], followed by standard Zlib compression.
To decompress in Python:
[code]
import struct, zlib

def unscramble(data: bytes, key: int) -> bytes:
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
        cipher_val = struct.unpack('<I', buf[i*4 : (i+1)*4])[0]
        plain_val = (ebx ^ cipher_val) & 0xFFFFFFFF
        buf[i*4 : (i+1)*4] = struct.pack('<I', plain_val)
        ecx = cipher_val & 3
        ebx = ((cipher_val << ecx) + edi) & 0xFFFFFFFF
        edi += 1
    return bytes(buf)

def decompress_radec(data: bytes, file_id: int) -> bytes:
    un = unscramble(data, file_id)
    decompressed_len = struct.unpack('<I', un[:4])[0]
    return zlib.decompress(un[4:])
[/code]

[h3]Layer B: The Gm::Variant AST[/h3]
Once decompressed, the data is a typed variant tree containing:
[list]
[*] [b]Type 0 (Map):[/b] Sequence of [code](key_string, variant_value)[/code].
[*] [b]Type 1 (List):[/b] Sequence of [code]variant_value[/code].
[*] [b]Type 3 (Int):[/b] 7-bit Variable-Length Integer (VLQ).
[*] [b]Type 8 (String):[/b] Length-prefixed string.
[/list]

Our Python class [code]VariantReader[/code] and [code]VariantWriter[/code] (available in the GitHub repository) can parse this tree into native Python structures and re-serialize it bit-for-bit without corruption.

---

[h2]5. The 6-Bit Text Codec (Why strings start with "|")[/h2]

In Radec tables, translated strings do not use plain UTF-8. They use a proprietary [b]6-bit packing scheme[/b]. Any string starting with the character [b]"|"[/b] is encoded.

Every 3 raw bytes are packed into 4 printable ASCII characters (offset by [code]0x28[/code], with [code]0x5C[/code] mapped to [code]0x7A[/code]).

[code]
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
[/code]

Use the companion [code]encode_radec(raw_bytes)[/code] in our repository when re-encoding your translated strings.

---

[h2]6. Critical Pitfalls & How to Avoid Game Crashes[/h2]

[h3]A. Font Atlas Limitation (1-Byte ASCII)[/h3]
The HD-2D engine renders text using an 8-bit character atlas. [b]Do not output multi-byte UTF-8 accented characters[/b] (like Spanish [i]ñ, á, é[/i] or German [i]ä, ö, ü[/i]) without checking font glyph mappings. Using standard ASCII replacements (or cleaning diacritics via [code]clean_retro_text()[/code]) guarantees clean, glitch-free rendering.

[h3]B. In-line Bytecode Control Tags (\x02 ... \x03)[/h3]
The dialogue and combat systems use dynamic formatting tags delimited by byte [code]0x02[/code] (Start) and [code]0x03[/code] (End):
[list]
[*] [code]\x02\x06\x02p\x03[/code] : Dialogue Box Pause / Wait for player input.
[*] [code]\x02\x10\x01\x03[/code] : End of Dialogue / Close Message.
[*] [code]\x02 \x03\xe8\x02\x03[/code] : Numerical value injection (Gold, Turns, Damage).
[/list]
[b]WARNING:[/b] You must preserve these tags [b]intact[/b] inside your translated sentences. If a closing [code]\x03[/code] is missing or displaced, the typewriter engine will hang.

[h3]C. The Infamous "talk_wife_11" Softlock[/h3]
In the dialogue table ([code]353109016.bin[/code]), entry [b]talk_wife_11[/b] (Tessie's gold tally when Torneko returns from the dungeon) contains hardcoded binary Pascal string length prefixes ([code]\xff\xb9[/code] and [code]\xff\x56[/code]).
If you translate this string into another language without updating the internal byte length offsets, the engine will enter an [b]infinite loop[/b] during shop expansions (game freezes completely with music playing, Alt+F4 unresponsive).
[b]Recommendation:[/b] Keep [code]talk_wife_11[/code] in English or calibrate its Pascal byte lengths precisely to prevent softlocking players!

---

[h2]7. The Translation Workflow (Step-by-Step)[/h2]

[olist]
[*] [b]Clone the Repository:[/b]
   Download the tools from our GitHub:
   [code]git clone https://github.com/Edsaje/French_Trad_Dragon_Quest_Heroes_Torneko-s_Mystery_Dungeon_-Classic-HD-.git[/code]

[*] [b]Dump Dialogue Chunks to JSON:[/b]
   Dialogue entries are divided into 4 chunks:
   [code]tools/dialogue_chunk_1_fr.json[/code] to [code]tools/dialogue_chunk_4_fr.json[/code].
   Translate the strings into your target language (Spanish, German, etc.) while keeping control tags ([code]\x02...\x03[/code]) intact.

[*] [b]Translate Database Bins:[/b]
   Edit [code]tools/build_french_mod.py[/code] (or copy it to [code]build_spanish_mod.py[/code]) to input your language's dictionary for:
   [list]
   [*] UI strings ([code]FRENCH_UI[/code])
   [*] Item names ([code]ITEM_TRANSLATIONS[/code])
   [*] Monster names ([code]MONSTER_TRANSLATIONS[/code])
   [/list]

[*] [b]Build the Translated Binaries:[/b]
   Run the assembly scripts:
   [code]
   python assemble_dialogue_and_build.py
   python build_french_mod.py
   python translate_descriptions.py
   python translate_dungeon_messages.py
   python translate_phase1.py
   [/code]

[*] [b]Repack & Encrypt the PAK:[/b]
   Run:
   [code]python repack_main_game_pak.py[/code]
   This script repacks the files with [code]repak[/code], recalculates directory hashes (Fnv64), applies 16-byte padding, and encrypts the primary, PHI, and FDI indices with AES-256-ECB.

[*] [b]Test on PC & Steam Deck:[/b]
   Copy the resulting [code]TornekosMysteryDungeon-Windows.pak[/code] into your game folder:
   [code]SteamLibrary/steamapps/common/TornekosMysteryDungeon/TornekosMysteryDungeon/Content/Paks/[/code]
   Ensure game language is set to [b]English[/b] in the game options. Your translated text will display immediately!
[/olist]

---

[h2]Conclusion & Credits[/h2]

We hope this technical documentation helps modding teams around the world bring [i]Torneko's Mystery Dungeon[/i] to more players in their native languages!

[b]Credits & Inquiries:[/b]
[list]
[*] [b]Reverse-Engineering & Pipeline:[/b] Hibouxe ([url=https://www.youtube.com/@Hibouxe]YouTube @Hibouxe[/url])
[*] [b]Game & Universe:[/b] Square Enix / Spike Chunsoft / Dragon Quest
[/list]

If you have questions or need help adapting the tools for your language, feel free to open an Issue or Discussion on the [url=https://github.com/Edsaje/French_Trad_Dragon_Quest_Heroes_Torneko-s_Mystery_Dungeon_-Classic-HD-]GitHub repository[/url]!
