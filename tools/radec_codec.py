"""
Torneko's Mystery Dungeon - Radec Binary Codec & Variant Serializer
Reverse-Engineered & Developed by Hibouxe (https://github.com/Edsaje)

Provides:
- VariantReader / VariantWriter: AST parser/serializer for Square Enix's Gm::Variant
- unscramble / scramble: Bitwise cipher keyed by 32-bit File ID
- decompress_radec / compress_and_scramble: Full pipeline decompressor & compressor
- decode_radec / encode_radec: 6-bit packed string text codec (starting with '|')
- clean_retro_text: Sanitizer for retro 1-byte font atlas
"""

import sys
import struct
import zlib
from typing import Any, List, Tuple, Union


# =========================================================================
# 1. Gm::Variant Binary AST Reader & Writer
# =========================================================================

class VariantReader:
    """
    Parses Square Enix / Chunsoft Gm::Variant typed AST from raw decompressed bytes.
    Types supported:
      0 = Map   (key-value pairs)
      1 = List  (sequence of items)
      3 = Int   (7-bit variable length integer)
      8 = Str   (length-prefixed UTF-8 string)
    """
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0

    def read_byte(self) -> int:
        b = self.data[self.pos]
        self.pos += 1
        return b

    def read_count(self) -> int:
        b0 = self.read_byte()
        if b0 & 0x80:
            b1 = self.read_byte()
            return ((b1 << 7) | (b0 & 0x7F))
        return b0

    def read_str(self) -> str:
        length = self.read_count()
        s = self.data[self.pos : self.pos + length].decode('utf-8', errors='replace')
        self.pos += length
        return s

    def parse(self) -> Tuple[str, Any]:
        t = self.read_byte()
        if t == 0:  # Map
            count = self.read_count()
            return ('map', [(self.read_str(), self.parse()) for _ in range(count)])
        elif t == 1:  # List
            count = self.read_count()
            return ('list', [self.parse() for _ in range(count)])
        elif t == 3:  # Int (VLQ)
            b0 = self.read_byte()
            if b0 & 0x80:
                b1 = self.read_byte()
                return ('int', ((b1 << 7) | (b0 & 0x7F)))
            return ('int', b0)
        elif t == 8:  # String
            return ('str', self.read_str())
        else:
            raise ValueError(f"Unknown variant type {t} at offset {hex(self.pos)}")


class VariantWriter:
    """
    Serializes a Gm::Variant AST tuple back into raw binary format bit-for-bit.
    """
    def __init__(self):
        self.buf = bytearray()

    def write_byte(self, b: int):
        self.buf.append(b & 0xFF)

    def write_count(self, n: int):
        if n >= 0x80:
            self.write_byte((n & 0x7F) | 0x80)
            self.write_byte((n >> 7) & 0xFF)
        else:
            self.write_byte(n)

    def write_str(self, s: str):
        raw = s.encode('utf-8')
        self.write_count(len(raw))
        self.buf.extend(raw)

    def write(self, val: Tuple[str, Any]):
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
        else:
            raise ValueError(f"Unknown AST type '{t}'")


# =========================================================================
# 2. Scramble / Unscramble Bitwise Cipher
# =========================================================================

def unscramble(data: bytes, key: int) -> bytes:
    """
    Decodes the bitwise obfuscation layer applied to Radec tables.
    The key is the integer 32-bit File ID (e.g. 353109016).
    """
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


def scramble(data: bytes, key: int) -> bytes:
    """
    Re-applies the bitwise obfuscation cipher using the 32-bit File ID.
    """
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


def decompress_radec(data: bytes, file_id: int) -> bytes:
    """
    Unscrambles and decompresses a Radec file (.bin) into raw Gm::Variant binary bytes.
    """
    un = unscramble(data, file_id)
    decompressed_len = struct.unpack('<I', un[:4])[0]
    return zlib.decompress(un[4:])


def compress_and_scramble(uncompressed_data: bytes, key: int) -> bytes:
    """
    Compresses raw Gm::Variant binary bytes with zlib level 9 and scrambles with key.
    """
    comp = zlib.compress(uncompressed_data, level=9)
    payload = struct.pack('<I', len(uncompressed_data)) + comp
    return scramble(payload, key)


# =========================================================================
# 3. 6-Bit Packed String Codec ("|...")
# =========================================================================

def decode_radec(s: str) -> bytes:
    """
    Decodes a proprietary Radec 6-bit packed string into raw bytes.
    If the string does not start with '|', returns latin1-encoded bytes.
    """
    if not s.startswith('|'):
        return s.encode('latin1')
    data = s[1:]
    rdi = int(len(data) * 3 * 0.25)
    out = bytearray()
    for ch in data[:rdi]:
        b = ord(ch)
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
    """
    Encodes raw bytes into the proprietary Radec 6-bit packed string prefixed by '|'.
    """
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
        # Pack 2 high bits of each of the 3 bytes into a single character
        top_bits = [ (b >> 6) & 0x03 for b in (b0, b1, b2) ]
        c2 = ((top_bits[0] << 4) | (top_bits[1] << 2) | top_bits[2]) + 0x28
        if c2 == 0x5C: c2 = 0x7A
        part2.append(chr(c2))
    return '|' + ''.join(part1) + ''.join(part2)


# =========================================================================
# 4. Text Normalizer for Retro 1-Byte Font Atlas
# =========================================================================

def clean_retro_text(s: str) -> str:
    """
    Cleans accented strings to fit inside the game's 1-byte ASCII font atlas,
    while preserving bytecode control sequences (\x02...\x03).
    """
    has_var_tag = '\x02)\x03\xeb\x0b\x03' in s
    replacements = {
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'à': 'a', 'â': 'a', 'ä': 'a',
        'î': 'i', 'ï': 'i',
        'ô': 'o', 'ö': 'o',
        'ù': 'u', 'û': 'u', 'ü': 'u',
        'ç': 'c',
        'É': 'E', 'È': 'E', 'Ê': 'E',
        'À': 'A', 'Â': 'A',
        'Î': 'I',
        'Ô': 'O',
        'Ù': 'U', 'Û': 'U',
        'œ': 'oe', 'Œ': 'OE',
        '’': "'", '«': '"', '»': '"', '–': '-', '—': '-'
    }
    for k, v in replacements.items():
        s = s.replace(k, v)
    if has_var_tag:
        s = s.replace('\x02)\x03e\x0b\x03', '\x02)\x03\xeb\x0b\x03')
    return s


# =========================================================================
# 5. Command-Line Interface
# =========================================================================

def main():
    if len(sys.argv) < 2:
        print("Torneko Radec Codec CLI")
        print("Usage:")
        print("  python radec_codec.py decompress <file_id.bin> <output.raw> [file_id]")
        print("  python radec_codec.py compress <input.raw> <output.bin> <file_id>")
        print("  python radec_codec.py decode-text <'|string'>")
        print("  python radec_codec.py encode-text <'string'>")
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == 'decompress':
        if len(sys.argv) < 4:
            print("Usage: python radec_codec.py decompress <file_id.bin> <output.raw> [file_id]")
            sys.exit(1)
        in_path = sys.argv[2]
        out_path = sys.argv[3]
        if len(sys.argv) >= 5:
            fid = int(sys.argv[4])
        else:
            # Try to extract file id from filename e.g. 353109016.bin
            import os
            base = os.path.basename(in_path).split('.')[0]
            fid = int(base)
        with open(in_path, 'rb') as f:
            data = f.read()
        dec = decompress_radec(data, fid)
        with open(out_path, 'wb') as f:
            f.write(dec)
        print(f"[OK] Decompressed {len(data)} bytes -> {len(dec)} bytes in {out_path}")

    elif cmd == 'compress':
        if len(sys.argv) < 5:
            print("Usage: python radec_codec.py compress <input.raw> <output.bin> <file_id>")
            sys.exit(1)
        in_path = sys.argv[2]
        out_path = sys.argv[3]
        fid = int(sys.argv[4])
        with open(in_path, 'rb') as f:
            data = f.read()
        comp = compress_and_scramble(data, fid)
        with open(out_path, 'wb') as f:
            f.write(comp)
        print(f"[OK] Compressed {len(data)} bytes -> {len(comp)} bytes in {out_path}")

    elif cmd == 'decode-text':
        if len(sys.argv) < 3:
            print("Usage: python radec_codec.py decode-text <'|string'>")
            sys.exit(1)
        s = sys.argv[2]
        decoded = decode_radec(s)
        print(f"Decoded: {decoded.decode('latin1', errors='replace')}")

    elif cmd == 'encode-text':
        if len(sys.argv) < 3:
            print("Usage: python radec_codec.py encode-text <'string'>")
            sys.exit(1)
        s = sys.argv[2]
        encoded = encode_radec(s.encode('latin1'))
        print(f"Encoded: {encoded}")
    else:
        print(f"Unknown command '{cmd}'")


if __name__ == '__main__':
    main()
