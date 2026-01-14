import csv
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class SpectralRecord:
    plot_id: str
    row: int
    col: int
    blue_480: float
    green_560: float
    red_665: float
    red_edge_705: float
    red_edge_740: float
    nir_842: float
    nir2_865: float
    swir_1610: float
    swir_2190: float


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def generate_spectral_grid(
    rows: int = 140, cols: int = 140, seed: int = 1337
) -> List[SpectralRecord]:
    """Create a reproducible grid of multispectral reflectance approximating field data."""

    rng = random.Random(seed)

    # Two stress pockets plus a mild northwest-southeast fertility gradient
    stress_centers = [
        (rows * 0.65, cols * 0.68, (rows * 0.20) ** 2),
        (rows * 0.30, cols * 0.25, (rows * 0.18) ** 2),
    ]

    # Column banding noise (e.g., sensor striping) and row-based illumination gradient
    col_bias = [rng.gauss(1.0, 0.01) for _ in range(cols)]
    row_gradient = [1.0 + 0.04 * math.sin(r / 11.0) for r in range(rows)]

    records: List[SpectralRecord] = []
    for r in range(rows):
        for c in range(cols):
            stress = 0.0
            for cr, cc, sigma2 in stress_centers:
                dist2 = (r - cr) ** 2 + (c - cc) ** 2
                stress += math.exp(-dist2 / (2 * sigma2))
            stress = _clamp(stress, 0.0, 1.6)

            fertility = 0.15 * (1 - r / rows) + 0.05 * (c / cols)
            illumination = rng.uniform(0.93, 1.07) * row_gradient[r] * col_bias[c]

            target_ndvi = 0.70 + fertility - 0.40 * stress + rng.gauss(0.0, 0.02)
            target_ndvi = _clamp(target_ndvi, 0.05, 0.92)

            total_reflectance = illumination * rng.uniform(0.42, 0.80)
            nir = (target_ndvi + 1.0) * total_reflectance / 2.0
            red = total_reflectance - nir

            nir += rng.gauss(0.0, 0.006)
            red += rng.gauss(0.0, 0.006)

            nir = _clamp(nir, 0.01, 0.95)
            red = _clamp(red, 0.01, 0.95)

            blue = _clamp(0.04 + 0.07 * (1.1 - target_ndvi) + rng.gauss(0.0, 0.006), 0.02, 0.22)
            green = _clamp(0.20 + 0.12 * (0.9 - stress) + rng.gauss(0.0, 0.01), 0.12, 0.42)
            red_edge = _clamp(0.18 + 0.40 * target_ndvi + rng.gauss(0.0, 0.008), 0.10, 0.70)
            red_edge2 = _clamp(red_edge + 0.05 * (target_ndvi - 0.5) + rng.gauss(0.0, 0.006), 0.10, 0.75)
            nir2 = _clamp(nir + rng.gauss(0.0, 0.004) + 0.02 * (1.0 - stress), 0.05, 0.95)

            swir1 = _clamp(0.22 + 0.28 * stress + rng.gauss(0.0, 0.01), 0.10, 0.70)
            swir2 = _clamp(swir1 + 0.05 * stress + rng.gauss(0.0, 0.01), 0.10, 0.75)

            # Occasional thin-cloud effect: brighten visible, mute NIR
            if rng.random() < 0.02:
                factor_vis = rng.uniform(1.05, 1.12)
                factor_nir = rng.uniform(0.90, 0.96)
                blue *= factor_vis
                green *= factor_vis
                red *= factor_vis
                red_edge *= factor_vis
                red_edge2 *= factor_vis
                nir *= factor_nir
                nir2 *= factor_nir
                swir1 *= factor_vis * 0.9
                swir2 *= factor_vis * 0.9

            plot_id = f"R{r + 1:03d}C{c + 1:03d}"
            records.append(
                SpectralRecord(
                    plot_id,
                    r,
                    c,
                    blue,
                    green,
                    red,
                    red_edge,
                    red_edge2,
                    nir,
                    nir2,
                    swir1,
                    swir2,
                )
            )

    return records


def save_records_csv(records: List[SpectralRecord], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "plot_id",
                "row",
                "col",
                "blue_480",
                "green_560",
                "red_665",
                "red_edge_705",
                "red_edge_740",
                "nir_842",
                "nir2_865",
                "swir_1610",
                "swir_2190",
            ]
        )
        for rec in records:
            writer.writerow(
                [
                    rec.plot_id,
                    rec.row,
                    rec.col,
                    f"{rec.blue_480:.4f}",
                    f"{rec.green_560:.4f}",
                    f"{rec.red_665:.4f}",
                    f"{rec.red_edge_705:.4f}",
                    f"{rec.red_edge_740:.4f}",
                    f"{rec.nir_842:.4f}",
                    f"{rec.nir2_865:.4f}",
                    f"{rec.swir_1610:.4f}",
                    f"{rec.swir_2190:.4f}",
                ]
            )


def load_records_csv(path: Path) -> List[SpectralRecord]:
    records: List[SpectralRecord] = []
    with path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(
                SpectralRecord(
                    plot_id=row["plot_id"],
                    row=int(row["row"]),
                    col=int(row["col"]),
                    blue_480=float(row["blue_480"]),
                    green_560=float(row["green_560"]),
                    red_665=float(row["red_665"]),
                    red_edge_705=float(row["red_edge_705"]),
                    red_edge_740=float(row["red_edge_740"]),
                    nir_842=float(row["nir_842"]),
                    nir2_865=float(row["nir2_865"]),
                    swir_1610=float(row["swir_1610"]),
                    swir_2190=float(row["swir_2190"]),
                )
            )
    return records
