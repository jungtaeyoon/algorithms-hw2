"""Write a two-page Korean PDF report comparing chaining and linear probing."""

import csv
from pathlib import Path

from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parent.parent
EXPERIMENTS = ROOT / "experiments"
FONT_REGULAR = "NanumGothic"
FONT_BOLD = "NanumGothic-Bold"
FONT_REGULAR_FILE = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
FONT_BOLD_FILE = "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf"


def read_rows():
    with (EXPERIMENTS / "results.csv").open("r", encoding="utf-8", newline="") as source:
        return list(csv.DictReader(source))


def text(pdf, x, y, text, size=10, bold=False, color=colors.HexColor("#20242a")):
    pdf.setFillColor(color)
    pdf.setFont(FONT_BOLD if bold else FONT_REGULAR, size)
    pdf.drawString(x, y, text)
    return y


def paragraph(pdf, x, y, text, size=9.5, leading=13, bold=False):
    words = text
    max_width = 522
    lines = []
    current = ""
    for char in words:
        candidate = current + char
        if pdf.stringWidth(candidate, FONT_REGULAR, size) > max_width:
            lines.append(current)
            current = char
        else:
            current = candidate
    if current:
        lines.append(current)

    pdf.setFillColor(colors.HexColor("#20242a"))
    pdf.setFont(FONT_BOLD if bold else FONT_REGULAR, size)
    for line in lines:
        pdf.drawString(x, y, line)
        y -= leading
    return y


def heading(pdf, y, title):
    pdf.setFillColor(colors.HexColor("#17324d"))
    pdf.setFont(FONT_BOLD, 15)
    pdf.drawString(45, y, title)
    pdf.setStrokeColor(colors.HexColor("#2f80ed"))
    pdf.setLineWidth(1.5)
    pdf.line(45, y - 7, 567, y - 7)
    return y - 24


def draw_chart(pdf, rows, x=45, y=210, width=522, height=280):
    left, bottom, right, top = x + 35, y + 25, x + width - 10, y + height - 24
    pdf.setFillColor(colors.white)
    pdf.setStrokeColor(colors.HexColor("#d5dce3"))
    pdf.rect(x, y, width, height, fill=1, stroke=1)

    pdf.setFont(FONT_REGULAR, 8)
    pdf.setFillColor(colors.HexColor("#52606d"))
    pdf.drawCentredString((left + right) / 2, y + 4, "적재율 alpha")
    for tick in range(0, 56, 10):
        ty = bottom + tick / 55 * (top - bottom)
        pdf.setStrokeColor(colors.HexColor("#e7ecf1"))
        pdf.line(left, ty, right, ty)
        pdf.setFillColor(colors.HexColor("#52606d"))
        pdf.drawRightString(left - 6, ty - 3, str(tick))

    alphas = [float(row["alpha"]) for row in rows]
    for alpha in alphas:
        tx = left + (alpha - 0.1) / 0.8 * (right - left)
        pdf.setStrokeColor(colors.HexColor("#edf1f4"))
        pdf.line(tx, bottom, tx, top)
        pdf.setFillColor(colors.HexColor("#52606d"))
        pdf.drawCentredString(tx, bottom - 13, f"{alpha:.1f}")

    def px(alpha):
        return left + (alpha - 0.1) / 0.8 * (right - left)

    def py(value):
        return bottom + value / 55 * (top - bottom)

    series = (
        ("chain_success", "#3769b0", "체이닝 실험 성공"),
        ("chain_theory_success", "#3769b0", "체이닝 이론 성공"),
        ("chain_failure", "#40a9a0", "체이닝 실험 실패"),
        ("chain_theory_failure", "#40a9a0", "체이닝 이론 실패"),
        ("linear_success", "#ef8a1f", "선형 실험 성공"),
        ("linear_theory_success", "#ef8a1f", "선형 이론 성공"),
        ("linear_failure", "#d84a4a", "선형 실험 실패"),
        ("linear_theory_failure", "#d84a4a", "선형 이론 실패"),
    )

    for field, color, _ in series:
        theory = "_theory_" in field
        pdf.setStrokeColor(colors.HexColor(color))
        pdf.setDash(4, 3) if theory else pdf.setDash()
        pdf.setLineWidth(1.6)
        for index in range(len(rows) - 1):
            a1 = float(rows[index]["alpha"])
            a2 = float(rows[index + 1]["alpha"])
            v1 = float(rows[index][field])
            v2 = float(rows[index + 1][field])
            pdf.line(px(a1), py(v1), px(a2), py(v2))
        if not theory:
            pdf.setFillColor(colors.HexColor(color))
            for row in rows:
                pdf.circle(px(float(row["alpha"])), py(float(row[field])), 2.2, fill=1, stroke=0)
        pdf.setDash()

    legend_y = y + height - 12
    labels = (
        ("실선", "#20242a", "실험값"),
        ("점선", "#20242a", "이론값"),
        ("청록", "#40a9a0", "체이닝"),
        ("주황", "#ef8a1f", "선형 성공"),
        ("빨강", "#d84a4a", "선형 실패"),
    )
    lx = x + 36
    for kind, color, label in labels:
        pdf.setFillColor(colors.HexColor(color))
        pdf.setStrokeColor(colors.HexColor(color))
        if kind == "실선":
            pdf.setLineWidth(2)
            pdf.line(lx, legend_y, lx + 18, legend_y)
        elif kind == "점선":
            pdf.setDash(3, 2)
            pdf.line(lx, legend_y, lx + 18, legend_y)
            pdf.setDash()
        else:
            pdf.circle(lx + 9, legend_y, 3.5, fill=1, stroke=0)
        pdf.drawString(lx + 24, legend_y - 3, label)
        lx += 100


def main():
    rows = read_rows()
    pdfmetrics.registerFont(TTFont(FONT_REGULAR, FONT_REGULAR_FILE))
    pdfmetrics.registerFont(TTFont(FONT_BOLD, FONT_BOLD_FILE))

    pdf = canvas.Canvas(str(ROOT / "report.pdf"), pagesize=(612, 792))
    pdf.setTitle("Separate Chaining vs Linear Probing")

    y = 760
    text(pdf, 45, y, "개별 체이닝과 선형 탐지 비교 보고서", 20, bold=True)
    y -= 29
    text(pdf, 45, y, "URL 단축기 해시 테이블 실험 · 적재율 0.10~0.90", 10)

    y = heading(pdf, y - 35, "1. 두 방식을 어떻게 구현했는가")
    y = paragraph(pdf, 45, y,
        "개별 체이닝은 크기 11 배열의 각 칸을 연결 노드의 머리로 사용한다. "
        "문자열 키를 호너 방식으로 계산해 bucket index를 구하고, 새 키는 칸 앞에 추가하며 기존 키는 값을 갱신한다.",
        bold=False)
    y -= 4
    y = paragraph(pdf, 45, y,
        "선형 탐지는 키 배열과 값 배열을 사용한다. 충돌이 발생하면 다음 칸을 순환하며 찾고, 삭제는 tombstone을 남겨 탐색을 이어가게 한다.",
        bold=False)

    y = heading(pdf, y - 16, "2. 실험 조건")
    y = paragraph(pdf, 45, y,
        "테이블 크기 503, 적재율 0.10·0.20·…·0.90, 난수 seed 2026을 사용했다. "
        "같은 생성 키를 두 테이블에 넣었고, 동일 개수의 없는 키를 실패 탐색 표본으로 사용했다.",
        leading=12)

    y = heading(pdf, y - 10, "3. 실험값과 이론값")
    draw_chart(pdf, rows, x=45, y=230, width=522, height=280)

    y = 205
    text(pdf, 45, y, "핵심 수치 (α=0.90)", 9.5, bold=True)
    high = rows[-1]
    y -= 16
    text(pdf, 45, y,
         f"체이닝 성공 {float(high['chain_success']):.3f} / 실패 {float(high['chain_failure']):.3f}  |  "
         f"선형 성공 {float(high['linear_success']):.3f} / 실패 {float(high['linear_failure']):.3f}",
         8.5)
    y -= 14
    text(pdf, 45, y,
         "실선은 유한 표본 실험값, 점선은 수학적 이론값이다.",
         8)
    pdf.showPage()

    y = 760
    text(pdf, 45, y, "결과 해석과 검증 과정", 20, bold=True)

    y = heading(pdf, y - 35, "4. 적재율 1 근처에서 선형 탐지가 나빠지는 이유")
    y = paragraph(pdf, 45, y,
        "선형 탐지의 충돌은 주변 칸을 점차 하나의 긴 기본 클러스터로 만든다.",
        leading=13)
    y -= 2
    y = paragraph(pdf, 45, y,
        "새 키가 빈 칸을 찾으려면 이미 찬 구간을 통과해야 하므로 탐색 비용이 증폭된다.",
        leading=13)
    y -= 2
    y = paragraph(pdf, 45, y,
        "실패 탐색 이론식은 1/2 · (1 + 1/(1-α)²)이고 성공 탐색 이론식은 "
        "1/2 · (1 + 1/(1-α))이다. α→1이면 분모 (1-α)와 그 제곱이 0에 가까워져 비용이 급격히 발산한다.",
        leading=13)
    y -= 2
    y = paragraph(pdf, 45, y,
        "반면 개별 체이닝의 성공·실패 비용은 각각 1+α/2와 α에 비례한다. "
        "전체 배열을 503칸으로 유지해도 체이닝은 짧은 개별 리스트만 확인하면 되므로 선형 탐지처럼 한 거대한 클러스터에 갇히지 않는다.",
        leading=13)

    y = heading(pdf, y - 12, "5. 실험 결괏값 해석")
    y = paragraph(pdf, 45, y,
        f"α=0.90에서 선형 성공 탐색은 실험값 {float(high['linear_success']):.3f}회(이론 5.500회), "
        f"선형 실패 탐색은 실험값 {float(high['linear_failure']):.3f}회(이론 50.500회)였다.",
        leading=13)
    y -= 3
    y = paragraph(pdf, 45, y,
        f"같은 적재율의 체이닝은 성공 {float(high['chain_success']):.3f}회, 실패 {float(high['chain_failure']):.3f}회로 "
        "선형 탐지와 크게 갈라진다. 유한 표본의 클러스터 배치 때문에 실험값과 이론값은 약간 차이나지만 방향은 일치한다.",
        leading=13)

    y = heading(pdf, y - 12, "6. 에이전트가 틀린 곳과 잡은 방법")
    y = paragraph(pdf, 45, y,
        "첫째, 초기 실험 그래프의 세로축을 최대 6으로 고정해 α=0.90의 선형 실패값 53.338이 그래프 밖으로 벗어났다.",
        leading=13)
    y -= 2
    y = paragraph(pdf, 45, y,
        "→ 생성 SVG와 CSV를 함께 확인하고 세로축을 실패값까지 표현하도록 최대 55로 확장했다.",
        leading=13)
    y -= 2
    y = paragraph(pdf, 45, y,
        "둘째, 초안 PDF가 실험값만 영어로 넣고 이론값·그래프·구체적인 해석이 빠졌다.",
        leading=13)
    y -= 2
    y = paragraph(pdf, 45, y,
        "→ 실제 results.csv의 이론값 열을 읽어 실험선과 이론선을 같은 그래프에 그렸고, 두 방식의 차이와 실패 원인을 두 페이지로 재구성했다.",
        leading=13)

    y = heading(pdf, y - 12, "참고 파일")
    y = paragraph(pdf, 45, y,
        "실험 코드: experiments/probe_experiment.py · 실험값: experiments/results.csv · 그래프: experiments/probe_experiment.svg",
        leading=13)

    pdf.save()


if __name__ == "__main__":
    main()
