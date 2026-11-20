"""Measure average probes for chained and linear-probing hash tables."""

from html import escape
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.hash_table import HashTable, LinearHashTable, horner_hash


def chain_success(table: HashTable, keys):
    total = 0
    for key in keys:
        index = horner_hash(key, table.size)
        node = table.table[index]
        probes = 1
        while node is not None:
            if node.key == key:
                break
            probes += 1
            node = node.next
        total += probes
    return total / len(keys)


def chain_failure(table: HashTable, keys):
    total = 0
    for key in keys:
        index = horner_hash(key, table.size)
        node = table.table[index]
        probes = 0
        while node is not None:
            probes += 1
            if node.key == key:
                break
            node = node.next
        total += probes
    return total / len(keys)


def linear_success(table: LinearHashTable, keys):
    total = 0
    for key in keys:
        index = horner_hash(key, table.size)
        probes = 1
        while table.keys[index] is not table._EMPTY:
            if table.keys[index] is not table._TOMB and table.keys[index] == key:
                break
            probes += 1
            index = (index + 1) % table.size
        total += probes
    return total / len(keys)


def linear_failure(table: LinearHashTable, keys):
    total = 0
    for key in keys:
        index = horner_hash(key, table.size)
        probes = 1
        while table.keys[index] is not table._EMPTY:
            probes += 1
            index = (index + 1) % table.size
            if probes > table.size:
                break
        total += probes
    return total / len(keys)


def write_svg(rows):
    width, height = 760, 420
    left, bottom = 70, 350
    chart_width, chart_height = 640, 280
    max_y = 8
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="380" y="24" text-anchor="middle" font-size="18">Probe Cost by Load Factor</text>',
    ]
    for tick in range(0, 9):
        y = bottom - tick * chart_height / max_y
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + chart_width}" y2="{y:.1f}" stroke="#ddd"/>')
        parts.append(f'<text x="{left-8}" y="{y+4:.1f}" text-anchor="end" font-size="12">{tick}</text>')
    for row in rows:
        alpha = row["alpha"]
        x = left + alpha * chart_width
        for key, color in (("chain_success", "#4c78a8"), ("chain_failure", "#72b7b2"),
                           ("linear_success", "#f58518"), ("linear_failure", "#e45756")):
            y = bottom - min(row[key], max_y) * chart_height / max_y
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{color}"/>')
    legend = (
        ("chain_success", "#4c78a8"), ("chain_failure", "#72b7b2"),
        ("linear_success", "#f58518"), ("linear_failure", "#e45756"),
    )
    for index, (key, color) in enumerate(legend):
        x = 90 + index * 160
        parts.append(f'<line x1="{x}" y1="385" x2="{x+24}" y2="385" stroke="{color}" stroke-width="4"/>')
        parts.append(f'<text x="{x+30}" y="390" font-size="11">{escape(key)}</text>')
    parts.append("</svg>")
    with open("experiments/probe_experiment.svg", "w", encoding="utf-8") as output:
        output.write("\n".join(parts))


def main():
    rows = []
    rng = random.Random(2026)
    for alpha in (0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90):
        size = 503
        count = int(size * alpha)
        keys = [f"key-{index}-{rng.randrange(1_000_000)}" for index in range(count)]
        missing = [f"missing-{index}-{rng.randrange(1_000_000)}" for index in range(count)]

        chain = HashTable(size)
        linear = LinearHashTable(size)
        for index, key in enumerate(keys):
            chain.put(key, index)
            linear.put(key, index)

        row = {
            "alpha": alpha,
            "chain_success": chain_success(chain, keys),
            "chain_failure": chain_failure(chain, missing),
            "linear_success": linear_success(linear, keys),
            "linear_failure": linear_failure(linear, missing),
        }
        rows.append(row)

    print("| Alpha | Chain Success | Chain Failure | Linear Success | Linear Failure |")
    print("|---:|---:|---:|---:|---:|")
    for row in rows:
        print(
            f"| {row['alpha']:.2f} | {row['chain_success']:.3f} | {row['chain_failure']:.3f} "
            f"| {row['linear_success']:.3f} | {row['linear_failure']:.3f} |"
        )
    write_svg(rows)


if __name__ == "__main__":
    main()
