$ErrorActionPreference = "Stop"
# Convert the Blueprint UI files to XML.
# This requires the blueprint-compiler submodule to be checked out.
.\blueprint-compiler\blueprint-compiler.py batch-compile skytemple_randomizer\frontend\gtk\widgets skytemple_randomizer\frontend\gtk\widgets (Resolve-Path skytemple_randomizer\frontend\gtk\widgets\*.blp)
if ($LASTEXITCODE) { exit $LASTEXITCODE }
