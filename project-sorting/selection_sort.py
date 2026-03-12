# selection_sort.py - Algoritma Selection Sort
# Mengembalikan langkah-langkah untuk animasi Tkinter

def selection_sort_steps(arr):
    """
    Selection sort: tiap iterasi cari minimum, lalu swap ke posisi yang benar.
    Returns: (sorted_arr, list_of_steps)
    """
    steps = []
    a = arr[:]
    n = len(a)

    for i in range(n):
        min_idx = i
        steps.append({
            'array': a[:],
            'current_pos': i,
            'min_idx': min_idx,
            'scanning': i,
            'sorted_until': i,
            'swapped': False,
            'message': f"Pass {i+1}: Cari minimum dari indeks [{i}] ke [{n-1}]"
        })

        for j in range(i + 1, n):
            steps.append({
                'array': a[:],
                'current_pos': i,
                'min_idx': min_idx,
                'scanning': j,
                'sorted_until': i,
                'swapped': False,
                'message': f"  Cek [{j}]={a[j]} vs min=[{min_idx}]={a[min_idx]}"
            })
            if a[j] < a[min_idx]:
                min_idx = j
                steps.append({
                    'array': a[:],
                    'current_pos': i,
                    'min_idx': min_idx,
                    'scanning': j,
                    'sorted_until': i,
                    'swapped': False,
                    'message': f"  ↓ Min baru ditemukan: [{min_idx}]={a[min_idx]}"
                })

        if min_idx != i:
            a[i], a[min_idx] = a[min_idx], a[i]
            steps.append({
                'array': a[:],
                'current_pos': i,
                'min_idx': min_idx,
                'scanning': -1,
                'sorted_until': i + 1,
                'swapped': True,
                'message': f"↔ SWAP [{i}] dan [{min_idx}] → {a[i]} ke posisi [{i}]"
            })
        else:
            steps.append({
                'array': a[:],
                'current_pos': i,
                'min_idx': min_idx,
                'scanning': -1,
                'sorted_until': i + 1,
                'swapped': False,
                'message': f"[{i}]={a[i]} sudah di posisi benar, tidak perlu swap"
            })

    steps.append({
        'array': a[:],
        'current_pos': n,
        'min_idx': -1,
        'scanning': -1,
        'sorted_until': n,
        'swapped': False,
        'message': f"✅ Selesai! Array terurut: {a}"
    })

    return a, steps
