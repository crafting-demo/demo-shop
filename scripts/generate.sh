#!/bin/bash

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

set -ex

cd "$SRC_DIR/src"
npx -y @bufbuild/buf generate
go generate -C go ./...
npm run -C ts/web codegen
