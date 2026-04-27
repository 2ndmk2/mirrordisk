from mirrordisk.workflows import analyze_residuals

try:
    from tests.test_config import make_configs
except ModuleNotFoundError:
    from test_config import make_configs


def main():
    config = make_configs()
    analyze_residuals(
        config["source_name"],
        config["source_fits"],
        config["mirror_dir"],
        config["moment_dir"],
        config["residual_analysis_config"],
        dsharp=False,
    )


if __name__ == "__main__":
    main()
