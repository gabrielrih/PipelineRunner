from importlib.metadata import version, PackageNotFoundError


PACKAGE_NAME = "pipelinerunner"


def get_version():
    try:
        return version(PACKAGE_NAME)
    except PackageNotFoundError:
        return "0.0.0-dev"
