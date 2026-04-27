import argparse

from mirrordisk.workflows import (
    PIPELINE_STEP_NAMES,
    build_pipeline_steps,
)

from config import DEFAULT_OUTPUT_ROOT, DEFAULT_TARGETS_CSV, list_datasets, make_configs


def main():
    parser = argparse.ArgumentParser(description="Run the test pipeline.")
    parser.add_argument(
        "--dataset",
        help="Dataset name defined in the targets CSV. If omitted, run all datasets in the CSV.",
    )
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help="Base directory for pipeline outputs.",
    )
    parser.add_argument(
        "--targets-csv",
        default=str(DEFAULT_TARGETS_CSV),
        help="CSV file defining input targets.",
    )
    parser.add_argument(
        "steps",
        nargs="*",
        choices=PIPELINE_STEP_NAMES,
        help="Pipeline steps to run. If omitted, all steps run in order.",
    )

    args = parser.parse_args()

    available_datasets = list_datasets(args.targets_csv)
    if args.dataset and args.dataset not in available_datasets:
        parser.error(
            f"unknown dataset '{args.dataset}'. Available datasets from {args.targets_csv}: "
            + ", ".join(available_datasets)
        )

    dataset_names = [args.dataset] if args.dataset else available_datasets
    for dataset_name in dataset_names:
        config = make_configs(
            dataset_name,
            output_root=args.output_root,
            targets_csv=args.targets_csv,
        )
        pipeline_steps = build_pipeline_steps(
            source_name=config["source_name"],
            source_fits=config["source_fits"],
            mirror_dir=config["mirror_dir"],
            channel_map_dir=config["channel_map_dir"],
            html_dir=config["html_dir"],
            moment_dir=config["moment_dir"],
            mirror_config=config["mirror_config"],
            channel_map_config=config["channel_map_config"],
            html_config=config["html_config"],
            residual_analysis_config=config["residual_analysis_config"],
            dsharp=False,
        )
        selected_steps = args.steps or list(pipeline_steps.keys())
        for step in selected_steps:
            pipeline_steps[step]()


if __name__ == "__main__":
    main()
