"""
-*- encoding=utf-8 -*-

Author :  winterTTr <winterTTr@gmail.com>
Desc   :  The 'export' command on win32 platform
Name   :  win32export.py
NOTE   :  Make sure the pywin32 has been installed.
Licence:  MIT License

"""

try :
    import win32gui
    import win32con
    import win32api
except ImportError:
    raise ImportError , "You Should install pywin32 if you want to use win32export"

__author__ = "winterTTr <winterTTr@gmail.com>"
__svnid__ = "$Id$"
__version__ = "$Revision$"[11:-2]


def export ( name , value , update_system = True ):
    """
    Export 'name' with 'value' to system .
    You can let update_system=False , if you don't want to make the
    change avaliable at once .( updateSystem is a time-consuming action.)
    """
    try :
        modifyVariableInRegister( name , value )
    except:
        return False

    if update_system :
        updateSystem()

    return True

def modifyVariableInRegister( name , value ):
    """
    Add ( or modify ) the 'name' with 'value' to the register.
    Register Postion : HKEY_CURRENT_USER/Environment
    """
    key = win32api.RegOpenKey( win32con.HKEY_CURRENT_USER,"Environment",0,win32con.KEY_ALL_ACCESS)
    if not key : raise
    win32api.RegSetValueEx( key , name , 0 , win32con.REG_SZ , value )
    win32api.RegCloseKey( key )

def updateSystem():
    """
    Call SendMessageTimeout to send broadcast to all window , notice
    that the system setting is changed 
    """
    rc,dwReturnValue = win32gui.SendMessageTimeout( win32con.HWND_BROADCAST , win32con.WM_SETTINGCHANGE , 0 , "Environment" , win32con.SMTO_ABORTIFHUNG, 5000)

