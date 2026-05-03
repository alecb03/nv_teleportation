# nv_teleportation

![PyPI version](https://img.shields.io/pypi/v/nv_teleportation.svg)

A simple quantum teleportation protocol with Simos Sspins

* [GitHub](https://github.com/alecb03/nv_teleportation/) | [PyPI](https://pypi.org/project/nv_teleportation/) | [Documentation](https://alecb03.github.io/nv_teleportation/)
* Created by [Alec Burnett](https://audrey.feldroy.com/) | GitHub [@alecb03](https://github.com/alecb03) | PyPI [@alecb03](https://pypi.org/user/alecb03/)
* MIT License

## Features

* TODO

## Documentation

Documentation is built with [Zensical](https://zensical.org/) and deployed to GitHub Pages.

* **Live site:** https://alecb03.github.io/nv_teleportation/
* **Preview locally:** `just docs-serve` (serves at http://localhost:8000)
* **Build:** `just docs-build`

API documentation is auto-generated from docstrings using [mkdocstrings](https://mkdocstrings.github.io/).

Docs deploy automatically on push to `main` via GitHub Actions. To enable this, go to your repo's Settings > Pages and set the source to **GitHub Actions**.

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
