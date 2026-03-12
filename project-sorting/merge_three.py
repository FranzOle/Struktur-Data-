# merge_three.py - Algoritma Merge 3 List Terurut
# Mengembalikan langkah-langkah untuk animasi Tkinter

def merge_three_steps(list1, list2, list3):
    """
    Menggabungkan 3 list yang sudah terurut menjadi satu list terurut.
    Menggunakan pendekatan pointer tiga-arah.
    Returns: (merged_result, list_of_steps)
    """
    steps = []
    a, b, c = sorted(list1), sorted(list2), sorted(list3)
    i, j, k = 0, 0, 0
    result = []

    steps.append({
        'list1': a[:], 'list2': b[:], 'list3': c[:],
        'ptr1': i, 'ptr2': j, 'ptr3': k,
        'result': result[:],
        'picked': -1, 'picked_from': -1,
        'message': f"Mulai merge: L1={a}, L2={b}, L3={c}"
    })

    while i < len(a) or j < len(b) or k < len(c):
        val_a = a[i] if i < len(a) else float('inf')
        val_b = b[j] if j < len(b) else float('inf')
        val_c = c[k] if k < len(c) else float('inf')

        candidates = []
        if i < len(a): candidates.append(('L1', i, val_a))
        if j < len(b): candidates.append(('L2', j, val_b))
        if k < len(c): candidates.append(('L3', k, val_c))

        cand_str = ", ".join([f"{name}[{idx}]={val}" for name, idx, val in candidates])
        steps.append({
            'list1': a[:], 'list2': b[:], 'list3': c[:],
            'ptr1': i, 'ptr2': j, 'ptr3': k,
            'result': result[:],
            'picked': -1, 'picked_from': -1,
            'message': f"Bandingkan: {cand_str}"
        })

        if val_a <= val_b and val_a <= val_c:
            picked, picked_from, picked_idx = val_a, 0, i
            result.append(val_a); i += 1
        elif val_b <= val_a and val_b <= val_c:
            picked, picked_from, picked_idx = val_b, 1, j
            result.append(val_b); j += 1
        else:
            picked, picked_from, picked_idx = val_c, 2, k
            result.append(val_c); k += 1

        src = ['L1', 'L2', 'L3'][picked_from]
        steps.append({
            'list1': a[:], 'list2': b[:], 'list3': c[:],
            'ptr1': i, 'ptr2': j, 'ptr3': k,
            'result': result[:],
            'picked': picked, 'picked_from': picked_from,
            'message': f"✅ Ambil {picked} dari {src} → result: {result}"
        })

    steps.append({
        'list1': a[:], 'list2': b[:], 'list3': c[:],
        'ptr1': i, 'ptr2': j, 'ptr3': k,
        'result': result[:],
        'picked': -1, 'picked_from': -1,
        'message': f"🎉 Merge selesai! Hasil: {result}"
    })

    return result, steps
