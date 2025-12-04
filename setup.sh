#!/bin/bash

# init uv
uv init & uv venv --python 3.13
uv python pin 3.13
# install tools
uv tool install ruff
uv tool install mypy
