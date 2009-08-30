"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""
#import ez_setup
#ez_setup.use_setuptools()

from setuptools import setup
import shutil
import os
import sys
from pdk.fileutils import safe_mkdirs, collect_files

main_script = 'CecogAnalyzer.py'

def tempsyspath(path):
    def decorate(f):
        def handler():
            sys.path.insert(0, path)
            value = f()
            del sys.path[0]
            return value
        return handler
    return decorate

def read_pkginfo_file(setup_file):
    path = os.path.dirname(setup_file)
    @tempsyspath(path)
    def _import_pkginfo_file():
        if '__pgkinfo__' in sys.modules:
            del sys.modules['__pkginfo__']
        return __import__('__pkginfo__')
    return _import_pkginfo_file()

pkginfo = read_pkginfo_file(__file__)

# delete target folder before execution of py2app
for path in ['dist', 'build']:
    if os.path.isdir(path):
        shutil.rmtree(path)

APP = [main_script]
if sys.platform == 'darwin':
    OPTIONS = {'app' : APP}
    DATA_FILES = []
    SYSTEM = 'py2app'
    EXTRA_OPTIONS = {'argv_emulation': True,
                     'includes': ['sip'],
                     'excludes': ['PyQt4.QtDesigner', 'PyQt4.QtNetwork',
                                  'PyQt4.QtOpenGL', 'PyQt4.QtScript',
                                  'PyQt4.QtSql', 'PyQt4.QtTest',
                                  'PyQt4.QtWebKit', 'PyQt4.QtXml',
                                  'PyQt4.phonon'],
                     'packages': ['pyvigra', 'cecog'],
                     'resources': [],
                     'optimize': 2,
                     'iconfile': 'resources/cecog_browser_icon.icns',
                    }
elif sys.platform == 'win32':
    import py2exe # pylint: disable-msg=F0401,W0611
    OPTIONS = {'windows': [{'script': main_script,
                           'icon_resources': \
                               [(1, r'..\CecogBrowser\resources\cecog_browser_icon.ico')],
                           }]
               }
    DATA_FILES = []#r'resources\cecog_browser_icon2.ico']
    SYSTEM = 'py2exe'
    EXTRA_OPTIONS = {'includes': ['sip',],
                     'excludes': ['pydoc',
                                  'pywin', 'pywin.debugger',
                                  'pywin.debugger.dbgcon',
                                  'pywin.dialogs', 'pywin.dialogs.list',
                                  'Tkconstants', 'Tkinter', 'tcl',
                                  ],
                     'packages': ['pyvigra',],
                     'optimize': 2,
                     'compressed': True,
                     'bundle_files': 1,
                     #'xref': True,
                    }


setup(
    data_files=DATA_FILES,
    options={SYSTEM: EXTRA_OPTIONS},
    setup_requires=[SYSTEM],
    name=pkginfo.name,
    version=pkginfo.version,
    author=pkginfo.author,
    author_email=pkginfo.author_email,
    license=pkginfo.license,
    description=pkginfo.description,
    long_description=pkginfo.long_description,
    url=pkginfo.url,
    download_url=pkginfo.download_url,
    classifiers=pkginfo.classifiers,
#    package_dir=pkginfo.package_dir,
#    packages=pkginfo.packages,
    platforms=pkginfo.platforms,
    provides=pkginfo.provides,
    **OPTIONS
)


if sys.platform == 'darwin':

    base_path = 'dist/CecogBrowser.app'

    # for unknown reasons the pyconfig.h is needed but not included
    target_path = os.path.join(base_path, 'Contents/Resources/include/python2.6')
    safe_mkdirs(target_path)
    shutil.copy('/Library/Frameworks/Python.framework/Versions/2.6/include/python2.6/pyconfig.h',
                target_path)

    # delete all stupid Qt4 debug files (~130MB!!!)
    target_path = os.path.join(base_path, 'Contents/Frameworks')
    filenames = collect_files(target_path, [], absolute=True, recursive=True)
    filenames = [x for x in filenames if 'debug' in os.path.split(x)[1]]
    for filename in filenames:
        if os.path.isdir(filename):
            shutil.rmtree(filename)
        elif os.path.isfile(filename):
            os.remove(filename)

    # copy the pyvigra dylibs into the right place
    DYLIBS = ['libboost_python.dylib',
              'libvigraimpex.dylib']
    for filename in DYLIBS:
        target = os.path.join(base_path,
                              'Contents/Frameworks',
                              filename)
        if os.path.isfile(target):
            os.remove(target)
        shutil.move(os.path.join(base_path,
                                 'Contents/Resources/lib/python2.6/pyvigra',
                                 filename),
                    os.path.join(base_path,
                                 'Contents/Frameworks'))
    for filename in DYLIBS:
        target = os.path.join(base_path,
                              'Contents/Resources/lib/python2.6/cecog/ccore',
                              filename)
        if os.path.isfile(target):
            os.remove(target)


    ## delete ALL .py files from lib (and use .pyc/.pyo instead)
    target = os.path.join(base_path, 'Contents/Resources/lib/python2.6/')
    for filename in collect_files(target, ['.py'], force_python=True,
                                  absolute=False, recursive=True):
        if filename != 'site.py':
            os.remove(os.path.join(target, filename))


elif sys.platform == 'win32':
    import zipfile
    lib_filename = r'dist\library.zip'
    zfile = zipfile.PyZipFile(lib_filename, 'a')
    vc_path = r'C:\Program Files\Microsoft Visual Studio 9.0\VC\redist\x86\Microsoft.VC90.CRT'
    filenames = [r'C:\Source\Lib\libfftw3-3.dll',
                 os.path.join(vc_path, 'msvcm90.dll'),
                 os.path.join(vc_path, 'msvcp90.dll'),
                 os.path.join(vc_path, 'msvcr90.dll'),]
    for filename in filenames:
        print "adding '%s' to '%s'" % (filename, lib_filename)
        zfile.write(filename, os.path.split(filename)[1])
    zfile.close()

