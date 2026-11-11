"""Contract: source CKAN native OpenGA (niente piu' `type: script`).

Protegge la migrazione da prefetch.py a N source `ckan` per dataset:

1. nessuna source `script`, ogni dataset ha le sedi attese (31, pareri 2);
2. le source usano il CSV diretto (`prefer_datastore: false`) e `download_all`;
3. nessun residuo di prefetch o dell'env CI dedicato.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
DATASETS_DIR = ROOT / "datasets"
EXPECTED_SOURCES = {"ga-pareri": 2}
DEFAULT_SOURCES = 31


def _dataset_dirs() -> list[Path]:
    return sorted(path.parent for path in DATASETS_DIR.glob("*/dataset.yml"))


@pytest.mark.contract
@pytest.mark.parametrize("dataset_dir", _dataset_dirs(), ids=lambda path: path.name)
def test_native_ckan_sources(dataset_dir: Path) -> None:
    config = yaml.safe_load((dataset_dir / "dataset.yml").read_text(encoding="utf-8"))
    sources = config["raw"]["sources"]

    expected = EXPECTED_SOURCES.get(dataset_dir.name, DEFAULT_SOURCES)
    assert len(sources) == expected
    assert all(source["type"] == "ckan" for source in sources)
    assert all(source["args"]["download_all"] is True for source in sources)
    assert all(source["args"]["prefer_datastore"] is False for source in sources)
    assert len({source["args"]["dataset_id"] for source in sources}) == expected
    assert len({source["args"]["filename"] for source in sources}) == expected


@pytest.mark.contract
def test_no_script_source_or_prefetch_leftovers() -> None:
    assert not (ROOT / "prefetch.py").exists()
    for name in ("Makefile", ".github/workflows/pipeline.yml"):
        text = (ROOT / name).read_text(encoding="utf-8")
        assert "TOOLKIT_ALLOW_SCRIPT_SOURCE" not in text, name
        assert "prefetch" not in text, name
