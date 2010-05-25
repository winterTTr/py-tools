import pdb
import cmd
import socket
import sys


DEFAULT_IP_ADDR = 'localhost'
DEFAULT_PORT    = 30001
DEFAULT_TIMEOUT = 0.1


class SocketFileObject(object):
    def __init__( self  , ip , port , is_server = True ):
        self.is_server = is_server
        if is_server:
            self.server_socket = socket.socket( socket.AF_INET , socket.SOCK_STREAM )
            self.server_socket.bind( (ip , port) )
            self.server_socket.listen(1)
            self.conn , self.addr = self.server_socket.accept()
        else:
            self.conn = socket.socket( socket.AF_INET , socket.SOCK_STREAM )
            self.conn.connect( ( ip , port ) )

        self.conn.settimeout( DEFAULT_TIMEOUT )

    def __del__( self ):
        self.conn.close()
        if self.is_server:
            self.server_socket.close()


    def close( self ):
        self.conn.close()

    def readline( self ):
        self.conn.settimeout( None )
        str =  self.conn.recv( 1024 )
        self.conn.settimeout( DEFAULT_TIMEOUT )
        return str

    def readall( self ):
        all_data = []
        while True:
            try:
                data = self.conn.recv( 1024 )
                all_data.append( data )
            except:
                break
        return ''.join( all_data )

    def write( self , str ):
        self.conn.sendall( str )

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
