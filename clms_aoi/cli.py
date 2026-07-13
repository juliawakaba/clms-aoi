"""Command-line interface with logging configuration."""

import argparse
import logging
import sys

from .auth import SentinelHubAuthenticator
from .config import ConfigLoader
from .exceptions import ClmsAoiError


def setup_logging(verbose: bool = False):
    """Sets up basic logging configuration."""
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

def cmd_validate_config(args):
    """Validates the given YAML configuration file."""
    try:
        config = ConfigLoader.load(args.path)
        logging.info("Config loaded successfully from '{args.path}'.")
        logging.info("Products configured: {config.products}")
    except ClmsAoiError as error:
        logging.error("Config Validation Error: {error}")
        return 1
    return 0

def cmd_check_auth(args):
    """Tests authentication against Sentinel Hub."""
    try:
        config = ConfigLoader.load(args.config)
        authenticator = SentinelHubAuthenticator(config.sentinelhub)
        token = authenticator.authenticate()
        logging.info("Authentication Successful!")
        logging.info(f"Access Token: {token[:15]}...")
    except ClmsAoiError as error:
        logging.error("Authentication Failed: {error}")
        return 1
    return 0


def main():
    parser = argparse.ArgumentParser(prog="clms-aoi", description="CLMS AOI Analysis Tool")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable debug logging output")
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Command to validate-config
    clms_validate = subparsers.add_parser("validate-config", help="Validate YAML config file")
    clms_validate.add_argument("path", help="Path to config YAML file")

    # Command to check-auth
    clms_auth = subparsers.add_parser("check-auth", help="Test Sentinel Hub authentication")
    clms_auth.add_argument("--config", default="config.yaml", help="Path to config YAML file")

    args = parser.parse_args()

    # Configure logging based on user flags
    setup_logging(args.verbose)

    if args.command == "validate-config":
        sys.exit(cmd_validate_config(args))
    elif args.command == "check-auth":
        sys.exit(cmd_check_auth(args))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()









# """Command-line interface for clms-aoi."""

# from __future__ import annotations

# import sys
# from pathlib import Path

# import click

# from clms_aoi import __version__
# from clms_aoi.auth import build_token_cache, load_config
# from clms_aoi.aoi import aoi_geojson, prepare_aoi
# from clms_aoi.outputs import write_chart, write_csv

# _PRODUCTS = ("corine", "forest_type", "imperviousness", "tree_cover")


# @click.group()
# @click.version_option(__version__, prog_name="clms-aoi")
# def cli() -> None:
#     """CLMS AOI — analyse Copernicus land-cover products for an area of interest."""


# @cli.command()
# @click.argument("aoi_path", metavar="AOI", type=click.Path(exists=True, path_type=Path))
# @click.option(
#     "--product",
#     "-p",
#     type=click.Choice(_PRODUCTS),
#     required=True,
#     help="CLMS product to analyse.",
# )
# @click.option(
#     "--year",
#     "-y",
#     required=True,
#     type=int,
#     help="Year to analyse (e.g. 2020).",
# )
# @click.option(
#     "--config",
#     "-c",
#     default="config/config.yaml",
#     show_default=True,
#     type=click.Path(path_type=Path),
#     help="Path to the YAML configuration file.",
# )
# @click.option(
#     "--out-csv",
#     default="output/summary.csv",
#     show_default=True,
#     type=click.Path(path_type=Path),
#     help="Output path for the summary CSV.",
# )
# @click.option(
#     "--out-chart",
#     default="output/chart.jpg",
#     show_default=True,
#     type=click.Path(path_type=Path),
#     help="Output path for the bar-chart JPG.",
# )
# def analyse(
#     aoi_path: Path,
#     product: str,
#     year: int,
#     config: Path,
#     out_csv: Path,
#     out_chart: Path,
# ) -> None:
#     """Fetch a CLMS raster for AOI and write a summary CSV + bar chart."""
#     cfg = load_config(config)
#     token_cache = build_token_cache(cfg)

#     gdf, bbox = prepare_aoi(aoi_path)
#     geometry = aoi_geojson(gdf)
#     click.echo(f"AOI bbox: {bbox}")

#     import importlib

#     mod = importlib.import_module(f"clms_aoi.products.{product}")
#     cls_name = "".join(part.title() for part in product.split("_")) + "Product"
#     product_obj = getattr(mod, cls_name)(token_cache)

#     df = product_obj.run(bbox, geometry, year)

#     csv_path = write_csv(df, out_csv)
#     click.echo(f"CSV written to {csv_path}")

#     if not df.empty:
#         x_col, y_col = df.columns[0], df.columns[1]
#         chart_path = write_chart(
#             df,
#             x=x_col,
#             y=y_col,
#             path=out_chart,
#             title=f"{product.replace('_', ' ').title()} — {year}",
#         )
#         click.echo(f"Chart written to {chart_path}")
#     else:
#         click.echo("Summary DataFrame is empty — no chart produced.", err=True)
#         sys.exit(1)


# def main() -> None:
#     cli()
