
#+Price Debug Enable Python remote debugger

#import ptvsd
#ptvsd.enable_attach(secret = None, address = (  '127.0.0.1' , 8080))
#ptvsd.wait_for_attach()

#ptvsd.break_into_debugger()
#-remote debugger


import sys
import subprocess
import codecs

#*****************************************************************************    
# Functions 
#*****************************************************************************    
def PrintUsage():
    print ("Takes an RSOD dump file as input and does an RSOD Decode.")
    print ("Rsod_Decode.exe must be in the path (or current directory.)")
    print ("")
    print ("Usage: RsodDecodeAll.py [-h]")
    print (" -rsodfile=<rsodfilename>")
    print (" -BiosPathX64=<path to x64 directory in build directory).")
    print ("")
    print ("Note: If using the default 'U:' mapping for the build, it must be")
    print ("mapped to the BIOS being debugged.")
    print ("")

def GetArgs():
    """Get command-line arguments and return in a dictionary."""
    
    UserArgs = {}
    UserArgs['help'] = False
    UserArgs['RsodFileName'] = ""
    UserArgs['BiosPathX64'] = ""

    for i in range(1,len(sys.argv)):
        if   sys.argv[i].lower() == "-help"           : UserArgs["help"] = True
        elif sys.argv[i].lower() == "-h"              : UserArgs["help"] = True
        elif "-rsodfile=" in sys.argv[i].lower()      : UserArgs['RsodFileName'] = sys.argv[i].split ('=', 1)[1]
        elif "-biospathx64=" in sys.argv[i].lower()   : UserArgs['BiosPathX64'] = sys.argv[i].split ('=', 1)[1]

    return UserArgs

#def StringValidforAnalyze(RsodDecodeOutput):


#
# ex: input: 'CpuBreakpoint u:\\mdepkg\\library\\baselib\\X64\\cpubreakpoint.c(38)'
#


def ShowCode(RsodDecodeOutput):
    if not 'u:\\' in RsodDecodeOutput: return
    if not '(' in RsodDecodeOutput: return
    if 'Unknown' in RsodDecodeOutput: return

    FileNamePath = (RsodDecodeOutput.split())[1].split('(') #[u:xxx , 38)]
    LineNumber = int(FileNamePath[1].rstrip(')')) #38) -> 38
    FilePath = FileNamePath[0].replace('\\','/') #get file path

    f = open(FilePath, "r")
    Lines = f.readlines()
    f.close() 
    print(Lines[LineNumber-1]) #print source code.


#*****************************************************************************    
#    Entry point.
#*****************************************************************************    
def main():
    print ("RSOD Decode Full v1.0\n")

    UserArgs = GetArgs()
    RsodFileName = UserArgs['RsodFileName']
    BiosPathX64 = UserArgs['BiosPathX64']
    
    if UserArgs['help']:
        PrintUsage()
        return

    if RsodFileName == "":
        PrintUsage()
        print ("!!! No RSOD File provided !!!\n")
        return

    if BiosPathX64 == "":
        PrintUsage()
        print ("!!! No BiosPathX64 provided !!!\n")
        return

#    # Given the provided BIOS path to the "..\..\x64" directory, find the root by findind the 
#    # directory above "\Build\."
#    if "\\Build\\" in BiosPathX64:
#        Index = BiosPathX64.find ("\\Build\\")
#        BiosBuildPath = BiosPathX64[:Index]
#    else:
#        PrintUsage()
#        print ("!!! BiosPathX64 does not have a 'Build' directory !!!")
#        return
#  
#    print ("Substiting U: for ", BiosBuildPath)
    BiosPathX64 = BiosPathX64 + "\\"
#    subprocess.call ("subst u: /d", shell=True)
#    subprocess.call ("subst u: %s"%BiosBuildPath, shell=True)
#price debug++    
    if 1:
        Lines = []
        AppendStart = False

        f = open(RsodFileName, "r", encoding="utf8", errors='ignore')

        while True:
            SingleLine = f.readline().encode('utf-8', 'replace')
            #SingleLine = b'xxxxxxxx\n'
 
            SingleLine = SingleLine.decode()

            if not SingleLine: break
         
            if "BIOS rev " in SingleLine: AppendStart = True
            
            if AppendStart:
                #Lines.append(str(SingleLine).lstrip('b').replace('\\n','').strip('\''))
                Lines.append(SingleLine)
    else:
    
        f = open(RsodFileName, "r")
        Lines = f.readlines()

    f.close()
#---    
    Index = 0
    NumberOfLines = len (Lines)
    
    # First for loop is to get past the register dump to the call stack.
    for Index in range (Index, NumberOfLines):
        Line = Lines[Index]
        # 13G RSOD style
        if "BIOS rev " in Line:  
            Index = Line.find ("BIOS rev ")
            BIOSRev = Line[Index+9:]    # +9 to skip "BIOS rev"
            print ("BIOS Version:", BIOSRev, end="")
        # 14G RSOD style
        elif "BIOS" in Line:  
            print (Line)

        # 13G TPL style
        if "(CurrentTPL" in Line:
            Index +=2
            break
    
        # 13G TPL style
        elif "LastMsg" in Line:
            Index +=2
            break

    # for each entry in the call stack call rsod_decode. Exit when we see "Stack" in the file.
    for Index in range (Index, NumberOfLines):
        Line = Lines[Index]
        if "LBR not available" in Line:
            continue
        if "Stack" in Line:
            break
        if not Line.strip():  #if blanke line,s exit
            break
 
        LbrStackInfo = Line.split()
        # LbrStackInfo[0]: "LBRxx" or "sxx" column.
        # LbrStackInfo[1]: Physical address
        # LbrStackInfo[2]: Driver Name
        # LbrStackInfo[3]: Offset within driver
        if len(LbrStackInfo) < 4:
            print ("Incomplete Info\n ", Line)
            continue
        RsodArg = BiosPathX64 + LbrStackInfo[2] + LbrStackInfo[3]
        RsodArg = RsodArg.replace("+", " ")
        RsodDecodeProcess = subprocess.Popen("Rsod_Decode.exe %s"%RsodArg, stdout=subprocess.PIPE)
        RsodDecodeOutput = RsodDecodeProcess.communicate()[0]

        print (LbrStackInfo[0], ": ", sep="", end="")
        print (LbrStackInfo[2] + LbrStackInfo[3], " ")
        print (RsodDecodeOutput.decode(), end="")
        # print out source code base on file path and line number.      
        ShowCode(RsodDecodeOutput.decode())

#        print ('\n')
        #...
#        print()

if __name__ == "__main__": main()  