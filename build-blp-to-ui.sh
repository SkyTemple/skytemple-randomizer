#!/bin/sh
# Convert the Blueprint UI files to XML.
# This requires the blueprint-compiler submodule to be checked out.
set -xe
./blueprint-compiler/blueprint-compiler.py \
  batch-compile \
  skytemple_randomizer/frontend/gtk/widgets \
  skytemple_randomizer/frontend/gtk/widgets \
  skytemple_randomizer/frontend/gtk/widgets/*.blp
