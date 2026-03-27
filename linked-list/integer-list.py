def create_bigint(value="0"):
    return [int(d) for d in reversed(value)]

def to_string(num):
    return ''.join(map(str, reversed(num)))

def to_int(num):
    return int(to_string(num))

def comparable(a, b):
    x, y = to_int(a), to_int(b)
    if x < y: return "<"
    if x > y: return ">"
    return "=="

def arithmetic(a, b, op):
    x, y = to_int(a), to_int(b)
    
    ops = {
        '+': x + y,
        '-': x - y,
        '*': x * y,
        '//': x // y,
        '%': x % y,
        '**': x ** y
    }
    
    if op not in ops:
        raise ValueError("Operator tidak valid")
        
    return create_bigint(str(ops[op]))

def bitwise_ops(a, b, op):
    x, y = to_int(a), to_int(b)
    
    ops = {
        '|': x | y,
        '&': x & y,
        '^': x ^ y,
        '<<': x << y,
        '>>': x >> y
    }
    
    if op not in ops:
        raise ValueError("Operator tidak valid")
        
    return create_bigint(str(ops[op]))

if __name__ == "__main__":
    a = create_bigint("45839")
    b = create_bigint("123")

    print(f"a = {to_string(a)}")
    print(f"b = {to_string(b)}")
    print(f"a * b = {to_string(arithmetic(a, b, '*'))}")