def create_bigint(value="0"):
    head = None
    tail = None
    for d in reversed(value):
        node = {"digit": int(d), "next": None}
        if head is None:
            head = node
            tail = node
        else:
            tail["next"] = node
            tail = node
    return head

def to_string(head):
    digits = []
    curr = head
    while curr:
        digits.append(str(curr["digit"]))
        curr = curr["next"]
    return "".join(reversed(digits))

def to_int(head):
    return int(to_string(head))

def comparable(a, b):
    x = to_int(a)
    y = to_int(b)
    if x < y: return "<"
    if x > y: return ">"
    return "=="

def arithmetic(a, b, op):
    x = to_int(a)
    y = to_int(b)
    if op == '+':
        res = x + y
    elif op == '-':
        res = x - y
    elif op == '*':
        res = x * y
    elif op == '//':
        res = x // y
    elif op == '%':
        res = x % y
    elif op == '**':
        res = x ** y
    else:
        raise ValueError("Operator tidak valid")
    return create_bigint(str(res))

def bitwise_ops(a, b, op):
    x = to_int(a)
    y = to_int(b)
    if op == '|':
        res = x | y
    elif op == '&':
        res = x & y
    elif op == '^':
        res = x ^ y
    elif op == '<<':
        res = x << y
    elif op == '>>':
        res = x >> y
    else:
        raise ValueError("Operator tidak valid")
    return create_bigint(str(res))

if __name__ == "__main__":
    a = create_bigint("45839")
    b = create_bigint("123")
    print("a =", to_string(a))
    print("b =", to_string(b))
    print("a + b =", to_string(arithmetic(a, b, '+')))