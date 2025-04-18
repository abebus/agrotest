import sys
import click
from pathlib import Path
from loguru import logger

from phone_extractor import PhoneExtractor


@click.command(
    help="""
    Extracts phone numbers from text or file input.

    All phone numbers are normalized to the format: +7(YYY)XXX-XX-XX.

    Examples:

        echo "call me at 8 926 123-45-67" | python cli.py
        python cli.py "+7 (999) 000 11 22"
        python cli.py input.txt --output output.txt
    """
)
@click.argument(
    "source",
    required=False,
    type=click.UNPROCESSED,
)
@click.option(
    "--output",
    "-o",
    type=click.Path(writable=True, path_type=Path),
    help="Path to the output file. If not set, prints to stdout.",
)
@click.option(
    "--encoding",
    "-e",
    help="Specify encoding explicitly. If not set, it will be auto-detected.",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose (debug-level) logging.",
)
def cli(source: str | None, output: Path | None, encoding: str | None, verbose: bool):
    _configure_logger(verbose)

    extractor = PhoneExtractor()

    if not source and not sys.stdin.isatty():
        logger.info("Reading from stdin...")
        text = sys.stdin.read()
        phones = extractor.from_string(text)
        _handle_output(phones, output)
        return

    if source and not Path(source).exists():
        logger.info("Processing as raw string...")
        phones = extractor.from_string(source)
        _handle_output(phones, output)
        return

    if source and Path(source).exists():
        input_path = Path(source)
        logger.info(f"Reading from file: {input_path}")
        phones = extractor.from_file(
            input_path, output_path=output if output else None, encoding=encoding
        )
        if not output:
            for p in phones:
                print(p)
        return

    click.echo(
        "Error: No input source provided (file, string, or stdin). Use --help for more info.",
        err=True,
    )
    sys.exit(1)


def _handle_output(phones: list[str], output: Path | None):
    if output:
        with open(output, "w", encoding="utf-8") as f:
            for p in phones:
                print(p, file=f)
        logger.success(f"Written to file: {output}")
    else:
        for p in phones:
            print(p)


def _configure_logger(verbose: bool):
    logger.remove()
    logger_level = "DEBUG" if verbose else "INFO"
    logger.add(
        sys.stderr,
        level=logger_level,
        format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>",
    )


if __name__ == "__main__":
    cli()
