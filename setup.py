import os
from distutils.core import setup
import py2exe


manifest = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1"
manifestVersion="1.0">
<assemblyIdentity
    version="0.64.1.0"
    processorArchitecture="x86"
    name="Controls"
    type="win32"
/>
<description>Airs</description>
<dependency>
    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.Windows.Common-Controls"
            version="6.0.0.0"
            processorArchitecture="X86"
            publicKeyToken="6595b64144ccf1df"
            language="*"
        />
    </dependentAssembly>
</dependency>
</assembly>
"""

"""
installs manifest and icon into the .exe
but icon is still needed as we open it
for the window icon (not just the .exe)
changelog and logo are included in dist
"""

#setup( console = [ { "script": "airs.py" } ] 
#      ,data_files=["setup\\dll\\msvcp71.dll"],
#    )

setup( windows = [ { "script": "airs.pyw",
                     "icon_resources": [(1, "airs.ico")],
                     "other_resources": [(24,1,manifest)] } ] 
      ,data_files=["setup\\dll\\msvcp71.dll"],
    )
