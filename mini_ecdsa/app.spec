# -*- coding: utf-8 -*-
# -*- mode: python -*-
a = Analysis(['app.py'],
             pathex=None,
             hiddenimports=['pkg_resources'],
             hookspath=None,
             runtime_hooks=None)

# http://stackoverflow.com/questions/19055089/pyinstaller-onefile-warning-pyconfig-h-when-importing-scipy-or-scipy-signal
for d in a.datas:
    if 'pyconfig' in d[0]:
        a.datas.remove(d)
        break

a.datas += [('main.ui', 'main.ui', 'DATA')]

pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='app.exe',
          debug=False,
          strip=False,
          upx=False,
          console=False)