# clms-aoi

A lightweight Python library and CLI for extracting and summarizing Copernicus Land Monitoring Service (CLMS) data for any area of interest.

Point it at a boundary file, pick a product and year, and get back a CSV table, a bar chart, or both. No custom API boilerplate required.

---

## Who is this for?

Land use analysts, GIS practitioners, students, NGOs, and small consultancies who want quick AOI-level summaries without setting up a full geospatial processing pipeline.

---

## Supported products

| Product | Description | Available years |
|---|---|---|
| Dynamic Land Cover | Annual global land cover classification (tree cover, cropland, grassland, built-up, water, etc.) | 2018–2024 |
| Tree Cover Density (TCD) | Pan-European canopy cover as a percentage (0–100) | 2018, 2021, 2024 |
| Forest Type (FTY) | Broadleaved vs. coniferous forest classification | 2018, 2021, 2024 |
| Grasslands | Pan-European presence/absence of grassland | 2018, 2021, 2024 |

---

## Installation
For users:
```bash
pip install clms-aoi
```
for devs
1. Clone the repository
2. Change directory into the cloned folder
```bash
cd clms-aoi
```
3. Create a virtual environment and activate it
```bash
python3 -m venv clms_aoi_env && source clms_aoi_env/bin/activate
```
4. Do an editable install which means edits to the source code keep working without reinstalling
```bash
pip install -e .
```
---

## Configuration

Create a config file at `config/config.yaml` with your Sentinel Hub credentials:

```yaml
sentinelhub:
  client_id: "your-client-id"
  client_secret: "your-client-secret"

aoi:
  path: "sample_data/sample_aoi.geojson"
  target_crs: "EPSG:4326"


defaults:
  output_dir: "./clms-aoi-output"
  dpi: 150
```

You can point to a different config file at runtime using the `--config` flag.

---

## CLI usage

```bash
# To check correct credentials 
clms-aoi check-auth --config config/config.yaml

# Single year, chart output
clms-aoi land-cover --aoi ./boundary.geojson --year 2020 --output ./out --format chart

# Multiple specific years, CSV output
clms-aoi tree-cover --aoi ./boundary.gpkg --year 2018,2021,2024 --output ./out --format csv

# Year range, chart output
clms-aoi forest-type --aoi ./boundary.geojson --year 2018-2024 --output ./out --format chart

# All available years, CSV and chart
clms-aoi grassland --aoi ./boundary.geojson --year all --output ./out --format both
```

### Options

| Option | Description |
|---|---|
| `--aoi` | Path to a GeoJSON or GeoPackage file. Multi-polygon inputs are dissolved before the request. |
| `--year` | Year(s) to analyse. Accepts a single year (`2020`), a comma-separated list (`2018,2021,2024`), a range (`2018-2024`), or `all`. Defaults to the most recent year available for the product. |
| `--output` | Directory where results are written. |
| `--format` | Output format: `csv`, `chart`, or `both`. |
| `--config` | Path to config file. Defaults to `~/.clms-aoi/config.yml`. |

If you request a year that is not available for a product, the CLI will tell you which years are valid and exit cleanly.

---

## Python API

You can call the library directly from notebooks or pipelines:

```python
from clms_aoi import LandCover, TreeCoverDensity

lc = LandCover(config_path="config.yml")

# Single year
result = lc.analyse(aoi="boundary.geojson", year=2020)

# Multiple years
result = lc.analyse(aoi="boundary.geojson", years=[2018, 2021, 2024])

# Range
result = lc.analyse(aoi="boundary.geojson", years=range(2018, 2025))

result.to_csv("landcover.csv")
result.to_chart("landcover.jpg")
```

---

## Outputs

### CSV

A tidy table with columns for class name, pixel count, area in hectares, and percentage of AOI. When multiple years are requested, a `year` column is added and all years are written to a single file.

Filename pattern: `<product>_<aoi-name>_<first-year>-<last-year>.csv`
Example: `land-cover_boundary_2018-2024.csv`

### Chart (JPG)

A bar chart of area per class, saved as a JPG with configurable DPI. When multiple years are requested, a single chart is produced with years on the x-axis so trends are visible at a glance.

---

## Dependencies

- `sentinelhub-py` — authenticated raster requests
- `geopandas` and `shapely` — AOI handling
- `rasterio` and `numpy` — raster summarisation
- `matplotlib` — chart rendering
- `pandas` — tabular output
- `click` — CLI
- `pyyaml` — config parsing

---

## Limitations and known constraints

- **No change detection.** The library reports values per year but does not compute transition matrices or gain/loss statistics between years. This is planned for a future release.
- **No map outputs.** Only summary statistics and charts are produced; clipped raster maps are not.
- **AOI size.** Sentinel Hub has request size and pixel count limits. For large AOIs the library will warn you when the limit is likely to be exceeded.
- **Products outside the four listed above** (imperviousness, water and wetness, bio-geophysical parameters, etc.) are not supported in this release.

---

## Quick start

Install the package, add your credentials to `~/.clms-aoi/config.yml`, then run:

```bash
clms-aoi land-cover --aoi ./my-boundary.geojson --year 2022 --output ./results --format both
```

Open `results/` and you will find a CSV table and a bar chart ready to share.