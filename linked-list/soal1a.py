class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class BigInteger:
    def __init__(self, initValue="0"):
        self.head = None
        initValue = str(initValue).strip()
        if initValue.startswith('-'):
            self.negatif = True
            initValue = initValue[1:]
        else:
            self.negatif = False
        
        for char in initValue:
            new_node = Node(int(char))
            new_node.next = self.head
            self.head = new_node

    def _ke_integer(self):
        hasil = 0
        sekarang = self.head
        pengali = 1
        while sekarang:
            hasil += sekarang.data * pengali
            pengali *= 10
            sekarang = sekarang.next
        return -hasil if self.negatif else hasil

    @staticmethod
    def _dari_integer(nilai):
        return BigInteger(str(nilai))

    def toString(self):
        if not self.head:
            return "0"
        angka = []
        sekarang = self.head
        while sekarang:
            angka.append(str(sekarang.data))
            sekarang = sekarang.next
        teks = "".join(reversed(angka))
        if self.negatif and teks != "0":
            return "-" + teks
        return teks

    def __lt__(self, other):
        return self._ke_integer() < other._ke_integer()

    def __le__(self, other):
        return self._ke_integer() <= other._ke_integer()

    def __gt__(self, other):
        return self._ke_integer() > other._ke_integer()

    def __ge__(self, other):
        return self._ke_integer() >= other._ke_integer()

    def __eq__(self, other):
        return self._ke_integer() == other._ke_integer()

    def __ne__(self, other):
        return self._ke_integer() != other._ke_integer()

    def __add__(self, other):
        return BigInteger._dari_integer(self._ke_integer() + other._ke_integer())

    def __mul__(self, other):
        return BigInteger._dari_integer(self._ke_integer() * other._ke_integer())

    def __floordiv__(self, other):
        return BigInteger._dari_integer(self._ke_integer() // other._ke_integer())

    def __pow__(self, other):
        return BigInteger._dari_integer(self._ke_integer() ** other._ke_integer())

    def __and__(self, other):
        return BigInteger._dari_integer(self._ke_integer() & other._ke_integer())

    def __lshift__(self, other):
        return BigInteger._dari_integer(self._ke_integer() << other._ke_integer())

    def __rshift__(self, other):
        return BigInteger._dari_integer(self._ke_integer() >> other._ke_integer())

if __name__ == "__main__":
    print("Pengujian Soal 1A (Singly Linked List)")
    val1 = input("Masukkan angka besar pertama: ")
    val2 = input("Masukkan angka besar kedua: ")
    
    a = BigInteger(val1)
    b = BigInteger(val2)
    
    print(f"Hasil toString a: {a.toString()}")
    print(f"a + b = {(a + b).toString()}")
    print(f"a * b = {(a * b).toString()}")
    print(f"a == b: {a == b}")
    print(f"a < b: {a < b}")
    print(f"a & b: {(a & b).toString()}")