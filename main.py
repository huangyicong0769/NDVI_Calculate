import math
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

import matplotlib.pyplot as plt

from data_gen import SpectralRecord, generate_spectral_grid, load_records_csv, save_records_csv


def ndvi(red: float, nir: float) -> float:
    """Compute NDVI; return NaN if the pair is invalid."""
    denom = nir + red
    if denom == 0:
        return float("nan")
    return (nir - red) / denom


NDVIResult = Tuple[int, int, str, float]


def run_example(
    records: Sequence[SpectralRecord], preview_count: int = 80
) -> List[NDVIResult]:
    """Process records, print preview, and return NDVI per plot."""
    results: List[NDVIResult] = []
    for rec in records:
        value = ndvi(rec.red_665, rec.nir_842)
        results.append((rec.row, rec.col, rec.plot_id, value))

    valid = [v for _, _, _, v in results if math.isfinite(v)]
    mean_ndvi = sum(valid) / len(valid) if valid else float("nan")
    lo = min(valid) if valid else float("nan")
    hi = max(valid) if valid else float("nan")

    shown = min(preview_count, len(results))
    print(f"Plot  NDVI (showing {shown}/{len(results)})")
    for idx, (r, c, plot_id, value) in enumerate(results):
        if idx >= preview_count:
            break
        print(f"{plot_id:>7}  r={r + 1:03d} c={c + 1:03d}  {value:6.3f}")
    if shown < len(results):
        print(f"... {len(results) - shown} more plots not shown")

    print("\nField summary:")
    print(f"mean={mean_ndvi:.3f}  min={lo:.3f}  max={hi:.3f}")

    stressed = [plot_id for _, _, plot_id, value in results if value < 0.30]
    if stressed:
        print("Potentially stressed plots: " + ", ".join(stressed))
    else:
        print("No plots under the 0.30 stress threshold.")

    return results


def visualize_ndvi(
    results: Sequence[NDVIResult], rows: int, cols: int, outfile: str = "ndvi_heatmap.png"
) -> None:
    """Render a heatmap for NDVI and write it to disk."""

    grid = [[float("nan") for _ in range(cols)] for _ in range(rows)]
    for r, c, _, value in results:
        if 0 <= r < rows and 0 <= c < cols:
            grid[r][c] = value

    plt.figure(figsize=(9, 7))
    img = plt.imshow(grid, cmap="YlGn", vmin=0.0, vmax=0.9, origin="lower")
    plt.colorbar(img, label="NDVI")
    plt.title("Synthetic Field NDVI (heatmap)")
    plt.xlabel("Column index (0-based)")
    plt.ylabel("Row index (0-based)")
    plt.tight_layout()
    plt.savefig(outfile, dpi=200)
    plt.close()


def main() -> None:
    data_path = Path("data/synthetic_field_multispec.csv")

    def regenerate() -> None:
        records_new = generate_spectral_grid(rows=140, cols=140, seed=2027)
        save_records_csv(records_new, data_path)
        print(f"Generated synthetic dataset at {data_path}")

    if not data_path.exists():
        regenerate()

    try:
        records = load_records_csv(data_path)
    except KeyError:
        regenerate()
        records = load_records_csv(data_path)
    rows = max(rec.row for rec in records) + 1
    cols = max(rec.col for rec in records) + 1

    results = run_example(records, preview_count=80)
    visualize_ndvi(results, rows, cols, outfile="ndvi_heatmap.png")


if __name__ == "__main__":
    main()
