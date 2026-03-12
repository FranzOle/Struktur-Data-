# inversion_counter.py - Algoritma Inversion Counter (menggunakan Merge Sort)
# Mengembalikan langkah-langkah untuk animasi Tkinter

def count_inversions_steps(arr):
    """
    Hitung jumlah inversi menggunakan modified merge sort.
    Inversi: pasangan (i,j) dimana i<j tetapi arr[i]>arr[j]
    Returns: (sorted_arr, total_inversions, list_of_steps)
    """
    steps = []
    total_inv = [0]
    found_pairs = []

    # Cari semua pasangan inversi untuk ditampilkan
    a = arr[:]
    for i in range(len(a)):
        for j in range(i + 1, len(a)):
            if a[i] > a[j]:
                found_pairs.append((i, j, a[i], a[j]))

    steps.append({
        'array': arr[:],
        'highlight': [],
        'inv_pairs': [],
        'count': 0,
        'phase': 'start',
        'message': f"Array awal: {arr} | Mencari semua pasangan inversi..."
    })

    # Tampilkan tiap pasangan inversi yang ditemukan
    running_pairs = []
    for idx, (i, j, vi, vj) in enumerate(found_pairs):
        running_pairs.append((i, j, vi, vj))
        steps.append({
            'array': arr[:],
            'highlight': [i, j],
            'inv_pairs': running_pairs[:],
            'count': len(running_pairs),
            'phase': 'scanning',
            'message': f"Inversi #{idx+1}: arr[{i}]={vi} > arr[{j}]={vj} ✓"
        })

    # Sekarang lakukan merge sort untuk menghitung total
    def merge_count(lst, depth=0):
        if len(lst) <= 1:
            return lst, 0
        mid = len(lst) // 2
        left, linv = merge_count(lst[:mid], depth+1)
        right, rinv = merge_count(lst[mid:], depth+1)
        merged = []
        inv = linv + rinv
        li, ri = 0, 0
        while li < len(left) and ri < len(right):
            if left[li] <= right[ri]:
                merged.append(left[li]); li += 1
            else:
                inv += len(left) - li
                merged.append(right[ri]); ri += 1
        merged += left[li:] + right[ri:]
        return merged, inv

    sorted_arr, total_inversions = merge_count(arr[:])

    steps.append({
        'array': arr[:],
        'highlight': list(range(len(arr))),
        'inv_pairs': found_pairs,
        'count': total_inversions,
        'phase': 'done',
        'message': f"🎉 Total Inversi: {total_inversions} pasangan | Array terurut: {sorted_arr}"
    })

    return sorted_arr, total_inversions, found_pairs, steps
