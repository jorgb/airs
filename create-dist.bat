rmdir /Q /S build
rmdir /Q /S dist
python setup.py py2exe build

cd setup

del Airs-Setup.exe
"c:\Program Files\Inno Setup 5\ISCC.exe" Airs-py2exe.iss
del Airs-Src.exe
"c:\Program Files\Inno Setup 5\ISCC.exe" Airs-source.iss

move Airs-Setup.exe D:\personal\databases\moin-wiki\mywiki\data\pages\MyProjects(2f)Airs(2f)Downloads(2f)Latest\attachments\
move Airs-Src.exe D:\personal\databases\moin-wiki\mywiki\data\pages\MyProjects(2f)Airs(2f)Downloads(2f)Latest\attachments\

cd ..

del airs.tar.gz
call C:\Python25\Scripts\bzr.bat export airs.tar.gz
move airs.tar.gz D:\personal\databases\moin-wiki\mywiki\data\pages\MyProjects(2f)Airs(2f)Downloads(2f)Latest\attachments\
