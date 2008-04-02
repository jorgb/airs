To create an install distributable you have the following options:

On Windows
----------
    
  >> To build a stand alone executable perform the following steps:
    
     1. Download and install InnoSetup (http://www.jrsoftware.org/isinfo.php)
     1. Download and install py2exe (http://www.py2exe.org/)
     3. Remove the following dirs if they exist: 'build' and 'dist' from your
        source directory
     2. Run 'create-dist.bat' from the main dir
     3. In the setup directory, compile the file Airs-py2exe.iss with 
        Inno Setup
     4. Distribute your exe
     
  >> To build a source version perform the following steps:
    
     1. In the setup directory, compile the file Airs-source.iss with 
        Inno Setup
     2. Make sure your target system has Python 2.5+ pre installed and 
        wxPython 2.8+
        
    Why a source version? 
    - On the fly editing, people can contribute back changes
    - Smaller in size also as distributable
    - Multiple apps using Python/wxPython do not generate an overhead
    
    Why a stand alone version?
    - No extra steps needed for people
    - Runs out of the box everywhere
    - Slightly optimized speed
