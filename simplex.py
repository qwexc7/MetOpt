from fractions import Fraction


peremennye = ["x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8"]


def drob(chislo):
    if chislo.denominator == 1:
        return str(chislo.numerator)
    return str(chislo.numerator) + "/" + str(chislo.denominator)


def stroka_c(tablica, bazis, c):
    cb = []
    for imya in bazis:
        nomer = peremennye.index(imya)
        cb.append(c[nomer])
    rezultat = []
    for j in range(8):
        zj = Fraction(0)
        for i in range(3):
            zj = zj + cb[i] * tablica[i][j]
        rezultat.append(c[j] - zj)
    f = Fraction(0)
    for i in range(3):
        f = f + cb[i] * tablica[i][8]
    rezultat.append(-f)
    return rezultat


def pechat(tablica, bazis, c, niz, nazvanie):
    shirina = 9
    nebazis = []
    nomera = []
    for j in range(8):
        if peremennye[j] not in bazis:
            nebazis.append(peremennye[j])
            nomera.append(j)
    zagolovok = ["Базис"] + nebazis + ["b"]
    liniya = "+" + "+".join(["-" * shirina] * 7) + "+"
    print("\n" + nazvanie)
    print(liniya)
    print("|", end="")
    for slovo in zagolovok:
        print(slovo.center(shirina) + "|", end="")
    print()
    print(liniya)
    for i in range(3):
        print("|" + bazis[i].center(shirina) + "|", end="")
        for j in nomera:
            print(drob(tablica[i][j]).rjust(shirina) + "|", end="")
        print(drob(tablica[i][8]).rjust(shirina) + "|", end="")
        print()
    print(liniya)
    c_stroka = stroka_c(tablica, bazis, c)
    print("|" + niz.center(shirina) + "|", end="")
    for j in nomera:
        print(drob(c_stroka[j]).rjust(shirina) + "|", end="")
    print(drob(c_stroka[8]).rjust(shirina) + "|", end="")
    print()
    print(liniya)


def obmen(tablica, bazis, vhodit, vihodit):
    stolbec = peremennye.index(vhodit)
    stroka = bazis.index(vihodit)
    vedushiy = tablica[stroka][stolbec]
    for j in range(9):
        tablica[stroka][j] = tablica[stroka][j] / vedushiy
    for i in range(3):
        if i != stroka:
            mnozhitel = tablica[i][stolbec]
            for j in range(9):
                tablica[i][j] = tablica[i][j] - mnozhitel * tablica[stroka][j]
    bazis[stroka] = vhodit


def shag(nomer, tablica, bazis, c, niz, vhodit, vihodit):
    stolbec = peremennye.index(vhodit)
    stroka = bazis.index(vihodit)
    print("\nШаг", nomer)
    print("Входит", vhodit + ", выходит", vihodit)
    print("Отношения b/a:", end=" ")
    otvet = []
    for i in range(3):
        if tablica[i][stolbec] > 0:
            otnoshenie = tablica[i][8] / tablica[i][stolbec]
            otvet.append(bazis[i] + ": " + drob(otnoshenie))
    print(", ".join(otvet))
    print("Пивот:", drob(tablica[stroka][stolbec]))
    obmen(tablica, bazis, vhodit, vihodit)
    pechat(tablica, bazis, c, niz, "Таблица после обмена " + vhodit + " ↔ " + vihodit)


tablica = [
    [Fraction(1), Fraction(1), Fraction(1), Fraction(1), Fraction(1), Fraction(0), Fraction(0), Fraction(0), Fraction(10)],
    [Fraction(2), Fraction(1), Fraction(-1), Fraction(1), Fraction(0), Fraction(0), Fraction(1), Fraction(0), Fraction(8)],
    [Fraction(0), Fraction(1), Fraction(2), Fraction(1), Fraction(0), Fraction(-1), Fraction(0), Fraction(1), Fraction(5)]
]
bazis = ["x5", "x7", "x8"]
c1 = [Fraction(0), Fraction(0), Fraction(0), Fraction(0), Fraction(0), Fraction(0), Fraction(1), Fraction(1)]

print("ВСПОМОГАТЕЛЬНАЯ ФАЗА")
pechat(tablica, bazis, c1, "C", "Начальная таблица")
shag(1, tablica, bazis, c1, "C", "x1", "x7")
shag(2, tablica, bazis, c1, "C", "x3", "x8")

c2 = [Fraction(2), Fraction(3), Fraction(1), Fraction(4), Fraction(0), Fraction(0), Fraction(0), Fraction(0)]

print("\nОСНОВНАЯ ФАЗА")
pechat(tablica, bazis, c2, "C", "Начальная таблица")
shag(1, tablica, bazis, c2, "C", "x4", "x3")
shag(2, tablica, bazis, c2, "C", "x6", "x1")
shag(3, tablica, bazis, c2, "C", "x3", "x5")

x1 = Fraction(0)
x2 = Fraction(0)
x3 = tablica[bazis.index("x3")][8]
x4 = tablica[bazis.index("x4")][8]
z = 2 * x1 + x3 + 4 * x4

print("\nИтог")
print("x* = (" + drob(x1) + ", " + drob(x2) + ", " + drob(x3) + ", " + drob(x4) + ")")
print("Zmax =", drob(z))
print("Проверка 1:", drob(x1 + x2 + x3 + x4), "<= 10")
print("Проверка 2:", drob(2 * x1 + x2 - x3 + x4), "= 8")
print("Проверка 3:", drob(x2 + 2 * x3 + x4), ">= 5")
