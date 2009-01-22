# -*- encoding=utf-8 -*-

__author__ = "winterTTr <winterTTr@gmail.com>"
__svnid__ = "$Id$"
__version__ = "$Revision$"[11:-2]


from optparse import OptionParser , make_option
import os , re , subprocess , sys

# command information
usage_string = "\t%prog -f filename -d directory --action=ACTION cmd\n\tUse -h option for more info."
cmd_option_list = [
        make_option( 
            "-d" , 
            "--directory" ,
            action = "store" , 
            type = "string" , 
            dest = "directory" , 
            help = 'the directory under where the command find the files , the default value is the current diretory' ) , 
        make_option( 
            "-f" ,
            "--filename" , 
            action = "store",
            type = "string" ,
            dest = "filename" ,
            help = 'the file name to find'),
        make_option(
            "--action",
            action = "store",
            choices = ["print" , "cmd" ],
            dest = "action" , 
            help = "The action do on the found files. You can choose the value from \"print\" , \"cmd\". The default value is \"print\". ")
        ]
default_dir = os.path.join( os.path.curdir , os.path.sep )


def do_shell_cmd( shell_cmd , filepath ):
    #print shell_cmd % filepath
    subp = subprocess.Popen( 
            shell_cmd % filepath , 
            stdin = subprocess.PIPE ,
            #stderr = subprocess.PIPE , 
            #stdout = subprocess.PIPE , 
            stderr = sys.stderr , 
            stdout = sys.stdout ,
            shell = True)
    subp.stdin.close()
    ret = subp.wait()
    

def default_action( filepath ):
    print filepath

def do_find( filename , dir , action_to_file ):
    # no action , no need to do find
    if action_to_file == None:
        return 

    cmd_flag = callable( action_to_file )

    match_re_obj = re.compile( filename )
    for ( rootdir , subdirs , files ) in os.walk( dir ):
        for each_file in files:
            if match_re_obj.search( each_file ):
                if cmd_flag :
                    action_to_file( os.path.join( rootdir , each_file ) )
                else:
                    do_shell_cmd( action_to_file , os.path.join( rootdir , each_file ) )

# main process
def main():

    # parse the cmd option
    opt_par = OptionParser( 
            option_list = cmd_option_list , 
            usage = usage_string)
    opt_par.set_defaults( directory = default_dir , action = "print" )
    (options , args) = opt_par.parse_args()

    if options.filename == None:
        opt_par.error( "You must give the file name to find at lease.")
    elif options.action == "cmd" :
        if len(args) != 1 :
            opt_par.error( "You must give the shell command if you use the action type \"cmd\" , and you just can give one command.")
        elif args[0].find("%s") == -1:
            opt_par.error( "You give the invalid cmd. Use %s to substitute the file name.")


    # find the file
    if options.action == "cmd":
        do_find( filename = options.filename , dir = options.directory , action_to_file = args[0] )
    else:
        do_find( filename = options.filename , dir = options.directory , action_to_file = default_action )




if __name__ == "__main__":
    main()
