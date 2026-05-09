from datetime import datetime

class NoteNode:
    def __init__(self, note_id, title, content, tags=None):
        self.note_id = note_id
        self.title = title
        self.content = content
        self.tags = tags if tags else []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.prev_chrono = None
        self.next_chrono = None
        self.prev_alpha = None
        self.next_alpha = None


class TagNode:
    def __init__(self, name):
        self.name = name
        self.notes = []

    def add_note(self, n):
        if n not in self.notes:
            self.notes.append(n)

    def remove_note(self, n):
        if n in self.notes:
            self.notes.remove(n)


class CircularBuffer:
    def __init__(self, cap=15):
        self.cap = cap
        self.buf = [None] * cap
        self.head = 0
        self.size = 0

    def push(self, ev):
        self.buf[self.head] = ev
        self.head = (self.head + 1) % self.cap
        if self.size < self.cap:
            self.size += 1

    def recent(self, n=15):
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
        self.notes = {}
        self.tags = {}
        self.chrono = ChronoList()
        self.alpha = AlphaList()
        self.sync_buf = CircularBuffer(15)
        self._ctr = 1

    def add(self, title, content, tags):
        nid = self._ctr
        self._ctr += 1
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
        if content is not None:
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
        return [n for n in t.notes if n.note_id in self.notes] if t else []

    def search(self, query):
        q = query.lower()
        return [n for n in self.chrono.all()
                if q in n.title.lower() or q in n.content.lower()
                or any(q in tag for tag in n.tags)]

    def _link(self, node, tag):
        if tag not in self.tags:
            self.tags[tag] = TagNode(tag)
        self.tags[tag].add_note(node)

    def _unlink(self, node, tag):
        if tag in self.tags:
            self.tags[tag].remove_note(node)


def seed(nm):
    nm.add("Belajar Python OOP",
           "Pelajari class, inheritance, encapsulation, dan polymorphism.\nReferensi: docs.python.org\n\nContoh kode:\nclass Animal:\n    def __init__(self, name):\n        self.name = name\n    def speak(self):\n        pass",
           ["coding", "belajar"])
    nm.add("Algoritma Sorting",
           "Bubble sort O(n²), Merge sort O(n log n), Quick sort O(n log n).\nLatihan: implementasikan semua dari scratch.\n\nTips: pahami dulu konsep dasar sebelum optimasi.",
           ["coding", "algoritma"])
    nm.add("Agenda Meeting Senin",
           "- Review sprint minggu lalu\n- Demo fitur baru\n- Planning sprint berikutnya\n- Diskusi arsitektur database\n- AOB",
           ["kerja", "penting"])
    nm.add("Resep Nasi Goreng Spesial",
           "Bahan: nasi, telur, bawang merah, kecap, saus tiram.\nMasak api besar supaya smoky!\n\nLangkah:\n1. Panaskan wajan\n2. Tumis bawang\n3. Masukkan nasi\n4. Tambahkan bumbu",
           ["masak", "favorit"])
    nm.add("Catatan Harian",
           "Hari ini belajar struktur data doubly linked list.\nLumayan paham sekarang!\n\nBesok lanjut circular buffer dan multi-linked list.",
           ["harian", "belajar"])