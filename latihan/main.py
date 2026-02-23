# 1. DEDUPLIKASI
def deduplikasi(len):
    seen = set()
    result = []
    for item in len:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result

print("1. Deduplikasi")
print(deduplikasi([1, 2, 3, 2, 1, 4, 3, 5])) 
print(deduplikasi(["a", "b", "a", "c", "b"])) 
print('\n')

# 2. INTERSECTION DUA ARRAY
def intersection(list1, list2):
    set2 = set(list2)
    return list({x for x in list1 if x in set2})

print("2. Intersection Dua Array")
print(intersection([1, 2, 3, 4], [2, 4, 6, 8]))
print(intersection(["a", "b", "c"], ["b", "c", "d"]))
print('\n')

# 3. ANAGRAM CHECK
def is_anagram(str1, str2):
    if len(str1) != len(str2):
        return False
    
    hitungan = {}
    for char in str1.lower():
        hitungan[char] = hitungan.get(char, 0) + 1
    for char in str2.lower():
        hitungan[char] = hitungan.get(char, 0) - 1
    
    return all(v == 0 for v in hitungan.values())

print("3. Anagram Check")
print(is_anagram("ular", "luar"))  
print(is_anagram("hello", "world"))   # False
print(is_anagram("kelapa", "kepaka"))     # True
print('\n')

# 4. RECURRING
def first_recurring_char(s):
    seen = set()
    for char in s:
        if char in seen:
            return char
        seen.add(char)
    return None 

print("\n=== 4. First Recurring Character ===")
print(first_recurring_char("abcabc"))  # 'a'
print(first_recurring_char("abcdef"))  # None
print(first_recurring_char("aabbc")) 
print('\n')

# 5. BUKU TELEPON
def tambah(data):
    nama = input("Nama kontak: ").strip()
    nomor = input("Nomor telepon: ").strip()

    if not nama or not nomor:
        print("Input tidak boleh kosong.")
        return

    # cek duplikat
    for n, _ in data:
        if n.lower() == nama.lower():
            print("Kontak sudah terdaftar.")
            return

    data.append((nama, nomor))
    print("Kontak berhasil ditambahkan.")


def cari(data):
    keyword = input("Masukkan nama yang dicari: ").strip().lower()
    hasil = [item for item in data if keyword in item[0].lower()]

    if hasil:
        print("\nHasil pencarian:")
        for nama, nomor in hasil:
            print(f"- {nama} : {nomor}")
    else:
        print("Kontak tidak ditemukan.")


def tampilkan(data):
    if not data:
        print("Buku telepon kosong.")
        return

    print("\nDaftar Kontak:")
    for i, (nama, nomor) in enumerate(data, start=1):
        print(f"{i}. {nama} - {nomor}")


def hapus(data):
    nama = input("Nama yang ingin dihapus: ").strip().lower()
    for item in data:
        if item[0].lower() == nama:
            data.remove(item)
            print("Kontak berhasil dihapus.")
            return
    print("Kontak tidak ditemukan.")


def menu():
    data = []

    aksi = {
        "1": tambah,
        "2": cari,
        "3": tampilkan,
        "4": hapus
    }

    while True:
        print("\n=== MENU BUKU TELEPON ===")
        print("1. Tambah")
        print("2. Cari")
        print("3. Tampilkan")
        print("4. Hapus")
        print("0. Keluar")

        pilihan = input("Pilih: ")

        if pilihan == "0":
            print("Program selesai.")
            break
        elif pilihan in aksi:
            aksi[pilihan](data)
        else:
            print("Pilihan tidak valid.")

menu()