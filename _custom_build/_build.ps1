$ErrorActionPreference = "Stop"
# Convert the Blueprint UI files to XML.
# This requires the blueprint-compiler submodule to be checked out.
python .\blueprint-compiler\blueprint-compiler.py batch-compile skytemple_randomizer\frontend\gtk\widgets skytemple_randomizer\frontend\gtk\widgets (Resolve-Path skytemple_randomizer\frontend\gtk\widgets\*.blp)
if ($LASTEXITCODE) { exit $LASTEXITCODE }
# Build MO message files
Get-ChildItem -Recurse -Path skytemple_randomizer\data\locale\ -Filter '*.po' | ForEach-Object {
  $poFile = $_.FullName;
  $moFile = [System.IO.Path]::ChangeExtension($poFile, ".mo");
  msgfmt -o $moFile $poFile
}
if ($LASTEXITCODE) { exit $LASTEXITCODE }
