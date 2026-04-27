from mirrordisk.workflows import generate_mirror_products

try:
    from tests.test_config import make_configs
except ModuleNotFoundError:
    from test_config import make_configs


def main():
    config = make_configs()
    generate_mirror_products(config["source_fits"], config["mirror_dir"], config["mirror_config"])


if __name__ == "__main__":
    main()
