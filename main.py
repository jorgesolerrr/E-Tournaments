prog = """

class A:
    def __init__(self):
        self.a = "A"

"""
exec(prog)

a = A()
b = A()
print(a.a, b.a)