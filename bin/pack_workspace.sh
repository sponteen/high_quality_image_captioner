#!/bin/bash
CODE_DIR="$(dirname $0)/.."

find . -iname '*.yaml' -print0 | tar -cvjf $CODE_DIR/tests/test_workspace.tar.xz --null -T -
