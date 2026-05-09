"""
╔══════════════════════════════════════════════════════════╗
║           📝  NOTE-TAKING APP  — CLI INTERAKTIF          ║
║                                                          ║
║  Struktur Data:                                          ║
║  • Multi-linked list   → multiple tags per note          ║
║  • Doubly linked list  → chronological & alphabetical    ║
║  • Circular buffer     → sync status tracking            ║
╚══════════════════════════════════════════════════════════╝
"""

import os
import sys
from datetime import datetime
import time

R  = "\033[0m"          # reset
B  = "\033[1m"          # bold
DIM= "\033[2m"          # dim
CY = "\033[96m"         # cyan
GR = "\033[92m"         # green
YL = "\033[93m"         # yellow
RD = "\033[91m"         # red
MG = "\033[95m"         # magenta
BL = "\033[94m"         # blue
WH = "\033[97m"         # white
BG_DARK = "\033[40m"    # dark bg

def clr():
    os.system("cls" if os.name == "nt" else "clear")

def pause():
    input(f"\n{DIM}  ↩  Tekan Enter untuk lanjut...{R}")


class NoteNode:
    def __init__(self, note_id, title, content, tags=None):
        self.note_id    = note_id
        self.title      = title
        self.content    = content
        self.tags       = tags if tags else []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.prev_chrono = None
        self.next_chrono = None
        self.prev_alpha  = None
        self.next_alpha  = None


class TagNode:
    def __init__(self, name):
        self.name  = name
        self.notes = []

    def add_note(self, n):
        if n not in self.notes:
            self.notes.append(n)

    def remove_note(self, n):
        if n in self.notes:
            self.notes.remove(n)


class CircularBuffer:
    def __init__(self, cap=15):
        self.cap    = cap
        self.buf    = [None] * cap
        self.head   = 0
        self.size   = 0

    def push(self, ev):
        self.buf[self.head] = ev
        self.head = (self.head + 1) % self.cap
        if self.size < self.cap:
            self.size += 1

    def recent(self, n=10):
        if self.size == 0:
            return []
        out, idx = [], (self.head - 1) % self.cap
        for _ in range(min(n, self.size)):
            out.append(self.buf[idx])
            idx = (idx - 1) % self.cap
        return out


class ChronoList:
    def __init__(self):
        self.head = self.tail = None

    def insert_front(self, node):
        node.next_chrono = self.head
        node.prev_chrono = None
        if self.head:
            self.head.prev_chrono = node
        self.head = node
        if self.tail is None:
            self.tail = node

    def remove(self, node):
        if node.prev_chrono:
            node.prev_chrono.next_chrono = node.next_chrono
        else:
            self.head = node.next_chrono
        if node.next_chrono:
            node.next_chrono.prev_chrono = node.prev_chrono
        else:
            self.tail = node.prev_chrono
        node.prev_chrono = node.next_chrono = None

    def bump(self, node):
        self.remove(node)
        self.insert_front(node)

    def all(self):
        cur, out = self.head, []
        while cur:
            out.append(cur)
            cur = cur.next_chrono
        return out


class AlphaList:
    def __init__(self):
        self.head = None

    def insert(self, node):
        if not self.head:
            self.head = node
            node.prev_alpha = node.next_alpha = None
            return
        cur = self.head
        while cur and cur.title.lower() < node.title.lower():
            cur = cur.next_alpha
        if cur is None:
            tail = self.head
            while tail.next_alpha:
                tail = tail.next_alpha
            tail.next_alpha = node
            node.prev_alpha = tail
            node.next_alpha = None
        elif cur == self.head:
            node.next_alpha = self.head
            node.prev_alpha = None
            self.head.prev_alpha = node
            self.head = node
        else:
            p = cur.prev_alpha
            p.next_alpha = node
            node.prev_alpha = p
            node.next_alpha = cur
            cur.prev_alpha = node

    def remove(self, node):
        if node.prev_alpha:
            node.prev_alpha.next_alpha = node.next_alpha
        else:
            self.head = node.next_alpha
        if node.next_alpha:
            node.next_alpha.prev_alpha = node.prev_alpha
        node.prev_alpha = node.next_alpha = None

    def reinsert(self, node):
        self.remove(node)
        self.insert(node)

    def all(self):
        cur, out = self.head, []
        while cur:
            out.append(cur)
            cur = cur.next_alpha
        return out


class NoteManager:
    def __init__(self):
        self.notes      = {}
        self.tags       = {}
        self.chrono     = ChronoList()
        self.alpha      = AlphaList()
        self.sync_buf   = CircularBuffer(15)
        self._ctr       = 1

    def add(self, title, content, tags):
        nid  = self._ctr; self._ctr += 1
        node = NoteNode(nid, title, content, tags)
        self.notes[nid] = node
        self.chrono.insert_front(node)
        self.alpha.insert(node)
        for t in tags:
            self._link(node, t)
        self.sync_buf.push({"op": "CREATE", "id": nid, "title": title,
                            "ts": datetime.now(), "status": "PENDING"})
        return node

    def update(self, nid, title=None, content=None, tags=None):
        node = self.notes.get(nid)
        if not node:
            return None
        if title and title != node.title:
            node.title = title
            self.alpha.reinsert(node)
        if content:
            node.content = content
        if tags is not None:
            for t in node.tags:
                self._unlink(node, t)
            node.tags = tags
            for t in tags:
                self._link(node, t)
        node.updated_at = datetime.now()
        self.chrono.bump(node)
        self.sync_buf.push({"op": "UPDATE", "id": nid, "title": node.title,
                            "ts": datetime.now(), "status": "PENDING"})
        return node

    def delete(self, nid):
        node = self.notes.pop(nid, None)
        if not node:
            return False
        self.chrono.remove(node)
        self.alpha.remove(node)
        for t in node.tags:
            self._unlink(node, t)
        self.sync_buf.push({"op": "DELETE", "id": nid, "title": node.title,
                            "ts": datetime.now(), "status": "PENDING"})
        return True

    def sync_note(self, nid):
        node = self.notes.get(nid)
        if not node:
            return False
        self.sync_buf.push({"op": "SYNC", "id": nid, "title": node.title,
                            "ts": datetime.now(), "status": "SYNCED"})
        return True

    def by_tag(self, tag_name):
        t = self.tags.get(tag_name)
        return t.notes if t else []

    def _link(self, node, tag):
        if tag not in self.tags:
            self.tags[tag] = TagNode(tag)
        self.tags[tag].add_note(node)

    def _unlink(self, node, tag):
        if tag in self.tags:
            self.tags[tag].remove_note(node)

def header(title="📝 NOTE-TAKING APP"):
    clr()
    w = 56
    print(f"\n{CY}{'═'*w}{R}")
    print(f"{CY}║{B}{WH}  {title:<{w-4}}{R}{CY}  ║{R}")
    print(f"{CY}{'═'*w}{R}\n")

def section(title):
    print(f"\n{BL}{'─'*54}{R}")
    print(f"{BL}  {B}{title}{R}")
    print(f"{BL}{'─'*54}{R}")

def success(msg):  print(f"\n  {GR}✅ {msg}{R}")
def warn(msg):     print(f"\n  {YL}⚠️  {msg}{R}")
def error(msg):    print(f"\n  {RD}❌ {msg}{R}")
def info(msg):     print(f"  {CY}ℹ  {msg}{R}")

def tag_str(tags):
    if not tags:
        return f"{DIM}(no tags){R}"
    return " ".join(f"{MG}#{t}{R}" for t in tags)

def fmt_time(dt):
    return dt.strftime("%d %b %Y %H:%M")

def note_card(n, idx=None, show_content=False):
    prefix = f"  {YL}{idx}.{R} " if idx else "  "
    print(f"{prefix}{B}{WH}{n.title}{R}  {DIM}[ID:{n.note_id}]{R}")
    print(f"     {tag_str(n.tags)}")
    if show_content:
        content_lines = n.content.split('\n')
        for line in content_lines[:3]:
            print(f"     {DIM}{line}{R}")
        if len(content_lines) > 3:
            print(f"     {DIM}...{R}")
    print(f"     {DIM}Updated: {fmt_time(n.updated_at)}{R}")

def prompt(msg, default=""):
    val = input(f"  {CY}▸ {WH}{msg}{R}{DIM} {'['+default+'] ' if default else ''}{R}").strip()
    return val if val else default

def prompt_tags():
    raw = prompt("Tags (pisah koma, contoh: coding,belajar)")
    return [t.strip().lower() for t in raw.split(",") if t.strip()] if raw else []

def pick_note(nm, prompt_msg="Pilih ID note"):
    notes = nm.chrono.all()
    if not notes:
        warn("Tidak ada note.")
        return None
    try:
        nid = int(prompt(prompt_msg))
        node = nm.notes.get(nid)
        if not node:
            error(f"Note ID {nid} tidak ditemukan.")
        return node
    except ValueError:
        error("ID harus angka.")
        return None

def screen_list(nm):
    header("📋 SEMUA NOTES")
    notes = nm.chrono.all()
    if not notes:
        warn("Belum ada note. Buat note baru dulu!")
    else:
        section(f"Total: {len(notes)} note")
        for i, n in enumerate(notes, 1):
            note_card(n, i)
            print()
    pause()


def screen_add(nm):
    header("➕ BUAT NOTE BARU")
    print()
    title   = prompt("Judul note")
    if not title:
        error("Judul tidak boleh kosong.")
        pause(); return
    print(f"  {CY}▸ {WH}Konten note{R} {DIM}(Enter 2x untuk selesai){R}")
    lines = []
    while True:
        line = input("    ")
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)
    content = "\n".join(lines[:-1] if lines and lines[-1] == "" else lines)
    if not content:
        content = "(tidak ada konten)"
    tags = prompt_tags()

    node = nm.add(title, content, tags)
    success(f"Note '{node.title}' berhasil ditambahkan! (ID: {node.note_id})")
    pause()


def screen_view(nm):
    header("🔍 LIHAT DETAIL NOTE")
    notes = nm.chrono.all()
    if not notes:
        warn("Belum ada note."); pause(); return

    section("Daftar Notes")
    for i, n in enumerate(notes, 1):
        print(f"  {YL}{i}.{R} [{n.note_id}] {B}{n.title}{R}")

    node = pick_note(nm)
    if not node:
        pause(); return

    clr()
    print(f"\n{CY}{'═'*56}{R}")
    print(f"{CY}║{R}  {B}{WH}{node.title:<52}{R}{CY}  ║{R}")
    print(f"{CY}{'═'*56}{R}")
    print(f"\n  {DIM}ID      :{R} {node.note_id}")
    print(f"  {DIM}Tags    :{R} {tag_str(node.tags)}")
    print(f"  {DIM}Dibuat  :{R} {fmt_time(node.created_at)}")
    print(f"  {DIM}Update  :{R} {fmt_time(node.updated_at)}")
    print(f"\n{BL}{'─'*56}{R}")
    print(f"\n{node.content}\n")
    print(f"{BL}{'─'*56}{R}")
    pause()


def screen_edit(nm):
    header("✏️  EDIT NOTE")
    notes = nm.chrono.all()
    if not notes:
        warn("Belum ada note."); pause(); return

    section("Pilih note untuk diedit")
    for i, n in enumerate(notes, 1):
        print(f"  {YL}{i}.{R} [{n.note_id}] {B}{n.title}{R}  {tag_str(n.tags)}")

    node = pick_note(nm)
    if not node:
        pause(); return

    print(f"\n  {DIM}Edit note: {B}{node.title}{R}")
    print(f"  {DIM}(Tekan Enter untuk skip / tidak ubah){R}\n")

    new_title   = prompt(f"Judul baru", default=node.title)
    print(f"  {CY}▸ {WH}Konten baru{R} {DIM}(Enter 2x selesai, kosong = skip){R}")
    lines = []
    while True:
        line = input("    ")
        if line == "" and (not lines or lines[-1] == ""):
            break
        lines.append(line)
    new_content = "\n".join(lines).strip() or None

    print(f"  {DIM}Tags sekarang: {tag_str(node.tags)}{R}")
    raw_tags = prompt("Tags baru (kosong = tidak ubah)")
    new_tags = ([t.strip().lower() for t in raw_tags.split(",") if t.strip()]
                if raw_tags else None)

    nm.update(node.note_id,
              title   = new_title if new_title != node.title else None,
              content = new_content,
              tags    = new_tags)
    success(f"Note '{node.title}' berhasil diupdate!")
    pause()


def screen_delete(nm):
    header("🗑️  HAPUS NOTE")
    notes = nm.chrono.all()
    if not notes:
        warn("Belum ada note."); pause(); return

    section("Pilih note untuk dihapus")
    for i, n in enumerate(notes, 1):
        print(f"  {YL}{i}.{R} [{n.note_id}] {B}{n.title}{R}")

    node = pick_note(nm)
    if not node:
        pause(); return

    confirm = prompt(f"Hapus '{node.title}'? (y/N)").lower()
    if confirm == "y":
        nm.delete(node.note_id)
        success(f"Note '{node.title}' berhasil dihapus!")
    else:
        info("Penghapusan dibatalkan.")
    pause()


def screen_chrono(nm):
    header("📅 CHRONOLOGICAL VIEW")
    section("Urut: Terbaru → Terlama  (Doubly Linked List)")
    notes = nm.chrono.all()
    if not notes:
        warn("Belum ada note.")
    else:
        for i, n in enumerate(notes, 1):
            note_card(n, i, show_content=True)
            print()
    pause()


def screen_alpha(nm):
    header("🔤 ALPHABETICAL VIEW")
    section("Urut: A → Z  (Doubly Linked Sorted)")
    notes = nm.alpha.all()
    if not notes:
        warn("Belum ada note.")
    else:
        for i, n in enumerate(notes, 1):
            note_card(n, i)
            print()
    pause()


def screen_tags(nm):
    header("🏷️  TAG INDEX")
    section("Multi-linked list — satu tag ke banyak note")
    if not nm.tags:
        warn("Belum ada tag.")
    else:
        for tag_name, tnode in sorted(nm.tags.items()):
            active = [n for n in tnode.notes if n.note_id in nm.notes]
            if not active:
                continue
            print(f"  {MG}#{tag_name}{R}  {DIM}({len(active)} note){R}")
            for n in active:
                print(f"    {DIM}└─{R} [{n.note_id}] {n.title}")
            print()
    pause()


def screen_search_tag(nm):
    header("🔎 CARI BERDASARKAN TAG")
    if not nm.tags:
        warn("Belum ada tag."); pause(); return

    section("Tag tersedia")
    all_tags = sorted(nm.tags.keys())
    for i, t in enumerate(all_tags, 1):
        active = [n for n in nm.tags[t].notes if n.note_id in nm.notes]
        print(f"  {i}. {MG}#{t}{R}  {DIM}({len(active)} note){R}")

    tag_input = prompt("Masukkan nama tag").lower().strip()
    results   = nm.by_tag(tag_input)
    results   = [n for n in results if n.note_id in nm.notes]

    clr()
    print(f"\n{CY}  Hasil pencarian: {MG}#{tag_input}{R}")
    print(f"{CY}{'─'*54}{R}\n")
    if not results:
        warn(f"Tidak ada note dengan tag #{tag_input}")
    else:
        for i, n in enumerate(results, 1):
            note_card(n, i, show_content=True)
            print()
    pause()


def screen_sync(nm):
    header("🔄 SYNC STATUS TRACKER")
    section(f"Circular Buffer  (kapasitas: {nm.sync_buf.cap} slot)")

    notes = nm.chrono.all()
    if notes:
        print(f"  {DIM}Tandai note sebagai SYNCED:{R}")
        for n in notes:
            print(f"  [{n.note_id}] {n.title}")
        raw = prompt("ID note untuk disync (Enter untuk skip)").strip()
        if raw:
            try:
                nid = int(raw)
                if nm.sync_note(nid):
                    success(f"Note [{nid}] ditandai SYNCED!")
                else:
                    error(f"Note [{nid}] tidak ditemukan.")
            except ValueError:
                error("ID harus angka.")

    clr()
    header("🔄 SYNC LOG")
    section("Riwayat perubahan terbaru (terbaru di atas)")

    events = nm.sync_buf.recent()
    if not events:
        warn("Belum ada event sync.")
    else:
        op_color = {"CREATE": GR, "UPDATE": YL, "DELETE": RD, "SYNC": CY}
        op_icon  = {"CREATE": "＋", "UPDATE": "✎", "DELETE": "✕", "SYNC": "⟳"}
        status_icon = {"PENDING": f"{YL}⏳{R}", "SYNCED": f"{GR}✅{R}"}
        for i, ev in enumerate(events, 1):
            c  = op_color.get(ev["op"], WH)
            ic = op_icon.get(ev["op"], "•")
            si = status_icon.get(ev["status"], "")
            ts = ev["ts"].strftime("%H:%M:%S")
            print(f"  {DIM}{i:2}.{R} {si} {c}{ic} {ev['op']:6}{R}  "
                  f"[{ev['id']}] {B}{ev['title'][:28]}{R}  {DIM}{ts}{R}")

    print(f"\n{BL}{'─'*54}{R}")
    print(f"  {DIM}Buffer state  ({nm.sync_buf.size}/{nm.sync_buf.cap} terisi):{R}")
    bar = ""
    for i in range(nm.sync_buf.cap):
        if i < nm.sync_buf.size:
            bar += f"{GR}█{R}"
        else:
            bar += f"{DIM}░{R}"
    print(f"  {bar}")
    pause()


def screen_struct_info(nm):
    header("📊 INFO STRUKTUR DATA")

    section("Struktur yang Digunakan")
    structs = [
        ("dict notes",        "Hashmap",           f"O(1) akses by ID",      str(len(nm.notes)) + " note"),
        ("dict tags",         "Hashmap",           f"O(1) akses by tag",     str(len(nm.tags)) + " tag"),
        ("ChronoList",        "Doubly Linked List","Insert/delete O(1)",     str(len(nm.chrono.all())) + " node"),
        ("AlphaList",         "Doubly Linked List","Insert sorted O(n)",     str(len(nm.alpha.all())) + " node"),
        ("CircularBuffer",    "Ring Buffer",       f"Fixed {nm.sync_buf.cap} slots",f"{nm.sync_buf.size} event"),
    ]
    for name, stype, complexity, stat in structs:
        print(f"  {CY}{name:<18}{R} {YL}{stype:<20}{R} {DIM}{complexity:<20}{R} {GR}{stat}{R}")

    section("Tag Multi-Link Detail")
    for tag_name, tnode in sorted(nm.tags.items()):
        active = [n for n in tnode.notes if n.note_id in nm.notes]
        if active:
            ids = ", ".join(f"[{n.note_id}]" for n in active)
            print(f"  {MG}#{tag_name:<15}{R} → {ids}")

    section("Traversal Kronologis (head → tail)")
    cn = nm.chrono.head
    path = []
    while cn:
        path.append(f"[{cn.note_id}]")
        cn = cn.next_chrono
    print("  " + f" {DIM}↔{R} ".join(path) if path else "  (kosong)")

    section("Traversal Alfabetis (head → tail)")
    an = nm.alpha.head
    path = []
    while an:
        path.append(f"{an.title[:12]}")
        an = an.next_alpha
    print("  " + f" {DIM}→{R} ".join(path) if path else "  (kosong)")

    pause()


MENU = [
    ("1", "📋 Lihat Semua Notes",           screen_list),
    ("2", "➕ Buat Note Baru",              screen_add),
    ("3", "🔍 Detail Note",                 screen_view),
    ("4", "✏️  Edit Note",                  screen_edit),
    ("5", "🗑️  Hapus Note",                 screen_delete),
    ("─", None, None),
    ("6", "📅 Chronological View",          screen_chrono),
    ("7", "🔤 Alphabetical View",           screen_alpha),
    ("8", "🏷️  Tag Index",                  screen_tags),
    ("9", "🔎 Cari by Tag",                 screen_search_tag),
    ("─", None, None),
    ("s", "🔄 Sync Status / Log",           screen_sync),
    ("i", "📊 Info Struktur Data",          screen_struct_info),
    ("q", "🚪 Keluar",                      None),
]

def main_menu(nm):
    while True:
        header("📝 NOTE-TAKING APP")
        print(f"  {DIM}Struktur Data: Multi-linked • Doubly Linked • Circular Buffer{R}\n")
        print(f"  {DIM}Notes: {len(nm.notes)}  |  Tags: {len(nm.tags)}  |  Sync log: {nm.sync_buf.size}/{nm.sync_buf.cap}{R}\n")

        for key, label, _ in MENU:
            if key == "─":
                print(f"  {DIM}{'·'*42}{R}")
            else:
                print(f"  {YL}[{key}]{R}  {label}")

        print()
        choice = prompt("Pilih menu").lower().strip()

        for key, label, fn in MENU:
            if key == choice and fn is not None:
                fn(nm)
                break
            elif key == choice and key == "q":
                header("👋 SAMPAI JUMPA!")
                print(f"  {GR}Terima kasih sudah menggunakan Note-Taking App!{R}\n")
                sys.exit(0)
        else:
            if choice not in [k for k, _, _ in MENU]:
                error("Pilihan tidak valid.")
                time.sleep(0.8)


def seed(nm):
    """Isi data awal supaya langsung bisa dicoba."""
    nm.add("Belajar Python OOP",
           "Pelajari class, inheritance, encapsulation, dan polymorphism.\n"
           "Referensi: docs.python.org",
           ["coding", "belajar"])
    nm.add("Algoritma Sorting",
           "Bubble sort O(n²), Merge sort O(n log n), Quick sort O(n log n).\n"
           "Latihan: implementasikan semua dari scratch.",
           ["coding", "algoritma"])
    nm.add("Agenda Meeting Senin",
           "- Review sprint minggu lalu\n- Demo fitur baru\n- Planning sprint berikutnya",
           ["kerja", "penting"])
    nm.add("Resep Nasi Goreng Spesial",
           "Bahan: nasi, telur, bawang merah, kecap, saus tiram.\n"
           "Masak api besar supaya smoky!",
           ["masak", "favorit"])
    nm.add("Catatan Harian",
           "Hari ini belajar struktur data doubly linked list.\n"
           "Lumayan paham sekarang!",
           ["harian", "belajar"])



if __name__ == "__main__":
    nm = NoteManager()

    clr()
    print(f"\n{CY}{'═'*56}{R}")
    print(f"{CY}║{B}{WH}  📝  NOTE-TAKING APP — SELAMAT DATANG!{' '*14}{R}{CY}║{R}")
    print(f"{CY}{'═'*56}{R}\n")
    print(f"  {DIM}Muat data contoh supaya bisa langsung dicoba?{R}")
    ans = input(f"  {CY}▸ {WH}Load sample data? (Y/n): {R}").strip().lower()
    if ans != "n":
        seed(nm)
        print(f"  {GR}✅ 5 sample note berhasil dimuat!{R}")
        time.sleep(1)

    main_menu(nm)