"""
Tugas: Analisis & Desain Algoritma Sorting Lanjutan + Binary Tree
Nama  : Lionel Jevon Chrismana Putra
NIM   : 25091397019
Kelas : 2025A
"""

import math
from typing import List, Optional
from collections import deque


# ==============================================================
#  BAGIAN 1 — AdvancedSorter
# ==============================================================

class ListNode:
    def __init__(self, data, next=None):
        self.data = data
        self.next = next


class AdvancedSorter:
    def __init__(self):
        pass

    # ----------------------------------------------------------
    # 1. ARRAY MERGE SORT (Virtual Sublists + Single tmpArray)
    # ----------------------------------------------------------

    def sort_array(self, arr: List[int]) -> List[int]:
        """
        Mengurutkan array secara ascending menggunakan Merge Sort.
        Hanya mengalokasikan satu tmpArray berukuran n di awal.
        Tidak ada alokasi tambahan di dalam rekursi.
        """
        if len(arr) <= 1:
            return arr
        tmp_array = [0] * len(arr)   # satu-satunya alokasi tambahan O(n)
        self._rec_merge_sort(arr, 0, len(arr) - 1, tmp_array)
        return arr

    def _rec_merge_sort(self, arr, first, last, tmp_array):
        """Rekursi merge sort dengan virtual sublists (tanpa slice)."""
        if first >= last:
            return
        mid = (first + last) // 2
        self._rec_merge_sort(arr, first, mid, tmp_array)
        self._rec_merge_sort(arr, mid + 1, last, tmp_array)
        self._merge_virtual(arr, first, mid, last, tmp_array)

    def _merge_virtual(self, arr, left_start, mid, right_end, tmp_array):
        """
        Menggabungkan dua virtual sublist yang bersebelahan:
          - sublist kiri  : arr[left_start .. mid]
          - sublist kanan : arr[mid+1    .. right_end]

        Menggunakan tmp_array sebagai buffer sementara.
        STABLE: ketika nilai sama, elemen dari sublist kiri diambil lebih dulu
                (kondisi arr[a] <= arr[b] mempertahankan urutan relatif asal).
        """
        a = left_start       # pointer sublist kiri
        b = mid + 1          # pointer sublist kanan
        k = left_start       # pointer tmp_array

        while a <= mid and b <= right_end:
            # Ambil dari kiri jika sama (menjaga stabilitas)
            if arr[a] <= arr[b]:
                tmp_array[k] = arr[a]
                a += 1
            else:
                tmp_array[k] = arr[b]
                b += 1
            k += 1

        # Salin sisa sublist kiri (jika ada)
        while a <= mid:
            tmp_array[k] = arr[a]
            a += 1
            k += 1

        # Salin sisa sublist kanan (jika ada)
        while b <= right_end:
            tmp_array[k] = arr[b]
            b += 1
            k += 1

        # Salin hasil dari tmp_array kembali ke arr
        for i in range(left_start, right_end + 1):
            arr[i] = tmp_array[i]

    # ----------------------------------------------------------
    # 2. LINKED LIST MERGE SORT (Fast-Slow + Dummy Merge)
    # ----------------------------------------------------------

    def sort_linked_list(self, head: Optional[ListNode]) -> Optional[ListNode]:
        """
        Mengurutkan singly linked list secara ascending menggunakan Merge Sort.
        - Pemisahan  : fast-slow pointer (satu traversal, tanpa hitung panjang).
        - Penggabungan: dummy node + tail reference (tanpa alokasi node baru).
        - Stabilitas : dijamin karena menggunakan <= saat perbandingan.
        - Space       : O(log n) hanya dari call stack rekursi.
        """
        if head is None or head.next is None:
            return head

        right_head = self._split_linked_list(head)
        left_head  = head

        left_sorted  = self.sort_linked_list(left_head)
        right_sorted = self.sort_linked_list(right_head)

        return self._merge_linked_lists(left_sorted, right_sorted)

    def _split_linked_list(self, head: ListNode) -> Optional[ListNode]:
        """
        Memisahkan linked list menjadi dua bagian menggunakan
        fast-slow pointer (Floyd's tortoise and hare):

          midPoint : bergerak 1 langkah per iterasi  (slow)
          curNode  : bergerak 2 langkah per iterasi  (fast)

        Ketika curNode mencapai akhir, midPoint berada di tengah.
        Setelah itu putus link midPoint.next = None dan kembalikan
        head sublist kanan.
        """
        midPoint = head          # slow pointer — akan berhenti di tengah
        curNode  = head.next     # fast pointer — memulai dari node kedua

        while curNode is not None and curNode.next is not None:
            midPoint = midPoint.next
            curNode  = curNode.next.next

        # midPoint sekarang berada di node tengah
        right_head       = midPoint.next   # kepala sublist kanan
        midPoint.next    = None            # putuskan koneksi → dua list terpisah
        return right_head

    def _merge_linked_lists(self,
                            listA: Optional[ListNode],
                            listB: Optional[ListNode]) -> Optional[ListNode]:
        """
        Menggabungkan dua linked list terurut menjadi satu linked list terurut.

        Teknik:
          - dummy node  : node sentinel statis, bukan alokasi dinamis baru.
          - tail        : selalu menunjuk ke node terakhir hasil merge.
          - Hanya pointer .next yang dimodifikasi; tidak ada node baru.

        STABLE: ketika nilai sama, node dari listA diambil lebih dulu.
        """
        dummy = ListNode(0)   # satu dummy node statis per pemanggilan merge
        tail  = dummy         # tail selalu ke ujung hasil

        while listA is not None and listB is not None:
            if listA.data <= listB.data:   # <= menjamin stabilitas
                tail.next = listA
                listA     = listA.next
            else:
                tail.next = listB
                listB     = listB.next
            tail = tail.next

        # Sambungkan sisa list yang belum habis (O(1), hanya ubah pointer)
        tail.next = listA if listA is not None else listB

        return dummy.next

    # ----------------------------------------------------------
    # 3. QUICK SORT  (Median-of-Three Pivot + Depth Limiter)
    # ----------------------------------------------------------

    def sort_array_quick(self, arr: List[int]) -> List[int]:
        """
        Entry point Quick Sort dengan fallback ke Merge Sort
        ketika kedalaman rekursi melebihi 2 * log2(n).
        """
        if len(arr) <= 1:
            return arr
        self._quick_sort_recursive(arr, 0, len(arr) - 1, depth=0)
        return arr

    def _quick_sort_recursive(self, arr: List[int],
                               first: int, last: int, depth: int):
        """
        Quick Sort rekursif dengan:
          - Pivot Median-of-Three   : mencegah worst-case O(n²) pada data terurut.
          - Depth Limiter           : fallback ke Merge Sort jika depth > 2*log2(n).
        """
        if first >= last:
            return

        n = last - first + 1

        # --- Depth Limiter: fallback ke Merge Sort ---
        if n > 1 and depth > 2 * math.log2(max(n, 2)):
            sub = arr[first:last + 1]   # slice hanya untuk fallback
            self.sort_array(sub)
            arr[first:last + 1] = sub
            return

        pivot_pos = self.partition_quick(arr, first, last)
        self._quick_sort_recursive(arr, first, pivot_pos - 1, depth + 1)
        self._quick_sort_recursive(arr, pivot_pos + 1, last, depth + 1)

    def partition_quick(self, arr: List[int], first: int, last: int) -> int:
        """
        Mempartisi arr[first..last] dan mengembalikan posisi akhir pivot.

        Strategi pivot: Median-of-Three
          1. Ambil kandidat: arr[first], arr[mid], arr[last].
          2. Urutkan ketiganya secara in-place sehingga:
               arr[first] <= arr[mid] <= arr[last]
          3. Gunakan arr[first] (yang sekarang adalah median) sebagai pivot
             dengan menukarnya ke posisi first sebelum partisi standar.

        Catatan stabilitas: partisi Quick Sort secara inheren tidak stabil
        karena swap jarak jauh dapat mengubah urutan relatif elemen bernilai sama.
        Untuk kebutuhan stable sort gunakan sort_linked_list() atau sort_array().
        """
        mid = (first + last) // 2

        # --- Langkah 1: Urutkan arr[first], arr[mid], arr[last] ---
        # Pastikan arr[first] <= arr[mid]
        if arr[first] > arr[mid]:
            arr[first], arr[mid] = arr[mid], arr[first]
        # Pastikan arr[first] <= arr[last]
        if arr[first] > arr[last]:
            arr[first], arr[last] = arr[last], arr[first]
        # Pastikan arr[mid] <= arr[last]
        if arr[mid] > arr[last]:
            arr[mid], arr[last] = arr[last], arr[mid]

        # Setelah tiga swap di atas: arr[first] <= arr[mid] <= arr[last]
        # arr[mid] adalah MEDIAN — jadikan pivot dengan tukar ke arr[first]
        arr[first], arr[mid] = arr[mid], arr[first]
        pivot = arr[first]

        # --- Langkah 2: Partisi standar (Lomuto-style kiri-kanan) ---
        left  = first + 1
        right = last

        while True:
            # Geser left ke kanan selama elemen < pivot
            while left <= right and arr[left] < pivot:
                left += 1
            # Geser right ke kiri selama elemen > pivot
            while left <= right and arr[right] > pivot:
                right -= 1

            if left > right:
                break

            arr[left], arr[right] = arr[right], arr[left]
            left  += 1
            right -= 1

        # Tempatkan pivot di posisi akhirnya
        arr[first], arr[right] = arr[right], arr[first]
        return right


# ==============================================================
#  BAGIAN 2 — ExprHeapSorter
# ==============================================================

class ExprHeapSorter:
    def __init__(self, expr_str: str):
        self.expr   = expr_str
        self.values = []

    # ----------------------------------------------------------
    # 1. Expression Tree Builder & Evaluator
    # ----------------------------------------------------------

    def parse_and_evaluate(self) -> List[int]:
        """
        Membangun pohon ekspresi dari string, mengevaluasinya,
        dan mengembalikan list nilai integer hasil evaluasi.
        """
        tokens    = deque(self.expr.replace(" ", ""))
        root      = self._build_tree(tokens)
        result    = self._eval_tree(root)
        self.values = [result]
        return self.values

    def _build_tree(self, tokens: deque) -> Optional[dict]:
        """
        Membangun pohon ekspresi secara rekursif dari antrian token.

        Pola rekursi (ekspresi fully-parenthesized):
          '('    → mulai node baru; rekursi untuk subpohon kiri
          operand → buat node leaf langsung, return
          operator → simpan sebagai nilai node saat ini; rekursi untuk subpohon kanan
          ')'    → konsumsi, return node yang sudah lengkap

        Node direpresentasikan sebagai dict:
          {'val': <operator/nilai>, 'left': <node>, 'right': <node>}
        """
        if not tokens:
            return None

        token = tokens.popleft()

        # --- Tanda kurung buka → ekspresi majemuk ---
        if token == '(':
            node = {}

            # Bangun subpohon kiri
            node['left'] = self._build_tree(tokens)

            # Token berikutnya harus operator
            if not tokens:
                raise ValueError("Token tidak valid: operator tidak ditemukan")
            op = tokens.popleft()
            if op not in ('+', '-', '*', '/'):
                raise ValueError(f"Token tidak valid: '{op}' bukan operator")
            node['val'] = op

            # Bangun subpohon kanan
            node['right'] = self._build_tree(tokens)

            # Token berikutnya harus tanda kurung tutup
            if not tokens:
                raise ValueError("Token tidak valid: ')' tidak ditemukan")
            close = tokens.popleft()
            if close != ')':
                raise ValueError(f"Token tidak valid: diharapkan ')' tetapi dapat '{close}'")

            return node

        # --- Digit / bilangan negatif → node leaf ---
        # Kumpulkan digit multi-karakter (misal "12", "345")
        num_str = token
        while tokens and tokens[0].isdigit():
            num_str += tokens.popleft()

        if num_str.lstrip('-').isdigit():
            return {'val': int(num_str), 'left': None, 'right': None}

        raise ValueError(f"Token tidak valid: '{num_str}'")

    def _eval_tree(self, node: Optional[dict]) -> int:
        """
        Mengevaluasi pohon ekspresi secara postorder (left → right → root).
        Mengembalikan nilai integer hasil evaluasi subtree.
        Raise ValueError pada pembagian nol.
        """
        if node is None:
            return 0

        # Node leaf: langsung kembalikan nilainya
        if node['left'] is None and node['right'] is None:
            return node['val']

        # Evaluasi rekursif subpohon kiri dan kanan
        left_val  = self._eval_tree(node['left'])
        right_val = self._eval_tree(node['right'])

        op = node['val']
        if op == '+':
            return left_val + right_val
        elif op == '-':
            return left_val - right_val
        elif op == '*':
            return left_val * right_val
        elif op == '/':
            if right_val == 0:
                raise ValueError("Pembagian dengan nol tidak diizinkan")
            return left_val // right_val   # integer division
        else:
            raise ValueError(f"Operator tidak dikenal: '{op}'")

    # ----------------------------------------------------------
    # 2. In-Place Max-Heap Construction & Heapsort
    # ----------------------------------------------------------

    def heapsort_inplace(self, arr: List[int]) -> List[int]:
        """
        Mengurutkan array secara ascending menggunakan in-place heapsort.

        Dua fase:
          Fase 1 — Build max-heap in-place:
            Iterasi dari node internal terakhir (n//2 - 1) ke root (0).
            Setiap node di-sift-down sehingga seluruh array memenuhi
            heap order property (setiap parent >= child-nya).

          Fase 2 — Extract & sort:
            Tukar arr[0] (maksimum) dengan arr[end], kurangi heap_size,
            lalu sift-down dari root untuk memulihkan heap.
            Ulangi hingga heap_size = 1.

        Kompleksitas: O(n log n) waktu, O(1) ruang tambahan.
        """
        n = len(arr)
        if n <= 1:
            return arr

        # Fase 1: Build max-heap
        for i in range(n // 2 - 1, -1, -1):
            self._sift_down(arr, n, i)

        # Fase 2: Extract elemen satu per satu
        for end in range(n - 1, 0, -1):
            arr[0], arr[end] = arr[end], arr[0]   # pindahkan max ke akhir
            self._sift_down(arr, end, 0)           # pulihkan heap pada [0..end-1]

        return arr

    def _sift_down(self, arr: List[int], heap_size: int, idx: int):
        """
        Memulihkan heap order property dengan cara menggeser node
        pada posisi idx ke bawah hingga kondisi max-heap terpenuhi.

        Algoritma:
          1. Hitung indeks anak kiri  (left  = 2*idx + 1).
          2. Hitung indeks anak kanan (right = 2*idx + 2).
          3. Tentukan 'largest': indeks node dengan nilai terbesar
             di antara {arr[idx], arr[left], arr[right]}.
          4. Jika largest != idx, tukar arr[idx] dengan arr[largest]
             dan lanjutkan sift-down dari posisi largest.
          5. Berhenti ketika largest == idx (kondisi heap terpenuhi)
             atau idx sudah merupakan node daun.

        Jumlah perbandingan maksimum: 2 * floor(log2(heap_size)) = O(log n).
        """
        while True:
            largest = idx
            left    = 2 * idx + 1
            right   = 2 * idx + 2

            # Bandingkan dengan anak kiri
            if left < heap_size and arr[left] > arr[largest]:
                largest = left

            # Bandingkan dengan anak kanan
            if right < heap_size and arr[right] > arr[largest]:
                largest = right

            # Jika idx sudah merupakan yang terbesar, heap terpenuhi
            if largest == idx:
                break

            # Tukar dan lanjutkan dari posisi baru
            arr[idx], arr[largest] = arr[largest], arr[idx]
            idx = largest

    # ----------------------------------------------------------
    # 3. Complete Tree Validator
    # ----------------------------------------------------------

    def is_complete_tree(self, arr: List[int]) -> bool:
        """
        Memvalidasi apakah array memenuhi properti complete binary tree
        ketika dipetakan ke struktur heap berbasis array.

        Definisi Complete Binary Tree:
          Semua level terisi penuh dari kiri ke kanan tanpa "lubang".
          Pada representasi array, ini berarti seluruh indeks 0..n-1
          terisi secara berurutan tanpa ada celah.

        Validasi dilakukan dengan memeriksa bahwa untuk setiap node i
        di dalam heap berukuran n:
          - Anak kiri  (2*i+1) ada jika dan hanya jika 2*i+1 < n.
          - Anak kanan (2*i+2) ada jika dan hanya jika 2*i+2 < n.
          - Tidak boleh ada node anak kanan tanpa node anak kiri.

        Array kosong atau berukuran 1 dianggap complete tree secara trivial.
        """
        n = len(arr)
        if n <= 1:
            return True

        found_null = False   # flag: apakah sudah menemukan "slot kosong"

        for i in range(n):
            left  = 2 * i + 1
            right = 2 * i + 2

            # Cek kiri
            if left < n:
                if found_null:
                    # Ada node setelah "lubang" → bukan complete tree
                    return False
            else:
                # Tidak ada anak kiri → semua node berikutnya harus None juga
                found_null = True

            # Cek anak kanan
            if right < n:
                if found_null:
                    return False
            else:
                found_null = True

        return True

#  TEST / DEMO


def linked_list_from(lst):
    """Helper: buat linked list dari Python list."""
    if not lst:
        return None
    head = ListNode(lst[0])
    cur  = head
    for val in lst[1:]:
        cur.next = ListNode(val)
        cur = cur.next
    return head

def linked_list_to(head):
    """Helper: ubah linked list ke Python list."""
    result = []
    while head:
        result.append(head.data)
        head = head.next
    return result


if __name__ == "__main__":
    print("=" * 60)
    print("  BAGIAN 1: AdvancedSorter")
    print("=" * 60)

    sorter = AdvancedSorter()

    # --- Array Merge Sort ---
    arr1 = [38, 27, 43, 3, 9, 82, 10]
    print(f"\n[Array Merge Sort]")
    print(f"  Input : {arr1}")
    print(f"  Output: {sorter.sort_array(arr1)}")

    arr2 = [5, 5, 3, 3, 1, 1, 4, 4, 2, 2]
    print(f"\n[Array Merge Sort - Data duplikat (uji stabilitas)]")
    print(f"  Input : {arr2}")
    print(f"  Output: {sorter.sort_array(arr2)}")

    # --- Linked List Merge Sort ---
    ll = linked_list_from([4, 2, 8, 1, 7, 3, 5])
    print(f"\n[Linked List Merge Sort]")
    print(f"  Input : {linked_list_to(ll)}")
    sorted_ll = sorter.sort_linked_list(ll)
    print(f"  Output: {linked_list_to(sorted_ll)}")

    # --- Quick Sort ---
    arr3 = [64, 34, 25, 12, 22, 11, 90]
    print(f"\n[Quick Sort - Median-of-Three]")
    print(f"  Input : {arr3}")
    print(f"  Output: {sorter.sort_array_quick(arr3)}")

    arr4 = [9, 8, 7, 6, 5, 4, 3, 2, 1]   # kasus terburuk naive pivot
    print(f"\n[Quick Sort - Data descending (worst-case naive, aman dg Median-of-Three)]")
    print(f"  Input : {arr4}")
    print(f"  Output: {sorter.sort_array_quick(arr4)}")

    print("\n" + "=" * 60)
    print("  BAGIAN 2: ExprHeapSorter")
    print("=" * 60)

    # --- Expression Tree & Evaluasi ---
    expr = "((8*5)+(9/(7-4)))"
    ehs  = ExprHeapSorter(expr)
    result = ehs.parse_and_evaluate()
    print(f"\n[Expression Tree Evaluator]")
    print(f"  Ekspresi : {expr}")
    print(f"  Hasil    : {result[0]}")   # (8*5)=40, (7-4)=3, (9/3)=3, 40+3=43

    # --- Heapsort In-Place ---
    data = [result[0], 15, 7, 22, 3, 40, 11, 1]
    print(f"\n[Heapsort In-Place]")
    print(f"  Input : {data}")
    ehs2 = ExprHeapSorter("")
    print(f"  Output: {ehs2.heapsort_inplace(data)}")

    # --- Complete Tree Validator ---
    arr_complete    = [1, 2, 3, 4, 5, 6, 7]    # complete
    arr_not_complete = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]  # still complete
    arr_single      = [42]
    print(f"\n[Complete Tree Validator]")
    print(f"  {arr_complete}  → complete: {ehs2.is_complete_tree(arr_complete)}")
    print(f"  {arr_not_complete} → complete: {ehs2.is_complete_tree(arr_not_complete)}")
    print(f"  {arr_single}           → complete: {ehs2.is_complete_tree(arr_single)}")

    # --- Error handling: division by zero ---
    print(f"\n[Division by Zero Handling]")
    try:
        ehs3 = ExprHeapSorter("(8/(4-4))")
        ehs3.parse_and_evaluate()
    except ValueError as e:
        print(f"  Tertangkap ValueError: {e}")

    # --- Error handling: token tidak valid ---
    print(f"\n[Invalid Token Handling]")
    try:
        ehs4 = ExprHeapSorter("(8@5)")
        ehs4.parse_and_evaluate()
    except ValueError as e:
        print(f"  Tertangkap ValueError: {e}")

    print("\n" + "=" * 60)
    print("  Semua test selesai.")
    print("=" * 60)