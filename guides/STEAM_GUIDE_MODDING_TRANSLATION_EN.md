[h1]Modding & Localization Guide: How to Translate Dragon Quest Heroes: Torneko's Mystery Dungeon -Classic HD-[/h1]

[b]A complete technical walkthrough on reverse-engineering, extracting, translating, and repacking Square Enix's Radec engine for any language (Spanish, German, Italian, etc.).[/b]

---

[h2]Introduction & Purpose[/h2]
When Square Enix released [i]Dragon Quest Heroes: Torneko's Mystery Dungeon -Classic HD-[/i] on Steam, the game was only made available in [b]Japanese and English[/b]. 

To bring the game to the French community, we reverse-engineered the engine, decoded its proprietary binary file formats, and developed an automated open-source translation pipeline. 

This guide is designed for modders and translators who want to localize Torneko into their own language. Everything you need—tools, file specifications, encryption keys, complete English/Japanese database mappings, and pitfalls to avoid—is documented below.

[b]Open-Source Repository & Python Tools:[/b]
👉 [url=https://github.com/Edsaje/French_Trad_Dragon_Quest_Heroes_Torneko-s_Mystery_Dungeon_-Classic-HD-]GitHub: Torneko Localization Pipeline & Radec Codec[/url]

---

[h2]1. Architecture Overview & Prerequisites[/h2]

The game uses a hybrid architecture:
[list]
[*] [b]Engine Wrapper:[/b] Unreal Engine (Windows x64).
[*] [b]Core Game Data:[/b] Custom proprietary Chunsoft/Square Enix engine named [b]Radec[/b].
[*] [b]Archive Container:[/b] Unreal PAK file format version [b]V11[/b] encrypted with [b]AES-256-ECB[/b], combined with an [b]IoStore[/b] container dispatcher (.utoc / .ucas).
[/list]

[h3]Prerequisites:[/h3]
[list]
[*] [b]Python 3.10+[/b] (with [b]cryptography[/b] installed: [code]pip install cryptography[/code]).
[*] [b]repak[/b] (an open-source CLI tool for Unreal Engine PAK archives).
[*] [b]Torneko AES-256 Encryption Key:[/b]
[code]0xC71FCA6F12BDD06334324F18A52199BDC45A03F23B0935D5641CA4E130449F8F[/code]
[*] [b]Unreal Path Hash Seed (Fnv64):[/b]
[code]0x6409933B (Decimal: 1678349115)[/code]
[/list]

---

[h2]2. Unpacking the Game PAK[/h2]

The game's assets reside in:
[code]TornekosMysteryDungeon / Content / Paks / TornekosMysteryDungeon-Windows.pak[/code]

To extract the archive using [b]repak[/b]:
[code]
repak.exe --aes-key 0xC71FCA6F12BDD06334324F18A52199BDC45A03F23B0935D5641CA4E130449F8F unpack -o extracted_pak TornekosMysteryDungeon-Windows.pak
[/code]

All text and game database tables are located in:
[code]extracted_pak / TornekosMysteryDungeon / Content / Anya / Radec /[/code]

Notice that the files do not have standard names—they are stored as [b]numeric 32-bit hash identifiers[/b].

---

[h2]3. Radec File ID Map (Complete English ⟷ Japanese Mapping)[/h2]

Here is the complete reverse-engineered mapping between English and Japanese binary tables in Square Enix's Radec engine:

[table]
[tr]
[th]Content / Database Description[/th]
[th]English File ID[/th]
[th]Japanese File ID[/th]
[th]Size / Entries[/th]
[/tr]
[tr]
[td][b]Story Dialogues, Cutscenes, Village NPCs[/b][/td]
[td][b]353109016[/b][/td]
[td][b]247540702[/b][/td]
[td]544 dialogue entries[/td]
[/tr]
[tr]
[td][b]General UI, Menu Options, Settings[/b][/td]
[td][b]287453834[/b][/td]
[td][b]332245516[/b][/td]
[td]252 UI strings[/td]
[/tr]
[tr]
[td][b]Items & Equipment Database (Weapons, Shields, Herbs, Rings)[/b][/td]
[td][b]1290896954[/b][/td]
[td][b]1255572860[/b][/td]
[td]160 items[/td]
[/tr]
[tr]
[td][b]Item Descriptions & Lore[/b][/td]
[td][b]1362871123[/b][/td]
[td][b]1557199733[/b][/td]
[td]All 160 item descriptions[/td]
[/tr]
[tr]
[td][b]Item Category Headers (Weapons, Shields, Herbs, Scrolls)[/b][/td]
[td][b]1537184055[/b][/td]
[td][b]2142944893[/b][/td]
[td]8 categories[/td]
[/tr]
[tr]
[td][b]Monster Directory & Bestiary Names[/b][/td]
[td][b]860534025[/b][/td]
[td][b]2071660299[/b][/td]
[td]34 monster species[/td]
[/tr]
[tr]
[td][b]Monster Lore & Bestiary Background[/b][/td]
[td][b]1762117298[/b][/td]
[td][b]917308820[/b][/td]
[td]34 species descriptions[/td]
[/tr]
[tr]
[td][b]Dungeon Messages, Combat Log, Status Effects, Traps[/b][/td]
[td][b]568064241[/b][/td]
[td][b]37267031[/b][/td]
[td]294 dungeon events[/td]
[/tr]
[tr]
[td][b]HUD Dynamic Value Labels (Gold, Floor, HP, Stats)[/b][/td]
[td][b]955749668[/b][/td]
[td][b]242190762[/b][/td]
[td]88 labels[/td]
[/tr]
[tr]
[td][b]System Confirmation Popups (Save, Suspend, Retry)[/b][/td]
[td][b]464627131[/b][/td]
[td][b]1338011025[/b][/td]
[td]29 prompts[/td]
[/tr]
[tr]
[td][b]Achievement Titles[/b][/td]
[td][b]1530265350[/b][/td]
[td][b]1273666140[/b][/td]
[td]31 feats[/td]
[/tr]
[tr]
[td][b]Achievement Descriptions & Unlock Criteria[/b][/td]
[td][b]1980620336[/b][/td]
[td][b]382436806[/b][/td]
[td]34 records[/td]
[/tr]
[tr]
[td][b]Gamepad / Keyboard Tutorial Prompts[/b][/td]
[td][b]801856052[/b][/td]
[td][b]1076805126[/b][/td]
[td]14 prompts[/td]
[/tr]
[tr]
[td][b]Debug Menu & Room Names[/b][/td]
[td][b]8513248[/b][/td]
[td][i]shared / debug[/i][/td]
[td]116 strings[/td]
[/tr]
[/table]

---

[h2]4. Understanding the Binary Format (Gm::Variant & Scramble)[/h2]

Each Radec file uses a two-layer protection and serialization structure:

[h3]Layer A: Bitwise Scramble + Zlib Compression[/h3]
The raw file on disk is obfuscated with a bitwise cipher keyed to its [b]File ID[/b], followed by standard Zlib compression.

[h3]Layer B: The Gm::Variant AST[/h3]
Once decompressed, the data is a typed variant tree containing:
[list]
[*] [b]Type 0 (Map):[/b] Sequence of [b](key_string, variant_value)[/b].
[*] [b]Type 1 (List):[/b] Sequence of [b]variant_value[/b].
[*] [b]Type 3 (Int):[/b] 7-bit Variable-Length Integer (VLQ).
[*] [b]Type 8 (String):[/b] Length-prefixed string.
[/list]

[h3]All-in-One CLI: tools/radec_codec.py[/h3]
To make modding easy, our repository provides an all-in-one command line tool:

[code]
# 1. Decompress any Radec file to raw AST:
python tools/radec_codec.py decompress 1290896954 items.raw 1290896954

# 2. Re-compress and scramble back to game format:
python tools/radec_codec.py compress items_translated.raw 1290896954 1290896954

# 3. Decode 6-bit packed text string:
python tools/radec_codec.py decode-text "|MVH4IHXZWKPIQVMHNWQ"

# 4. Encode text string to 6-bit Radec format:
python tools/radec_codec.py encode-text "Potion de soin"
[/code]

---

[h2]5. The 6-Bit Text Codec (Why strings start with "|")[/h2]

In Radec tables, text strings do not use plain UTF-8. They use a proprietary [b]6-bit packing scheme[/b]. Any string starting with the character [b]"|"[/b] is encoded.

Every 3 raw bytes are packed into 4 printable ASCII characters (offset by [b]0x28[/b], with [b]0x5C[/b] mapped to [b]0x7A[/b]).

Use the companion [b]encode_radec()[/b] and [b]decode_radec()[/b] functions in [b]tools/radec_codec.py[/b] when converting strings in Python:

[code]
from tools.radec_codec import encode_radec, decode_radec

# Decodes to raw bytes
raw_bytes = decode_radec("|AW]ZHIL^MVz]ZMH...")

# Encodes raw bytes back to 6-bit pipe string
encoded_string = encode_radec(b"Your text here")
[/code]

---

[h2]6. Critical Pitfalls & How to Avoid Game Crashes[/h2]

[h3]A. Font Atlas Limitation (1-Byte ASCII)[/h3]
The default HD-2D font renders text using an 8-bit character atlas. [b]Do not output multi-byte UTF-8 accented characters[/b] (like Spanish [i]ñ, á, é[/i] or German [i]ä, ö, ü[/i]) without verifying the font texture sheet. Using standard ASCII replacements (or cleaning diacritics via [b]clean_retro_text()[/b]) guarantees glitch-free rendering.

[h3]B. In-line Bytecode Control Tags (\x02 ... \x03)[/h3]
The dialogue and combat systems use dynamic formatting tags delimited by byte [b]0x02[/b] (Start) and [b]0x03[/b] (End):
[list]
[*] [b]\x02\x06\x02p\x03[/b] : Dialogue Box Pause / Wait for player button press.
[*] [b]\x02\x10\x01\x03[/b] : End of Dialogue / Close Message Box.
[*] [b]\x02 \x03\xe8\x02\x03[/b] : Numerical value injection (Gold, Floor numbers, Damage).
[/list]
[b]WARNING:[/b] You must preserve these tags [b]intact[/b] inside your translated sentences. If a closing [b]\x03[/b] is missing or displaced, the typewriter engine will hang.

[h3]C. The Infamous "talk_wife_11" Softlock[/h3]
In the dialogue table ([b]353109016.bin[/b]), entry [b]talk_wife_11[/b] (Tessie's gold tally when Torneko returns from the dungeon) contains hardcoded binary Pascal string length prefixes ([b]\xff\xb9[/b] and [b]\xff\x56[/b]).
If you translate this string into another language without updating the internal byte length offsets, the engine will enter an [b]infinite loop[/b] during shop expansions (game freezes completely with music playing).
[b]Recommendation:[/b] Keep [b]talk_wife_11[/b] in English or calibrate its Pascal byte lengths precisely to prevent softlocking players!

---

[h2]7. Building a Lightweight IoStore Patch Trio (_P.pak + .utoc + .ucas)[/h2]

Instead of redistributing the entire 112 MB game PAK, you can generate a clean [b]~100 KB patch[/b] that mounts on top of the vanilla game without replacing anything!

[h3]The Unreal Engine IoStore Architecture:[/h3]
Because Torneko uses Unreal Engine's [b]IoStore[/b] container dispatcher, dropping a loose [.pak] alone will be [b]ignored[/b] by the engine at startup.
To mount a mod properly, you must supply a trio of 3 matching files:
[olist]
[*] [b]YourMod_P.pak (~100 KB):[/b] Contains your translated Radec binaries from [b]mod_staging[/b], packed with [b]repak[/b] (version V11, Fnv64 path hash seed [b]0x6409933B[/b]) and encrypted with the game's AES-256 key.
[*] [b]YourMod_P.utoc (144 bytes):[/b] A minimal IoStore Table of Contents header (EntryCount = 0) with a unique Container ID.
[*] [b]YourMod_P.ucas (0 bytes):[/b] An empty dummy container file.
[/olist]

[b]Why this works:[/b]
When Torneko boots, Unreal's [b]FIoDispatcher[/b] scans [code]Content/Paks/[/code] for [.utoc] files. The 144-byte [.utoc] and 0-byte [.ucas] validate the container registration, allowing [b]FPakPlatformFile[/b] to mount the companion [b]_P.pak[/b] with patch priority.

Our automated script [b]tools/build_patch_pak.py[/b] packages and encrypts the entire trio automatically:
[code]python tools/build_patch_pak.py[/code]

---

[h2]8. Multi-Modding & Stacking Mods (e.g. Custom Pixel Fonts)[/h2]

Because patch packages mount in alphabetical priority order, you can cleanly combine your translation mod with visual mods (such as Beardmo's pixel font mod [b]BeardmosPixelyDungeon_P[/b]).

[list]
[*] If your patch name starts with a letter after other mods (for example [b]HibouxeDonjonMystere_FR_P[/b] or [b]zSpanish_P[/b]), your translated texts will safely override any vanilla UI tables included in font mods, while retaining the custom font textures!
[*] Players simply drop the 3 mod files into [code]Content/Paks/[/code] alongside any other mods.
[*] Uninstalling is as simple as deleting the 3 mod files.
[/list]

---

[h2]Conclusion & Credits[/h2]

We hope this technical documentation helps modding teams around the world bring [i]Torneko's Mystery Dungeon[/i] to more players in their native languages!

[b]Credits & Inquiries:[/b]
[list]
[*] [b]Reverse-Engineering & Pipeline:[/b] Hibouxe ([url=https://www.youtube.com/@Hibouxe]YouTube @Hibouxe[/url])
[*] [b]Game & Universe:[/b] Square Enix / Spike Chunsoft / Dragon Quest
[/list]

If you have questions or need help adapting the tools for your language, feel free to open an Issue or Discussion on the [url=https://github.com/Edsaje/French_Trad_Dragon_Quest_Heroes_Torneko-s_Mystery_Dungeon_-Classic-HD-]GitHub repository[/url]!

---

[h2]Support the Guide 👍⭐🏆[/h2]

If this guide helped you or saved you time in reverse-engineering the game:
[list]
[*] [b]Rate Up 👍[/b] – Helps other modders and translators discover this resource.
[*] [b]Favorite ⭐[/b] – Keep it handy for your translation pipeline.
[*] [b]Give an Award 🏆[/b] – Always greatly appreciated for the hundreds of hours of reverse-engineering and open-source work!
[/list]

Happy modding, and long live the Dragon Quest community!
