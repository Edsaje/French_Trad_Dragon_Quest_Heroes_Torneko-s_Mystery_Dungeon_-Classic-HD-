import os
import shutil
import struct
import hashlib
import subprocess
import io
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

SCRATCH_DIR = r"C:\Users\quent\.gemini\antigravity-cli\brain\45f9af8b-81a5-42de-9c01-542f477f783b\scratch"
EXTRACTED_PAK = os.path.join(SCRATCH_DIR, "extracted_pak")
MOD_STAGING = os.path.join(SCRATCH_DIR, "mod_staging")
REPAK_EXE = os.path.join(SCRATCH_DIR, "repak.exe")
TARGET_PAK = os.path.join(SCRATCH_DIR, "TornekosMysteryDungeon-Windows.pak")
GAME_PAKS_DIR = r"E:\SteamLibrary\steamapps\common\TornekosMysteryDungeon\TornekosMysteryDungeon\Content\Paks"
FINAL_GAME_PAK = os.path.join(GAME_PAKS_DIR, "TornekosMysteryDungeon-Windows.pak")

AES_KEY_HEX = "C71FCA6F12BDD06334324F18A52199BDC45A03F23B0935D5641CA4E130449F8F"
AES_KEY = bytes.fromhex(AES_KEY_HEX)
PATH_HASH_SEED = 1678349115 # 0x6409933B

def main():
    print("Step 1: Copying translated files into extracted_pak...")
    # Copy translated 287453834 and 1290896954 from mod_staging into extracted_pak
    staged_radec = os.path.join(MOD_STAGING, "TornekosMysteryDungeon", "Content", "Anya", "Radec")
    dest_radec = os.path.join(EXTRACTED_PAK, "TornekosMysteryDungeon", "Content", "Anya", "Radec")

    for fname in os.listdir(staged_radec):
        src = os.path.join(staged_radec, fname)
        dst = os.path.join(dest_radec, fname)
        if os.path.isfile(src):
            shutil.copy2(src, dst)
            print(f"  Overwrote {fname} in extracted_pak ({os.path.getsize(dst)} bytes)")

    print("\nStep 2: Packing extracted_pak with repak...")
    cmd = [
        REPAK_EXE,
        "pack",
        "-m", "../../../",
        "--version", "V11",
        "-p", str(PATH_HASH_SEED),
        EXTRACTED_PAK,
        TARGET_PAK
    ]
    subprocess.run(cmd, check=True)
    print(f"  Packed: {TARGET_PAK} ({os.path.getsize(TARGET_PAK)} bytes)")

    print("\nStep 3: Encrypting primary, PHI, and FDI index buffers with AES-256-ECB...")
    with open(TARGET_PAK, "rb") as f:
        data = bytearray(f.read())

    magic_idx = data.rfind(b"\xe1\x12\x6f\x5a")
    magic, ver, idx_off, idx_size = struct.unpack("<IIQQ", data[magic_idx : magic_idx + 24])
    print(f"  repak unencrypted index at {idx_off}, size {idx_size}")

    raw_idx = data[idx_off : idx_off + idx_size]
    idx_stream = io.BytesIO(raw_idx)
    str_len = struct.unpack("<i", idx_stream.read(4))[0]
    mount_point = idx_stream.read(str_len)
    rec_count = struct.unpack("<I", idx_stream.read(4))[0]
    seed = struct.unpack("<Q", idx_stream.read(8))[0]
    has_phi = struct.unpack("<I", idx_stream.read(4))[0]
    phi_off = struct.unpack("<Q", idx_stream.read(8))[0]
    phi_size = struct.unpack("<Q", idx_stream.read(8))[0]
    phi_hash = idx_stream.read(20)
    has_fdi = struct.unpack("<I", idx_stream.read(4))[0]
    fdi_off = struct.unpack("<Q", idx_stream.read(8))[0]
    fdi_size = struct.unpack("<Q", idx_stream.read(8))[0]
    fdi_hash = idx_stream.read(20)
    enc_rec_size = struct.unpack("<I", idx_stream.read(4))[0]
    enc_rec = idx_stream.read(enc_rec_size)
    unused_file_count = struct.unpack("<I", idx_stream.read(4))[0]

    raw_phi = data[phi_off : phi_off + phi_size]
    raw_fdi = data[fdi_off : fdi_off + fdi_size]

    # Pad phi and fdi to multiple of 16
    pad_phi = (16 - (len(raw_phi) % 16)) % 16
    padded_phi = raw_phi + b"\x00" * pad_phi
    pad_fdi = (16 - (len(raw_fdi) % 16)) % 16
    padded_fdi = raw_fdi + b"\x00" * pad_fdi

    new_phi_size = len(padded_phi)
    new_fdi_size = len(padded_fdi)

    # Calculate index size when padded to 16
    new_idx_unpadded_len = len(raw_idx)
    pad_idx = (16 - (new_idx_unpadded_len % 16)) % 16
    new_idx_size = new_idx_unpadded_len + pad_idx

    new_phi_off = idx_off + new_idx_size
    new_fdi_off = new_phi_off + new_phi_size

    # Rebuild primary index
    new_idx_buf = bytearray()
    new_idx_buf.extend(struct.pack("<i", str_len))
    new_idx_buf.extend(mount_point)
    new_idx_buf.extend(struct.pack("<I", rec_count))
    new_idx_buf.extend(struct.pack("<Q", seed))
    new_idx_buf.extend(struct.pack("<I", 1))
    new_idx_buf.extend(struct.pack("<Q", new_phi_off))
    new_idx_buf.extend(struct.pack("<Q", new_phi_size))
    new_idx_buf.extend(hashlib.sha1(padded_phi).digest())
    new_idx_buf.extend(struct.pack("<I", 1))
    new_idx_buf.extend(struct.pack("<Q", new_fdi_off))
    new_idx_buf.extend(struct.pack("<Q", new_fdi_size))
    new_idx_buf.extend(hashlib.sha1(padded_fdi).digest())
    new_idx_buf.extend(struct.pack("<I", enc_rec_size))
    new_idx_buf.extend(enc_rec)
    new_idx_buf.extend(struct.pack("<I", 0))

    pad_idx = (16 - (len(new_idx_buf) % 16)) % 16
    padded_idx = bytes(new_idx_buf) + b"\x00" * pad_idx
    idx_hash = hashlib.sha1(padded_idx).digest()

    def aes_enc(buf):
        cipher = Cipher(algorithms.AES(AES_KEY), modes.ECB(), backend=default_backend())
        e = cipher.encryptor()
        return e.update(buf) + e.finalize()

    enc_idx = aes_enc(padded_idx)
    enc_phi = aes_enc(padded_phi)
    enc_fdi = aes_enc(padded_fdi)

    orig_footer = bytearray(data[magic_idx - 17 :])
    orig_footer[16] = 1 # bEncrypted
    struct.pack_into("<IIQQ", orig_footer, 17, magic, ver, idx_off, len(enc_idx))
    orig_footer[41 : 61] = idx_hash

    new_pak = data[:idx_off] + enc_idx + enc_phi + enc_fdi + orig_footer
    with open(TARGET_PAK, "wb") as f:
        f.write(new_pak)
    print(f"  Encrypted pak generated: {len(new_pak)} bytes")

    print("\nStep 4: Verifying encrypted pak with repak...")
    test_cmd = [
        REPAK_EXE,
        "--aes-key", "0x" + AES_KEY_HEX,
        "info",
        TARGET_PAK
    ]
    proc = subprocess.run(test_cmd, capture_output=True, text=True)
    print(proc.stdout)
    if proc.stderr:
        print("repak stderr:", proc.stderr)

    if "encrypted index: true" in proc.stdout and "2432 file entries" in proc.stdout:
        print("Verification SUCCESSFUL! Copying to game folder...")
        shutil.copy2(TARGET_PAK, FINAL_GAME_PAK)
        print(f"Successfully installed translated pak to: {FINAL_GAME_PAK}")
    else:
        print("Verification FAILED! Not deploying to game folder.")

if __name__ == "__main__":
    main()
