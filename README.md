# NDVI Calculate

Tiny, contest-style NDVI calculator with an in-memory example that mimics raw measurements from a small field grid.

## Run with uv

```bash
uv run python main.py
```

Example output (truncated preview from a 140x140 grid):

```text
Plot  NDVI (showing 80/19600)
  R001C001  r=001 c=001   0.832
  R001C002  r=001 c=002   0.807
  R001C003  r=001 c=003   0.753
  R001C004  r=001 c=004   0.807
  R001C005  r=001 c=005   0.824
  R001C006  r=001 c=006   0.806
  R001C007  r=001 c=007   0.783
  R001C008  r=001 c=008   0.810
  R001C009  r=001 c=009   0.757
  R001C010  r=001 c=010   0.825
... 19520 more plots not shown

Field summary:
mean=0.637  min=0.289  max=0.963
Potentially stressed plots: R093C088
```

Generates `data/synthetic_field_multispec.csv` (blue_480/green_560/red_665/red_edge_705/red_edge_740/nir_842/nir2_865/swir_1610/swir_2190 per plot) and `ndvi_heatmap.png` to visualize the whole grid.

Data columns in the CSV:

- `plot_id`: grid code (row/col encoded)
- `row`, `col`: zero-based indices so visualizations map cleanly
- `blue_480`, `green_560`, `red_665`, `red_edge_705`, `red_edge_740`, `nir_842`, `nir2_865`, `swir_1610`, `swir_2190`: reflectance values (unitless ratios)

## What the code does

- Uses raw red and near-infrared reflectance pairs from a handheld or drone sensor.
- Computes NDVI via `(nir - red) / (nir + red)` and prints plot-level values.
- Flags plots whose NDVI falls below 0.30, a rough stress line for early warning.
- Reports quick field stats (mean, min, max) to guide scouting.

## Why it matters for precision agriculture

- Early stress detection: Low NDVI patches cue targeted field walks before yield loss.
- Variable-rate decisions: NDVI gradients support zone-specific fertilizer or irrigation.
- Harvest planning: Tracking NDVI trends refines maturity maps for logistics.
- QA on raw data: Running on the raw reflectance pairs lets you spot sensor dropouts or saturation before mapping.
