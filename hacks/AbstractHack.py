from . import hexutil #doesn't propagate to modules importing this one?

class AbstractHack:
    """
    Abstract class, blah blah
    """
    
    def __init__(self):
        raise NotImplementedError( "Should have implemented this" )

    def detect( self, ROM ):
        """
        returns True if the hack is detected in the bytearray
        """
        raise NotImplementedError( "Should have implemented this" )

    def remove( self, ROM ):
        raise NotImplementedError( "Should have implemented this" )

    def apply( self, ROM ):
        raise NotImplementedError( "Should have implemented this" )

    def configure( self, ROM ):
        raise NotImplementedError( "Should have implemented this" )

    def info( self, ROM ):
        raise NotImplementedError( "Should have implemented this" )

    def toapply( self, ROM ):
        """
        returns True if the hack is configured to be applied.  False if configured to not be applied.
        """
        raise NotImplementedError( "Should have implemented this" )
