"""Лабораторная работа по динамическому программированию.

Вариант 1 «Дорога к морю».
Распределение 9 суток между перевалом, долиной и берегом.
"""


TOTAL_DAYS = 9

PASS_SCORE = {1: 4, 2: 6, 3: 9, 4: 11, 5: 12, 6: 13, 7: 14}
VALLEY_SCORE = {1: 5, 2: 9, 3: 12, 4: 14, 5: 15, 6: 16, 7: 16}

COAST_SCORE = {1: 7, 2: 10, 3: 14, 4: 20}


def calculate():
    """Заполняет строки Беллмана и восстанавливает все лучшие планы."""

    written_3 = COAST_SCORE.copy()

    written_2 = {}
    best_valley_actions = {}
    stage_2_calculations = {}

    for remaining in range(2, TOTAL_DAYS):
        variants = []

        for valley_days, valley_points in VALLEY_SCORE.items():
            coast_days = remaining - valley_days

            if coast_days not in written_3:
                continue

            total = valley_points + written_3[coast_days]
            variants.append((valley_days, coast_days, total))

        best_total = max(total for _, _, total in variants)
        best_actions = [
            valley_days
            for valley_days, _, total in variants
            if total == best_total
        ]

        written_2[remaining] = best_total
        best_valley_actions[remaining] = best_actions
        stage_2_calculations[remaining] = variants

    stage_1_calculations = []

    for pass_days, pass_points in PASS_SCORE.items():
        remaining = TOTAL_DAYS - pass_days

        if remaining not in written_2:
            continue

        total = pass_points + written_2[remaining]
        stage_1_calculations.append((pass_days, remaining, total))

    maximum_score = max(total for _, _, total in stage_1_calculations)
    best_pass_actions = [
        pass_days
        for pass_days, _, total in stage_1_calculations
        if total == maximum_score
    ]

    optimal_plans = []

    for pass_days in best_pass_actions:
        remaining = TOTAL_DAYS - pass_days

        for valley_days in best_valley_actions[remaining]:
            coast_days = remaining - valley_days
            optimal_plans.append((pass_days, valley_days, coast_days))

    return {
        "written_3": written_3,
        "written_2": written_2,
        "best_valley_actions": best_valley_actions,
        "stage_2_calculations": stage_2_calculations,
        "stage_1_calculations": stage_1_calculations,
        "maximum_score": maximum_score,
        "optimal_plans": optimal_plans,
    }


def print_source_table():
    """Печатает исходную таблицу оценок."""

    print("ИСХОДНЫЕ ДАННЫЕ")
    print("-" * 73)
    print(f"{'суток':<17}" + "".join(f"{day:>8}" for day in range(1, 9)))

    rows = (
        ("1 — перевал", PASS_SCORE),
        ("2 — долина", VALLEY_SCORE),
        ("3 — берег", COAST_SCORE),
    )

    for name, scores in rows:
        values = "".join(f"{scores.get(day, '·'):>8}" for day in range(1, 9))
        print(f"{name:<17}{values}")

    print("-" * 73)


def print_results(result):
    """Печатает таблицы Беллмана, обратный ход и проверку."""

    print_source_table()

    print("\nЭТАП 3. СТРОКА «ВЫПИСАЛИ 3»")
    print("Берег получает весь оставшийся ресурс.")
    for remaining, points in result["written_3"].items():
        print(f"Осталось {remaining}: выписали {points}")

    print("\nЭТАП 2. ДОЛИНА + БЕРЕГ")
    print("-" * 66)
    print(
        f"{'Осталось':>8} {'2 взяла':>9} {'Осталось 3':>12} "
        f"{'Сумма':>8} {'Лучший результат':>18}"
    )
    print("-" * 66)

    for remaining, variants in result["stage_2_calculations"].items():
        best = result["written_2"][remaining]

        for row_number, (valley_days, coast_days, total) in enumerate(variants):
            remaining_text = str(remaining) if row_number == 0 else ""
            best_text = str(best) if total == best else ""
            print(
                f"{remaining_text:>8} {valley_days:>9} {coast_days:>12} "
                f"{total:>8} {best_text:>18}"
            )

        actions = ", ".join(map(str, result["best_valley_actions"][remaining]))
        print(f"         Записали {best}; оптимальное x2: {actions}")
        print("-" * 66)

    print("\nИТОГОВЫЕ ВЫПИСАННЫЕ СТРОКИ")
    columns = range(1, 9)
    print(f"{'суток':<17}" + "".join(f"{day:>8}" for day in columns))
    print(
        f"{'выписали 3':<17}"
        + "".join(f"{result['written_3'].get(day, '·'):>8}" for day in columns)
    )
    print(
        f"{'выписали 2':<17}"
        + "".join(f"{result['written_2'].get(day, '·'):>8}" for day in columns)
    )

    print("\nЭТАП 1. ПЕРЕВАЛ")
    print("-" * 61)
    print(
        f"{'1 взял':>8} {'Оценка 1':>10} {'Осталось':>10} "
        f"{'Выписали 2':>12} {'Сумма':>8}"
    )
    print("-" * 61)

    for pass_days, remaining, total in result["stage_1_calculations"]:
        print(
            f"{pass_days:>8} {PASS_SCORE[pass_days]:>10} {remaining:>10} "
            f"{result['written_2'][remaining]:>12} {total:>8}"
        )

    print("-" * 61)
    print(f"\nМаксимальная оценка: {result['maximum_score']}")
    print("\nВсе оптимальные планы:")

    for number, plan in enumerate(result["optimal_plans"], start=1):
        pass_days, valley_days, coast_days = plan
        score = (
            PASS_SCORE[pass_days]
            + VALLEY_SCORE[valley_days]
            + COAST_SCORE[coast_days]
        )

        assert pass_days + valley_days + coast_days == TOTAL_DAYS
        assert pass_days >= 1 and valley_days >= 1
        assert 1 <= coast_days <= 4
        assert score == result["maximum_score"]

        print(
            f"{number}. Перевал — {pass_days}, долина — {valley_days}, "
            f"берег — {coast_days}; W = {score}"
        )

    print("\nПроверка ограничений и оценок выполнена успешно.")


def main():
    result = calculate()
    print_results(result)


if __name__ == "__main__":
    main()
