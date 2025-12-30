# simpleagent.spec

# -*- mode: python ; coding: utf-8 -*-

import sys
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# --- Data files ---
# Bundle the default config file with the application.
# The main.py script is written to look for 'config.yaml' in the bundle.
datas = [('sample_config.yaml', 'config.yaml')]

# Bleak may require its platform-specific data files.
datas += collect_data_files('bleak')

# --- Hidden Imports ---
# Bleak uses different backends for different operating systems.
# PyInstaller's static analysis might miss these, so we specify them here.
hiddenimports = []
if sys.platform == "win32":
    hiddenimports.append('bleak.backends.winrt')
elif sys.platform == "darwin":
    hiddenimports.append('bleak.backends.corebluetooth')
else:  # Assuming Linux
    hiddenimports.append('bleak.backends.bluezdbus')
    # The BlueZ backend might need this as well
    hiddenimports.append('dbus_next.auth')


a = Analysis(
    ['main.py'],
    pathex=['/home/kp/github/python_scripts/simpleagent'],  # Adjust if your project root is different
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    name='simpleagent',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=True,
    icon=None,  # You can add an icon here, e.g., 'app.ico'
)