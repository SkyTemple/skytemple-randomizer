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
pip install setuptools wheel 'pyinstaller~=6.0'

# Install certifi for cert handling
pip3 install -U certifi

# install SkyTemple Randomizer
pip3 install -r ../requirements-frozen.txt
# No build isolation to re-use system PyGObject.
pip3 install --no-build-isolation '..[gtk]'
# pip likes to troll us. Force reinstall the proper PyGObject versions
pip install --force-reinstall (Resolve-Path C:\gtk-build\build\x64\release\pygobject\dist\PyGObject*.whl)
pip install --force-reinstall (Resolve-Path C:\gtk-build\build\x64\release\pycairo\dist\pycairo*.whl)

if ($env:IS_DEV_BUILD) {
  bash .\install-skytemple-components-from-git.sh
}

pyinstaller --log-level=DEBUG skytemple-randomizer.spec
if ($LASTEXITCODE) { exit $LASTEXITCODE }

if(!(Test-Path ".\dist\skytemple_randomizer\skytemple_randomizer.exe")){
    exit 1
}

python gen_list_files_for_nsis.py dist\skytemple_randomizer install_list.nsh uninstall_list.nsh

if ($LASTEXITCODE) { exit $LASTEXITCODE }
