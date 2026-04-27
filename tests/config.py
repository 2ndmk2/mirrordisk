import csv
from pathlib import Path

import numpy as np

from mirrordisk.workflows import (
    ChannelMapConfig,
    HtmlConfig,
    MirrorProcessingConfig,
    ResidualAnalysisConfig,
    build_mirror_paths,
)


DEFAULT_OUTPUT_ROOT = Path("/Volumes/T7 Shield/exoalma_for_code/output")
DEFAULT_TARGETS_CSV = Path(__file__).with_name("targets.csv")

# Common mirror-fitting defaults shared across targets.
MIRROR_DEFAULT_PARAMS = {
    "inp_max": 6.0,
    "n_points": 120,
    "vec_offsets": np.array([-1.4, -1.2, -1.0, -0.8, -0.6, -0.4, -0.2]),
}

CHANNEL_MAP_PARAMS = {
    "dv": 0.1,
    "vlim": 2.5,
    "plot_lim": 7.5,
    "font_size": 22,
    "axes_labelsize": 22,
}

HTML_PARAMS = {
    "skip1": 3,
    "skip2": 1,
    "vlim": 2.5,
    "plot_lim": 5.0,
    "contour_sigma": 6.5,
}

RESIDUAL_ANALYSIS_PARAMS = {
    "skip1": 1,
    "skip2": 1,
    "vlim": 2.5,
    "min_npix": 1000,
    "nsigma": 5,
    "plot_lim": 5.0,
}

DEFAULT_DATASET = "J1615"


def load_targets(targets_csv: str | Path = DEFAULT_TARGETS_CSV) -> dict[str, dict[str, object]]:
    datasets: dict[str, dict[str, object]] = {}
    with Path(targets_csv).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            source_name = row["source_name"].strip()
            datasets[source_name] = {
                "source_fits_path": Path(row["source_fits_path"].strip()),
                "pa_deg_initial": float(row["pa_deg_initial"]),
                "x_cen_initial": float(row["x_cen_initial"]),
                "vsys_initial": None if row["vsys_initial"].strip() == "" else float(row["vsys_initial"]),
            }
    return datasets


def list_datasets(targets_csv: str | Path = DEFAULT_TARGETS_CSV) -> list[str]:
    return sorted(load_targets(targets_csv))


def make_configs(
    dataset_name: str = DEFAULT_DATASET,
    output_root: str | Path = DEFAULT_OUTPUT_ROOT,
    targets_csv: str | Path = DEFAULT_TARGETS_CSV,
) -> dict[str, object]:
    datasets = load_targets(targets_csv)
    if dataset_name not in datasets:
        available = ", ".join(sorted(datasets))
        raise KeyError(f"Unknown dataset '{dataset_name}'. Available datasets: {available}")

    dataset_row = datasets[dataset_name]
    output_root_path = Path(output_root)
    mirror_params = {
        **MIRROR_DEFAULT_PARAMS,
        "source_name": dataset_name,
        "source_fits_name": Path(dataset_row["source_fits_path"]).name,
        "pa_deg_initial": dataset_row["pa_deg_initial"],
        "x_cen_initial": dataset_row["x_cen_initial"],
        "vsys_initial": dataset_row["vsys_initial"],
    }
    mirror_config = MirrorProcessingConfig(**mirror_params)
    channel_map_config = ChannelMapConfig(**CHANNEL_MAP_PARAMS)
    html_config = HtmlConfig(**HTML_PARAMS)
    residual_analysis_config = ResidualAnalysisConfig(**RESIDUAL_ANALYSIS_PARAMS)

    source_fits = Path(dataset_row["source_fits_path"])
    mirror_dir = output_root_path / "result" / "mirror"
    mirror_paths = build_mirror_paths(source_fits, mirror_dir)

    return {
        "source_name": mirror_config.source_name,
        "source_fits": source_fits,
        "mirror_config": mirror_config,
        "channel_map_config": channel_map_config,
        "html_config": html_config,
        "residual_analysis_config": residual_analysis_config,
        "output_root": output_root_path,
        "mirror_dir": mirror_dir,
        "mirror_paths": mirror_paths,
        "channel_map_dir": output_root_path / "result" / "channel_maps" / mirror_config.source_name,
        "moment_dir": output_root_path / "moms",
        "html_dir": output_root_path / "html",
    }
