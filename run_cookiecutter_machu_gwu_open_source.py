# -*- coding: utf-8 -*-

"""
"""

import typing as T
import dataclasses
import shutil
from pathlib import Path
from cookiecutter.main import cookiecutter


@dataclasses.dataclass
class Context:
    package_name: str = dataclasses.field()
    github_username: str = dataclasses.field()
    author: str = dataclasses.field()
    author_email: str = dataclasses.field()
    license: str = dataclasses.field()
    license_classifier: str = dataclasses.field()
    version: str = dataclasses.field()
    dev_python_version: str = dataclasses.field()
    token_name: str = dataclasses.field()
    readthedocs_username: str = dataclasses.field()

    # --- Derived
    package_name_slug: str = dataclasses.field(init=False)

    def __post_init__(self):
        self.package_name_slug = self.package_name.replace("_", "-")

    def to_dict(self) -> dict[str, T.Any]:
        return dataclasses.asdict(self)



if __name__ == "__main__":
    context = Context(
        package_name="cookiecutter_pywf_open_source_demo",
        github_username="MacHu-GWU",
        license="MIT",
        license_classifier="License :: OSI Approved :: MIT License",
        author="Sanhe Hu",
        author_email="husanhe@gmail.com",
        version="0.1.1",
        dev_python_version="3.11.8",
        token_name="sanhe-dev",
        readthedocs_username="machugwu",
    )

    dir_here: Path = Path(__file__).absolute().parent
    dir_output = dir_here.joinpath("tmp")
    if dir_output.exists():
        shutil.rmtree(dir_output)

    cookiecutter(
        template=f"{dir_here}",
        no_input=True,
        extra_context=context.to_dict(),
        output_dir=f"{dir_output}",
    )
