"""Command-line interface for clms-aoi."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from clms_aoi import __version__
from clms_aoi.auth import build_token_cache, load_config
from clms_aoi.aoi import prepare_aoi
from clms_aoi.outputs import write_chart, write_csv

_PRODUCTS = ("corine", "forest_type", "imperviousness", "tree_cover")


@click.group()
@click.version_option(__version__, prog_name="clms-aoi")
def cli() -> None:
    """CLMS AOI — analyse Copernicus land-cover products for an area of interest."""


@cli.command()
@click.argument("aoi_path", metavar="AOI", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--product",
    "-p",
    type=click.Choice(_PRODUCTS),
    required=True,
    help="CLMS product to analyse.",
)
@click.option(
    "--date",
    "-d",
    required=True,
    metavar="YYYY-MM-DD",
    help="Acquisition date for the product.",
)
@click.option(
    "--config",
    "-c",
    default="config/config.yaml",
    show_default=True,
    type=click.Path(path_type=Path),
    help="Path to the YAML configuration file.",
)
@click.option(
    "--out-csv",
    default="output/summary.csv",
    show_default=True,
    type=click.Path(path_type=Path),
    help="Output path for the summary CSV.",
)
@click.option(
    "--out-chart",
    default="output/chart.jpg",
    show_default=True,
    type=click.Path(path_type=Path),
    help="Output path for the bar-chart JPG.",
)
def analyse(
    aoi_path: Path,
    product: str,
    date: str,
    config: Path,
    out_csv: Path,
    out_chart: Path,
) -> None:
    """Fetch a CLMS raster for AOI and write a summary CSV + bar chart."""
    cfg = load_config(config)
    token_cache = build_token_cache(cfg)
    token = token_cache.get_token()

    gdf, bbox = prepare_aoi(aoi_path)
    click.echo(f"AOI bbox: {bbox}")

    # Import the requested product module dynamically.
    import importlib

    mod = importlib.import_module(f"clms_aoi.products.{product}")
    cls_name = "".join(part.title() for part in product.split("_")) + "Product"
    product_obj = getattr(mod, cls_name)(token)

    df = product_obj.run(bbox, date)

    csv_path = write_csv(df, out_csv)
    click.echo(f"CSV written to {csv_path}")

    if not df.empty:
        x_col, y_col = df.columns[0], df.columns[1]
        chart_path = write_chart(
            df,
            x=x_col,
            y=y_col,
            path=out_chart,
            title=f"{product.replace('_', ' ').title()} — {date}",
        )
        click.echo(f"Chart written to {chart_path}")
    else:
        click.echo("Summary DataFrame is empty — no chart produced.", err=True)
        sys.exit(1)


def main() -> None:
    cli()
