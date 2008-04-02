rem start clean
rmdir /Q /S export
mkdir export

rem copy custom template code
copy moindump.tpl export

rem copy all styles to the export dir
xcopy htdocs\modern\*.* export\modern /I /E

python c:\Python25\Lib\site-packages\MoinMoin\script\moin.py --config-dir=d:\personal\databases\moin-wiki\config\ --wiki-url=127.0.0.1/mywiki export dump --target-dir=d:\personal\src\airs\doc\export --page=MyProjects/Airs

copy logo.png export\logo.png