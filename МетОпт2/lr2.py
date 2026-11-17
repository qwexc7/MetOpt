"""Лабораторная работа №2: метод ломаных (метод Пиявского).

Программа ищет глобальный минимум липшицевой функции одной переменной
на отрезке. Точки испытаний выбираются как нижние вершины ломаной,
а не перебором значений функции по равномерной сетке.
"""

from __future__ import annotations

import argparse
import time
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import sympy as sp


@dataclass(frozen=True)
class Trial:
    """Верхняя вершина: точка испытания и настоящее значение функции."""

    x: float
    y: float


@dataclass(frozen=True)
class LowerVertex:
    """Нижняя вершина ломаной между двумя соседними испытаниями."""

    left_index: int
    x: float
    p: float


@dataclass
class Result:
    x_min: float
    f_min: float
    lower_bound: float
    error_bound: float
    iterations: int
    evaluations: int
    elapsed_seconds: float
    lipschitz: float
    trials: list[Trial]
    history: list[tuple[int, float, float, float, float]]


def parse_function(expression: str):
    """Преобразовать строку в символьную и численную функции."""

    x = sp.Symbol("x", real=True)
    allowed = {
        "x": x,
        "sin": sp.sin,
        "cos": sp.cos,
        "tan": sp.tan,
        "exp": sp.exp,
        "sqrt": sp.sqrt,
        "log": sp.log,
        "abs": sp.Abs,
        "pi": sp.pi,
        "E": sp.E,
    }
    try:
        symbolic = sp.sympify(expression.replace("^", "**"), locals=allowed)
    except (sp.SympifyError, TypeError, SyntaxError) as exc:
        raise ValueError(f"Не удалось разобрать функцию: {exc}") from exc

    extra_symbols = symbolic.free_symbols - {x}
    if extra_symbols:
        raise ValueError(f"Неизвестные переменные: {sorted(map(str, extra_symbols))}")

    numeric = sp.lambdify(x, symbolic, modules=["numpy"])

    def scalar(value: float) -> float:
        result = float(numeric(float(value)))
        if not np.isfinite(result):
            raise ValueError(f"Функция не определена в x={value}")
        return result

    return x, symbolic, numeric, scalar


def estimate_lipschitz(
    x_symbol: sp.Symbol,
    symbolic_function: sp.Expr,
    a: float,
    b: float,
    safety_factor: float = 1.10,
    sample_count: int = 20_001,
) -> tuple[float, sp.Expr, float]:
    """Оценить L по max |f'(x)|; сетка применяется только для оценки L."""

    derivative = sp.diff(symbolic_function, x_symbol)
    derivative_numeric = sp.lambdify(x_symbol, derivative, modules=["numpy"])
    grid = np.linspace(a, b, sample_count)
    values = np.asarray(derivative_numeric(grid), dtype=float)
    if values.ndim == 0:
        values = np.full_like(grid, float(values))
    if not np.all(np.isfinite(values)):
        raise ValueError("Производная не конечна на всём отрезке; задайте L вручную.")

    max_abs_derivative = float(np.max(np.abs(values)))
    if max_abs_derivative == 0.0:
        max_abs_derivative = 1e-12
    return safety_factor * max_abs_derivative, derivative, max_abs_derivative


def lower_vertices(trials: list[Trial], lipschitz: float) -> list[LowerVertex]:
    """Вычислить все нижние вершины между соседними верхними вершинами."""

    vertices: list[LowerVertex] = []
    for i, (left, right) in enumerate(zip(trials, trials[1:])):
        x_cross = (left.x + right.x) / 2 + (left.y - right.y) / (2 * lipschitz)
        p_cross = (left.y + right.y - lipschitz * (right.x - left.x)) / 2

        tolerance = 1e-12 * max(1.0, abs(left.x), abs(right.x))
        if not left.x - tolerance <= x_cross <= right.x + tolerance:
            raise ValueError(
                "Нижняя вершина вышла за границы интервала. "
                "Вероятно, заданная константа L слишком мала."
            )
        vertices.append(LowerVertex(i, float(x_cross), float(p_cross)))
    return vertices


def piyavsky(
    function,
    a: float,
    b: float,
    eps: float,
    lipschitz: float,
    max_iterations: int = 100_000,
) -> Result:
    """Найти глобальный минимум методом ломаных."""

    if not a < b:
        raise ValueError("Должно выполняться a < b.")
    if eps <= 0:
        raise ValueError("Точность eps должна быть положительной.")
    if lipschitz <= 0:
        raise ValueError("Константа L должна быть положительной.")

    started = time.perf_counter()
    trials = [Trial(a, function(a)), Trial(b, function(b))]
    history: list[tuple[int, float, float, float, float]] = []

    for iteration in range(1, max_iterations + 1):
        vertices = lower_vertices(trials, lipschitz)
        candidate = min(vertices, key=lambda vertex: (vertex.p, vertex.x))
        best = min(trials, key=lambda trial: trial.y)

        certified_gap = best.y - candidate.p
        if certified_gap <= eps:
            elapsed = time.perf_counter() - started
            return Result(
                best.x,
                best.y,
                candidate.p,
                certified_gap,
                iteration - 1,
                len(trials),
                elapsed,
                lipschitz,
                trials,
                history,
            )

        new_y = function(candidate.x)
        local_gap = new_y - candidate.p
        history.append((iteration, candidate.x, candidate.p, new_y, local_gap))
        trials.insert(candidate.left_index + 1, Trial(candidate.x, new_y))

    raise RuntimeError(
        f"Не удалось достичь eps={eps} за {max_iterations} итераций. "
        "Проверьте L или увеличьте max_iterations."
    )


def plot_result(
    vector_function,
    result: Result,
    a: float,
    b: float,
    output_path: Path,
) -> None:
    """Построить функцию, итоговую миноранту и точки испытаний."""

    x_plot = np.linspace(a, b, 4000)
    y_plot = np.asarray(vector_function(x_plot), dtype=float)
    if y_plot.ndim == 0:
        y_plot = np.full_like(x_plot, float(y_plot))

    trial_x = np.array([point.x for point in result.trials])
    trial_y = np.array([point.y for point in result.trials])
    minorant = np.max(
        trial_y[:, None] - result.lipschitz * np.abs(x_plot[None, :] - trial_x[:, None]),
        axis=0,
    )

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(x_plot, y_plot, color="#202124", linewidth=2.2, label="Исходная функция W(x)")
    ax.plot(x_plot, minorant, color="#2e7d32", linewidth=1.7, label="Итоговая ломаная p(x)")
    ax.scatter(trial_x, trial_y, s=28, color="#1565c0", zorder=4, label="Точки испытаний")
    ax.scatter(
        [result.x_min],
        [result.f_min],
        s=130,
        marker="*",
        color="#c62828",
        zorder=5,
        label=f"Найденный минимум: x={result.x_min:.6g}, W={result.f_min:.6g}",
    )
    ax.set_title("Глобальная минимизация методом Пиявского")
    ax.set_xlabel("x")
    ax.set_ylabel("W(x)")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Метод ломаных (Пиявского)")
    parser.add_argument(
        "--function",
        default="10 + x**2 - 10*cos(2*pi*x)",
        help="Функция одной переменной x",
    )
    parser.add_argument("--a", type=float, default=-5.12, help="Левая граница")
    parser.add_argument("--b", type=float, default=5.12, help="Правая граница")
    parser.add_argument("--eps", type=float, default=0.01, help="Точность")
    parser.add_argument(
        "--L",
        type=float,
        default=None,
        help="Константа Липшица; если не указана, оценивается по производной",
    )
    parser.add_argument("--safety-factor", type=float, default=1.10, help="Запас для L")
    parser.add_argument("--max-iterations", type=int, default=100_000)
    parser.add_argument("--plot", type=Path, default=Path("piyavsky_result.png"))
    parser.add_argument("--show", action="store_true", help="Показать окно с итоговым графиком")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    x, symbolic, vector_function, scalar_function = parse_function(args.function)

    if args.L is None:
        lipschitz, derivative, max_derivative = estimate_lipschitz(
            x, symbolic, args.a, args.b, args.safety_factor
        )
        print(f"W'(x) = {derivative}")
        print(f"Оценка max |W'(x)| = {max_derivative:.10g}")
        print(f"L с запасом {100 * (args.safety_factor - 1):.1f}% = {lipschitz:.10g}")
    else:
        lipschitz = args.L
        print(f"Используется заданная L = {lipschitz:.10g}")

    result = piyavsky(
        scalar_function,
        args.a,
        args.b,
        args.eps,
        lipschitz,
        args.max_iterations,
    )
    plot_result(vector_function, result, args.a, args.b, args.plot)

    print("\nРезультат")
    print(f"x* ≈ {result.x_min:.12g}")
    print(f"W(x*) ≈ {result.f_min:.12g}")
    print(f"Глобальная нижняя оценка ≈ {result.lower_bound:.12g}")
    print(f"Гарантированный зазор ≤ {result.error_bound:.12g}")
    print(f"Итераций: {result.iterations}")
    print(f"Вычислений функции: {result.evaluations}")
    print(f"Время: {result.elapsed_seconds:.6f} с")
    print(f"График сохранён: {args.plot.resolve()}")

    if args.show:
        image = plt.imread(args.plot)
        plt.figure(figsize=(12, 7))
        plt.imshow(image)
        plt.axis("off")
        plt.show()


if __name__ == "__main__":
    main()
