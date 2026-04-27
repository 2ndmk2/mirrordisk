from mirrordisk.workflows import generate_channel_maps

try:
    from tests.test_config import make_configs
except ModuleNotFoundError:
    from test_config import make_configs


def main():
    config = make_configs()
    generate_channel_maps(
        config["source_name"],
        config["source_fits"],
        config["mirror_dir"],
        config["channel_map_dir"],
        config["channel_map_config"],
    )


if __name__ == "__main__":
    main()
