# -*- encoding=utf-8 -*-

__version__ = "$Revision$"[11:-2]
__author__ = "winterTTr<winterTTr@gmail.com"

import vim
import re
import string

# IDE {{{1
def SetBreakpoint(): # {{{2

    nLine = int( vim.eval( 'line(".")'))

    strLine = vim.current.line
    strWhite = re.search( '^(\s*)', strLine).group(1)

    vim.current.buffer.append(
            "%(space)spdb.set_trace() %(mark)s Breakpoint %(mark)s" %
            {'space':strWhite, 'mark': '#' * 30}, nLine - 1)

    for strLine in vim.current.buffer:
        if strLine == "import pdb":
            break
    else:
        vim.current.buffer.append( 'import pdb', 0)
        vim.command( 'normal j1')
# }}}2
vim.command( 'nmap <f7> :py SetBreakpoint()<cr>')

def RemoveBreakpoints(): # {{{2

    nCurrentLine = int( vim.eval( 'line(".")'))

    nLines = []
    nLine = 1
    for strLine in vim.current.buffer:
        if strLine == 'import pdb' or strLine.lstrip()[:15] == 'pdb.set_trace()':
            nLines.append( nLine)
        nLine += 1

    nLines.reverse()

    for nLine in nLines:
        vim.command( 'normal %dG' % nLine)
        vim.command( 'normal dd')
        if nLine < nCurrentLine:
            nCurrentLine -= 1

    vim.command( 'normal %dG' % nCurrentLine)
# }}}2
vim.command( 'nmap <s-f7> :py RemoveBreakpoints()<cr>')

def RunDebugger(): # {{{2
    vim.command( 'wall')
    strFile = vim.eval( 'expand(\'%:p\')')
    vim.command( "!start python -m pdb %s" % strFile)
# }}}2
vim.command( 'nmap <s-f12> :py RunDebugger()<cr>')

def RunCurrentFile(): # {{{2
    vim.command( 'wall' )
    strFile = vim.eval( 'expand(\'%:p\')')
    vim.command( "!start python %s" % strFile)
# }}}2
vim.command( 'nmap <F5> :py RunCurrentFile()<CR>')
# }}}1

# Auto complete {{{1

def getAttributesByName(ModulePath, partName): #{{{2
    if not needToStartMaigc():
        return ""

    if len(ModulePath) == 0 :
        return ""

    # split the ModulePath to ModuleName and MemberPath , ex : os.path
    # ==> 'os' & '.path'
    findResult = re.match('(\w+)(.*)',ModulePath)
    ModuleName = findResult.group(1)
    MemberPath = findResult.group(2)

    # import Module as objModule
    try:
        objModule = __import__(ModuleName)
        strMemeberList = eval('dir(objModule' + MemberPath + ')')
    except:
        return ""

    # Construct the reObj as Search pattern
    reObj = re.compile('<.*\'(.*)\'>')
    reIfMatch = re.compile( '^' + partName )

    # Make the result
    MemberList = []
    for MemberName in strMemeberList:
        TypeStr = eval( 'type(objModule ' + MemberPath + '.' + MemberName + ')' )
        if len(partName) == 0 or ( len(partName) != 0 and reIfMatch.match( MemberName ) ):
            MemberList.append( MemberName + '!' + reObj.match(str(TypeStr)).group(1) )

    return string.join(MemberList,',')
#}}}2


vim_cmd_dict = {}
vim_cmd_dict['closeShowMode'] = 'setlocal noshowmode'
vim_cmd_dict['echoWarning_f'] = 'echohl WarningMsg | echomsg "%s" | echohl None'

def needToStartMaigc(): # {{{2
    """
    check if the punctuation is invalid.

    [True] means the punctuation is 
           not in [doc area] && not in [str object]
           and need to do "magic" action if need

    [False] means not need to do "magic" action
    """

    # get current line and line number
    curLine = vim.current.line
    curLineNo , curRowNo = vim.current.window.cursor

    # check if it is a empty line
    stripLine = curLine.strip()
    if len(stripLine) == 0:
        return None

    # Check if it is in line begin with[#]
    if stripLine[0] == '#':
        return False


    # Check if it is in the doc area
    threeNo = 0 
    for i in xrange(curLineNo - 1):
        threeNo += vim.current.buffer[i].count('"""')
    threeNo += vim.current.buffer[curLineNo - 1][:curRowNo+1].count('"""')

    if threeNo % 2 == 1 :
        return False

    # Check if it is in the [str object]
    frontLine = curLine[:curRowNo]
    single = frontLine.count('\'')
    invalidSingle = frontLine.count('\\\'')
    double =  frontLine.count('"')
    invalidDouble = frontLine.count('\\"')

    if ( single - invalidSingle ) % 2 == 1 or ( double - invalidDouble )%2 == 1 :
        return False

    return True
# }}}2

# }}}1
