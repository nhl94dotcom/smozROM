call create_exe.bat smozROM.py

mkdir smozROM
copy dist\*.* smozROM
copy README.txt smozROM
copy weightscale.txt smozROM
copy gpl.txt smozROM
copy *.html smozROM

mkdir smozROM\src
mkdir smozROM\src\hacks

copy hexutil.py smozROM\src
copy smozROM.py smozROM\src
copy hacks\*.py smozROM\src\hacks

mkdir "smozROM\NOSE update"
copy "NOSE update\*.*" "smozROM\NOSE update"