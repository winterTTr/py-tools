import pdb
import cmd
import socket
import sys


DEFAULT_IP_ADDR = 'localhost'
DEFAULT_PORT    = 30001
DEFAULT_TIMEOUT = 0.1


class SocketFileObject(object):
    __socket_server_singleton__  = None
    __client_connection_singleton__ = None
    def __init__( self  , ip , port , is_server = True ):
        self.is_server = is_server
        if is_server :
            if SocketFileObject.__socket_server_singleton__ == None :
                SocketFileObject.__socket_server_singleton__ = socket.socket( socket.AF_INET , socket.SOCK_STREAM )
                SocketFileObject.__socket_server_singleton__.bind( (ip , port) )
                SocketFileObject.__socket_server_singleton__.listen(1)
                SocketFileObject.__client_connection_singleton__ , addr = SocketFileObject.__socket_server_singleton__.accept()
        else:
            SocketFileObject.__client_connection_singleton__ = socket.socket( socket.AF_INET , socket.SOCK_STREAM )
            SocketFileObject.__client_connection_singleton__.connect( ( ip , port ) )

        SocketFileObject.__client_connection_singleton__.settimeout( DEFAULT_TIMEOUT )

    def close( self ):
        pass
        #SocketFileObject.__client_connection_singleton__.close()

    def readline( self ):
        SocketFileObject.__client_connection_singleton__.settimeout( None )
        str =  SocketFileObject.__client_connection_singleton__.recv( 1024 )
        SocketFileObject.__client_connection_singleton__.settimeout( DEFAULT_TIMEOUT )
        return str

    def readall( self ):
        all_data = []
        while True:
            try:
                data = SocketFileObject.__client_connection_singleton__.recv( 1024 )
                all_data.append( data )
            except:
                break
        return ''.join( all_data )

    def write( self , str ):
        SocketFileObject.__client_connection_singleton__.sendall( str )

    def flush( self ):
        pass


class SocketPdbServer( pdb.Pdb ):
    def __init__( self , ip = DEFAULT_IP_ADDR , port = DEFAULT_PORT ):
        self.sfo = SocketFileObject( ip , port , True )
        pdb.Pdb.__init__( self , stdin = self.sfo , stdout = self.sfo )
        self.use_rawinput = False 


class SocketPdbClient( cmd.Cmd ):
    def __init__( self , ip = DEFAULT_IP_ADDR , port = DEFAULT_PORT ):
        self.sfo = SocketFileObject( ip , port , False )
        cmd.Cmd.__init__( self , stdout = self.sfo )
        self.prompt = ''
        sys.stdout.write( self.sfo.readall() )

    def onecmd( self , line ):
        self.sfo.write( line + '\n' )
        if line == 'q' :
            self.sfo.close()
            return True
        sys.stdout.write( self.sfo.readall() )


def set_trace():
    SocketPdbServer().set_trace( sys._getframe().f_back )

def catch_trace():
    SocketPdbClient().cmdloop()
