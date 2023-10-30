Set-PSDebug -Trace 1
$ErrorActionPreference = "Stop"

if (test-path build) {
  rm build -r -force
}
if (test-path dist) {
  rm dist -r -force
}

# Download armips and other binary depedencies
curl https://skytemple.org/build_deps/armips.exe -O

# Install NSIS
curl https://skytemple.org/build_deps/nsis.zip -O
unzip -o nsis.zip -d "C:\Program Files (x86)\NSIS"

python -m venv C:\skytemple-venv
C:\skytemple-venv\Scripts\activate.ps1

# Install PyInstaller
pip install setuptools wheel 'pyinstaller~=5.0'

# Install certifi for cert handling
pip3 install -U certifi

# Generate MO localization files
bash .\generate-mo.sh

# install SkyTemple Randomizer
pip3 install -r ../requirements-mac-windows.txt
pip3 install ..

if ($env:IS_DEV_BUILD) {
  bash .\install-skytemple-components-from-git.sh
}

pyinstaller skytemple-randomizer.spec
if ($LASTEXITCODE) { exit $LASTEXITCODE }

if(!(Test-Path ".\dist\skytemple_randomizer\skytemple_randomizer.exe")){
    exit 1
}

# Check if we need to copy the cacert file
if (Test-Path ".\dist\skytemple\certifi\cacert.pem") {
  echo "Moved cacert to correct place"
  cp dist/skytemple/certifi/cacert.pem dist/skytemple/certifi.pem
}

echo $env:PACKAGE_VERSION | Out-File -FilePath dist/skytemple_randomizer/VERSION -Encoding utf8
echo $env:PACKAGE_VERSION | Out-File -FilePath dist/skytemple_randomizer/data/VERSION -Encoding utf8
