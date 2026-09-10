import os
import struct
import zlib
import json
from build_french_mod import (
    clean_retro_text,
    compress_and_scramble,
    VariantReader,
    VariantWriter,
    SCRATCH_DIR,
    DECOMP_DIR,
    MOD_STAGING
)
from translate_phase1 import encode_radec, stage_file

def assemble_dialogue():
    merged = {}
    missing_chunks = []
    for b in range(1, 5):
        chunk_file = os.path.join(SCRATCH_DIR, f"dialogue_chunk_{b}_fr.json")
        if not os.path.exists(chunk_file):
            missing_chunks.append(chunk_file)
            continue
        with open(chunk_file, 'r', encoding='utf-8') as fp:
            data = json.load(fp)
            print(f"Loaded chunk {b}: {len(data)} items")
            merged.update(data)

    if missing_chunks:
        print(f"Waiting on chunks: {missing_chunks}")
        return False

    print(f"Total merged dialogue entries: {len(merged)}")
    if len(merged) != 544:
        print(f"Warning: Expected 544 items, got {len(merged)}")

    # Load original bin
    src_bin = os.path.join(DECOMP_DIR, "353109016.bin")
    with open(src_bin, 'rb') as fp:
        tree = VariantReader(fp.read()).parse()
    rows = dict(dict(tree[1])['rows'][1])

    applied = 0
    for k, v in rows.items():
        if k in merged:
            fr_text = clean_retro_text(merged[k])
            clean_bytes = fr_text.encode('latin1')
            rows[k][1][0] = ('str', encode_radec(clean_bytes))
            applied += 1
        else:
            print(f"Missing dialogue translation for {k}!")

    print(f"Dialogue: Applied {applied}/{len(rows)} French translations.")
    writer = VariantWriter()
    writer.write(tree)
    new_bin = bytes(writer.buf)

    stage_file("353109016", new_bin)
    print("353109016 staged successfully!")
    return True

if __name__ == "__main__":
    assemble_dialogue()
