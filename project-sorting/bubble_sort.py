# bubble_sort.py - Algoritma Bubble Sort
# Mengembalikan langkah-langkah untuk animasi Tkinter

def bubble_sort_steps(arr):
    """
    Bubble sort dengan rekaman tiap langkah perbandingan dan swap.
    Returns: list_of_steps
    """
    steps = []
    a = arr[:]
    n = len(a)

    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            # Langkah perbandingan
            steps.append({
                'array': a[:],
                'compare': [j, j + 1],
                'swap': False,
                'sorted_boundary': n - i,
                'message': f"Bandingkan indeks [{j}]={a[j]} dan [{j+1}]={a[j+1]}"
            })
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
                # Langkah swap
                steps.append({
                    'array': a[:],
                    'compare': [j, j + 1],
                    'swap': True,
                    'sorted_boundary': n - i,
                    'message': f"↔ SWAP! [{j}] dan [{j+1}] → array: {a}"
                })
        if not swapped:
            steps.append({
                'array': a[:],
                'compare': [],
                'swap': False,
                'sorted_boundary': n - i,
                'message': f"Tidak ada swap di pass ke-{i+1} → Array sudah terurut!"
            })
            break

    # Langkah akhir: semua terurut
    steps.append({
        'array': a[:],
        'compare': [],
        'swap': False,
        'sorted_boundary': 0,
        'message': f"✅ Selesai! Array terurut: {a}"
    })

    return a, steps
