"""Writes a minimal Outlook .msg (Compound File, version 3) for tests: a plain-text body and
optional attachments. Only test_itin.py uses it; the app reads .msg files with app/itin.js."""
import struct
END, FREE, FATSECT = 0xFFFFFFFE, 0xFFFFFFFF, 0xFFFFFFFD
SS, MS, CUTOFF = 512, 64, 4096
def _u16(s): return s.encode("utf-16le") + b"\0\0"
def write(path, body, attachments=()):
    # tree: root -> [__substg1.0_1000001F, __attach_version1.0_#0000000N -> [data, names, mime]]
    ents = [{"name": "Root Entry", "type": 5, "kids": []}]
    def add(parent, name, typ, data=b""):
        ents.append({"name": name, "type": typ, "data": data, "kids": []}); ents[parent]["kids"].append(len(ents) - 1); return len(ents) - 1
    add(0, "__substg1.0_1000001F", 2, body.encode("utf-16le"))
    for i, (name, mime, data) in enumerate(attachments):
        a = add(0, f"__attach_version1.0_#{i:08X}", 1)
        add(a, "__substg1.0_37010102", 2, data); add(a, "__substg1.0_3707001F", 2, name.encode("utf-16le")); add(a, "__substg1.0_370E001F", 2, mime.encode("utf-16le"))
    # streams below the cutoff go in the mini stream
    mini, minifat = bytearray(), []
    big = []
    for i, e in enumerate(ents):
        if e["type"] != 2: continue
        d = e["data"]; e["size"] = len(d)
        if len(d) < CUTOFF:
            n = (len(d) + MS - 1) // MS or 1; e["start"] = len(minifat)
            minifat += [len(minifat) + k + 1 for k in range(n)]; minifat[-1] = END
            mini += d + b"\0" * (n * MS - len(d))
        else: big.append(e)
    nsec = lambda nbytes: (nbytes + SS - 1) // SS
    dir_secs, mfat_secs, mini_secs = nsec(len(ents) * 128), nsec(len(minifat) * 4), nsec(len(mini))
    big_secs = sum(nsec(e["size"]) for e in big)
    fat_secs = 1
    while (fat_secs + dir_secs + mfat_secs + mini_secs + big_secs) > fat_secs * (SS // 4): fat_secs += 1
    fat = [FATSECT] * fat_secs; pos = fat_secs
    def run(n):
        nonlocal pos
        start = pos
        for k in range(n): fat.append(start + k + 1 if k < n - 1 else END)
        pos += n; return start
    dir_start = run(dir_secs); mfat_start = run(mfat_secs) if mfat_secs else END
    ents[0]["start"] = run(mini_secs) if mini_secs else END; ents[0]["size"] = len(mini)
    for e in big: e["start"] = run(nsec(e["size"]))
    fat += [FREE] * (fat_secs * (SS // 4) - len(fat))
    # directory: children of a storage as a chain of right siblings
    for e in ents: e["left"] = e["right"] = e["child"] = FREE
    for e in ents:
        k = e["kids"]
        if k: e["child"] = k[0]
        for a, b in zip(k, k[1:]): ents[a]["right"] = b
    d = bytearray()
    for e in ents:
        nm = _u16(e["name"]); rec = nm + b"\0" * (64 - len(nm))
        rec += struct.pack("<HBB3I", len(nm), e["type"], 1, e["left"], e["right"], e["child"]) + b"\0" * 36
        rec += struct.pack("<IQ", e.get("start", 0) if e["type"] != 1 else 0, e.get("size", 0)); d += rec
    d += b"\0" * (dir_secs * SS - len(d))
    hdr = bytearray(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\0" * 16 + struct.pack("<HHHHH", 0x3E, 3, 0xFFFE, 9, 6) + b"\0" * 6)
    hdr += struct.pack("<IIIIIIIII", 0, fat_secs, dir_start, 0, CUTOFF, mfat_start, mfat_secs, END, 0)
    hdr += b"".join(struct.pack("<I", i if i < fat_secs else FREE) for i in range(109))
    out = bytes(hdr) + struct.pack(f"<{len(fat)}I", *fat) + bytes(d)
    out += struct.pack(f"<{len(minifat)}I", *minifat) + b"\xff" * (mfat_secs * SS - len(minifat) * 4) if mfat_secs else b""
    out += bytes(mini) + b"\0" * (mini_secs * SS - len(mini))
    for e in big: out += e["data"] + b"\0" * (nsec(e["size"]) * SS - e["size"])
    open(path, "wb").write(out)
