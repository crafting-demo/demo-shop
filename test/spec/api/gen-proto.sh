#!/bin/bash

set -e

cd "$(dirname "${BASH_SOURCE[0]}")"

rm -fr proto

uv run -m grpc_tools.protoc \
    -Iproto=../../../src/apis/proto \
    --python_out=. --grpc_python_out=. --pyi_out=. \
    ../../../src/apis/proto/demoshop/v1/*.proto

touch proto/__init__.py
touch proto/demoshop/__init__.py
touch proto/demoshop/v1/__init__.py
