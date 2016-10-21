#from distutils.core import setup
import sys
from cx_Freeze import setup, Executable
import matplotlib

includefiles = ["icon18.png",]
includes = ["scipy.special._ufuncs_cxx", "scipy.integrate"]
packages = ['scipy', 'scipy.integrate', 'scipy.signal', 'numpy']
build_exe_options = {"packages": packages, "includes":includes, "excludes": ["tkinter",], "include_files":includefiles}


base = None
if sys.platform == "win32":
	base = "Win32GUI"

setup(  name = "MapCreator",
	version = "3.0",
	description = "Application for creating maps from NKS-files.",
	options = {"build_exe": build_exe_options, },
	executables = [Executable("MapCreator.pyw", base=base)],)

# Usage:
#python2.7 setup.py build
