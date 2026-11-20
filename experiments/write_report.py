"""Write a two-page PDF report from probe results using only the Python standard library."""

import csv
from pathlib import Path


def pdf_text(lines):
    escaped = []
    for line in lines:
        text = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        escaped.append(f"({text}) Tj")
    commands = "/F1 11 Tf\n72 720 Td\n14 TL\n" + "\n".join(
        item if index == 0 else "T*\n" + item
        for index, item in enumerate(escaped)
    ) + "\n"
    return commands.encode("ascii", errors="replace")


def build_pdf(page_lines):
    objects = []
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    objects.append(b"<< /Type /Pages /Kids [3 0 R 5 0 R] /Count 2 >>")

    for page_number, lines in enumerate(page_lines):
        page_object = 3 + page_number * 2
        content_object = 4 + page_number * 2
        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 7 0 R >> >> "
            f"/Contents {content_object} 0 R >>".encode("ascii")
        )
        stream = pdf_text(lines)
        objects.append(
            f"<< /Length {len(stream)} >>\nstream\n".encode("ascii")
            + stream
            + b"endstream"
        )

    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")

    xref = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n\n".encode("ascii"))
    pdf.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref}\n%%EOF\n".encode("ascii")
    )
    return pdf


def main():
    experiments_dir = Path(__file__).resolve().parent
    with (experiments_dir / "results.csv").open("r", encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source))

    first_page = [
        "Separate Chaining vs Linear Probing",
        "",
        "1. Experimental setup",
        "Size-503 tables, load factors 0.10 through 0.90.",
        "The same generated keys were inserted into both tables.",
        "",
        "Alpha  Chain success  Chain failure  Linear success  Linear failure",
    ]
    for row in rows:
        first_page.append(
            f"{float(row['alpha']):.2f}    "
            f"{float(row['chain_success']):.3f}          "
            f"{float(row['chain_failure']):.3f}          "
            f"{float(row['linear_success']):.3f}           "
            f"{float(row['linear_failure']):.3f}"
        )

    high = rows[-1]
    second_page = [
        "2. Result summary",
        f"At alpha 0.90, chaining success probes = {float(high['chain_success']):.3f}.",
        f"At alpha 0.90, linear success probes = {float(high['linear_success']):.3f}.",
        f"At alpha 0.90, chaining failure probes = {float(high['chain_failure']):.3f}.",
        f"At alpha 0.90, linear failure probes = {float(high['linear_failure']):.3f}.",
        "",
        "Separate chaining keeps short independent lists.",
        "Linear probing grows primary-cluster costs as alpha rises.",
        "The 0.90 finite-sample result shows the linear-probing failure cost sharply.",
        "",
        "Source: experiments/results.csv",
        "Graph: experiments/probe_experiment.svg",
    ]

    (Path(__file__).resolve().parent.parent / "report.pdf").write_bytes(
        build_pdf([first_page, second_page])
    )


if __name__ == "__main__":
    main()
