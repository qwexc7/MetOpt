import sympy as sp


x, y, lam = sp.symbols("x y lambda", real=True)

f = x**2 + y**2
g = x - y - 2

L = f + lam * g

variables = (x, y, lam)
equations = [sp.diff(L, variable) for variable in variables]

solutions = sp.solve(equations, variables, dict=True)

print("Целевая функция: f(x, y) =", f)
print("Ограничение:g(x, y) =", g, "= 0")
print("Функция Лагранжа:L =", L)

print("\nСистема, полученная дифференцированием L:")
for variable, equation in zip(variables, equations):
    print(f"dL/d{variable} = {equation} = 0")

print(f"\nКоличество найденных корней: {len(solutions)}")

for number, solution in enumerate(solutions, start=1):
    point = {x: solution[x], y: solution[y]}
    residual = sp.simplify(g.subs(point))
    function_value = sp.simplify(f.subs(point))

    print(f"\nКорень {number}:")
    print("x=", solution[x])
    print("y=", solution[y])
    print("lambda =", solution[lam])
    print("Невязка g(x, y)=", residual)
    print("Значение f(x, y)=", function_value)

