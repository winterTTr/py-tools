# -*- encoding=utf-8 -*-

"""
Shell Extension from winterTTr
"""

__author__ = "winterTTr <winterTTr@gmail.com>"
__svnid__ = "$Id$"
__version__ = "$Revision$"[11:-2]


import pythoncom
from win32com.shell import shell, shellcon
import win32gui
import win32con
import os
#import winerror
#from win32com.server.exception import COMException

class ShellExtension:
    _reg_progid_ = "Python.ShellExtension.winterTTr"
    _reg_desc_ = "Python extension from winterTTr"
    _reg_clsid_ = "{EB0D2B97-287A-4B91-A455-D2E021B894AC}"
    _com_interfaces_ = [ 
            shell.IID_IShellExtInit, 
            shell.IID_IContextMenu ]
            #"{0000010b-0000-0000-C000-000000000046}",
            #"{00021500-0000-0000-C000-000000000046}"]
    #_public_methods_ = shellcon.IContextMenu_Methods + shellcon.IShellExtInit_Methods + ['IsDirty','Save','Load','SaveCompleted','GetCurFile','GetInfoFlags','GetInfoTip']
    _public_methods_ = shellcon.IContextMenu_Methods + shellcon.IShellExtInit_Methods 

#    def GetInfoFlags():
#        raise COMException(desc="No Implemented",scode=winerror.E_NOTIMPL)
#
#    def GetInfoTip(dwFlags):
#        print "########################GetInfoTip##############################"
#        print dwFlags
#
#    def IsDirty():
#        raise COMException(desc="No Implemented",scode=winerror.E_NOTIMPL)
#
#    def Load(pszFileName, dwMode):
#        print "########################Load##############################"
#        print pszFileName
#
#    def Save(pszFileName, fRemember):
#        raise COMException(desc="No Implemented",scode=winerror.E_NOTIMPL)
#
#    def SaveCompleted(pszFileName):
#        raise COMException(desc="No Implemented",scode=winerror.E_NOTIMPL)
#
#    def GetCurFile():
#        raise COMException(desc="No Implemented",scode=winerror.E_NOTIMPL)

    def Initialize(self, folder, dataobj, hkey):
        print "======================Init==================="
        print folder, dataobj, hkey
        print "============================================="
        self.dataobj = dataobj
        self.selection_list = []


    def QueryContextMenu(self, hMenu, indexMenu, idCmdFirst, idCmdLast, uFlags):
        print "======================QCM ==================="
        print hMenu, indexMenu, idCmdFirst, idCmdLast, uFlags
        print "============================================="

        # save user selection
        try:
            format_etc = win32con.CF_HDROP, None, pythoncom.DVASPECT_CONTENT , -1, pythoncom.TYMED_HGLOBAL
            sm = self.dataobj.GetData(format_etc)
        except pythoncom.com_error:
            return 0

        num_files = shell.DragQueryFile(sm.data_handle, -1)
        for index in xrange(num_files):
            fname = shell.DragQueryFile( sm.data_handle , index )
            self.selection_list.append( fname )
            print fname

        if (uFlags & 0x000F) == shellcon.CMF_NORMAL: # Check == here, since CMF_NORMAL=0
            print "CMF_NORMAL..."
        elif uFlags & shellcon.CMF_VERBSONLY:        # Short cut item
            print "CMF_VERBSONLY..."
        elif uFlags & shellcon.CMF_EXPLORE:          # in explorer
            print "CMF_EXPLORE..."
        elif uFlags & CMF_DEFAULTONLY:               # should do nothing
            print "CMF_DEFAULTONLY...\r\n"
            return 0
        else:                                        # something wrong maybe
            print "** unknown flags", uFlags

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
        #        u"看！我偷偷加了一个菜单")
        #indexMenu += 1

        # add items to sub menu
        #sub_index = 0 
        #idCmd = idCmdFirst
        #for item in self.selection_list:
        #    win32gui.InsertMenu(
        #            root_menu, 
        #            sub_index,
        #            win32con.MF_STRING|win32con.MF_BYPOSITION,
        #            idCmd, 
        #            item)
        #    sub_index += 1
        #    idCmd += 1

        if len(self.selection_list) == 1 :
            path , filename = os.path.split( self.selection_list[0] )
            if filename.startswith(u"爱我么".encode('cp936')):
                win32gui.InsertMenu(
                        hMenu, 
                        indexMenu,
                        win32con.MF_STRING|win32con.MF_BYPOSITION ,
                        idCmdFirst, 
                        u"==看！我偷偷加了一个菜单==")
                indexMenu += 1


        # add one separator
        win32gui.InsertMenu(
                hMenu, 
                indexMenu,
                win32con.MF_SEPARATOR|win32con.MF_BYPOSITION,
                0,
                None)
        indexMenu += 1

        #return idCmd-idCmdFirst # Must return number of menu items we added.
        return 1

    def InvokeCommand(self, ci):
        mask, hwnd, verb, params, dir, nShow, hotkey, hicon = ci
        win32gui.MessageBox(hwnd, u"这还用问，当然爱悦悦啦，么么么", u"啦啦啦", win32con.MB_OK)

    def GetCommandString(self, cmd, typ):
        return "Windows Shell Extesion From winterTTr"

def DllRegisterServer():
    import _winreg

    # add to all file
    key = _winreg.CreateKey(
            _winreg.HKEY_CLASSES_ROOT,
            "*\\shellex")
    subkey = _winreg.CreateKey(key, "ContextMenuHandlers")
    subkey2 = _winreg.CreateKey(subkey, "PyShellExtension")
    _winreg.SetValueEx(subkey2, None, 0, _winreg.REG_SZ, ShellExtension._reg_clsid_)
    print ShellExtension._reg_desc_, "registration [file] complete."

    # add to all folder
    key = _winreg.CreateKey(
            _winreg.HKEY_CLASSES_ROOT,
            "Folder\\shellex")
    subkey = _winreg.CreateKey(key, "ContextMenuHandlers")
    subkey2 = _winreg.CreateKey(subkey, "PyShellExtension")
    _winreg.SetValueEx(subkey2, None, 0, _winreg.REG_SZ, ShellExtension._reg_clsid_)
    print ShellExtension._reg_desc_, "registration [folder] complete."

def DllUnregisterServer():
    import _winreg

    # remove the all file
    try:
        key = _winreg.DeleteKey(
                _winreg.HKEY_CLASSES_ROOT,
                "*\\shellex\\ContextMenuHandlers\\PythonSample")
    except WindowsError, details:
        import errno
        if details.errno != errno.ENOENT:
            raise
    print ShellExtension._reg_desc_, "unregistration [file] complete."

    # remove the all folder
    try:
        key = _winreg.DeleteKey(
                _winreg.HKEY_CLASSES_ROOT,
                "Folder\\shellex\\ContextMenuHandlers\\PythonSample")
    except WindowsError, details:
        import errno
        if details.errno != errno.ENOENT:
            raise
    print ShellExtension._reg_desc_, "unregistration [Folder] complete."

if __name__=='__main__':
    from win32com.server import register
    register.UseCommandLine(ShellExtension , 
                   finalize_register = DllRegisterServer,
                   finalize_unregister = DllUnregisterServer)
