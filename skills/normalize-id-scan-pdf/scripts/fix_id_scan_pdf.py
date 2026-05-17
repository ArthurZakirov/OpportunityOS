#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
import sys
import unicodedata
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:
    from pypdf import PdfReader, PdfWriter
    from pypdf._page import PageObject
    from pypdf.generic import ContentStream
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Missing dependency: pypdf. Create a local virtualenv and install `pypdf`, "
        "then rerun this script."
    ) from exc


STOPWORDS = {
    "scan",
    "scanned",
    "scanne",
    "scans",
    "copy",
    "copie",
    "neu",
    "new",
    "original",
    "bronze",
    "silver",
    "gold",
    "rotated",
    "rotation",
    "portrait",
    "landscape",
    "fit",
    "fixed",
    "normalized",
    "normalised",
    "enlarged",
    "seite",
    "page",
    "front",
    "back",
}

DOC_TYPE_ALIASES = {
    "ausweis": "personal_id",
    "personalausweis": "personal_id",
    "id": "personal_id",
    "identity": "personal_id",
    "identitycard": "personal_id",
    "identity_card": "personal_id",
    "personalid": "personal_id",
    "personal_id": "personal_id",
    "passport": "passport",
    "reisepass": "passport",
    "fuehrerschein": "drivers_license",
    "fuhrerschein": "drivers_license",
    "driverlicense": "drivers_license",
    "driverslicense": "drivers_license",
    "driver_licence": "drivers_license",
    "drivers_licence": "drivers_license",
}


@dataclass(frozen=True)
class Box:
    xmin: float
    ymin: float
    xmax: float
    ymax: float

    @property
    def width(self) -> float:
        return self.xmax - self.xmin

    @property
    def height(self) -> float:
        return self.ymax - self.ymin

    @property
    def area(self) -> float:
        return max(self.width, 0.0) * max(self.height, 0.0)


@dataclass(frozen=True)
class TransformCandidate:
    angle: int
    scale: float
    tx: float
    ty: float
    output_box: Box
    coverage: float


def multiply(m1: tuple[float, float, float, float, float, float], m2: tuple[float, float, float, float, float, float]) -> tuple[float, float, float, float, float, float]:
    a1, b1, c1, d1, e1, f1 = m1
    a2, b2, c2, d2, e2, f2 = m2
    return (
        a1 * a2 + c1 * b2,
        b1 * a2 + d1 * b2,
        a1 * c2 + c1 * d2,
        b1 * c2 + d1 * d2,
        a1 * e2 + c1 * f2 + e1,
        b1 * e2 + d1 * f2 + f1,
    )


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", ascii_text.lower()).strip("_")
    slug = re.sub(r"_+", "_", slug)
    return slug or "document"


def stem_tokens(stem: str) -> list[str]:
    return [token for token in slugify(stem).split("_") if token]


def infer_doc_type(tokens: Iterable[str], explicit_doc_type: str | None) -> str:
    if explicit_doc_type:
        return slugify(explicit_doc_type)
    for token in tokens:
        if token in DOC_TYPE_ALIASES:
            return DOC_TYPE_ALIASES[token]
    return "personal_id"


def infer_subject_slug(tokens: Iterable[str], doc_type: str) -> str | None:
    filtered: list[str] = []
    for token in tokens:
        if token in STOPWORDS:
            continue
        if token in DOC_TYPE_ALIASES:
            continue
        if token == doc_type:
            continue
        filtered.append(token)
    return "_".join(filtered) or None


def silver_name(source: Path, page_mode: str, angle: int) -> str:
    return f"{slugify(source.stem)}__silver__{page_mode}_rotate_{angle}_fit.pdf"


def gold_name(source: Path, explicit_gold: str | None, explicit_doc_type: str | None) -> str:
    if explicit_gold:
        base = slugify(Path(explicit_gold).stem)
        return f"{base}.pdf"
    tokens = stem_tokens(source.stem)
    doc_type = infer_doc_type(tokens, explicit_doc_type)
    subject = infer_subject_slug(tokens, doc_type)
    if subject:
        return f"{subject}__{doc_type}.pdf"
    return f"{doc_type}.pdf"


def measure_visible_content(page) -> Box:
    content = page.get_contents()
    if content is None:
        return Box(0.0, 0.0, float(page.mediabox.width), float(page.mediabox.height))

    xs: list[float] = []
    ys: list[float] = []
    stream = ContentStream(content, page.pdf)
    ctm = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
    stack: list[tuple[float, float, float, float, float, float]] = []

    for operands, op in stream.operations:
        if op == b"q":
            stack.append(ctm)
        elif op == b"Q":
            ctm = stack.pop()
        elif op == b"cm":
            ctm = multiply(ctm, tuple(float(value) for value in operands))
        elif op == b"Do":
            a, b, c, d, e, f = ctm
            for x, y in ((0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (1.0, 1.0)):
                xs.append(a * x + c * y + e)
                ys.append(b * x + d * y + f)

    def visitor_text(text, text_ctm, tm, font_dict, font_size):
        if not text.strip():
            return
        a, b, c, d, e, f = text_ctm
        tx, ty = tm[4], tm[5]
        xs.append(a * tx + c * ty + e)
        ys.append(b * tx + d * ty + f)

    try:
        page.extract_text(visitor_text=visitor_text)
    except Exception:
        pass

    if not xs or not ys:
        return Box(0.0, 0.0, float(page.mediabox.width), float(page.mediabox.height))

    return Box(min(xs), min(ys), max(xs), max(ys))


def rotate_point(x: float, y: float, angle: int) -> tuple[float, float]:
    turns = angle % 360
    if turns == 0:
        return x, y
    if turns == 90:
        return -y, x
    if turns == 180:
        return -x, -y
    if turns == 270:
        return y, -x
    raise ValueError(f"Unsupported rotation angle: {angle}")


def transformed_box(box: Box, angle: int, scale: float, tx: float, ty: float) -> Box:
    points = [
        rotate_point(box.xmin, box.ymin, angle),
        rotate_point(box.xmin, box.ymax, angle),
        rotate_point(box.xmax, box.ymin, angle),
        rotate_point(box.xmax, box.ymax, angle),
    ]
    xs = [scale * x + tx for x, _ in points]
    ys = [scale * y + ty for _, y in points]
    return Box(min(xs), min(ys), max(xs), max(ys))


def fit_candidate(box: Box, page_w: float, page_h: float, angle: int, margin: float) -> TransformCandidate:
    rotated = [
        rotate_point(box.xmin, box.ymin, angle),
        rotate_point(box.xmin, box.ymax, angle),
        rotate_point(box.xmax, box.ymin, angle),
        rotate_point(box.xmax, box.ymax, angle),
    ]
    rot_xmin = min(x for x, _ in rotated)
    rot_xmax = max(x for x, _ in rotated)
    rot_ymin = min(y for _, y in rotated)
    rot_ymax = max(y for _, y in rotated)
    rot_w = rot_xmax - rot_xmin
    rot_h = rot_ymax - rot_ymin
    usable_w = max(page_w - 2.0 * margin, 1.0)
    usable_h = max(page_h - 2.0 * margin, 1.0)
    scale = min(usable_w / rot_w, usable_h / rot_h)
    tx = margin - scale * rot_xmin + (usable_w - scale * rot_w) / 2.0
    ty = margin - scale * rot_ymin + (usable_h - scale * rot_h) / 2.0
    output_box = transformed_box(box, angle, scale, tx, ty)
    coverage = output_box.area / max(page_w * page_h, 1.0)
    return TransformCandidate(angle=angle, scale=scale, tx=tx, ty=ty, output_box=output_box, coverage=coverage)


def target_page_size(orig_w: float, orig_h: float, page_mode: str) -> tuple[float, float]:
    if page_mode == "portrait":
        return min(orig_w, orig_h), max(orig_w, orig_h)
    return max(orig_w, orig_h), min(orig_w, orig_h)


def choose_candidate(box: Box, page_w: float, page_h: float, margin: float, page_mode: str) -> TransformCandidate:
    allowed = (0, 90, 180, 270)
    candidates = [fit_candidate(box, page_w, page_h, angle, margin) for angle in allowed]
    if page_mode == "portrait":
        return max(candidates, key=lambda item: (item.coverage, item.scale, item.angle in (90, 270)))
    return max(candidates, key=lambda item: (item.coverage, item.scale))


def matrix_for_candidate(candidate: TransformCandidate) -> tuple[float, float, float, float, float, float]:
    angle = candidate.angle % 360
    scale = candidate.scale
    if angle == 0:
        return (scale, 0.0, 0.0, scale, candidate.tx, candidate.ty)
    if angle == 90:
        return (0.0, scale, -scale, 0.0, candidate.tx, candidate.ty)
    if angle == 180:
        return (-scale, 0.0, 0.0, -scale, candidate.tx, candidate.ty)
    if angle == 270:
        return (0.0, -scale, scale, 0.0, candidate.tx, candidate.ty)
    raise ValueError(f"Unsupported rotation angle: {candidate.angle}")


def validate_output(box: Box, page_w: float, page_h: float, margin: float) -> tuple[bool, str]:
    eps = 0.5
    if box.xmin < margin - eps:
        return False, "content crosses the left margin"
    if box.ymin < margin - eps:
        return False, "content crosses the bottom margin"
    if box.xmax > page_w - margin + eps:
        return False, "content crosses the right margin"
    if box.ymax > page_h - margin + eps:
        return False, "content crosses the top margin"
    return True, "content fits within the requested margins"


def build_output(page, page_w: float, page_h: float, candidate: TransformCandidate):
    work_page = deepcopy(page)
    work_page.add_transformation(matrix_for_candidate(candidate))
    output_page = PageObject.create_blank_page(width=page_w, height=page_h)
    output_page.merge_page(work_page)
    return output_page


def preview_first_page(source: Path, margin: float, page_mode: str) -> TransformCandidate:
    reader = PdfReader(str(source))
    page = reader.pages[0]
    page_w, page_h = target_page_size(float(page.mediabox.width), float(page.mediabox.height), page_mode)
    return choose_candidate(
        measure_visible_content(page),
        page_w,
        page_h,
        margin,
        page_mode,
    )


def write_pdf(source: Path, destination: Path, margin: float, page_mode: str) -> tuple[float, int, list[tuple[Box, Box]]]:
    reader = PdfReader(str(source))
    writer = PdfWriter()
    reports: list[tuple[Box, Box]] = []
    first_scale = 0.0
    first_angle = 0

    for index, page in enumerate(reader.pages):
        page_w, page_h = target_page_size(
            float(page.mediabox.width),
            float(page.mediabox.height),
            page_mode,
        )
        input_box = measure_visible_content(page)
        candidate = choose_candidate(input_box, page_w, page_h, margin, page_mode)
        if index == 0:
            first_scale = candidate.scale
            first_angle = candidate.angle

        validated_candidate = candidate
        working_margin = margin
        while True:
            output_page = build_output(page, page_w, page_h, validated_candidate)
            output_box = measure_visible_content(output_page)
            ok, _reason = validate_output(output_box, page_w, page_h, margin)
            if ok:
                writer.add_page(output_page)
                reports.append((input_box, output_box))
                if index == 0:
                    first_scale = validated_candidate.scale
                    first_angle = validated_candidate.angle
                break
            working_margin += 2.0
            validated_candidate = fit_candidate(
                input_box,
                page_w,
                page_h,
                validated_candidate.angle,
                working_margin,
            )
            if validated_candidate.scale <= 0:
                raise RuntimeError("Could not find a non-clipping scale")

    with destination.open("wb") as handle:
        writer.write(handle)

    return first_scale, first_angle, reports


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rotate and fit an ID scan PDF without clipping.")
    parser.add_argument("source_pdf", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--page-mode", choices=("portrait", "landscape"), default="portrait")
    parser.add_argument("--margin-pt", type=float, default=24.0)
    parser.add_argument("--doc-type")
    parser.add_argument("--gold-name")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.source_pdf.expanduser().resolve()
    if not source.exists():
        print(f"Source PDF not found: {source}", file=sys.stderr)
        return 2

    output_dir = args.output_dir.expanduser().resolve() if args.output_dir else source.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    preview = preview_first_page(source, args.margin_pt, args.page_mode)
    silver_path = output_dir / silver_name(source, args.page_mode, preview.angle)
    gold_path = output_dir / gold_name(source, args.gold_name, args.doc_type)

    scale, angle, reports = write_pdf(source, silver_path, args.margin_pt, args.page_mode)
    if gold_path != silver_path:
        shutil.copy2(silver_path, gold_path)
    elif gold_path != silver_path:
        shutil.copy2(silver_path, gold_path)

    print(f"bronze={source}")
    print(f"silver={silver_path}")
    print(f"gold={gold_path}")
    print(f"angle={angle}")
    print(f"scale={scale:.6f}")
    for index, (input_box, output_box) in enumerate(reports, start=1):
        print(f"page_{index}_input={input_box.xmin:.2f},{input_box.ymin:.2f},{input_box.xmax:.2f},{input_box.ymax:.2f}")
        print(f"page_{index}_output={output_box.xmin:.2f},{output_box.ymin:.2f},{output_box.xmax:.2f},{output_box.ymax:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
