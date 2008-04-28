rmdir /Q /S build
rmdir /Q /S dist
python setup.py py2exe build

cd setup

del Airs-Setup.exe
"c:\Program Files\Inno Setup 5\ISCC.exe" Airs-py2exe.iss
del Airs-Src.exe
"c:\Program Files\Inno Setup 5\ISCC.exe" Airs-source.iss

cd ..

del airs.tar.gz
call C:\Python25\Scripts\bzr.bat export airs.tar.gz
move airs.tar.gz setup
