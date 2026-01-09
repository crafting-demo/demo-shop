#!/bin/bash

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

set -ex

rm -fr "$SRC_DIR/bin"
go build -C "$SRC_DIR/src/go" -o ../../bin/ ./cmd/...
npm run -C "$SRC_DIR/src/ts/web" build -- --outDir ../../../bin/web --emptyOutDir
