# nv_teleportation

![PyPI version](https://img.shields.io/pypi/v/nv_teleportation.svg)

A simple quantum teleportation protocol with Simos Sspins

* [GitHub](https://github.com/alecb03/nv_teleportation/)| [Documentation](https://nv-teleportation.readthedocs.io/en/latest/index.html)
* Created by [Alec Burnett] | GitHub [@alecb03](https://github.com/alecb03)


## Development

To set up for local development:

```bash
# Clone your fork
git clone git@github.com:your_username/nv_teleportation.git
cd nv_teleportation

# Install in editable mode with live updates
uv tool install --editable .
```

This installs the CLI globally but with live updates - any changes you make to the source code are immediately available when you run `nv_teleportation`.

Run tests:

```bash
uv run pytest
```

Run quality checks (format, lint, type check, test):

```bash
just qa
```

## Author

nv_teleportation was created in 2026 by Alec Burnett.

Built with [Cookiecutter](https://github.com/cookiecutter/cookiecutter) and the [audreyfeldroy/cookiecutter-pypackage](https://github.com/audreyfeldroy/cookiecutter-pypackage) project template.
