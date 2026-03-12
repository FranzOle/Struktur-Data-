# binary_search.py - Algoritma Binary Search
# Mengembalikan langkah-langkah untuk animasi Tkinter

def binary_search_steps(arr, target):
    """
    Binary search pada array yang sudah diurutkan otomatis.
    Returns: (sorted_arr, list_of_steps)
    """
    steps = []
    sorted_arr = sorted(arr)
    low, high = 0, len(sorted_arr) - 1

    while low <= high:
        mid = (low + high) // 2
        step = {
            'array': sorted_arr[:],
            'low': low,
            'high': high,
            'mid': mid,
            'target': target,
            'status': 'searching',
            'message': f"Cek tengah: indeks [{mid}] = {sorted_arr[mid]}"
        }
        if sorted_arr[mid] == target:
            step['status'] = 'found'
            step['message'] = f"✅ Target {target} DITEMUKAN di indeks [{mid}]!"
            steps.append(step)
            break
        elif sorted_arr[mid] < target:
            step['message'] = f"[{mid}]={sorted_arr[mid]} < {target} → geser kanan (low={mid+1})"
            steps.append(step)
            low = mid + 1
        else:
            step['message'] = f"[{mid}]={sorted_arr[mid]} > {target} → geser kiri (high={mid-1})"
            steps.append(step)
            high = mid - 1
    else:
        steps.append({
            'array': sorted_arr[:],
            'low': low, 'high': low, 'mid': -1,
            'target': target, 'status': 'not_found',
            'message': f"❌ Target {target} TIDAK DITEMUKAN dalam array!"
        })

    return sorted_arr, steps
