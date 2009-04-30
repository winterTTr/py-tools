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
import winerror
from win32com.server.exception import COMException

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

    def QueryContextMenu(self, hMenu, indexMenu, idCmdFirst, idCmdLast, uFlags):
        print "======================QCM ==================="
        print hMenu, indexMenu, idCmdFirst, idCmdLast, uFlags
        print "============================================="
        # Query the items clicked on
        format_etc = win32con.CF_HDROP, None, pythoncom.DVASPECT_CONTENT , -1, pythoncom.TYMED_HGLOBAL
        sm = self.dataobj.GetData(format_etc)
        num_files = shell.DragQueryFile(sm.data_handle, -1)
        if num_files > 1:
            msg = "(with %d files selected)" % num_files
        else:
            fname = shell.DragQueryFile(sm.data_handle, 0)
            msg = "(with '%s' selected)" % fname

        idCmd = idCmdFirst
        items = []
        if (uFlags & 0x000F) == shellcon.CMF_NORMAL: # Check == here, since CMF_NORMAL=0
            print "CMF_NORMAL..."
            items.append(msg)
        elif uFlags & shellcon.CMF_VERBSONLY:
            print "CMF_VERBSONLY..."
            items.append(msg + " - shortcut")
        elif uFlags & shellcon.CMF_EXPLORE:
            print "CMF_EXPLORE..."
            items.append(msg + " - normal file, right-click in Explorer")
        elif uFlags & CMF_DEFAULTONLY:
            print "CMF_DEFAULTONLY...\r\n"
        else:
            print "** unknown flags", uFlags

        ## Insert Separator
        win32gui.InsertMenu(hMenu, indexMenu,
                            win32con.MF_SEPARATOR|win32con.MF_BYPOSITION,
                            0, None)
        indexMenu += 1


        # add for test
        root_menu = win32gui.CreatePopupMenu()
        win32gui.InsertMenu(hMenu, indexMenu,
                win32con.MF_STRING|win32con.MF_BYPOSITION | win32con.MF_POPUP,
                root_menu, "ROOT MENU")
        indexMenu += 1

        sub_index = 0 
        for item in items:
            win32gui.InsertMenu(root_menu, sub_index,
                                win32con.MF_STRING|win32con.MF_BYPOSITION,
                                idCmd, item)
            sub_index += 1
            idCmd += 1
        ## end ###

        #indexMenu += 1
        #for item in items:
        #    win32gui.InsertMenu(hMenu, indexMenu,
        #                        win32con.MF_STRING|win32con.MF_BYPOSITION,
        #                        idCmd, item)
        #    indexMenu += 1
        #    idCmd += 1

        win32gui.InsertMenu(hMenu, indexMenu,
                            win32con.MF_SEPARATOR|win32con.MF_BYPOSITION,
                            0, None)
        indexMenu += 1
        return idCmd-idCmdFirst # Must return number of menu items we added.

    def InvokeCommand(self, ci):
        mask, hwnd, verb, params, dir, nShow, hotkey, hicon = ci
        win32gui.MessageBox(hwnd, "Hello", "Wow", win32con.MB_OK)

    def GetCommandString(self, cmd, typ):
        return "Hello from Python!!"

def DllRegisterServer():
    import _winreg
    key = _winreg.CreateKey(_winreg.HKEY_CLASSES_ROOT,
                            "Python.File\\shellex")
    subkey = _winreg.CreateKey(key, "ContextMenuHandlers")
    subkey2 = _winreg.CreateKey(subkey, "PythonSample")
    _winreg.SetValueEx(subkey2, None, 0, _winreg.REG_SZ, ShellExtension._reg_clsid_)
    print ShellExtension._reg_desc_, "registration complete."

def DllUnregisterServer():
    import _winreg
    try:
        key = _winreg.DeleteKey(_winreg.HKEY_CLASSES_ROOT,
                                "Python.File\\shellex\\ContextMenuHandlers\\PythonSample")
    except WindowsError, details:
        import errno
        if details.errno != errno.ENOENT:
            raise
    print ShellExtension._reg_desc_, "unregistration complete."

if __name__=='__main__':
    from win32com.server import register
    register.UseCommandLine(ShellExtension , 
                   finalize_register = DllRegisterServer,
                   finalize_unregister = DllUnregisterServer)
