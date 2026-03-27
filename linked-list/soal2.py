class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class BigInteger:
    def __init__(self, initValue="0"):
        self._bangun_struktur(str(initValue))

    def _bangun_struktur(self, teks):
        self.head = None
        teks = teks.strip()
        if teks.startswith('-'):
            self.negatif = True
            teks = teks[1:]
        else:
            self.negatif = False
        for char in teks:
            simpul_baru = Node(int(char))
            simpul_baru.next = self.head
            self.head = simpul_baru

    def _ke_integer(self):
        hasil = 0
        sekarang = self.head
        pengali = 1
        while sekarang:
            hasil += sekarang.data * pengali
            pengali *= 10
            sekarang = sekarang.next
        return -hasil if self.negatif else hasil

    def toString(self):
        angka = []
        sekarang = self.head
        while sekarang:
            angka.append(str(sekarang.data))
            sekarang = sekarang.next
        teks = "".join(reversed(angka)) if angka else "0"
        if self.negatif and teks != "0":
            return "-" + teks
        return teks

    def __iadd__(self, other):
        hasil = self._ke_integer() + other._ke_integer()
        self._bangun_struktur(str(hasil))
        return self

    def __isub__(self, other):
        hasil = self._ke_integer() - other._ke_integer()
        self._bangun_struktur(str(hasil))
        return self

    def __imul__(self, other):
        hasil = self._ke_integer() * other._ke_integer()
        self._bangun_struktur(str(hasil))
        return self

    def __ifloordiv__(self, other):
        hasil = self._ke_integer() // other._ke_integer()
        self._bangun_struktur(str(hasil))
        return self

    def __imod__(self, other):
        hasil = self._ke_integer() % other._ke_integer()
        self._bangun_struktur(str(hasil))
        return self

    def __ipow__(self, other):
        hasil = self._ke_integer() ** other._ke_integer()
        self._bangun_struktur(str(hasil))
        return self

    def __ilshift__(self, other):
        hasil = self._ke_integer() << other._ke_integer()
        self._bangun_struktur(str(hasil))
        return self

    def __irshift__(self, other):
        hasil = self._ke_integer() >> other._ke_integer()
        self._bangun_struktur(str(hasil))
        return self

    def __iand__(self, other):
        hasil = self._ke_integer() & other._ke_integer()
        self._bangun_struktur(str(hasil))
        return self

    def __ior__(self, other):
        hasil = self._ke_integer() | other._ke_integer()
        self._bangun_struktur(str(hasil))
        return self

    def __ixor__(self, other):
        hasil = self._ke_integer() ^ other._ke_integer()
        self._bangun_struktur(str(hasil))
        return self

if __name__ == "__main__":
    print("Pengujian Soal 2 (Assignment Combo Operators)")
    awal = input("Masukkan angka awal: ")
    tambah = input("Masukkan angka untuk += : ")
    kali = input("Masukkan angka untuk *= : ")
    
    obj = BigInteger(awal)
    b = BigInteger(tambah)
    c = BigInteger(kali)
    
    print(f"Nilai awal: {obj.toString()}")
    obj += b
    print(f"Setelah += : {obj.toString()}")
    obj *= c
    print(f"Setelah *= : {obj.toString()}")
    
    geser = int(input("Masukkan angka untuk <<= (integer): "))
    d = BigInteger(str(geser))
    obj <<= d
    print(f"Setelah <<= : {obj.toString()}")