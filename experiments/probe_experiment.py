"""Measure chained hash-table probes at fixed load factors."""

import csv
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.hash_table import HashTable, horner_hash


TABLE_SIZE = 4093
ALPHAS = (0.25, 0.50, 0.75, 1.00, 1.50, 2.00, 3.00, 4.00)
SEED = 2026


def random_urls(count, rng, prefix="url"):
    urls = []
    for index in range(count):
        urls.append(
            f"https://{prefix}.example/{index}-{rng.randrange(1_000_000_000)}"
        )
    return urls


def success_probe_average(table, keys):
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


def failure_probe_average(table, keys):
    total = 0
    for key in keys:
        node = table.table[horner_hash(key, table.size)]
        probes = 0
        while node is not None:
            probes += 1
            node = node.next
        total += probes
    return total / len(keys)


def write_csv(rows, path):
    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "alpha",
                "item_count",
                "success_observed",
                "success_theory",
                "failure_observed",
                "failure_theory",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_svg(rows, path):
    width, height = 800, 500
    left, right, top, bottom = 75, 760, 55, 430
    chart_width = right - left
    chart_height = bottom - top
    max_alpha = 4.0
    max_y = 5.0

    def x(alpha):
        return left + alpha / max_alpha * chart_width

    def y(value):
        return bottom - value / max_y * chart_height

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="400" y="24" text-anchor="middle" font-size="18">'
        "Probe Cost by Load Factor</text>",
    ]

    for tick in range(6):
        y_value = tick
        y_pos = y(y_value)
        lines.append(
            f'<line x1="{left}" y1="{y_pos:.1f}" x2="{right}" y2="{y_pos:.1f}" '
            'stroke="#ddd"/>'
        )
        lines.append(
            f'<text x="{left-10}" y="{y_pos+4:.1f}" text-anchor="end" '
            f'font-size="12">{tick}</text>'
        )

    for alpha_tick in (0.25, 0.50, 1.00, 2.00, 3.00, 4.00):
        x_pos = x(alpha_tick)
        lines.append(
            f'<line x1="{x_pos:.1f}" y1="{top}" x2="{x_pos:.1f}" '
            f'y2="{bottom}" stroke="#eee"/>'
        )
        lines.append(
            f'<text x="{x_pos:.1f}" y="{bottom+20}" text-anchor="middle" '
            f'font-size="12">{alpha_tick:g}</text>'
        )

    series = (
        ("success_observed", "#4c78a8", "Measured success"),
        ("success_theory", "#72b7b2", "Theory 1 + alpha/2"),
        ("failure_observed", "#e45756", "Measured failure"),
        ("failure_theory", "#f58518", "Theory alpha"),
    )

    for field, color, label in series:
        points = []
        for row in rows:
            points.append(f"{x(row['alpha']):.1f},{y(row[field]):.1f}")
        lines.append(
            f'<polyline points="{" ".join(points)}" fill="none" '
            f'stroke="{color}" stroke-width="2"/>'
        )
        for row in rows:
            lines.append(
                f'<circle cx="{x(row["alpha"]):.1f}" cy="{y(row[field]):.1f}" '
                f'r="3.5" fill="{color}"/>'
            )

    legend_y = 460
    for index, (_, color, label) in enumerate(series):
        x_pos = 100 + index * 175
        lines.append(
            f'<line x1="{x_pos}" y1="{legend_y}" x2="{x_pos+24}" '
            f'y2="{legend_y}" stroke="{color}" stroke-width="4"/>'
        )
        lines.append(
            f'<text x="{x_pos+30}" y="{legend_y+4}" font-size="11">{label}</text>'
        )

    lines.append(
        f'<text x="{(left+right)/2:.1f}" y="490" text-anchor="middle" '
        'font-size="12">Load factor alpha</text>'
    )
    lines.append(
        f'<text x="18" y="{(top+bottom)/2:.1f}" text-anchor="middle" '
        'font-size="12" transform="rotate(-90 18 {(top+bottom)/2:.1f})">'
        "Compared nodes</text>"
    )
    lines.append("</svg>")
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    rng = random.Random(SEED)
    rows = []
    for alpha in ALPHAS:
        item_count = int(TABLE_SIZE * alpha)
        keys = random_urls(item_count, rng)
        missing = random_urls(item_count, rng, prefix="missing")

        table = HashTable(TABLE_SIZE, max_load=None)
        for index, key in enumerate(keys):
            table.put(key, index)

        success_observed = success_probe_average(table, keys)
        failure_observed = failure_probe_average(table, missing)
        rows.append(
            {
                "alpha": f"{alpha:.2f}",
                "item_count": item_count,
                "success_observed": f"{success_observed:.6f}",
                "success_theory": f"{1 + alpha / 2:.6f}",
                "failure_observed": f"{failure_observed:.6f}",
                "failure_theory": f"{alpha:.6f}",
            }
        )

    experiments_dir = Path(__file__).resolve().parent
    write_csv(rows, experiments_dir / "results.csv")
    write_svg(
        [
            {
                "alpha": float(row["alpha"]),
                "success_observed": float(row["success_observed"]),
                "success_theory": float(row["success_theory"]),
                "failure_observed": float(row["failure_observed"]),
                "failure_theory": float(row["failure_theory"]),
            }
            for row in rows
        ],
        experiments_dir / "probe_experiment.svg",
    )

    print("| Alpha | Items | Success measured | Success theory | Failure measured | Failure theory |")
    print("|---:|---:|---:|---:|---:|---:|")
    for row in rows:
        print(
            f"| {row['alpha']} | {row['item_count']} | {row['success_observed']} "
            f"| {row['success_theory']} | {row['failure_observed']} "
            f"| {row['failure_theory']} |"
        )


if __name__ == "__main__":
    main()
