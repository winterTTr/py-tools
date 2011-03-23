# -*- encoding=utf-8 -*-

"""
Shell Extension from winterTTr
"""

__author__ = "winterTTr <winterTTr@gmail.com>"
__svnid__ = "$Id$"
__version__ = "$Revision$"[11:-2]


import os
import re
import _winreg
## com
import winerror
import pythoncom
from win32com.shell import shell, shellcon
from win32com.server.exception import COMException
## win32
import win32gui
import win32con
## XML
from xml.etree import cElementTree as et
## Process
import subprocess
## log
import logging

# global const
CWD = os.path.split( __file__ )[0]

class SHEMenu:
    def __init__( self , xmlNode ):
        # menu name
        self.name = xmlNode.find("name").text

        # match 
        ## number
        number = xmlNode.find("match/number")
        print "[==]SHEMenu::__init__ number:" , number
        print "[==]SHEMenu::__init__ number:" , number.text
        self.number =  int( number.text ) if number else 0
        print "[==]SHEMenu::__init__ number:" , self.number
        ## type
        type = xmlNode.find("match/type")
        print "[==]SHEMenu::__init__ type:" , type
        print "[==]SHEMenu::__init__ type:" , type.text
        self.type = set( type.text.split(",") if type else [ "dir" , "file" , "background" , "link" ] )
        print "[==]SHEMenu::__init__ number:" , self.type
        ## pattern
        pattern = xmlNode.find("match/pattern")
        print "[==]SHEMenu::__init__ pattern:" , pattern
        print "[==]SHEMenu::__init__ pattern:" , pattern.text if pattern else ""
        self._pattern = pattern.text if pattern else ".*"
        self.pattern = re.compile( self._pattern )
        print "[==]SHEMenu::__init__ number:" , self._pattern

        # command
        self.command = xmlNode.find("command").text


    def isValid( self , context ):
        if context.defaultOnly: return False
        if self.number != 0 and self.number != len ( context.selection ): return False
        if not self.type.issubset( context.type ): return False

        for s in context.selection:
            if not self.pattern.match( s ):
                return False
        return True


    def str( self ):
        ret = []
        ret.append( "[==] --- menu item ---" )
        ret.append( "name         :" + self.name )
        ret.append( "match/number :" + str( self.number ) )
        ret.append( "match/type   :" + str( self.type )  )
        ret.append( "match/pattern:" + self._pattern  )
        ret.append( "command      :" + self.command )
        ret.append( "[==] ------------------" )
        return "\n".join( ret )

class SHEConfig:
    def __init__( self , configFileName = None ):
        if not configFileName :
            configFileName = os.path.join( CWD , "config.xml" )
        with open( configFileName , 'r' ) as f:
            etree = et.parse( configFileName )
        self.menu = map( lambda x : SHEMenu(x) , etree.findall("menu") )

    def getValidMenu( self , context ):
        return filter( lambda x : x.isValid( context ) , self.menu )

class SHEContext:
    def __init__( self ):
        self.selection = []
        self.isBackground = False
        self.type = set()
        self.flag = 0
        self.defaultOnly = False


    def addSelection( self , selection ):
        self.selection.append( selection )
        if os.path.isdir( selection ):
            self.type.add("dir")
        elif os.path.isfile( selection ):
            ## NOTE: link will also be trade as file
            self.type.add("file")

    @property
    def flag( self ):
        return self.flag

    @flag.setter
    def flag( self, uFlags ):
        self.flag = uFlags
        if (uFlags & 0x000F) == shellcon.CMF_NORMAL: # use == here, since CMF_NORMAL=0
            print "[==]SHEContext::flag CMF_NORMAL"
        elif uFlags & shellcon.CMF_VERBSONLY:        # Short cut item
            self.type.add('link')
            print "[==]SHEContext::flag CMF_VERBSONLY"
        elif uFlags & shellcon.CMF_EXPLORE:          # in explorer
            print "[==]SHEContext::flag CMF_EXPLORE"
        elif uFlags & CMF_DEFAULTONLY:               # should do nothing
            print "[==]SHEContext::flag CMF_DEFAULTONLY"
            self.defaultOnly = True
        else:                                        # something wrong maybe
            print "[==]SHEContext::flag ** unknown flags ", uFlags



class ShellExtension:
    _register_tag_ = "PyShellExtension"

    _reg_progid_ = "Python.ShellExtension.winterTTr"
    _reg_desc_ = "Python Shell Extension from winterTTr"
    _reg_clsid_ = "{EB0D2B97-287A-4B91-A455-D2E021B894AC}"
    _com_interfaces_ = [ 
            shell.IID_IShellExtInit, 
            shell.IID_IContextMenu ]
            #shell.IID_ICopyHook ]
    _public_methods_ = \
            shellcon.IContextMenu_Methods + \
            shellcon.IShellExtInit_Methods 
            #["CopyCallBack"]


# =============== ICopyHook : from ======================
    #def CopyCallBack(self, hwnd, func, flags, srcName, srcAttr, destName, destAttr):
    #    if func == shellcon.FO_COPY:
    #        print "==[CopyCallBack] Copy Folder"
    #    elif func == shellcon.FO_DELETE:
    #        print "==[CopyCallBack] Delete Folder"
    #    elif func == shellcon.FO_MOVE:
    #        print "==[CopyCallBack] Move folder."
    #    elif func == shellcon.FO_RENAME:
    #        print "==[CopyCallBack] rename folder."
    #    #return win32gui.MessageBox(hwnd, "Allow operation?", "CopyHook", win32con.MB_YESNO)
    #    return win32con.IDYES
# =============== ICopyHook : to ======================



# =============== IShellExtInit : from  ======================

    def Initialize(self, folder, dataobj, hkey):
        self.context = SHEContext()

        if dataobj : # select file/directory 
            try:
                format_etc = win32con.CF_HDROP, None, pythoncom.DVASPECT_CONTENT , -1, pythoncom.TYMED_HGLOBAL
                sm = dataobj.GetData(format_etc)
            except pythoncom.com_error:
                raise COMException(desc='GetData Error' , scode = winerror.E_INVALIDARG)
            selection = map ( 
                    lambda x : shell.DragQueryFile( sm.data_handle , x ) , 
                    range( shell.DragQueryFile(sm.data_handle, -1) ) )
            for s in selection:
                self.context.addSelection( s )

        if folder: # select directory background
            targetDir = shell.SHGetPathFromIDList( folder )
            self.context.addSelection( targetDir )
            self.context.isBackground = True

        for f in self.context.selection:
            print "[==]ShellExtension::Initialize select file : %s" %  f

# =============== IShellExtInit : to  ======================



# =============== IContextMenu : from  ======================
    def QueryContextMenu(self, hMenu, indexMenu, idCmdFirst, idCmdLast, uFlags):
        self.context.flag = uFlags

        self.config = SHEConfig()
        for m in self.config.menu:
            print m.str()

        menu = self.config.getValidMenu( self.context )


        #self.menu_item = self.GetValidMenuItem( self.selection_list , uFlags )
        #if len( self.menu_item ) == 0:
        #    print "==[QueryContextMenu] No Menu find"
        #    return 0

        ## insert a separator
        win32gui.InsertMenu(
                hMenu, 
                indexMenu,
                win32con.MF_SEPARATOR|win32con.MF_BYPOSITION,
                0, 
                None)
        indexMenu += 1


        ## add sub menu
        #root_menu = win32gui.CreatePopupMenu()
        #win32gui.InsertMenu(
        #        hMenu, 
        #        indexMenu,
        #        win32con.MF_STRING|win32con.MF_BYPOSITION | win32con.MF_POPUP,
        #        root_menu, 
        #        u"Py&ShellExtension")
        #indexMenu += 1

        ### add items to sub menu
        #sub_index = 0 
        #idCmd = idCmdFirst
        #for item in self.menu_item:
        #    menu_name = item.find('menu').text
        #    win32gui.InsertMenu(
        #            root_menu, 
        #            sub_index,
        #            win32con.MF_STRING|win32con.MF_BYPOSITION,
        #            idCmd, 
        #            menu_name)
        #    sub_index += 1
        #    idCmd += 1

        ## add one separator
        #win32gui.InsertMenu(
        #        hMenu, 
        #        indexMenu,
        #        win32con.MF_SEPARATOR|win32con.MF_BYPOSITION,
        #        0,
        #        None)
        #indexMenu += 1

        #return idCmd-idCmdFirst # Must return number of menu items we added.
        return 1

    def InvokeCommand(self, ci):
        mask, hwnd, verb, params, dir, nShow, hotkey, hicon = ci
        #win32gui.MessageBox(hwnd, u"x", u"xx", win32con.MB_OK)
        print "[==]" , mask, hwnd, verb, params, dir, nShow, hotkey, hicon

        #cmd_exec = self.menu_item[verb].find('command/exec').text
        #
        ## make path
        #path = subprocess.list2cmdline( self.selection_list )
        #print "==[InvokeCommand] path = %s" % path
        #try:
        #    full_command_exec = cmd_exec % path 
        #except:
        #    full_command_exec = cmd_exec
        #subprocess.Popen( full_command_exec )

        

    def GetCommandString(self, cmd, typ):
        return "Windows Shell Extesion From winterTTr"

# =============== IContextMenu : to  ======================

REGISTER_PATH_LIST = [
        "*\\shellex\\ContextMenuHandlers\\",
        "directory\\shellex\\ContextMenuHandlers\\",
        "directory\\background\\shellex\\ContextMenuHandlers\\" ]

def addRegisterKeyUnderPath( aPath ):
    key = _winreg.CreateKey(
            _winreg.HKEY_CLASSES_ROOT,
            aPath + ShellExtension._register_tag_ )
    _winreg.SetValueEx( key , None, 0, _winreg.REG_SZ, ShellExtension._reg_clsid_)

def removeRegisterKeyUnderPath( aPath ):
    _winreg.DeleteKey( _winreg.HKEY_CLASSES_ROOT, aPath + ShellExtension._register_tag_)


def DllRegisterServer():
    for path in REGISTER_PATH_LIST:
        addRegisterKeyUnderPath( path )
    print ShellExtension._reg_desc_, "registration [ContextMenuHandler] complete."

    ## add CopyHookHandler
    #addRegisterKeyUnderPath( "directory\\shellex\\CopyHookHandlers\\" )
    #print ShellExtension._reg_desc_, "registration [CopyHookHandler] complete."

    # register to approve
    key = _winreg.OpenKey( _winreg.HKEY_LOCAL_MACHINE , "Software\\Microsoft\\Windows\\CurrentVersion\\Shell Extensions\\Approved"  , 0 , _winreg.KEY_ALL_ACCESS )
    _winreg.SetValueEx( key , ShellExtension._reg_clsid_ , 0 , _winreg.REG_SZ , ShellExtension._reg_progid_ )
    print ShellExtension._reg_desc_, "Add to approve list"


def DllUnregisterServer():
    # remove ContextMenuHandler
    try:
        for path in REGISTER_PATH_LIST:
            removeRegisterKeyUnderPath( path )
    except WindowsError, details:
        import errno
        if details.errno != errno.ENOENT:
            raise
    print ShellExtension._reg_desc_, "unregistration [ContextMenuHandler] complete."

    ## remove CopyHookHandler
    #try:
    #    removeRegisterKeyUnderPath( "directory\\shellex\\CopyHookHandlers\\" )
    #except WindowsError, details:
    #    import errno
    #    if details.errno != errno.ENOENT:
    #        raise
    #print ShellExtension._reg_desc_, "unregistration [CopyHookHandler] complete."

    # remove from approve list
    try:
        key = _winreg.OpenKey( _winreg.HKEY_LOCAL_MACHINE , "Software\\Microsoft\\Windows\\CurrentVersion\\Shell Extensions\\Approved" , 0 , _winreg.KEY_ALL_ACCESS)
        _winreg.DeleteValue( key , ShellExtension._reg_clsid_ )
    except WindowsError, details:
        import errno
        if details.errno != errno.ENOENT:
            raise
    print ShellExtension._reg_desc_, "Remove Approve list complete."


if __name__=='__main__':
    from win32com.server import register
    register.UseCommandLine(ShellExtension , 
                   finalize_register = DllRegisterServer,
                   finalize_unregister = DllUnregisterServer)
