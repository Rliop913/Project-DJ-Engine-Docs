#!/bin/bash
doxygen ./Doxyfile
uv run sphinx-build -b html ./srcs docs
