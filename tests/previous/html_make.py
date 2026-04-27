from mirrordisk.workflows import generate_isosurface_html

try:
    from tests.test_config import make_configs
except ModuleNotFoundError:
    from test_config import make_configs


def main():
    config = make_configs()
    contour_value = generate_isosurface_html(
        config["source_name"],
        config["source_fits"],
        config["mirror_dir"],
        config["html_dir"],
        config["html_config"],
        dsharp=False,
    )
    print(config["source_name"], contour_value)


if __name__ == "__main__":
    main()
