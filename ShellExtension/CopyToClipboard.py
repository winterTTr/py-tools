import sys
import win32clipboard
win32clipboard.OpenClipboard()
win32clipboard.EmptyClipboard()
win32clipboard.SetClipboardText( sys.argv[1] )
win32clipboard.CloseClipboard()
