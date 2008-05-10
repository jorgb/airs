cd ..

rmdir /Q /S build
rmdir /Q /S dist
python setup.py py2exe build

cd setup

mkdir build-win32

del build-win32\Airs-Setup.exe
"c:\Program Files\Inno Setup 5\ISCC.exe" Airs-py2exe.iss
move Airs-Setup.exe build-win32

del build-win32\Airs-Src.exe
"c:\Program Files\Inno Setup 5\ISCC.exe" Airs-source.iss
move Airs-Src.exe build-win32

cd ..

