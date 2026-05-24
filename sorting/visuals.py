"""
Tugas: Analisis & Desain Algoritma Sorting Lanjutan + Binary Tree
Nama  : Lionel Jevon Chrismana Putra
NIM   : 25091397019
Kelas : 2025A
Versi : GUI Tkinter dengan Visualisasi Dinamis
"""

import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
import math
import time
import random
import threading
from typing import List, Optional
from collections import deque

C = {
    "sidebar_bg"   : "#0F172A",   
    "sidebar_hover": "#1E293B",
    "sidebar_active": "#1E293B",
    "accent"       : "#6C63FF",  
    "accent2"      : "#10B981",   
    "accent3"      : "#F59E0B",   
    "accent4"      : "#EF4444",   
    "content_bg"   : "#F8FAFC",
    "card_bg"      : "#FFFFFF",
    "text_dark"    : "#0F172A",
    "text_mid"     : "#475569",
    "text_light"   : "#94A3B8",
    "text_white"   : "#F8FAFC",
    "border"       : "#E2E8F0",
    "bar_default"  : "#6C63FF",
    "bar_compare"  : "#F59E0B",
    "bar_sorted"   : "#10B981",
    "bar_pivot"    : "#EF4444",
    "canvas_bg"    : "#0F172A",
}

class ListNode:
    def __init__(self, data, next=None):
        self.data = data
        self.next = next

class AdvancedSorter:
    def __init__(self):
        self.steps = []      
        self.comparisons = 0
        self.swaps = 0

    def reset_stats(self):
        self.steps = []
        self.comparisons = 0
        self.swaps = 0

    def _snapshot(self, arr, highlights=None, label=""):
        self.steps.append((list(arr), highlights or [], label))

    def sort_array(self, arr: List[int]) -> List[int]:
        self.reset_stats()
        if len(arr) <= 1:
            return arr
        tmp_array = [0] * len(arr)
        self._snapshot(arr, [], "Input awal")
        self._rec_merge_sort(arr, 0, len(arr) - 1, tmp_array)
        self._snapshot(arr, list(range(len(arr))), "Selesai! ✓")
        return arr

    def _rec_merge_sort(self, arr, first, last, tmp_array):
        if first >= last:
            return
        mid = (first + last) // 2
        self._rec_merge_sort(arr, first, mid, tmp_array)
        self._rec_merge_sort(arr, mid + 1, last, tmp_array)
        self._merge_virtual(arr, first, mid, last, tmp_array)

    def _merge_virtual(self, arr, left_start, mid, right_end, tmp_array):
        a, b, k = left_start, mid + 1, left_start
        while a <= mid and b <= right_end:
            self.comparisons += 1
            if arr[a] <= arr[b]:
                tmp_array[k] = arr[a]; a += 1
            else:
                tmp_array[k] = arr[b]; b += 1
            k += 1
        while a <= mid:
            tmp_array[k] = arr[a]; a += 1; k += 1
        while b <= right_end:
            tmp_array[k] = arr[b]; b += 1; k += 1
        for i in range(left_start, right_end + 1):
            arr[i] = tmp_array[i]
        highlights = list(range(left_start, right_end + 1))
        self._snapshot(arr, highlights, f"Merge [{left_start}..{mid}] + [{mid+1}..{right_end}]")

    def sort_linked_list(self, head: Optional[ListNode]) -> Optional[ListNode]:
        self.reset_stats()
        if head is None or head.next is None:
            return head
        return self._ll_merge_sort(head)

    def _ll_merge_sort(self, head):
        if head is None or head.next is None:
            return head
        right_head = self._split_linked_list(head)
        left_sorted  = self._ll_merge_sort(head)
        right_sorted = self._ll_merge_sort(right_head)
        return self._merge_linked_lists(left_sorted, right_sorted)

    def _split_linked_list(self, head):
        midPoint = head
        curNode  = head.next
        while curNode is not None and curNode.next is not None:
            midPoint = midPoint.next
            curNode  = curNode.next.next
        right_head    = midPoint.next
        midPoint.next = None
        return right_head

    def _merge_linked_lists(self, listA, listB):
        dummy = ListNode(0)
        tail  = dummy
        while listA is not None and listB is not None:
            self.comparisons += 1
            if listA.data <= listB.data:
                tail.next = listA; listA = listA.next
            else:
                tail.next = listB; listB = listB.next
            tail = tail.next
        tail.next = listA if listA is not None else listB
        return dummy.next

    def sort_array_quick(self, arr: List[int]) -> List[int]:
        self.reset_stats()
        if len(arr) <= 1:
            return arr
        self._snapshot(arr, [], "Input awal")
        self._quick_sort_recursive(arr, 0, len(arr) - 1, depth=0)
        self._snapshot(arr, list(range(len(arr))), "Selesai! ✓")
        return arr

    def _quick_sort_recursive(self, arr, first, last, depth):
        if first >= last:
            return
        n = last - first + 1
        if n > 1 and depth > 2 * math.log2(max(n, 2)):
            sub = arr[first:last + 1]
            self.sort_array(sub)
            arr[first:last + 1] = sub
            return
        pivot_pos = self.partition_quick(arr, first, last)
        self._quick_sort_recursive(arr, first, pivot_pos - 1, depth + 1)
        self._quick_sort_recursive(arr, pivot_pos + 1, last, depth + 1)

    def partition_quick(self, arr, first, last):
        mid = (first + last) // 2
        if arr[first] > arr[mid]:  arr[first], arr[mid]  = arr[mid],  arr[first]
        if arr[first] > arr[last]: arr[first], arr[last] = arr[last], arr[first]
        if arr[mid]   > arr[last]: arr[mid],   arr[last] = arr[last], arr[mid]
        arr[first], arr[mid] = arr[mid], arr[first]
        pivot = arr[first]
        left, right = first + 1, last
        self._snapshot(arr, [first], f"Pivot = {pivot} (Median-of-Three)")
        while True:
            self.comparisons += 1
            while left <= right and arr[left] < pivot:
                left += 1
            while left <= right and arr[right] > pivot:
                right -= 1
            if left > right:
                break
            arr[left], arr[right] = arr[right], arr[left]
            self.swaps += 1
            self._snapshot(arr, [left, right], f"Swap [{left}]↔[{right}]")
            left += 1; right -= 1
        arr[first], arr[right] = arr[right], arr[first]
        self.swaps += 1
        self._snapshot(arr, [right], f"Pivot ditempatkan di [{right}]")
        return right


class ExprHeapSorter:
    def __init__(self, expr_str: str):
        self.expr   = expr_str
        self.values = []
        self.steps  = []
        self.comparisons = 0

    def reset_stats(self):
        self.steps = []
        self.comparisons = 0

    def _snapshot(self, arr, highlights=None, label=""):
        self.steps.append((list(arr), highlights or [], label))

    def parse_and_evaluate(self) -> List[int]:
        tokens = deque(self.expr.replace(" ", ""))
        root   = self._build_tree(tokens)
        result = self._eval_tree(root)
        self.values = [result]
        return self.values

    def _build_tree(self, tokens):
        if not tokens: return None
        token = tokens.popleft()
        if token == '(':
            node = {}
            node['left'] = self._build_tree(tokens)
            op = tokens.popleft()
            if op not in ('+', '-', '*', '/'):
                raise ValueError(f"Operator tidak valid: '{op}'")
            node['val'] = op
            node['right'] = self._build_tree(tokens)
            close = tokens.popleft()
            if close != ')':
                raise ValueError(f"Diharapkan ')' tapi dapat '{close}'")
            return node
        num_str = token
        while tokens and tokens[0].isdigit():
            num_str += tokens.popleft()
        if num_str.lstrip('-').isdigit():
            return {'val': int(num_str), 'left': None, 'right': None}
        raise ValueError(f"Token tidak valid: '{num_str}'")

    def _eval_tree(self, node):
        if node is None: return 0
        if node['left'] is None and node['right'] is None:
            return node['val']
        lv = self._eval_tree(node['left'])
        rv = self._eval_tree(node['right'])
        op = node['val']
        if op == '+': return lv + rv
        elif op == '-': return lv - rv
        elif op == '*': return lv * rv
        elif op == '/':
            if rv == 0: raise ValueError("Pembagian dengan nol tidak diizinkan")
            return lv // rv
        raise ValueError(f"Operator tidak dikenal: '{op}'")

    def heapsort_inplace(self, arr: List[int]) -> List[int]:
        self.reset_stats()
        n = len(arr)
        if n <= 1: return arr
        self._snapshot(arr, [], "Input awal")
        for i in range(n // 2 - 1, -1, -1):
            self._sift_down(arr, n, i)
        self._snapshot(arr, [], "Max-Heap terbentuk")
        for end in range(n - 1, 0, -1):
            arr[0], arr[end] = arr[end], arr[0]
            self._snapshot(arr, [end], f"Ekstrak max={arr[end]} ke pos [{end}]")
            self._sift_down(arr, end, 0)
        self._snapshot(arr, list(range(n)), "Selesai! ✓")
        return arr

    def _sift_down(self, arr, heap_size, idx):
        while True:
            largest = idx
            left    = 2 * idx + 1
            right   = 2 * idx + 2
            self.comparisons += 1
            if left  < heap_size and arr[left]  > arr[largest]: largest = left
            if right < heap_size and arr[right] > arr[largest]: largest = right
            if largest == idx: break
            arr[idx], arr[largest] = arr[largest], arr[idx]
            idx = largest

    def is_complete_tree(self, arr: List[int]) -> bool:
        n = len(arr)
        if n <= 1: return True
        found_null = False
        for i in range(n):
            left  = 2 * i + 1
            right = 2 * i + 2
            if left < n:
                if found_null: return False
            else:
                found_null = True
            if right < n:
                if found_null: return False
            else:
                found_null = True
        return True


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tugas Sorting — Lionel Jevon")
        self.geometry("1280x800")
        self.minsize(1100, 700)
        self.configure(bg=C["sidebar_bg"])
        self.resizable(True, True)

        self.history = []
        self.current_page = None

        self._setup_fonts()
        self._build_ui()
        self._navigate("dashboard")

    def _setup_fonts(self):
        self.f_title   = tkfont.Font(family="Segoe UI", size=22, weight="bold")
        self.f_heading = tkfont.Font(family="Segoe UI", size=14, weight="bold")
        self.f_sub     = tkfont.Font(family="Segoe UI", size=11)
        self.f_body    = tkfont.Font(family="Segoe UI", size=10)
        self.f_small   = tkfont.Font(family="Segoe UI", size=9)
        self.f_mono    = tkfont.Font(family="Consolas", size=10)
        self.f_big_num = tkfont.Font(family="Segoe UI", size=28, weight="bold")
        self.f_nav     = tkfont.Font(family="Segoe UI", size=11)

    def _build_ui(self):
        self.sidebar = tk.Frame(self, bg=C["sidebar_bg"], width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        logo_frame = tk.Frame(self.sidebar, bg=C["sidebar_bg"], pady=20)
        logo_frame.pack(fill="x")
        tk.Label(logo_frame, text="{≡}", font=tkfont.Font(family="Segoe UI", size=28, weight="bold"),
                 fg=C["accent"], bg=C["sidebar_bg"]).pack()
        tk.Label(logo_frame, text="Tugas Sorting", font=tkfont.Font(family="Segoe UI", size=13, weight="bold"),
                 fg=C["text_white"], bg=C["sidebar_bg"]).pack()

        ttk.Separator(self.sidebar, orient="horizontal").pack(fill="x", padx=16, pady=8)

        self.nav_buttons = {}
        nav_items = [
            ("dashboard",    "⊞", "Dashboard"),
            ("array_sort",   "⊟", "Array Sort"),
            ("ll_sort",      "⊠", "Linked List Sort"),
            ("heap_sort",    "△", "Heap Sort"),
            ("expr_tree",    "❖", "Expression Tree"),
            ("visualisasi",  "◈", "Visualisasi"),
            ("teori",        "☰", "Teori & Analisis"),
            ("tentang",      "◉", "Tentang"),
        ]
        for page_id, icon, label in nav_items:
            btn = self._make_nav_btn(page_id, icon, label)
            self.nav_buttons[page_id] = btn

        tk.Label(self.sidebar, text="v1.0.0", font=self.f_small,
                 fg=C["text_light"], bg=C["sidebar_bg"]).pack(side="bottom", pady=12)

        self.content_frame = tk.Frame(self, bg=C["content_bg"])
        self.content_frame.pack(side="left", fill="both", expand=True)

    def _make_nav_btn(self, page_id, icon, label):
        frame = tk.Frame(self.sidebar, bg=C["sidebar_bg"], cursor="hand2")
        frame.pack(fill="x", padx=8, pady=2)
        icon_lbl = tk.Label(frame, text=icon, width=3, font=self.f_nav,
                             fg=C["text_light"], bg=C["sidebar_bg"])
        icon_lbl.pack(side="left")
        text_lbl = tk.Label(frame, text=label, font=self.f_nav, anchor="w",
                             fg=C["text_light"], bg=C["sidebar_bg"])
        text_lbl.pack(side="left", fill="x", expand=True)

        def on_click(e=None):
            self._navigate(page_id)
        def on_enter(e):
            if self.current_page != page_id:
                frame.configure(bg=C["sidebar_hover"])
                icon_lbl.configure(bg=C["sidebar_hover"])
                text_lbl.configure(bg=C["sidebar_hover"])
        def on_leave(e):
            if self.current_page != page_id:
                frame.configure(bg=C["sidebar_bg"])
                icon_lbl.configure(bg=C["sidebar_bg"])
                text_lbl.configure(bg=C["sidebar_bg"])

        for w in (frame, icon_lbl, text_lbl):
            w.bind("<Button-1>", on_click)
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)

        return (frame, icon_lbl, text_lbl)

    def _navigate(self, page_id):
        if self.current_page and self.current_page in self.nav_buttons:
            f, il, tl = self.nav_buttons[self.current_page]
            f.configure(bg=C["sidebar_bg"]); il.configure(bg=C["sidebar_bg"], fg=C["text_light"]); tl.configure(bg=C["sidebar_bg"], fg=C["text_light"])

        self.current_page = page_id

        if page_id in self.nav_buttons:
            f, il, tl = self.nav_buttons[page_id]
            f.configure(bg=C["sidebar_active"])
            il.configure(bg=C["sidebar_active"], fg=C["accent"])
            tl.configure(bg=C["sidebar_active"], fg=C["text_white"])

        for w in self.content_frame.winfo_children():
            w.destroy()

        pages = {
            "dashboard"   : PageDashboard,
            "array_sort"  : PageArraySort,
            "ll_sort"     : PageLinkedList,
            "heap_sort"   : PageHeapSort,
            "expr_tree"   : PageExprTree,
            "visualisasi" : PageVisualisasi,
            "teori"       : PageTeori,
            "tentang"     : PageTentang,
        }
        PageClass = pages.get(page_id, PageDashboard)
        PageClass(self.content_frame, self)

    def add_history(self, record):
        self.history.append(record)


def make_card(parent, padx=16, pady=12):
    frame = tk.Frame(parent, bg=C["card_bg"],
                     highlightbackground=C["border"], highlightthickness=1)
    frame.pack(fill="x", padx=padx, pady=pady)
    return frame

def make_label(parent, text, font, fg=C["text_dark"], bg=C["card_bg"], **kw):
    return tk.Label(parent, text=text, font=font, fg=fg, bg=bg, **kw)

def make_btn(parent, text, command, color=C["accent"], fg="white", **kw):
    btn = tk.Button(parent, text=text, command=command,
                    bg=color, fg=fg, activebackground=color,
                    activeforeground=fg, relief="flat",
                    font=tkfont.Font(family="Segoe UI", size=10, weight="bold"),
                    padx=16, pady=7, cursor="hand2", **kw)
    return btn

def page_header(parent, title, subtitle=""):
    hdr = tk.Frame(parent, bg=C["content_bg"])
    hdr.pack(fill="x", padx=28, pady=(24, 8))
    tk.Label(hdr, text=title, font=tkfont.Font(family="Segoe UI", size=20, weight="bold"),
             fg=C["text_dark"], bg=C["content_bg"]).pack(anchor="w")
    if subtitle:
        tk.Label(hdr, text=subtitle, font=tkfont.Font(family="Segoe UI", size=11),
                 fg=C["text_mid"], bg=C["content_bg"]).pack(anchor="w")
    ttk.Separator(parent, orient="horizontal").pack(fill="x", padx=28, pady=4)


class PageDashboard:
    def __init__(self, parent, app):
        self.parent = parent
        self.app    = app
        self._build()

    def _build(self):
        page_header(self.parent, "Dashboard", "Ringkasan aktivitas dan performa pengurutan.")

        stats_frame = tk.Frame(self.parent, bg=C["content_bg"])
        stats_frame.pack(fill="x", padx=24, pady=8)

        total  = len(self.app.history)
        arr_c  = sum(1 for h in self.app.history if h.get("type") == "Array")
        ll_c   = sum(1 for h in self.app.history if h.get("type") == "Linked List")
        heap_c = sum(1 for h in self.app.history if h.get("type") == "Heap")
        avg_t  = (sum(h.get("time", 0) for h in self.app.history) / total) if total else 0

        cards = [
            ("Total Eksekusi", str(total), "Kali", C["accent"]),
            ("Array Sort",     str(arr_c),  "Kali", C["accent"]),
            ("Linked List",    str(ll_c),   "Kali", C["accent2"]),
            ("Heap Sort",      str(heap_c), "Kali", C["accent3"]),
            ("Rata-rata Waktu", f"{avg_t:.4f}s", "Per Eksekusi", C["accent4"]),
        ]
        for title, val, unit, color in cards:
            c = tk.Frame(stats_frame, bg=C["card_bg"],
                         highlightbackground=C["border"], highlightthickness=1)
            c.pack(side="left", fill="both", expand=True, padx=5, pady=4)
            tk.Frame(c, bg=color, height=3).pack(fill="x")
            tk.Label(c, text=title, font=tkfont.Font(family="Segoe UI", size=9),
                     fg=C["text_mid"], bg=C["card_bg"]).pack(anchor="w", padx=12, pady=(10,0))
            tk.Label(c, text=val, font=tkfont.Font(family="Segoe UI", size=22, weight="bold"),
                     fg=C["text_dark"], bg=C["card_bg"]).pack(anchor="w", padx=12)
            tk.Label(c, text=unit, font=tkfont.Font(family="Segoe UI", size=9),
                     fg=C["text_light"], bg=C["card_bg"]).pack(anchor="w", padx=12, pady=(0,12))

        # History table
        hist_card = tk.Frame(self.parent, bg=C["card_bg"],
                             highlightbackground=C["border"], highlightthickness=1)
        hist_card.pack(fill="both", expand=True, padx=28, pady=12)
        tk.Label(hist_card, text="Riwayat Eksekusi", font=tkfont.Font(family="Segoe UI", size=12, weight="bold"),
                 fg=C["text_dark"], bg=C["card_bg"]).pack(anchor="w", padx=16, pady=(12,4))

        cols = ("No", "Tipe", "Algoritma", "Elemen", "Waktu (s)", "Perbandingan", "Status")
        tree = ttk.Treeview(hist_card, columns=cols, show="headings", height=10)
        style = ttk.Style()
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=28, background="white", fieldbackground="white")
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=110, anchor="center")

        for i, h in enumerate(reversed(self.app.history[-20:]), 1):
            tree.insert("", "end", values=(
                i, h.get("type","—"), h.get("algo","—"),
                h.get("n",0), f"{h.get('time',0):.4f}",
                h.get("comparisons",0), "✓ Selesai"
            ))

        vsb = ttk.Scrollbar(hist_card, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y", padx=(0,8), pady=8)
        tree.pack(fill="both", expand=True, padx=16, pady=(0,12))

        #Quick actions
        qa = tk.Frame(self.parent, bg=C["content_bg"])
        qa.pack(fill="x", padx=28, pady=8)
        tk.Label(qa, text="Aksi Cepat:", font=tkfont.Font(family="Segoe UI", size=11, weight="bold"),
                 fg=C["text_dark"], bg=C["content_bg"]).pack(side="left", padx=(0,12))
        for label, page in [("Array Sort", "array_sort"), ("Linked List Sort", "ll_sort"), ("Heap Sort", "heap_sort")]:
            make_btn(qa, label, lambda p=page: self.app._navigate(p)).pack(side="left", padx=4)



class PageArraySort:
    def __init__(self, parent, app):
        self.parent = parent
        self.app    = app
        self.sorter = AdvancedSorter()
        self.arr    = []
        self.steps  = []
        self.step_idx = 0
        self.anim_running = False
        self._build()

    def _build(self):
        page_header(self.parent, "Array Sort  (List / Array)",
                    "Urutkan data dalam Python List/Array menggunakan algoritma lanjutan.")

        pane = tk.Frame(self.parent, bg=C["content_bg"])
        pane.pack(fill="both", expand=True, padx=24, pady=4)

        left = tk.Frame(pane, bg=C["content_bg"], width=340)
        left.pack(side="left", fill="y", padx=(0,12))
        left.pack_propagate(False)

        # Input card
        inp_card = tk.Frame(left, bg=C["card_bg"], highlightbackground=C["border"], highlightthickness=1)
        inp_card.pack(fill="x", pady=6)
        tk.Label(inp_card, text="Input Data", font=tkfont.Font(family="Segoe UI",size=12,weight="bold"),
                 fg=C["text_dark"], bg=C["card_bg"]).pack(anchor="w", padx=14, pady=(12,4))

        tk.Label(inp_card, text="Jumlah Elemen (n)", font=tkfont.Font(family="Segoe UI",size=9),
                 fg=C["text_mid"], bg=C["card_bg"]).pack(anchor="w", padx=14)
        self.n_var = tk.StringVar(value="20")
        tk.Entry(inp_card, textvariable=self.n_var, font=tkfont.Font(family="Segoe UI",size=11),
                 width=10, relief="solid").pack(anchor="w", padx=14, pady=2)

        tk.Label(inp_card, text="Mode Input", font=tkfont.Font(family="Segoe UI",size=9),
                 fg=C["text_mid"], bg=C["card_bg"]).pack(anchor="w", padx=14, pady=(8,0))
        self.mode_var = tk.StringVar(value="Acak (Random)")
        mode_cb = ttk.Combobox(inp_card, textvariable=self.mode_var, width=20, state="readonly",
                               values=["Acak (Random)", "Terurut Naik", "Terurut Turun", "Hampir Terurut"])
        mode_cb.pack(anchor="w", padx=14, pady=2)

        tk.Label(inp_card, text="Range Nilai  Min", font=tkfont.Font(family="Segoe UI",size=9),
                 fg=C["text_mid"], bg=C["card_bg"]).pack(anchor="w", padx=14, pady=(8,0))
        range_row = tk.Frame(inp_card, bg=C["card_bg"])
        range_row.pack(anchor="w", padx=14, pady=2)
        self.min_var = tk.StringVar(value="1")
        self.max_var = tk.StringVar(value="99")
        tk.Entry(range_row, textvariable=self.min_var, width=6, relief="solid").pack(side="left")
        tk.Label(range_row, text="  Max", bg=C["card_bg"], font=tkfont.Font(family="Segoe UI",size=9), fg=C["text_mid"]).pack(side="left")
        tk.Entry(range_row, textvariable=self.max_var, width=8, relief="solid").pack(side="left", padx=4)

        make_btn(inp_card, "⟳  Generate Data", self._generate).pack(anchor="w", padx=14, pady=(10,4))

        tk.Label(inp_card, text="Atau ketik manual (pisah koma):", font=tkfont.Font(family="Segoe UI",size=9),
                 fg=C["text_mid"], bg=C["card_bg"]).pack(anchor="w", padx=14, pady=(8,0))
        self.manual_var = tk.StringVar()
        tk.Entry(inp_card, textvariable=self.manual_var, font=tkfont.Font(family="Consolas",size=9),
                 relief="solid", width=32).pack(anchor="w", padx=14, pady=(2,12))

        algo_card = tk.Frame(left, bg=C["card_bg"], highlightbackground=C["border"], highlightthickness=1)
        algo_card.pack(fill="x", pady=6)
        tk.Label(algo_card, text="Pilih Algoritma", font=tkfont.Font(family="Segoe UI",size=12,weight="bold"),
                 fg=C["text_dark"], bg=C["card_bg"]).pack(anchor="w", padx=14, pady=(12,6))
        self.algo_var = tk.StringVar(value="merge")
        algos = [
            ("merge", "Merge Sort (Stabil)", "O(n log n) waktu, O(n) ruang (1 tmpArray)"),
            ("quick", "Quick Sort (Median-of-Three)", "O(n log n) rata-rata, fallback ke Merge Sort"),
        ]
        for val, name, desc in algos:
            row = tk.Frame(algo_card, bg=C["card_bg"])
            row.pack(fill="x", padx=14, pady=3)
            tk.Radiobutton(row, variable=self.algo_var, value=val,
                           bg=C["card_bg"], activebackground=C["card_bg"]).pack(side="left")
            sub = tk.Frame(row, bg=C["card_bg"])
            sub.pack(side="left")
            tk.Label(sub, text=name, font=tkfont.Font(family="Segoe UI",size=10,weight="bold"),
                     fg=C["text_dark"], bg=C["card_bg"]).pack(anchor="w")
            tk.Label(sub, text=desc, font=tkfont.Font(family="Segoe UI",size=8),
                     fg=C["text_mid"], bg=C["card_bg"]).pack(anchor="w")
        tk.Frame(algo_card, bg=C["card_bg"], height=8).pack()

        ctrl_card = tk.Frame(left, bg=C["card_bg"], highlightbackground=C["border"], highlightthickness=1)
        ctrl_card.pack(fill="x", pady=6)
        tk.Label(ctrl_card, text="Kontrol", font=tkfont.Font(family="Segoe UI",size=12,weight="bold"),
                 fg=C["text_dark"], bg=C["card_bg"]).pack(anchor="w", padx=14, pady=(12,6))
        btn_row = tk.Frame(ctrl_card, bg=C["card_bg"])
        btn_row.pack(padx=14, pady=(0,4))
        make_btn(btn_row, "▶  Mulai Sort", self._run_sort).pack(side="left", padx=(0,6))
        make_btn(btn_row, "↺  Reset", self._reset, color="#64748B").pack(side="left")

        tk.Label(ctrl_card, text="Kecepatan Animasi", font=tkfont.Font(family="Segoe UI",size=9),
                 fg=C["text_mid"], bg=C["card_bg"]).pack(anchor="w", padx=14, pady=(8,0))
        self.speed_var = tk.DoubleVar(value=0.3)
        tk.Scale(ctrl_card, variable=self.speed_var, from_=0.05, to=1.5, resolution=0.05,
                 orient="horizontal", length=260, bg=C["card_bg"], troughcolor=C["border"],
                 highlightthickness=0).pack(padx=14, pady=(2,12))

        # RIGHT: Canvas + stats
        right = tk.Frame(pane, bg=C["content_bg"])
        right.pack(side="left", fill="both", expand=True)

        viz_card = tk.Frame(right, bg=C["card_bg"], highlightbackground=C["border"], highlightthickness=1)
        viz_card.pack(fill="both", expand=True)
        tk.Label(viz_card, text="Visualisasi Pengurutan", font=tkfont.Font(family="Segoe UI",size=12,weight="bold"),
                 fg=C["text_dark"], bg=C["card_bg"]).pack(anchor="w", padx=14, pady=(12,4))

        self.canvas = tk.Canvas(viz_card, bg=C["canvas_bg"], highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=14, pady=(0,6))

        self.step_lbl = tk.Label(viz_card, text="Langkah: —", font=tkfont.Font(family="Consolas",size=10),
                                  fg=C["text_mid"], bg=C["card_bg"])
        self.step_lbl.pack(anchor="w", padx=14)

        # Stats row
        stats_row = tk.Frame(viz_card, bg=C["card_bg"])
        stats_row.pack(fill="x", padx=14, pady=(4,12))
        self.lbl_cmp  = tk.Label(stats_row, text="Perbandingan: —", font=tkfont.Font(family="Segoe UI",size=10),
                                  fg=C["text_mid"], bg=C["card_bg"])
        self.lbl_cmp.pack(side="left", padx=(0,16))
        self.lbl_swap = tk.Label(stats_row, text="Swap: —", font=tkfont.Font(family="Segoe UI",size=10),
                                  fg=C["text_mid"], bg=C["card_bg"])
        self.lbl_swap.pack(side="left", padx=(0,16))
        self.lbl_time = tk.Label(stats_row, text="Waktu: —", font=tkfont.Font(family="Segoe UI",size=10),
                                  fg=C["text_mid"], bg=C["card_bg"])
        self.lbl_time.pack(side="left")

        nav_row = tk.Frame(viz_card, bg=C["card_bg"])
        nav_row.pack(fill="x", padx=14, pady=(0,8))
        make_btn(nav_row, "◀ Prev", self._prev_step, color="#475569").pack(side="left", padx=(0,4))
        make_btn(nav_row, "▶ Animate", self._animate_steps, color=C["accent"]).pack(side="left", padx=(0,4))
        make_btn(nav_row, "Next ▶", self._next_step, color="#475569").pack(side="left")
        self.step_counter_lbl = tk.Label(nav_row, text="Step 0/0", font=tkfont.Font(family="Segoe UI",size=9),
                                          fg=C["text_mid"], bg=C["card_bg"])
        self.step_counter_lbl.pack(side="left", padx=12)

        # legend
        leg = tk.Frame(viz_card, bg=C["card_bg"])
        leg.pack(anchor="w", padx=14, pady=(0,10))
        for color, label in [(C["bar_default"],"Normal"),(C["bar_compare"],"Aktif/Dibandingkan"),
                              (C["bar_sorted"],"Terurut"),(C["bar_pivot"],"Pivot")]:
            lf = tk.Frame(leg, bg=C["card_bg"])
            lf.pack(side="left", padx=6)
            tk.Frame(lf, bg=color, width=14, height=14).pack(side="left")
            tk.Label(lf, text=label, font=tkfont.Font(family="Segoe UI",size=8),
                     fg=C["text_mid"], bg=C["card_bg"]).pack(side="left", padx=3)

        self._generate()

    def _generate(self):
        try:
            n    = max(4, min(60, int(self.n_var.get())))
            lo   = int(self.min_var.get())
            hi   = int(self.max_var.get())
        except:
            n, lo, hi = 20, 1, 99
        mode = self.mode_var.get()
        if mode == "Acak (Random)":
            self.arr = [random.randint(lo, hi) for _ in range(n)]
        elif mode == "Terurut Naik":
            self.arr = sorted([random.randint(lo, hi) for _ in range(n)])
        elif mode == "Terurut Turun":
            self.arr = sorted([random.randint(lo, hi) for _ in range(n)], reverse=True)
        else:
            base = sorted([random.randint(lo, hi) for _ in range(n)])
            for _ in range(max(1, n//10)):
                i, j = random.sample(range(n), 2)
                base[i], base[j] = base[j], base[i]
            self.arr = base
        manual = self.manual_var.get().strip()
        if manual:
            try:
                self.arr = [int(x.strip()) for x in manual.split(",") if x.strip()]
            except: pass
        self.steps    = []
        self.step_idx = 0
        self._draw(self.arr, [], "Input Data")
        self.step_lbl.configure(text="Generate selesai. Klik 'Mulai Sort'.")
        self.step_counter_lbl.configure(text="Step 0/0")
        self.lbl_cmp.configure(text="Perbandingan: —")
        self.lbl_swap.configure(text="Swap: —")
        self.lbl_time.configure(text="Waktu: —")

    def _run_sort(self):
        if not self.arr:
            messagebox.showwarning("Input Kosong", "Generate data terlebih dahulu.")
            return
        arr_copy = list(self.arr)
        t0 = time.time()
        if self.algo_var.get() == "merge":
            self.sorter.sort_array(arr_copy)
            algo_name = "Merge Sort"
        else:
            self.sorter.sort_array_quick(arr_copy)
            algo_name = "Quick Sort"
        elapsed = time.time() - t0
        self.steps    = self.sorter.steps
        self.step_idx = 0
        self.lbl_cmp.configure(text=f"Perbandingan: {self.sorter.comparisons:,}")
        self.lbl_swap.configure(text=f"Swap: {self.sorter.swaps:,}")
        self.lbl_time.configure(text=f"Waktu: {elapsed:.4f}s")
        self.step_counter_lbl.configure(text=f"Step 1/{len(self.steps)}")
        self.app.add_history({"type":"Array","algo":algo_name,"n":len(self.arr),
                              "time":elapsed,"comparisons":self.sorter.comparisons})
        if self.steps:
            arr_, hl, lbl = self.steps[0]
            self._draw(arr_, hl, lbl)

    def _animate_steps(self):
        if not self.steps:
            messagebox.showinfo("Info","Jalankan sort terlebih dahulu.")
            return
        if self.anim_running:
            return
        self.anim_running = True
        self.step_idx = 0
        self._anim_loop()

    def _anim_loop(self):
        if self.step_idx >= len(self.steps) or not self.anim_running:
            self.anim_running = False
            return
        arr_, hl, lbl = self.steps[self.step_idx]
        self._draw(arr_, hl, lbl)
        self.step_counter_lbl.configure(text=f"Step {self.step_idx+1}/{len(self.steps)}")
        self.step_idx += 1
        delay = max(30, int(self.speed_var.get() * 1000))
        self.canvas.after(delay, self._anim_loop)

    def _prev_step(self):
        self.anim_running = False
        if self.step_idx > 0:
            self.step_idx -= 1
        if self.steps and self.step_idx < len(self.steps):
            arr_, hl, lbl = self.steps[self.step_idx]
            self._draw(arr_, hl, lbl)
            self.step_counter_lbl.configure(text=f"Step {self.step_idx+1}/{len(self.steps)}")

    def _next_step(self):
        self.anim_running = False
        if self.steps and self.step_idx < len(self.steps):
            arr_, hl, lbl = self.steps[self.step_idx]
            self._draw(arr_, hl, lbl)
            self.step_counter_lbl.configure(text=f"Step {self.step_idx+1}/{len(self.steps)}")
            self.step_idx = min(self.step_idx + 1, len(self.steps))

    def _draw(self, arr, highlights, label):
        self.canvas.delete("all")
        if not arr: return
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 50 or h < 50:
            w, h = 700, 300

        n      = len(arr)
        mx     = max(arr) if arr else 1
        bar_w  = max(2, (w - 20) // n)
        gap    = max(1, bar_w // 8)
        pad_x  = (w - n * bar_w) // 2
        pad_y  = 30
        max_bh = h - 60

        is_final = label.startswith("Selesai")

        for i, val in enumerate(arr):
            bh    = max(4, int(val / mx * max_bh))
            x0    = pad_x + i * bar_w + gap
            x1    = pad_x + (i + 1) * bar_w - gap
            y0    = h - pad_y - bh
            y1    = h - pad_y

            if is_final:
                color = C["bar_sorted"]
            elif i in highlights:
                color = C["bar_compare"]
            else:
                color = C["bar_default"]

            self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")
            if n <= 30:
                self.canvas.create_text((x0+x1)//2, y0 - 6, text=str(val),
                                         fill="white", font=("Segoe UI", 7))

        self.step_lbl.configure(text=f"Langkah: {label}")

    def _reset(self):
        self.anim_running = False
        self.steps    = []
        self.step_idx = 0
        self._generate()


class PageLinkedList:
    def __init__(self, parent, app):
        self.parent  = parent
        self.app     = app
        self.sorter  = AdvancedSorter()
        self.ll_data = []
        self._build()

    def _build(self):
        page_header(self.parent, "Linked List Sort  (Singly Linked List)",
                    "Urutkan data Singly Linked List secara stabil tanpa alokasi node baru.")

        pane = tk.Frame(self.parent, bg=C["content_bg"])
        pane.pack(fill="both", expand=True, padx=24, pady=4)

        left = tk.Frame(pane, bg=C["content_bg"], width=320)
        left.pack(side="left", fill="y", padx=(0,12))
        left.pack_propagate(False)

        cfg = tk.Frame(left, bg=C["card_bg"], highlightbackground=C["border"], highlightthickness=1)
        cfg.pack(fill="x", pady=6)
        tk.Label(cfg, text="Bangun Linked List", font=tkfont.Font(family="Segoe UI",size=12,weight="bold"),
                 fg=C["text_dark"], bg=C["card_bg"]).pack(anchor="w", padx=14, pady=(12,4))

        tk.Label(cfg, text="Jumlah Node (n)", font=tkfont.Font(family="Segoe UI",size=9),
                 fg=C["text_mid"], bg=C["card_bg"]).pack(anchor="w", padx=14)
        self.n_var = tk.StringVar(value="15")
        tk.Entry(cfg, textvariable=self.n_var, width=10, relief="solid").pack(anchor="w", padx=14, pady=2)

        tk.Label(cfg, text="Mode Input", font=tkfont.Font(family="Segoe UI",size=9),
                 fg=C["text_mid"], bg=C["card_bg"]).pack(anchor="w", padx=14, pady=(8,0))
        self.mode_var = tk.StringVar(value="Acak (Random)")
        ttk.Combobox(cfg, textvariable=self.mode_var, width=20, state="readonly",
                     values=["Acak (Random)","Terurut Turun","Hampir Terurut"]).pack(anchor="w", padx=14, pady=2)

        range_row = tk.Frame(cfg, bg=C["card_bg"])
        range_row.pack(anchor="w", padx=14, pady=(6,0))
        tk.Label(range_row, text="Min:", bg=C["card_bg"], font=tkfont.Font(family="Segoe UI",size=9), fg=C["text_mid"]).pack(side="left")
        self.min_v = tk.StringVar(value="1")
        self.max_v = tk.StringVar(value="50")
        tk.Entry(range_row, textvariable=self.min_v, width=5, relief="solid").pack(side="left", padx=2)
        tk.Label(range_row, text="Max:", bg=C["card_bg"], font=tkfont.Font(family="Segoe UI",size=9), fg=C["text_mid"]).pack(side="left")
        tk.Entry(range_row, textvariable=self.max_v, width=5, relief="solid").pack(side="left", padx=2)

        make_btn(cfg, "⟳  Generate List", self._generate).pack(anchor="w", padx=14, pady=(10,12))

        # Manual
        tk.Label(cfg, text="Atau ketik manual (koma):", font=tkfont.Font(family="Segoe UI",size=9),
                 fg=C["text_mid"], bg=C["card_bg"]).pack(anchor="w", padx=14)
        self.manual_v = tk.StringVar()
        tk.Entry(cfg, textvariable=self.manual_v, font=tkfont.Font(family="Consolas",size=9),
                 relief="solid", width=30).pack(anchor="w", padx=14, pady=(2,12))

        run_card = tk.Frame(left, bg=C["card_bg"], highlightbackground=C["border"], highlightthickness=1)
        run_card.pack(fill="x", pady=6)
        tk.Label(run_card, text="Algoritma", font=tkfont.Font(family="Segoe UI",size=12,weight="bold"),
                 fg=C["text_dark"], bg=C["card_bg"]).pack(anchor="w", padx=14, pady=(12,6))
        info = tk.Label(run_card, text="Merge Sort (Linked List)\nO(n log n) waktu, O(log n) ruang\nStabil: Ya ✓  Alokasi node baru: Tidak",
                        font=tkfont.Font(family="Segoe UI",size=9), fg=C["text_mid"], bg=C["card_bg"], justify="left")
        info.pack(anchor="w", padx=14)

        br = tk.Frame(run_card, bg=C["card_bg"])
        br.pack(padx=14, pady=10)
        make_btn(br, "▶  Mulai Sort", self._run_sort).pack(side="left", padx=(0,6))
        make_btn(br, "↺  Reset", self._reset, color="#64748B").pack(side="left")

        self.res_card = tk.Frame(left, bg=C["card_bg"], highlightbackground=C["border"], highlightthickness=1)
        self.res_card.pack(fill="x", pady=6)
        tk.Label(self.res_card, text="Hasil", font=tkfont.Font(family="Segoe UI",size=12,weight="bold"),
                 fg=C["text_dark"], bg=C["card_bg"]).pack(anchor="w", padx=14, pady=(12,4))
        self.status_lbl = tk.Label(self.res_card, text="Status: Belum dijalankan", font=tkfont.Font(family="Segoe UI",size=9),
                                    fg=C["text_mid"], bg=C["card_bg"])
        self.status_lbl.pack(anchor="w", padx=14)
        self.time_lbl = tk.Label(self.res_card, text="Waktu: —", font=tkfont.Font(family="Segoe UI",size=9),
                                  fg=C["text_mid"], bg=C["card_bg"])
        self.time_lbl.pack(anchor="w", padx=14)
        self.cmp_lbl = tk.Label(self.res_card, text="Perbandingan: —", font=tkfont.Font(family="Segoe UI",size=9),
                                 fg=C["text_mid"], bg=C["card_bg"])
        self.cmp_lbl.pack(anchor="w", padx=14, pady=(0,12))

        right = tk.Frame(pane, bg=C["content_bg"])
        right.pack(side="left", fill="both", expand=True)

        viz = tk.Frame(right, bg=C["card_bg"], highlightbackground=C["border"], highlightthickness=1)
        viz.pack(fill="both", expand=True)
        tk.Label(viz, text="Visualisasi Linked List", font=tkfont.Font(family="Segoe UI",size=12,weight="bold"),
                 fg=C["text_dark"], bg=C["card_bg"]).pack(anchor="w", padx=14, pady=(12,4))

        self.canvas = tk.Canvas(viz, bg=C["canvas_bg"], highlightthickness=0, height=180)
        self.canvas.pack(fill="x", padx=14, pady=(0,6))

        tk.Label(viz, text="Preview Data (setelah sort)", font=tkfont.Font(family="Segoe UI",size=10,weight="bold"),
                 fg=C["text_dark"], bg=C["card_bg"]).pack(anchor="w", padx=14, pady=(8,4))

        self.bar_canvas = tk.Canvas(viz, bg=C["canvas_bg"], highlightthickness=0)
        self.bar_canvas.pack(fill="both", expand=True, padx=14, pady=(0,14))

        self.info_lbl = tk.Label(viz, text="", font=tkfont.Font(family="Segoe UI",size=9),
                                  fg=C["accent2"], bg=C["card_bg"])
        self.info_lbl.pack(anchor="w", padx=14, pady=(0,8))

        self._generate()

    def _generate(self):
        try:
            n = max(4, min(40, int(self.n_var.get())))
            lo = int(self.min_v.get()); hi = int(self.max_v.get())
        except: n, lo, hi = 15, 1, 50
        mode = self.mode_var.get()
        if mode == "Terurut Turun":
            vals = sorted([random.randint(lo,hi) for _ in range(n)], reverse=True)
        elif mode == "Hampir Terurut":
            vals = sorted([random.randint(lo,hi) for _ in range(n)])
            for _ in range(max(1,n//10)):
                i,j = random.sample(range(n),2); vals[i],vals[j]=vals[j],vals[i]
        else:
            vals = [random.randint(lo,hi) for _ in range(n)]
        manual = self.manual_v.get().strip()
        if manual:
            try: vals = [int(x.strip()) for x in manual.split(",") if x.strip()]
            except: pass
        self.ll_data = vals
        self._draw_ll(vals, sorted_=False)
        self._draw_bars(vals, [])

    def _run_sort(self):
        if not self.ll_data: return
        head = _list_to_ll(self.ll_data)
        t0 = time.time()
        sorted_head = self.sorter.sort_linked_list(head)
        elapsed = time.time() - t0
        result = _ll_to_list(sorted_head)
        self.status_lbl.configure(text="Status: ✓ Selesai", fg=C["accent2"])
        self.time_lbl.configure(text=f"Waktu: {elapsed:.4f}s")
        self.cmp_lbl.configure(text=f"Perbandingan: {self.sorter.comparisons:,}")
        self._draw_ll(result, sorted_=True)
        self._draw_bars(result, list(range(len(result))))
        self.info_lbl.configure(text="✓ Pengurutan stabil: urutan relatif elemen sama dipertahankan.")
        self.app.add_history({"type":"Linked List","algo":"Merge Sort (LL)","n":len(result),
                              "time":elapsed,"comparisons":self.sorter.comparisons})

    def _draw_ll(self, vals, sorted_=False):
        self.canvas.delete("all")
        w = self.canvas.winfo_width() or 700
        h = 180
        n = len(vals)
        if n == 0: return
        max_show = min(n, 12)
        node_w, node_h = 54, 36
        gap = max(10, (w - 30 - max_show * node_w) // max(1, max_show - 1))
        start_x = 20
        cy = h // 2

        for i in range(max_show):
            x = start_x + i * (node_w + gap)
            color = C["bar_sorted"] if sorted_ else C["accent"]
            self.canvas.create_rectangle(x, cy-node_h//2, x+node_w-8, cy+node_h//2,
                                          fill=color, outline="white", width=1)
            self.canvas.create_text(x+(node_w-8)//2, cy, text=str(vals[i]),
                                    fill="white", font=("Segoe UI",10,"bold"))

            if i < max_show - 1:
                ax = x + node_w - 8
                self.canvas.create_line(ax, cy, ax+gap, cy, fill="#94A3B8", arrow="last", width=2)

        if n > max_show:
            self.canvas.create_text(start_x + max_show*(node_w+gap), cy,
                                    text=f"... +{n-max_show}", fill="#94A3B8",
                                    font=("Segoe UI",9))

        last_x = start_x + (max_show-1)*(node_w+gap) + node_w
        self.canvas.create_text(min(last_x+20, w-30), cy, text="NULL", fill="#64748B",
                                font=("Segoe UI",9,"bold"))

    def _draw_bars(self, vals, highlights):
        self.bar_canvas.delete("all")
        if not vals: return
        self.bar_canvas.update_idletasks()
        w = self.bar_canvas.winfo_width() or 700
        h = self.bar_canvas.winfo_height() or 200
        n = len(vals); mx = max(vals) if vals else 1
        bar_w = max(2, (w - 20) // n)
        pad_x = (w - n*bar_w)//2
        for i, v in enumerate(vals):
            bh = max(4, int(v/mx*(h-30)))
            x0 = pad_x + i*bar_w + 1; x1 = pad_x + (i+1)*bar_w - 1
            y0 = h - 20 - bh; y1 = h - 20
            color = C["bar_sorted"] if i in highlights else C["bar_default"]
            self.bar_canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")
            if n <= 25:
                self.bar_canvas.create_text((x0+x1)//2, y0-5, text=str(v),
                                             fill="white", font=("Segoe UI",7))

    def _reset(self): self._generate()


class PageHeapSort:
    def __init__(self, parent, app):
        self.parent = parent
        self.app    = app
        self.sorter = ExprHeapSorter("")
        self.arr    = []
        self.steps  = []
        self.step_idx = 0
        self.anim_running = False
        self._build()

    def _build(self):
        page_header(self.parent, "Heap Sort  (In-Place)",
                    "Sortir menggunakan Max-Heap dengan visualisasi pohon biner.")

        pane = tk.Frame(self.parent, bg=C["content_bg"])
        pane.pack(fill="both", expand=True, padx=24, pady=4)

        left = tk.Frame(pane, bg=C["content_bg"], width=300)
        left.pack(side="left", fill="y", padx=(0,12))
        left.pack_propagate(False)

        cfg = tk.Frame(left, bg=C["card_bg"], highlightbackground=C["border"], highlightthickness=1)
        cfg.pack(fill="x", pady=6)
        tk.Label(cfg, text="Input Data", font=tkfont.Font(family="Segoe UI",size=12,weight="bold"),
                 fg=C["text_dark"], bg=C["card_bg"]).pack(anchor="w", padx=14, pady=(12,4))
        tk.Label(cfg, text="Jumlah Elemen", font=tkfont.Font(family="Segoe UI",size=9), fg=C["text_mid"], bg=C["card_bg"]).pack(anchor="w", padx=14)
        self.n_var = tk.StringVar(value="15")
        tk.Entry(cfg, textvariable=self.n_var, width=10, relief="solid").pack(anchor="w", padx=14, pady=2)
        make_btn(cfg, "⟳  Generate", self._generate).pack(anchor="w", padx=14, pady=8)

        tk.Label(cfg, text="Atau manual (koma):", font=tkfont.Font(family="Segoe UI",size=9), fg=C["text_mid"], bg=C["card_bg"]).pack(anchor="w", padx=14)
        self.manual_v = tk.StringVar()
        tk.Entry(cfg, textvariable=self.manual_v, width=28, relief="solid", font=tkfont.Font(family="Consolas",size=9)).pack(anchor="w", padx=14, pady=(2,12))

        ctrl = tk.Frame(left, bg=C["card_bg"], highlightbackground=C["border"], highlightthickness=1)
        ctrl.pack(fill="x", pady=6)
        tk.Label(ctrl, text="Kontrol", font=tkfont.Font(family="Segoe UI",size=12,weight="bold"),
                 fg=C["text_dark"], bg=C["card_bg"]).pack(anchor="w", padx=14, pady=(12,6))
        br = tk.Frame(ctrl, bg=C["card_bg"])
        br.pack(padx=14, pady=(0,4))
        make_btn(br, "▶  Mulai Sort", self._run_sort).pack(side="left", padx=(0,6))
        make_btn(br, "↺  Reset", self._reset, color="#64748B").pack(side="left")

        tk.Label(ctrl, text="Kecepatan Animasi", font=tkfont.Font(family="Segoe UI",size=9),
                 fg=C["text_mid"], bg=C["card_bg"]).pack(anchor="w", padx=14, pady=(8,0))
        self.speed_var = tk.DoubleVar(value=0.4)
        tk.Scale(ctrl, variable=self.speed_var, from_=0.1, to=1.5, resolution=0.05,
                 orient="horizontal", length=230, bg=C["card_bg"], troughcolor=C["border"],
                 highlightthickness=0).pack(padx=14, pady=(2,12))

        res = tk.Frame(left, bg=C["card_bg"], highlightbackground=C["border"], highlightthickness=1)
        res.pack(fill="x", pady=6)
        tk.Label(res, text="Hasil", font=tkfont.Font(family="Segoe UI",size=12,weight="bold"),
                 fg=C["text_dark"], bg=C["card_bg"]).pack(anchor="w", padx=14, pady=(12,4))
        self.stat_lbl = tk.Label(res, text="Belum dijalankan", font=tkfont.Font(family="Segoe UI",size=9),
                                  fg=C["text_mid"], bg=C["card_bg"], justify="left")
        self.stat_lbl.pack(anchor="w", padx=14, pady=(0,12))

        right = tk.Frame(pane, bg=C["content_bg"])
        right.pack(side="left", fill="both", expand=True)

        viz = tk.Frame(right, bg=C["card_bg"], highlightbackground=C["border"], highlightthickness=1)
        viz.pack(fill="both", expand=True)
        hdr = tk.Frame(viz, bg=C["card_bg"])
        hdr.pack(fill="x", padx=14, pady=(12,4))
        tk.Label(hdr, text="Visualisasi Heap & Pengurutan", font=tkfont.Font(family="Segoe UI",size=12,weight="bold"),
                 fg=C["text_dark"], bg=C["card_bg"]).pack(side="left")
        self.step_lbl = tk.Label(hdr, text="", font=tkfont.Font(family="Consolas",size=10),
                                  fg=C["accent"], bg=C["card_bg"])
        self.step_lbl.pack(side="right")

        self.tree_canvas = tk.Canvas(viz, bg=C["canvas_bg"], highlightthickness=0, height=220)
        self.tree_canvas.pack(fill="x", padx=14, pady=(0,6))

        self.bar_canvas = tk.Canvas(viz, bg=C["canvas_bg"], highlightthickness=0)
        self.bar_canvas.pack(fill="both", expand=True, padx=14, pady=(0,6))

        nav_row = tk.Frame(viz, bg=C["card_bg"])
        nav_row.pack(fill="x", padx=14, pady=(0,8))
        make_btn(nav_row, "◀", self._prev_step, color="#475569").pack(side="left", padx=(0,4))
        make_btn(nav_row, "▶ Animasi", self._animate, color=C["accent"]).pack(side="left", padx=(0,4))
        make_btn(nav_row, "▶", self._next_step, color="#475569").pack(side="left")
        self.sc_lbl = tk.Label(nav_row, text="Step 0/0", font=tkfont.Font(family="Segoe UI",size=9),
                                fg=C["text_mid"], bg=C["card_bg"])
        self.sc_lbl.pack(side="left", padx=12)

        self._generate()

    def _generate(self):
        try: n = max(4, min(31, int(self.n_var.get())))
        except: n = 15
        manual = self.manual_v.get().strip()
        if manual:
            try: self.arr = [int(x.strip()) for x in manual.split(",") if x.strip()]
            except: self.arr = [random.randint(1,99) for _ in range(n)]
        else:
            self.arr = [random.randint(1,99) for _ in range(n)]
        self.steps = []; self.step_idx = 0
        self._draw_tree(self.arr, [])
        self._draw_bars(self.arr, [])
        self.sc_lbl.configure(text="Step 0/0")
        self.stat_lbl.configure(text="Generate selesai.")

    def _run_sort(self):
        arr_copy = list(self.arr)
        t0 = time.time()
        self.sorter.heapsort_inplace(arr_copy)
        elapsed = time.time() - t0
        self.steps = self.sorter.steps
        self.step_idx = 0
        self.stat_lbl.configure(text=f"Waktu: {elapsed:.4f}s\nPerbandingan: {self.sorter.comparisons:,}\nCompleteTree: {self.sorter.is_complete_tree(arr_copy)}")
        self.sc_lbl.configure(text=f"Step 1/{len(self.steps)}")
        self.app.add_history({"type":"Heap","algo":"Heapsort In-Place","n":len(self.arr),
                              "time":elapsed,"comparisons":self.sorter.comparisons})
        if self.steps:
            a, hl, lb = self.steps[0]
            self._draw_tree(a, hl); self._draw_bars(a, hl)
            self.step_lbl.configure(text=lb)

    def _animate(self):
        if not self.steps: return
        if self.anim_running: return
        self.anim_running = True
        self.step_idx = 0
        self._anim_loop()

    def _anim_loop(self):
        if self.step_idx >= len(self.steps) or not self.anim_running:
            self.anim_running = False
            return
        a, hl, lb = self.steps[self.step_idx]
        self._draw_tree(a, hl)
        self._draw_bars(a, hl)
        self.step_lbl.configure(text=lb)
        self.sc_lbl.configure(text=f"Step {self.step_idx+1}/{len(self.steps)}")
        self.step_idx += 1
        delay = max(50, int(self.speed_var.get()*1000))
        self.bar_canvas.after(delay, self._anim_loop)

    def _prev_step(self):
        self.anim_running = False
        if self.step_idx > 1: self.step_idx -= 2
        elif self.step_idx == 1: self.step_idx = 0
        if self.steps and self.step_idx < len(self.steps):
            a, hl, lb = self.steps[self.step_idx]
            self._draw_tree(a, hl); self._draw_bars(a, hl)
            self.step_lbl.configure(text=lb)
            self.sc_lbl.configure(text=f"Step {self.step_idx+1}/{len(self.steps)}")
            self.step_idx += 1

    def _next_step(self):
        self.anim_running = False
        if self.steps and self.step_idx < len(self.steps):
            a, hl, lb = self.steps[self.step_idx]
            self._draw_tree(a, hl); self._draw_bars(a, hl)
            self.step_lbl.configure(text=lb)
            self.sc_lbl.configure(text=f"Step {self.step_idx+1}/{len(self.steps)}")
            self.step_idx = min(self.step_idx+1, len(self.steps))

    def _draw_tree(self, arr, highlights):
        self.tree_canvas.delete("all")
        if not arr: return
        w = self.tree_canvas.winfo_width() or 700
        h = 220
        n = len(arr)
        if n == 0: return
        r = 18
        levels = int(math.log2(n)) + 1

        def draw_node(i):
            if i >= n: return
            level = int(math.log2(i+1))
            pos_in_level = i - (2**level - 1)
            nodes_in_level = 2**level
            spacing = w / (nodes_in_level + 1)
            cx = spacing * (pos_in_level + 1)
            cy = 20 + level * (h - 20) / max(levels, 1)
            color = C["bar_compare"] if i in highlights else (C["bar_sorted"] if i >= n//2 else C["accent"])

            for child_offset, c_i in [(1, 2*i+1), (2, 2*i+2)]:
                if c_i < n:
                    cl = int(math.log2(c_i+1))
                    cp = c_i - (2**cl - 1)
                    cs = w / (2**cl + 1)
                    ccx = cs * (cp + 1)
                    ccy = 20 + cl * (h - 20) / max(levels, 1)
                    self.tree_canvas.create_line(cx, cy, ccx, ccy, fill="#334155", width=1)
            self.tree_canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=color, outline="white")
            self.tree_canvas.create_text(cx, cy, text=str(arr[i]), fill="white",
                                          font=("Segoe UI",8,"bold"))
            draw_node(2*i+1)
            draw_node(2*i+2)

        draw_node(0)

    def _draw_bars(self, arr, highlights):
        self.bar_canvas.delete("all")
        if not arr: return
        self.bar_canvas.update_idletasks()
        w = self.bar_canvas.winfo_width() or 700
        h = self.bar_canvas.winfo_height() or 150
        n = len(arr); mx = max(arr) if arr else 1
        bar_w = max(2, (w-20)//n)
        pad_x = (w - n*bar_w)//2
        for i, v in enumerate(arr):
            bh = max(4, int(v/mx*(h-25)))
            x0 = pad_x+i*bar_w+1; x1 = pad_x+(i+1)*bar_w-1
            y0 = h-20-bh; y1 = h-20
            is_final = highlights == list(range(n))
            color = C["bar_sorted"] if i in highlights else C["bar_default"]
            self.bar_canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")
            if n <= 25:
                self.bar_canvas.create_text((x0+x1)//2, y0-5, text=str(v),
                                             fill="white", font=("Segoe UI",7))

    def _reset(self): self.anim_running=False; self._generate()


class PageExprTree:
    def __init__(self, parent, app):
        self.parent = parent
        self.app    = app
        self._build()

    def _build(self):
        page_header(self.parent, "Expression Tree  (Pohon Ekspresi)",
                    "Membangun dan mengevaluasi ekspresi aritmetika via pohon ekspresi.")

        pane = tk.Frame(self.parent, bg=C["content_bg"])
        pane.pack(fill="both", expand=True, padx=24, pady=4)

        left = tk.Frame(pane, bg=C["content_bg"], width=340)
        left.pack(side="left", fill="y", padx=(0,12))
        left.pack_propagate(False)

        cfg = tk.Frame(left, bg=C["card_bg"], highlightbackground=C["border"], highlightthickness=1)
        cfg.pack(fill="x", pady=6)
        tk.Label(cfg, text="Input Ekspresi", font=tkfont.Font(family="Segoe UI",size=12,weight="bold"),
                 fg=C["text_dark"], bg=C["card_bg"]).pack(anchor="w", padx=14, pady=(12,4))
        tk.Label(cfg, text="Ekspresi harus fully parenthesized.\nContoh: ((8*5)+(9/(7-4)))",
                 font=tkfont.Font(family="Segoe UI",size=9), fg=C["text_mid"], bg=C["card_bg"],
                 justify="left").pack(anchor="w", padx=14)
        self.expr_var = tk.StringVar(value="((8*5)+(9/(7-4)))")
        tk.Entry(cfg, textvariable=self.expr_var, font=tkfont.Font(family="Consolas",size=11),
                 relief="solid", width=30).pack(anchor="w", padx=14, pady=6)

        examples = [
            ("((8*5)+(9/(7-4)))", "Contoh 1"),
            ("((3+4)*(2-1))", "Contoh 2"),
            ("(((2+3)*(4-1))/(5+0))", "Contoh 3"),
            ("((10/2)+(3*4))", "Contoh 4"),
        ]
        tk.Label(cfg, text="Contoh cepat:", font=tkfont.Font(family="Segoe UI",size=9),
                 fg=C["text_mid"], bg=C["card_bg"]).pack(anchor="w", padx=14)
        for expr, lbl in examples:
            def pick(e=expr): self.expr_var.set(e)
            tk.Button(cfg, text=lbl, command=pick, font=tkfont.Font(family="Segoe UI",size=8),
                      bg=C["border"], fg=C["text_dark"], relief="flat", cursor="hand2",
                      padx=6, pady=2).pack(anchor="w", padx=14, pady=1)

        br = tk.Frame(cfg, bg=C["card_bg"])
        br.pack(padx=14, pady=10)
        make_btn(br, "▶  Evaluasi", self._evaluate).pack(side="left", padx=(0,6))
        make_btn(br, "↺  Reset", lambda: self.expr_var.set("((8*5)+(9/(7-4)))"), color="#64748B").pack(side="left")

        res = tk.Frame(left, bg=C["card_bg"], highlightbackground=C["border"], highlightthickness=1)
        res.pack(fill="x", pady=6)
        tk.Label(res, text="Hasil Evaluasi", font=tkfont.Font(family="Segoe UI",size=12,weight="bold"),
                 fg=C["text_dark"], bg=C["card_bg"]).pack(anchor="w", padx=14, pady=(12,4))
        self.result_lbl = tk.Label(res, text="—", font=tkfont.Font(family="Segoe UI",size=32,weight="bold"),
                                    fg=C["accent"], bg=C["card_bg"])
        self.result_lbl.pack(anchor="w", padx=14)
        self.err_lbl = tk.Label(res, text="", font=tkfont.Font(family="Segoe UI",size=9),
                                 fg=C["accent4"], bg=C["card_bg"])
        self.err_lbl.pack(anchor="w", padx=14, pady=(0,12))

        # Traversal
        trav = tk.Frame(left, bg=C["card_bg"], highlightbackground=C["border"], highlightthickness=1)
        trav.pack(fill="x", pady=6)
        tk.Label(trav, text="Hasil Traversal", font=tkfont.Font(family="Segoe UI",size=12,weight="bold"),
                 fg=C["text_dark"], bg=C["card_bg"]).pack(anchor="w", padx=14, pady=(12,4))
        self.inorder_lbl  = tk.Label(trav, text="Inorder  : —", font=tkfont.Font(family="Consolas",size=9),
                                      fg=C["text_mid"], bg=C["card_bg"], wraplength=280, justify="left")
        self.inorder_lbl.pack(anchor="w", padx=14)
        self.preorder_lbl = tk.Label(trav, text="Preorder : —", font=tkfont.Font(family="Consolas",size=9),
                                      fg=C["text_mid"], bg=C["card_bg"], wraplength=280, justify="left")
        self.preorder_lbl.pack(anchor="w", padx=14)
        self.postorder_lbl= tk.Label(trav, text="Postorder: —", font=tkfont.Font(family="Consolas",size=9),
                                      fg=C["text_mid"], bg=C["card_bg"], wraplength=280, justify="left")
        self.postorder_lbl.pack(anchor="w", padx=14, pady=(0,12))

        right = tk.Frame(pane, bg=C["content_bg"])
        right.pack(side="left", fill="both", expand=True)
        viz = tk.Frame(right, bg=C["card_bg"], highlightbackground=C["border"], highlightthickness=1)
        viz.pack(fill="both", expand=True)
        tk.Label(viz, text="Pohon Ekspresi", font=tkfont.Font(family="Segoe UI",size=12,weight="bold"),
                 fg=C["text_dark"], bg=C["card_bg"]).pack(anchor="w", padx=14, pady=(12,4))
        self.tree_canvas = tk.Canvas(viz, bg=C["canvas_bg"], highlightthickness=0)
        self.tree_canvas.pack(fill="both", expand=True, padx=14, pady=(0,14))

    def _evaluate(self):
        expr = self.expr_var.get().strip()
        if not expr:
            return
        try:
            ehs = ExprHeapSorter(expr)
            result = ehs.parse_and_evaluate()
            self.result_lbl.configure(text=str(result[0]), fg=C["accent"])
            self.err_lbl.configure(text="✓ Evaluasi berhasil")

            tokens = deque(expr.replace(" ",""))
            tree_root = ehs._build_tree(tokens)
            self._draw_tree(tree_root)

            # traversals
            inorder   = []; self._inorder(tree_root, inorder)
            preorder  = []; self._preorder(tree_root, preorder)
            postorder = []; self._postorder(tree_root, postorder)
            self.inorder_lbl.configure(text=f"Inorder  : {' '.join(map(str,inorder))}")
            self.preorder_lbl.configure(text=f"Preorder : {' '.join(map(str,preorder))}")
            self.postorder_lbl.configure(text=f"Postorder: {' '.join(map(str,postorder))}")
        except Exception as e:
            self.result_lbl.configure(text="Error", fg=C["accent4"])
            self.err_lbl.configure(text=str(e))
            self.tree_canvas.delete("all")

    def _inorder(self, node, out):
        if node is None: return
        self._inorder(node.get('left'), out)
        out.append(node['val'])
        self._inorder(node.get('right'), out)

    def _preorder(self, node, out):
        if node is None: return
        out.append(node['val'])
        self._preorder(node.get('left'), out)
        self._preorder(node.get('right'), out)

    def _postorder(self, node, out):
        if node is None: return
        self._postorder(node.get('left'), out)
        self._postorder(node.get('right'), out)
        out.append(node['val'])

    def _tree_height(self, node):
        if node is None: return 0
        return 1 + max(self._tree_height(node.get('left')), self._tree_height(node.get('right')))

    def _draw_tree(self, root):
        self.tree_canvas.delete("all")
        if root is None: return
        self.tree_canvas.update_idletasks()
        w = self.tree_canvas.winfo_width() or 700
        h = self.tree_canvas.winfo_height() or 400
        height = self._tree_height(root)
        r = 22

        def draw(node, x, y, dx):
            if node is None: return
            val = node['val']
            is_op = val in ('+','-','*','/')
            color = C["accent3"] if is_op else C["accent2"]
            lc = node.get('left')
            rc = node.get('right')
            if lc:
                lx = x - dx; ly = y + 70
                self.tree_canvas.create_line(x, y, lx, ly, fill="#334155", width=2)
                draw(lc, lx, ly, dx//2)
            if rc:
                rx = x + dx; ry = y + 70
                self.tree_canvas.create_line(x, y, rx, ry, fill="#334155", width=2)
                draw(rc, rx, ry, dx//2)
            self.tree_canvas.create_oval(x-r, y-r, x+r, y+r, fill=color, outline="white", width=2)
            self.tree_canvas.create_text(x, y, text=str(val), fill="white",
                                          font=("Segoe UI", 12, "bold"))

        draw(root, w//2, 40, w//4)


class PageVisualisasi:
    def __init__(self, parent, app):
        self.parent = parent
        self.app    = app
        self._build()

    def _build(self):
        page_header(self.parent, "Visualisasi Perbandingan Algoritma",
                    "Bandingkan performa Merge Sort vs Quick Sort vs Heap Sort.")

        pane = tk.Frame(self.parent, bg=C["content_bg"])
        pane.pack(fill="both", expand=True, padx=24, pady=4)

        left = tk.Frame(pane, bg=C["content_bg"], width=280)
        left.pack(side="left", fill="y", padx=(0,12))
        left.pack_propagate(False)

        cfg = tk.Frame(left, bg=C["card_bg"], highlightbackground=C["border"], highlightthickness=1)
        cfg.pack(fill="x", pady=6)
        tk.Label(cfg, text="Konfigurasi Benchmark", font=tkfont.Font(family="Segoe UI",size=12,weight="bold"),
                 fg=C["text_dark"], bg=C["card_bg"]).pack(anchor="w", padx=14, pady=(12,6))

        tk.Label(cfg, text="Ukuran data (koma):", font=tkfont.Font(family="Segoe UI",size=9),
                 fg=C["text_mid"], bg=C["card_bg"]).pack(anchor="w", padx=14)
        self.sizes_var = tk.StringVar(value="100,500,1000,2000,5000")
        tk.Entry(cfg, textvariable=self.sizes_var, width=28, relief="solid").pack(anchor="w", padx=14, pady=2)

        tk.Label(cfg, text="Mode Data:", font=tkfont.Font(family="Segoe UI",size=9),
                 fg=C["text_mid"], bg=C["card_bg"]).pack(anchor="w", padx=14, pady=(6,0))
        self.bmode_var = tk.StringVar(value="Acak (Random)")
        ttk.Combobox(cfg, textvariable=self.bmode_var, width=22, state="readonly",
                     values=["Acak (Random)","Terurut Naik","Terurut Turun"]).pack(anchor="w", padx=14, pady=2)

        make_btn(cfg, "▶  Jalankan Benchmark", self._run_benchmark).pack(anchor="w", padx=14, pady=(10,12))

        res = tk.Frame(left, bg=C["card_bg"], highlightbackground=C["border"], highlightthickness=1)
        res.pack(fill="both", expand=True, pady=6)
        tk.Label(res, text="Tabel Hasil", font=tkfont.Font(family="Segoe UI",size=12,weight="bold"),
                 fg=C["text_dark"], bg=C["card_bg"]).pack(anchor="w", padx=14, pady=(12,4))
        self.result_txt = tk.Text(res, font=tkfont.Font(family="Consolas",size=8), bg=C["canvas_bg"],
                                   fg="white", relief="flat", wrap="none", state="disabled")
        self.result_txt.pack(fill="both", expand=True, padx=14, pady=(0,12))

        right = tk.Frame(pane, bg=C["content_bg"])
        right.pack(side="left", fill="both", expand=True)

        viz = tk.Frame(right, bg=C["card_bg"], highlightbackground=C["border"], highlightthickness=1)
        viz.pack(fill="both", expand=True)
        tk.Label(viz, text="Grafik Perbandingan Waktu (s)", font=tkfont.Font(family="Segoe UI",size=12,weight="bold"),
                 fg=C["text_dark"], bg=C["card_bg"]).pack(anchor="w", padx=14, pady=(12,4))
        self.chart_canvas = tk.Canvas(viz, bg=C["canvas_bg"], highlightthickness=0)
        self.chart_canvas.pack(fill="both", expand=True, padx=14, pady=(0,8))

        leg = tk.Frame(viz, bg=C["card_bg"])
        leg.pack(anchor="w", padx=14, pady=(0,12))
        for color, label in [(C["accent"],"Merge Sort"),(C["accent3"],"Quick Sort"),(C["accent2"],"Heap Sort")]:
            lf = tk.Frame(leg, bg=C["card_bg"])
            lf.pack(side="left", padx=8)
            tk.Frame(lf, bg=color, width=16, height=16).pack(side="left")
            tk.Label(lf, text=label, font=tkfont.Font(family="Segoe UI",size=9),
                     fg=C["text_mid"], bg=C["card_bg"]).pack(side="left", padx=3)

    def _run_benchmark(self):
        try:
            sizes = [int(x.strip()) for x in self.sizes_var.get().split(",") if x.strip()]
        except: sizes = [100,500,1000,2000,5000]

        mode = self.bmode_var.get()
        results = {"Merge Sort": [], "Quick Sort": [], "Heap Sort": []}

        for n in sizes:
            if mode == "Terurut Naik":
                data = list(range(1, n+1))
            elif mode == "Terurut Turun":
                data = list(range(n, 0, -1))
            else:
                data = [random.randint(1, n*10) for _ in range(n)]

            s = AdvancedSorter()
            t0 = time.time(); s.sort_array(list(data)); results["Merge Sort"].append(time.time()-t0)
            t0 = time.time(); s.sort_array_quick(list(data)); results["Quick Sort"].append(time.time()-t0)
            ehs = ExprHeapSorter("")
            t0 = time.time(); ehs.heapsort_inplace(list(data)); results["Heap Sort"].append(time.time()-t0)

        # Update text
        self.result_txt.configure(state="normal")
        self.result_txt.delete("1.0","end")
        header = f"{'n':>8} | {'Merge':>8} | {'Quick':>8} | {'Heap':>8}\n"
        sep    = "-"*40+"\n"
        self.result_txt.insert("end", header+sep)
        for i, n in enumerate(sizes):
            row = f"{n:>8} | {results['Merge Sort'][i]:>8.4f} | {results['Quick Sort'][i]:>8.4f} | {results['Heap Sort'][i]:>8.4f}\n"
            self.result_txt.insert("end", row)
        self.result_txt.configure(state="disabled")

        self._draw_chart(sizes, results)

    def _draw_chart(self, sizes, results):
        self.chart_canvas.delete("all")
        self.chart_canvas.update_idletasks()
        w = self.chart_canvas.winfo_width() or 700
        h = self.chart_canvas.winfo_height() or 350
        pad_l, pad_r, pad_t, pad_b = 60, 30, 30, 50

        all_vals = [v for algo_vals in results.values() for v in algo_vals]
        max_val  = max(all_vals) if all_vals else 1
        n_sizes  = len(sizes)
        if n_sizes < 2: return

        # axes
        self.chart_canvas.create_line(pad_l, pad_t, pad_l, h-pad_b, fill="#334155", width=2)
        self.chart_canvas.create_line(pad_l, h-pad_b, w-pad_r, h-pad_b, fill="#334155", width=2)

        # y labels
        for i in range(5):
            yv = max_val * i / 4
            y  = h - pad_b - (yv/max_val) * (h-pad_t-pad_b)
            self.chart_canvas.create_text(pad_l-8, y, text=f"{yv:.4f}", fill="#64748B",
                                           font=("Segoe UI",7), anchor="e")
            self.chart_canvas.create_line(pad_l, y, w-pad_r, y, fill="#1E293B", dash=(4,4))

        # x labels
        chart_w = w - pad_l - pad_r
        for i, n in enumerate(sizes):
            x = pad_l + i * chart_w / (n_sizes-1)
            self.chart_canvas.create_text(x, h-pad_b+14, text=str(n), fill="#64748B",
                                           font=("Segoe UI",8))

        colors = {"Merge Sort": C["accent"], "Quick Sort": C["accent3"], "Heap Sort": C["accent2"]}
        for algo, vals in results.items():
            color = colors[algo]
            points = []
            for i, v in enumerate(vals):
                x = pad_l + i * chart_w / max(1, n_sizes-1)
                y = h - pad_b - (v/max_val) * (h-pad_t-pad_b)
                points.append((x, y))
            for i in range(len(points)-1):
                x0,y0 = points[i]; x1,y1 = points[i+1]
                self.chart_canvas.create_line(x0,y0,x1,y1, fill=color, width=2, smooth=True)
            for x, y in points:
                self.chart_canvas.create_oval(x-4,y-4,x+4,y+4, fill=color, outline="white")


class PageTeori:
    def __init__(self, parent, app):
        self.parent = parent
        self.app    = app
        self._build()

    def _build(self):
        page_header(self.parent, "Teori & Analisis Algoritma",
                    "Penjelasan mendalam tentang setiap algoritma dan kompleksitasnya.")

        scroll_frame = tk.Frame(self.parent, bg=C["content_bg"])
        scroll_frame.pack(fill="both", expand=True, padx=24, pady=4)

        canvas = tk.Canvas(scroll_frame, bg=C["content_bg"], highlightthickness=0)
        vsb = ttk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=C["content_bg"])
        canvas.create_window(0, 0, anchor="nw", window=inner)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        sections = [
            ("A. Merge Sort — Array", C["accent"], [
                ("Konsep", "Membagi array menjadi dua bagian, mengurutkan secara rekursif, lalu menggabungkan (divide and conquer)."),
                ("Virtual Sublists", "Tidak membuat array baru di setiap rekursi. Menggunakan indeks [first..mid] dan [mid+1..last] sebagai batas sublist virtual. Hanya satu tmpArray berukuran n yang dialokasikan di awal."),
                ("Kompleksitas Waktu", "O(n log n) — semua kasus (best, average, worst). Karena rekursi selalu membagi dua secara seimbang."),
                ("Kompleksitas Ruang", "O(n) untuk tmpArray. O(log n) untuk stack rekursi. Total: O(n)."),
                ("Stabilitas", "STABIL ✓ — kondisi arr[a] <= arr[b] memastikan elemen kiri diambil lebih dulu ketika nilainya sama."),
                ("Kenapa tidak Radix Sort?", "Radix Sort memerlukan 10 queue/bucket untuk setiap digit, total O(n+k) ruang tambahan. Ini melanggar batasan O(1) ekstra pada Modul A."),
            ]),
            ("B. Merge Sort — Linked List", C["accent2"], [
                ("Konsep", "Identik dengan array, namun pemisahan menggunakan fast-slow pointer dan penggabungan via dummy node."),
                ("Fast-Slow Pointer (Floyd's)", "midPoint bergerak 1 langkah, curNode 2 langkah. Ketika curNode mencapai akhir, midPoint berada di tengah. Hanya 1 traversal, tanpa menghitung panjang."),
                ("Dummy Node Trick", "Node sentinel statis (bukan alokasi baru). tail selalu menunjuk ke ujung hasil merge. Hanya memodifikasi pointer .next, tidak ada node baru."),
                ("Kompleksitas Ruang", "O(log n) — hanya dari call stack rekursi. Tidak ada alokasi node baru selama sorting."),
                ("Mengapa Merge Sort unggul?", "Quick Sort pada linked list memerlukan traversal O(n) untuk akses random ke pivot. Median-of-Three tidak efisien. Merge Sort selalu O(n log n) tanpa overhead akses acak."),
            ]),
            ("C. Quick Sort — Median-of-Three + Depth Limiter", C["accent3"], [
                ("Pivot Naive vs Median-of-Three", "Pivot naive (selalu elemen pertama) pada data descending menghasilkan partisi paling tidak seimbang (n-1 dan 0), sehingga rekursi mencapai kedalaman O(n) dan waktu O(n²)."),
                ("Median-of-Three", "Ambil arr[first], arr[mid], arr[last]. Urutkan ketiganya, gunakan yang di tengah sebagai pivot. Menghindari worst-case pada data terurut."),
                ("Depth Limiter", "Jika kedalaman rekursi > 2·log₂(n), otomatis beralih ke Merge Sort. Ini menjamin kompleksitas waktu O(n log n) di semua kasus (seperti Introsort)."),
                ("Stabilitas", "TIDAK STABIL ✗ — swap jarak jauh mengubah urutan relatif elemen bernilai sama."),
                ("Quick Sort pada Linked List", "Tidak direkomendasikan. Akses indeks arr[mid] memerlukan traversal O(n). Overhead ini membuat Quick Sort lebih lambat dari Merge Sort pada linked list."),
            ]),
            ("D. Heap Sort — In-Place", C["accent4"], [
                ("Fase 1: Build Max-Heap", "Iterasi dari node internal terakhir (n//2-1) ke root (0). Setiap node di-sift-down. Biaya total: O(n) bukan O(n log n) karena sebagian besar sift-down pendek."),
                ("Fase 2: Extract & Sort", "Tukar root (max) dengan elemen terakhir, kurangi heap_size, sift-down dari root. Ulangi n-1 kali. Setiap ekstraksi: O(log n). Total: O(n log n)."),
                ("Sift-Down", "Bandingkan node dengan anak kiri dan kanan. Tukar dengan yang terbesar (jika ada). Ulangi dari posisi baru. Maksimum 2·⌊log₂(n)⌋ perbandingan."),
                ("Kompleksitas", "Waktu: O(n log n) selalu. Ruang: O(1) — benar-benar in-place, hanya variabel indeks."),
                ("Kenapa tidak melanggar Ω(n log n)?", "Batas bawah berlaku untuk semua comparison sort. Heap Sort adalah comparison sort dan memang O(n log n) — tidak melanggar, justru mencapai batas optimal."),
                ("Complete Binary Tree", "Array memenuhi CBT jika setiap indeks 0..n-1 terisi berurutan tanpa lubang. Rumus: parent=(i-1)//2, left=2i+1, right=2i+2 valid hanya jika CBT terpenuhi."),
            ]),
            ("E. Expression Tree", "#8B5CF6", [
                ("Membangun Pohon", "Gunakan deque token. '(' → buat node, rekursi untuk subpohon kiri, ambil operator, rekursi untuk subpohon kanan, konsumsi ')'. Operand → node leaf."),
                ("Evaluasi Postorder", "Evaluasi kiri → kanan → root. Secara otomatis menghasilkan notasi postfix yang valid. Inorder memerlukan penanganan kurung eksplisit."),
                ("Kedalaman Rekursi", "Untuk pohon tinggi h: O(h) frame pada call stack. Untuk ekspresi fully-parenthesized seimbang: h = O(log n) di mana n = jumlah operand."),
                ("Error Handling", "Pembagian nol → raise ValueError. Token tidak valid → raise ValueError. Kurung tidak seimbang → raise ValueError."),
            ]),
            ("F. Batas Teoretis — Ω(n log n) vs Radix O(dn)", "#06B6D4", [
                ("Mengapa tidak kontradiktif?", "Ω(n log n) berlaku untuk comparison sort: algoritma yang hanya menggunakan perbandingan a < b. Radix Sort tidak membandingkan elemen secara langsung — ia mendistribusikan berdasarkan digit."),
                ("Asumsi implisit Radix Sort", "1) Kunci adalah bilangan bulat (atau string) dengan d digit terbatas (d = O(log n) untuk kunci yang reasonable). 2) Nilai digit terbatas pada rentang k kecil (mis. 0-9 untuk desimal, 0-255 untuk byte)."),
                ("Kapan Radix tidak 'linear'?", "Jika d tumbuh dengan n (mis. kunci bisa sampai n^n), maka d = O(n log n) dan Radix Sort menjadi O(n² log n) — lebih buruk dari comparison sort."),
                ("Kesimpulan", "Radix Sort 'melampaui' Ω(n log n) dengan mengeksploitasi struktur internal kunci, bukan dengan melanggar teori. Perbandingan hanya valid jika domain kunci terbatas dan diketahui."),
            ]),
        ]

        for title, accent, items in sections:
            sec = tk.Frame(inner, bg=C["card_bg"], highlightbackground=C["border"], highlightthickness=1)
            sec.pack(fill="x", pady=8)
            tk.Frame(sec, bg=accent, height=3).pack(fill="x")
            tk.Label(sec, text=title, font=tkfont.Font(family="Segoe UI",size=13,weight="bold"),
                     fg=C["text_dark"], bg=C["card_bg"]).pack(anchor="w", padx=16, pady=(10,6))
            for label, content in items:
                row = tk.Frame(sec, bg=C["card_bg"])
                row.pack(fill="x", padx=16, pady=3)
                tk.Label(row, text=f"• {label}:", font=tkfont.Font(family="Segoe UI",size=10,weight="bold"),
                         fg=accent, bg=C["card_bg"], width=22, anchor="nw").pack(side="left", anchor="n")
                tk.Label(row, text=content, font=tkfont.Font(family="Segoe UI",size=10),
                         fg=C["text_mid"], bg=C["card_bg"], wraplength=560, justify="left").pack(side="left", anchor="nw")
            tk.Frame(sec, bg=C["card_bg"], height=8).pack()


class PageTentang:
    def __init__(self, parent, app):
        self.parent = parent
        self.app    = app
        self._build()

    def _build(self):
        page_header(self.parent, "Tentang Aplikasi")

        card = tk.Frame(self.parent, bg=C["card_bg"], highlightbackground=C["border"], highlightthickness=1)
        card.pack(fill="x", padx=28, pady=16)
        tk.Frame(card, bg=C["accent"], height=3).pack(fill="x")
        tk.Label(card, text="{≡}", font=tkfont.Font(family="Segoe UI",size=48,weight="bold"),
                 fg=C["accent"], bg=C["card_bg"]).pack(pady=(20,4))
        tk.Label(card, text="Tugas Sorting", font=tkfont.Font(family="Segoe UI",size=22,weight="bold"),
                 fg=C["text_dark"], bg=C["card_bg"]).pack()
        tk.Label(card, text="AdvancedSorter — Modul Pengurutan Lanjutan", font=tkfont.Font(family="Segoe UI",size=12),
                 fg=C["text_mid"], bg=C["card_bg"]).pack(pady=(2,16))

        info_frame = tk.Frame(card, bg=C["card_bg"])
        info_frame.pack()
        for label, val in [
            ("Nama",     "Lionel Jevon Chrismana Putra"),
            ("NIM",      "25091397019"),
            ("Kelas",    "2025A"),
            ("Mata Kuliah", "Struktur Data"),
        ]:
            row = tk.Frame(info_frame, bg=C["card_bg"])
            row.pack(pady=2)
            tk.Label(row, text=f"{label}:", width=14, font=tkfont.Font(family="Segoe UI",size=11),
                     fg=C["text_light"], bg=C["card_bg"], anchor="e").pack(side="left")
            tk.Label(row, text=val, font=tkfont.Font(family="Segoe UI",size=11,weight="bold"),
                     fg=C["text_dark"], bg=C["card_bg"]).pack(side="left", padx=8)
        tk.Frame(card, bg=C["card_bg"], height=20).pack()

        feat_card = tk.Frame(self.parent, bg=C["card_bg"], highlightbackground=C["border"], highlightthickness=1)
        feat_card.pack(fill="x", padx=28, pady=8)
        tk.Label(feat_card, text="Fitur Aplikasi", font=tkfont.Font(family="Segoe UI",size=14,weight="bold"),
                 fg=C["text_dark"], bg=C["card_bg"]).pack(anchor="w", padx=16, pady=(16,8))
        features = [
            (C["accent"],  "Merge Sort Array",      "Virtual sublists + single tmpArray, O(n log n), STABIL"),
            (C["accent2"], "Merge Sort Linked List", "Fast-slow pointer + dummy node, O(n log n), O(log n) ruang"),
            (C["accent3"], "Quick Sort",             "Median-of-Three pivot + Depth Limiter fallback ke Merge Sort"),
            (C["accent4"], "Heap Sort In-Place",     "Build max-heap + sift-down, O(n log n), O(1) ruang tambahan"),
            ("#8B5CF6",    "Expression Tree",        "Parser rekursif + evaluator postorder + traversal (inorder, preorder, postorder)"),
            ("#06B6D4",    "Visualisasi Dinamis",    "Animasi langkah-per-langkah, pohon biner, grafik perbandingan"),
        ]
        for color, name, desc in features:
            row = tk.Frame(feat_card, bg=C["card_bg"])
            row.pack(fill="x", padx=16, pady=4)
            tk.Frame(row, bg=color, width=4).pack(side="left", fill="y", padx=(0,10))
            sub = tk.Frame(row, bg=C["card_bg"])
            sub.pack(side="left")
            tk.Label(sub, text=name, font=tkfont.Font(family="Segoe UI",size=11,weight="bold"),
                     fg=C["text_dark"], bg=C["card_bg"]).pack(anchor="w")
            tk.Label(sub, text=desc, font=tkfont.Font(family="Segoe UI",size=9),
                     fg=C["text_mid"], bg=C["card_bg"]).pack(anchor="w")
        tk.Frame(feat_card, bg=C["card_bg"], height=12).pack()



def _list_to_ll(lst):
    if not lst: return None
    head = ListNode(lst[0])
    cur = head
    for v in lst[1:]:
        cur.next = ListNode(v); cur = cur.next
    return head

def _ll_to_list(head):
    out = []
    while head: out.append(head.data); head = head.next
    return out


if __name__ == "__main__":
    app = App()
    app.mainloop()