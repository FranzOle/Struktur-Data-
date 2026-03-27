class BigInteger:
    def __init__(self, initValue="0"):
        initValue = str(initValue).strip()
        if initValue.startswith('-'):
            self.negatif = True
            initValue = initValue[1:]
        else:
            self.negatif = False
        self.digit_list = [int(d) for d in reversed(initValue)]

    def _ke_integer(self):
        hasil = 0
        for i, d in enumerate(self.digit_list):
            hasil += d * (10 ** i)
        return -hasil if self.negatif else hasil

    @staticmethod
    def _dari_integer(nilai):
        return BigInteger(str(nilai))

    def toString(self):
        teks = "".join(str(d) for d in reversed(self.digit_list))
        if not teks:
            teks = "0"
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
    print("Pengujian Soal 1B (Python List)")
    val1 = input("Masukkan angka besar pertama: ")
    val2 = input("Masukkan angka besar kedua: ")
    
    a = BigInteger(val1)
    b = BigInteger(val2)
    
    print(f"Hasil toString a: {a.toString()}")
    print(f"a + b = {(a + b).toString()}")
    print(f"a // b = {(a // b).toString()}")
    print(f"a > b: {a > b}")