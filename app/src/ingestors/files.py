from pathlib import Path


def file(out_dir: Path, file: Path):
    file.rename(out_dir / "ingested" / file.name)
