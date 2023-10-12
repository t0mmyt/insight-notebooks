#!/bin/bash
set -euo pipefail

build_dir="build/seisglitch"

rm -rf ${build_dir}
mkdir -p ${build_dir}
cd ${build_dir}

python3 -m venv .venv
. .venv/bin/activate
pip install setuptools wheel numpy
git clone https://github.com/t0mmyt/seisglitch
cd seisglitch
git checkout numpy_version

python3 setup.py bdist_wheel
cp dist/seisglitch-1.0.1-py3-none-any.whl ../../