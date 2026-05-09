"""
=============================================================
  STRUKTUR DATA APLIKASI NOTE-TAKING
=============================================================
  Fitur:
  1. Multiple Tags per Note  → Multi-linked list (many-to-many)
  2. Chronological & Alpha   → Doubly Linked List (sorted)
  3. Sync Status Tracking    → Circular Buffer (ring buffer)
=============================================================
"""

from datetime import datetime
import time


# ─────────────────────────────────────────────────────────────
# BAGIAN 1: NODE & STRUKTUR DASAR
# ─────────────────────────────────────────────────────────────

class NoteNode:
    """Node untuk satu catatan dalam Doubly Linked List."""
    def __init__(self, note_id, title, content, tags=None):
        self.note_id   = note_id
        self.title     = title
        self.content   = content
        self.tags      = tags if tags else []   # list of tag names
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

        # Pointer doubly linked list (kronologis)
        self.prev_chrono = None
        self.next_chrono = None

        # Pointer doubly linked list (alfabetis)
        self.prev_alpha  = None
        self.next_alpha  = None

    def __repr__(self):
        return f"NoteNode(id={self.note_id}, title='{self.title}')"


class TagNode:
    """Node untuk satu tag. Menyimpan referensi ke semua note yang pakai tag ini."""
    def __init__(self, tag_name):
        self.tag_name = tag_name
        self.notes    = []   # list of NoteNode (multi-linked)

    def add_note(self, note_node):
        if note_node not in self.notes:
            self.notes.append(note_node)

    def remove_note(self, note_node):
        if note_node in self.notes:
            self.notes.remove(note_node)

    def __repr__(self):
        return f"TagNode(tag='{self.tag_name}', notes={len(self.notes)})"


# ─────────────────────────────────────────────────────────────
# BAGIAN 2: CIRCULAR BUFFER (untuk Sync Status Tracking)
# ─────────────────────────────────────────────────────────────

class CircularBuffer:
    """
    Ring buffer ukuran tetap untuk melacak perubahan terbaru.
    Kalau penuh, data paling lama otomatis ditimpa.
    """
    def __init__(self, capacity=10):
        self.capacity = capacity
        self.buffer   = [None] * capacity
        self.head     = 0   # index tulis berikutnya
        self.size     = 0   # jumlah item aktif

    def push(self, event):
        """Tambahkan event perubahan ke buffer."""
        self.buffer[self.head] = event
        self.head = (self.head + 1) % self.capacity
        if self.size < self.capacity:
            self.size += 1

    def get_recent(self):
        """Ambil semua event dari yang terbaru ke terlama."""
        if self.size == 0:
            return []
        result = []
        # mulai dari slot sebelum head (paling baru)
        idx = (self.head - 1) % self.capacity
        for _ in range(self.size):
            result.append(self.buffer[idx])
            idx = (idx - 1) % self.capacity
        return result

    def __repr__(self):
        return f"CircularBuffer(capacity={self.capacity}, size={self.size})"


# ─────────────────────────────────────────────────────────────
# BAGIAN 3: DOUBLY LINKED LIST (Kronologis & Alfabetis)
# ─────────────────────────────────────────────────────────────

class ChronologicalList:
    """
    Doubly linked list urut berdasarkan waktu (terbaru di depan).
    """
    def __init__(self):
        self.head = None
        self.tail = None

    def insert(self, note_node):
        """Insert di depan (terbaru dulu)."""
        note_node.next_chrono = self.head
        note_node.prev_chrono = None
        if self.head:
            self.head.prev_chrono = note_node
        self.head = note_node
        if self.tail is None:
            self.tail = note_node

    def remove(self, note_node):
        if note_node.prev_chrono:
            note_node.prev_chrono.next_chrono = note_node.next_chrono
        else:
            self.head = note_node.next_chrono
        if note_node.next_chrono:
            note_node.next_chrono.prev_chrono = note_node.prev_chrono
        else:
            self.tail = note_node.prev_chrono
        note_node.prev_chrono = None
        note_node.next_chrono = None

    def move_to_front(self, note_node):
        """Pindahkan note ke depan saat di-update."""
        self.remove(note_node)
        self.insert(note_node)

    def traverse_forward(self):
        result = []
        current = self.head
        while current:
            result.append(current)
            current = current.next_chrono
        return result

    def traverse_backward(self):
        result = []
        current = self.tail
        while current:
            result.append(current)
            current = current.prev_chrono
        return result


class AlphabeticalList:
    """
    Doubly linked list urut A–Z berdasarkan judul.
    """
    def __init__(self):
        self.head = None

    def insert(self, note_node):
        """Insert pada posisi yang benar secara alfabetis."""
        if self.head is None:
            self.head = note_node
            note_node.prev_alpha = None
            note_node.next_alpha = None
            return

        current = self.head
        while current and current.title.lower() < note_node.title.lower():
            current = current.next_alpha

        if current is None:
            # Insert di akhir
            tail = self.head
            while tail.next_alpha:
                tail = tail.next_alpha
            tail.next_alpha = note_node
            note_node.prev_alpha = tail
            note_node.next_alpha = None
        elif current == self.head:
            # Insert di depan
            note_node.next_alpha = self.head
            note_node.prev_alpha = None
            self.head.prev_alpha = note_node
            self.head = note_node
        else:
            # Insert di tengah
            prev_node = current.prev_alpha
            prev_node.next_alpha = note_node
            note_node.prev_alpha = prev_node
            note_node.next_alpha = current
            current.prev_alpha = note_node

    def remove(self, note_node):
        if note_node.prev_alpha:
            note_node.prev_alpha.next_alpha = note_node.next_alpha
        else:
            self.head = note_node.next_alpha
        if note_node.next_alpha:
            note_node.next_alpha.prev_alpha = note_node.prev_alpha
        note_node.prev_alpha = None
        note_node.next_alpha = None

    def reinsert(self, note_node):
        """Hapus dan masukkan ulang setelah title berubah."""
        self.remove(note_node)
        self.insert(note_node)

    def traverse(self):
        result = []
        current = self.head
        while current:
            result.append(current)
            current = current.next_alpha
        return result


# ─────────────────────────────────────────────────────────────
# BAGIAN 4: NOTE MANAGER (sistem utama)
# ─────────────────────────────────────────────────────────────

class NoteManager:
    """
    Mengelola semua catatan dengan struktur data:
    - dict notes           → akses cepat O(1) via note_id
    - dict tags            → akses cepat O(1) via tag_name
    - ChronologicalList    → doubly linked, urut waktu
    - AlphabeticalList     → doubly linked, urut A-Z
    - CircularBuffer       → ring buffer 10 slot sync events
    """
    def __init__(self, sync_buffer_size=10):
        self.notes         = {}                              # id → NoteNode
        self.tags          = {}                              # name → TagNode
        self.chrono_list   = ChronologicalList()
        self.alpha_list    = AlphabeticalList()
        self.sync_buffer   = CircularBuffer(sync_buffer_size)
        self._id_counter   = 1

    # ── CREATE ─────────────────────────────────────────────
    def add_note(self, title, content, tags=None):
        note_id   = self._id_counter
        self._id_counter += 1
        tags      = tags if tags else []

        node = NoteNode(note_id, title, content, tags)

        # Simpan di dict
        self.notes[note_id] = node

        # Masukkan ke doubly linked lists
        self.chrono_list.insert(node)
        self.alpha_list.insert(node)

        # Hubungkan ke tag nodes (multi-linked)
        for tag_name in tags:
            self._link_tag(node, tag_name)

        # Catat di circular buffer
        self.sync_buffer.push({
            "action"  : "CREATE",
            "note_id" : note_id,
            "title"   : title,
            "time"    : datetime.now().strftime("%H:%M:%S"),
            "status"  : "PENDING"
        })

        print(f"  ✅ Note ditambahkan: [{note_id}] '{title}' | Tags: {tags}")
        return node

    # ── READ ───────────────────────────────────────────────
    def get_note(self, note_id):
        return self.notes.get(note_id)

    # ── UPDATE ─────────────────────────────────────────────
    def update_note(self, note_id, title=None, content=None, tags=None):
        node = self.notes.get(note_id)
        if not node:
            print(f"  ❌ Note ID {note_id} tidak ditemukan.")
            return

        old_title = node.title

        if title:
            node.title = title
            # Re-sort di alpha list
            self.alpha_list.reinsert(node)

        if content:
            node.content = content

        if tags is not None:
            # Hapus link tag lama
            for tag_name in node.tags:
                self._unlink_tag(node, tag_name)
            node.tags = tags
            # Buat link tag baru
            for tag_name in tags:
                self._link_tag(node, tag_name)

        node.updated_at = datetime.now()
        # Pindahkan ke depan di chrono list
        self.chrono_list.move_to_front(node)

        self.sync_buffer.push({
            "action"  : "UPDATE",
            "note_id" : note_id,
            "title"   : node.title,
            "time"    : datetime.now().strftime("%H:%M:%S"),
            "status"  : "PENDING"
        })

        print(f"  ✏️  Note diupdate: [{note_id}] '{old_title}' → '{node.title}'")

    # ── DELETE ─────────────────────────────────────────────
    def delete_note(self, note_id):
        node = self.notes.get(note_id)
        if not node:
            print(f"  ❌ Note ID {note_id} tidak ditemukan.")
            return

        # Lepas dari semua linked list
        self.chrono_list.remove(node)
        self.alpha_list.remove(node)

        # Lepas dari semua tag
        for tag_name in node.tags:
            self._unlink_tag(node, tag_name)

        del self.notes[note_id]

        self.sync_buffer.push({
            "action"  : "DELETE",
            "note_id" : note_id,
            "title"   : node.title,
            "time"    : datetime.now().strftime("%H:%M:%S"),
            "status"  : "PENDING"
        })

        print(f"  🗑️  Note dihapus: [{note_id}] '{node.title}'")

    # ── TAG HELPERS ────────────────────────────────────────
    def _link_tag(self, note_node, tag_name):
        if tag_name not in self.tags:
            self.tags[tag_name] = TagNode(tag_name)
        self.tags[tag_name].add_note(note_node)

    def _unlink_tag(self, note_node, tag_name):
        if tag_name in self.tags:
            self.tags[tag_name].remove_note(note_node)

    def get_notes_by_tag(self, tag_name):
        tag = self.tags.get(tag_name)
        if not tag:
            return []
        return tag.notes

    # ── SYNC STATUS ────────────────────────────────────────
    def mark_synced(self, note_id):
        """Tandai note sudah tersinkronisasi."""
        self.sync_buffer.push({
            "action"  : "SYNC",
            "note_id" : note_id,
            "title"   : self.notes[note_id].title if note_id in self.notes else "?",
            "time"    : datetime.now().strftime("%H:%M:%S"),
            "status"  : "SYNCED"
        })
        print(f"  🔄 Note [{note_id}] ditandai SYNCED")

    # ── DISPLAY ────────────────────────────────────────────
    def show_chrono_view(self):
        print("\n" + "="*55)
        print("  📅 CHRONOLOGICAL VIEW (terbaru → terlama)")
        print("="*55)
        notes = self.chrono_list.traverse_forward()
        if not notes:
            print("  (kosong)")
        for i, n in enumerate(notes, 1):
            print(f"  {i}. [{n.note_id}] {n.title}")
            print(f"      Tags    : {n.tags}")
            print(f"      Updated : {n.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")

    def show_alpha_view(self):
        print("\n" + "="*55)
        print("  🔤 ALPHABETICAL VIEW (A → Z)")
        print("="*55)
        notes = self.alpha_list.traverse()
        if not notes:
            print("  (kosong)")
        for i, n in enumerate(notes, 1):
            print(f"  {i}. [{n.note_id}] {n.title}")
            print(f"      Tags: {n.tags}")

    def show_tag_index(self):
        print("\n" + "="*55)
        print("  🏷️  TAG INDEX (multi-linked)")
        print("="*55)
        if not self.tags:
            print("  (tidak ada tag)")
        for tag_name, tag_node in sorted(self.tags.items()):
            note_titles = [f"[{n.note_id}]{n.title}" for n in tag_node.notes]
            print(f"  #{tag_name}")
            print(f"    → {', '.join(note_titles)}")

    def show_sync_log(self):
        print("\n" + "="*55)
        print("  🔄 SYNC LOG (circular buffer — terbaru dulu)")
        print("="*55)
        events = self.sync_buffer.get_recent()
        if not events:
            print("  (belum ada event)")
        for i, ev in enumerate(events, 1):
            status_icon = "✅" if ev["status"] == "SYNCED" else "⏳"
            print(f"  {i}. {status_icon} [{ev['time']}] {ev['action']:6s} "
                  f"→ [{ev['note_id']}] '{ev['title']}' ({ev['status']})")



def separator(title):
    print(f"\n{'─'*55}")
    print(f"  {title}")
    print(f"{'─'*55}")

def main():
    print("="*55)
    print("  STRUKTUR DATA: APLIKASI NOTE-TAKING")
    print("="*55)

    nm = NoteManager(sync_buffer_size=10)

    separator("1️⃣  MENAMBAHKAN NOTES")
    time.sleep(0.01)
    n1 = nm.add_note("Belajar Python",
                     "Mempelajari dasar-dasar Python.",
                     tags=["coding", "belajar"])
    time.sleep(0.01)
    n2 = nm.add_note("Resep Nasi Goreng",
                     "Bahan: nasi, telur, kecap...",
                     tags=["masak", "favorit"])
    time.sleep(0.01)
    n3 = nm.add_note("Algoritma Sorting",
                     "Bubble sort, merge sort, quick sort.",
                     tags=["coding", "algoritma"])
    time.sleep(0.01)
    n4 = nm.add_note("Agenda Meeting",
                     "Meeting Senin jam 10 pagi.",
                     tags=["kerja", "belajar"])
    time.sleep(0.01)
    n5 = nm.add_note("Catatan Harian",
                     "Hari ini produktif sekali.",
                     tags=["favorit"])

    nm.show_chrono_view()
    nm.show_alpha_view()
    nm.show_tag_index()

    separator("2️⃣  CARI NOTE BERDASARKAN TAG")
    for tag in ["coding", "belajar", "favorit"]:
        results = nm.get_notes_by_tag(tag)
        print(f"  #{tag} → {[f'[{n.note_id}]{n.title}' for n in results]}")

    separator("3️⃣  UPDATE NOTE")
    nm.update_note(n1.note_id,
                   title="Belajar Python & OOP",
                   tags=["coding", "belajar", "favorit"])
    nm.update_note(n3.note_id,
                   content="Diperbaharui: tambah heap sort.")

    nm.show_chrono_view()
    nm.show_alpha_view()
    nm.show_tag_index()

    separator("4️⃣  HAPUS NOTE")
    nm.delete_note(n2.note_id)

    nm.show_chrono_view()
    nm.show_tag_index()

    separator("5️⃣  SYNC STATUS (Circular Buffer)")
    nm.mark_synced(n1.note_id)
    nm.mark_synced(n4.note_id)

    nm.show_sync_log()

    separator("📊 RINGKASAN STRUKTUR DATA")
    print(f"  Total notes aktif  : {len(nm.notes)}")
    print(f"  Total tags         : {len(nm.tags)}")
    print(f"  Sync buffer size   : {nm.sync_buffer.capacity} slot")
    print(f"  Sync events tercatat: {nm.sync_buffer.size}")
    print()
    print("  Struktur yang digunakan:")
    print("  ┌─ dict notes        → O(1) akses by ID")
    print("  ├─ dict tags         → O(1) akses by name")
    print("  ├─ ChronologicalList → Doubly Linked (urut waktu)")
    print("  ├─ AlphabeticalList  → Doubly Linked (urut A-Z)")
    print("  └─ CircularBuffer    → Ring Buffer (sync tracking)")
    print()
    print("="*55)
    print("  ✅ Demo selesai!")
    print("="*55)


if __name__ == "__main__":
    main()