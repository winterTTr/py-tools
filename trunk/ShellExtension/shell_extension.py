# -*- encoding=utf-8 -*-

"""
Shell Extension from winterTTr
"""

__author__ = "winterTTr <winterTTr@gmail.com>"
__svnid__ = "$Id$"
__version__ = "$Revision$"[11:-2]


import os
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
from xml.etree import cElementTree as ET
## Process
import subprocess
from pywintypes import IID
## log
import logging

# global const
CWD = os.path.split( __file__ )[0]

class ShellExtension:
    _register_tag_ = "PyShellExtension"

    _reg_progid_ = "Python.ShellExtension.winterTTr"
    _reg_desc_ = "Python Shell Extension from winterTTr"
    _reg_clsid_ = "{EB0D2B97-287A-4B91-A455-D2E021B894AC}"
    _com_interfaces_ = [ 
            shell.IID_IShellExtInit, 
            shell.IID_IContextMenu ,
            shell.IID_ICopyHook ]
    _public_methods_ = \
            shellcon.IContextMenu_Methods + \
            shellcon.IShellExtInit_Methods + \
            ["CopyCallBack"]


# =============== ICopyHook : from ======================
    def CopyCallBack(self, hwnd, func, flags, srcName, srcAttr, destName, destAttr):
        if func == shellcon.FO_COPY:
            print "==[CopyCallBack] Copy Folder"
        elif func == shellcon.FO_DELETE:
            print "==[CopyCallBack] Delete Folder"
        elif func == shellcon.FO_MOVE:
            print "==[CopyCallBack] Move folder."
        elif func == shellcon.FO_RENAME:
            print "==[CopyCallBack] rename folder."
        #return win32gui.MessageBox(hwnd, "Allow operation?", "CopyHook", win32con.MB_YESNO)
        return win32con.IDYES
# =============== ICopyHook : to ======================



# =============== IShellExtInit : from  ======================

    def Initialize(self, folder, dataobj, hkey):
        self.selectionList = []
        if dataobj : # select file/directory 
            try:
                format_etc = win32con.CF_HDROP, None, pythoncom.DVASPECT_CONTENT , -1, pythoncom.TYMED_HGLOBAL
                sm = dataobj.GetData(format_etc)
            except pythoncom.com_error:
                raise COMException(desc='GetData Error' , scode = winerror.E_INVALIDARG)
            self.selectionList = map ( 
                    lambda x : shell.DragQueryFile( sm.data_handle , x ) , 
                    range( shell.DragQueryFile(sm.data_handle, -1) ) )

        if folder: # select background
            targetDir = shell.SHGetPathFromIDList( folder )
            self.selectionList.append( targetDir )

        for f in self.selectionList:
            print "ShellExtension::Initialize] select file : %s" %  f

# =============== IShellExtInit : to  ======================



# =============== IContextMenu : from  ======================

    def GetValidMenuItem( self , name_list , uFlags):
        
        # make target type
        self.condition_dict['num']= len( name_list )
        self.condition_dict['type']= []
        
        if (uFlags & 0x000F) == shellcon.CMF_NORMAL: # use == here, since CMF_NORMAL=0
            print "==[GetValidMenuItem] CMF_NORMAL..."
        elif uFlags & shellcon.CMF_VERBSONLY:        # Short cut item
            self.condition_dict['type'].append('link')
            print "==[GetValidMenuItem] CMF_VERBSONLY..."
        elif uFlags & shellcon.CMF_EXPLORE:          # in explorer
            print "==[GetValidMenuItem] CMF_EXPLORE..."
        elif uFlags & CMF_DEFAULTONLY:               # should do nothing
            print "==[GetValidMenuItem] CMF_DEFAULTONLY..."
            return []
        else:                                        # something wrong maybe
            print "==[GetValidMenuItem] ** unknown flags", uFlags
            return []


        if len( self.condition_dict['type'] ) == 0:
            tag_file = False
            tag_dir = False
            for x in name_list :
                if os.path.isdir( x ):
                    tag_dir = True
                else:
                    tag_file = True

                if tag_file and tag_dir:
                    break

            if tag_file:
                self.condition_dict['type'].append('file')
            if tag_dir:
                self.condition_dict['type'].append('dir')


            print "==[GetValidMenuItem] No Link , type" , self.condition_dict['type']

        # get valid item
        config_file_path = os.path.join( os.path.split( __file__ )[0] , 'config.xml' )
        print "==[GetValidMenuItem] %s" % config_file_path
        return filter( self.CheckItem , ET.ElementTree( file= config_file_path ).findall('item') )

    def CheckItem( self , item ):
        target_conf = item.find('target')
        tc_num = int( target_conf.find('num').text )
        tc_type = target_conf.find('type').text.split(',')

        print "==[CheckItem] : tc_num " , tc_num , "| tc_type :" , tc_type

        # check num
        if tc_num != -1 and ( self.condition_dict['num'] != tc_num ):
            return False

        # check type
        for x in self.condition_dict['type']:
            if not ( x in tc_type ):
                return False

        return True
        
    def QueryContextMenu(self, hMenu, indexMenu, idCmdFirst, idCmdLast, uFlags):
        #print "======================QCM ==================="
        #print hMenu, indexMenu, idCmdFirst, idCmdLast, uFlags
        #print "============================================="


        #self.menu_item = self.GetValidMenuItem( self.selection_list , uFlags )
        #if len( self.menu_item ) == 0:
        #    print "==[QueryContextMenu] No Menu find"
        #    return 0

        ### insert a separator
        #win32gui.InsertMenu(
        #        hMenu, 
        #        indexMenu,
        #        win32con.MF_SEPARATOR|win32con.MF_BYPOSITION,
        #        0, 
        #        None)
        #indexMenu += 1


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
        return 0

    def InvokeCommand(self, ci):
        mask, hwnd, verb, params, dir, nShow, hotkey, hicon = ci
        #win32gui.MessageBox(hwnd, u"x", u"xx", win32con.MB_OK)

        cmd_exec = self.menu_item[verb].find('command/exec').text
        
        # make path
        path = subprocess.list2cmdline( self.selection_list )
        print "==[InvokeCommand] path = %s" % path
        try:
            full_command_exec = cmd_exec % path 
        except:
            full_command_exec = cmd_exec
        subprocess.Popen( full_command_exec )

        

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

    # add CopyHookHandler
    addRegisterKeyUnderPath( "directory\\shellex\\CopyHookHandlers\\" )
    print ShellExtension._reg_desc_, "registration [CopyHookHandler] complete."

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

    # remove CopyHookHandler
    try:
        removeRegisterKeyUnderPath( "directory\\shellex\\CopyHookHandlers\\" )
    except WindowsError, details:
        import errno
        if details.errno != errno.ENOENT:
            raise
    print ShellExtension._reg_desc_, "unregistration [CopyHookHandler] complete."

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
