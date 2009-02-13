# -*- encoding=utf-8 -*-

"""
Use basic python funcions to build the sync script for myself ,
as well as practicing python tech :-)

Use to sync the files and folders between two directory.
"""

__author__ = "winterTTr <winterTTr@gmail.com>"
__svnid__ = "$Id$"
__version__ = "$Revision$"[11:-2]


import sys
import os
import stat

PY_SYNC_SAME_DIR  = 0
PY_SYNC_SAME_FILE = 1
PY_SYNC_L_FILE    = 2
PY_SYNC_R_FILE    = 3

def checkStatus( path_l , path_r ):
    status_l = os.stat( path_l )
    status_r = os.stat( path_r )


def diffFolderEx( fp_l , fp_r ):
    list_l = os.listdir( fp_l )
    list_r = os.listdir( fp_r )
    for x in list_l :
        if x in list_r:
            

def main():
    diffFolderEx( sys.argv[1] , sys.argv[2] )


if __name__ == "__main__":
    main()
