"""Compare chained and linear-probing hash tables at the same load factors."""

import csv
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.hash_table import HashTable, LinearHashTable, horner_hash


TABLE_SIZE = 503
ALPHAS = (0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90)
SEED = 2026


def chain_success(table, keys):
    total = 0
    for key in keys:
        node = table.table[horner_hash(key, table.size)]
        probes = 1
        while node is not None:
            if node.key == key:
                break
            probes += 1
            node = node.next
        total += probes
    return total / len(keys)


def chain_failure(table, keys):
    total = 0
    for key in keys:
        node = table.table[horner_hash(key, table.size)]
        probes = 0
        while node is not None:
            probes += 1
            node = node.next
        total += probes
    return total / len(keys)


def linear_success(table, keys):
    total = 0
    for key in keys:
        index = horner_hash(key, table.size)
        start = index
        probes = 1
        while True:
            if table.keys[index] is table._EMPTY:
                break
            if table.keys[index] is not table._TOMB and table.keys[index] == key:
                break
            probes += 1
            index = (index + 1) % table.size
            if index == start:
                break
        total += probes
    return total / len(keys)


def linear_failure(table, keys):
    total = 0
    for key in keys:
        index = horner_hash(key, table.size)
        start = index
        probes = 1
        while table.keys[index] is not table._EMPTY:
            probes += 1
            index = (index + 1) % table.size
            if index == start:
                break
        total += probes
    return total / len(keys)


def write_csv(rows, path):
    fields = [
        "alpha",
        "item_count",
        "chain_success",
        "chain_failure",
        "linear_success",
        "linear_failure",
        "chain_theory_success",
        "chain_theory_failure",
        "linear_theory_success",
        "linear_theory_failure",
    ]
    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_svg(rows, path):
    width, height = 800, 500
    left, right, top, bottom = 75, 760, 55, 430
    max_y = 55

    def x(alpha):
        return left + alpha * (right - left)

    def y(value):
        return bottom - value / max_y * (bottom - top)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="400" y="24" text-anchor="middle" font-size="18">Probe Cost Comparison</text>',
    ]
    for tick in range(max_y + 1):
        y_pos = y(tick)
        parts.append(f'<line x1="{left}" y1="{y_pos:.1f}" x2="{right}" y2="{y_pos:.1f}" stroke="#ddd"/>')
        parts.append(f'<text x="{left-10}" y="{y_pos+4:.1f}" text-anchor="end" font-size="12">{tick}</text>')
    for alpha in ALPHAS:
        x_pos = x(alpha)
        parts.append(f'<line x1="{x_pos:.1f}" y1="{top}" x2="{x_pos:.1f}" y2="{bottom}" stroke="#eee"/>')
        parts.append(f'<text x="{x_pos:.1f}" y="{bottom+20}" text-anchor="middle" font-size="12">{alpha:.1f}</text>')

    series = (
        ("chain_success", "#4c78a8", "Chain success"),
        ("chain_failure", "#72b7b2", "Chain failure"),
        ("linear_success", "#f58518", "Linear success"),
        ("linear_failure", "#e45756", "Linear failure"),
        ("chain_theory_success", "#28527a", "Chain success theory"),
        ("chain_theory_failure", "#2d7f78", "Chain failure theory"),
        ("linear_theory_success", "#b85a0a", "Linear success theory"),
        ("linear_theory_failure", "#a83232", "Linear failure theory"),
    )
    for field, color, label in series:
        theory = "_theory_" in field
        points = []
        for row in rows:
            points.append(f"{x(row['alpha']):.1f},{y(row[field]):.1f}")
        dash = ' stroke-dasharray="6,4"' if theory else ""
        parts.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="2"{dash}/>')
        if not theory:
            for row in rows:
                parts.append(
                    f'<circle cx="{x(row["alpha"]):.1f}" cy="{y(row[field]):.1f}" '
                    f'r="3.5" fill="{color}"/>'
                )

    legend_y = 460
    for index, (_, color, label) in enumerate(series):
        row = index // 4
        column = index % 4
        x_pos = 55 + column * 185
        item_y = legend_y + row * 18
        dash = ' stroke-dasharray="6,4"' if "_theory_" in series[index][0] else ""
        parts.append(f'<line x1="{x_pos}" y1="{item_y}" x2="{x_pos+24}" y2="{item_y}" stroke="{color}" stroke-width="4"{dash}/>')
        parts.append(f'<text x="{x_pos+30}" y="{item_y+4}" font-size="10">{label}</text>')
    parts.append(f'<text x="400" y="490" text-anchor="middle" font-size="12">Load factor alpha</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def main():
    rng = random.Random(SEED)
    rows = []
    for alpha in ALPHAS:
        count = int(TABLE_SIZE * alpha)
        keys = [f"key-{index}-{rng.randrange(1_000_000)}" for index in range(count)]
        missing = [f"missing-{index}-{rng.randrange(1_000_000)}" for index in range(count)]

        chain = HashTable(TABLE_SIZE, max_load=None)
        linear = LinearHashTable(TABLE_SIZE, max_load=None)
        for index, key in enumerate(keys):
            chain.put(key, index)
            linear.put(key, index)

        row = {
            "alpha": alpha,
            "item_count": count,
            "chain_success": chain_success(chain, keys),
            "chain_failure": chain_failure(chain, missing),
            "linear_success": linear_success(linear, keys),
            "linear_failure": linear_failure(linear, missing),
            "chain_theory_success": 1 + alpha / 2,
            "chain_theory_failure": alpha,
            "linear_theory_success": (1 + 1 / (1 - alpha)) / 2 if alpha < 1 else None,
            "linear_theory_failure": (1 + 1 / ((1 - alpha) ** 2)) / 2 if alpha < 1 else None,
        }
        rows.append(row)

    experiments_dir = Path(__file__).resolve().parent
    write_csv(rows, experiments_dir / "results.csv")
    write_svg(rows, experiments_dir / "probe_experiment.svg")

    print("| Alpha | Chain success | Chain failure | Linear success | Linear failure |")
    print("|---:|---:|---:|---:|---:|")
    for row in rows:
        print(
            f"| {row['alpha']:.2f} | {row['chain_success']:.3f} | {row['chain_failure']:.3f} "
            f"| {row['linear_success']:.3f} | {row['linear_failure']:.3f} |"
        )


if __name__ == "__main__":
    main()
