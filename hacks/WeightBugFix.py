import inspect

#guh i don't get python imports yet :/
from . import AbstractHack
from . import hexutil
from . import util

class WeightBugFix(AbstractHack.AbstractHack):
    """
    
    """
    
    name = "Weight Bug Fix"
    
    def __init__(self):
        #AbstractHack.__init__(self) # call superclass init... not for ABC's of course!
        #print(self.__class__.__name__ + "." + inspect.stack()[0][3])
        self.isDetected = False
        self.toApply = False

    def detect( self, ROM ):
        """
        sets self.isDetected to True if the hack is detected in the bytearray
        returns True if the hack is detected in the bytearray
        """
        #print(self.__class__.__name__ + "." + inspect.stack()[0][3])
        
        if hexutil.matchHex("4eb9", ROM, 0x00013D72):
            self.isDetected = True
            #print("weight bug fix found")
        return True

    def configure( self ):
        #print(self.__class__.__name__ + "." + inspect.stack()[0][3])
        print("\n  Weight Bug Fix:" 
            "\n\n     Do you want to include the weight bug fix?"
            "\n     The original game has a bug that makes light players good at checking and"
            "\n     heavy players easy to knock over.  This hack reverses this and also"
            "\n     includes the players' checking rating when deciding if a check succeeds.\n")
        tmp = util.inputString("     Enter 'y' or 'n':  ", ['y', 'n'])
        if tmp == 'y':
            self.toApply = True
        else: 
            self.toApply = False

    def toDo( self ):
        #print(self.__class__.__name__ + "." + inspect.stack()[0][3])
        if self.isDetected:
            if self.toApply:
                print("LEAVE  - ", end='')
            else:
                print("REMOVE - ", end='')
        else:
            if self.toApply:
                print("ADD    - ", end='')
            else:
                print("OMIT   - ", end='')
        print (WeightBugFix.name)


    def info( self ):
        #print(self.__class__.__name__ + "." + inspect.stack()[0][3])
        return ("     Weight Bug Fix:"
                "\n\n     The original game has a bug that makes light players good at checking and"
                "\n     heavy players easy to knock over.  This hack reverses this and also"
                "\n     includes the players' checking rating when deciding if a check succeeds.")


    def remove( self, ROM ):
        #print(self.__class__.__name__ + "." + inspect.stack()[0][3])
        if self.isDetected:
            hexutil.overwriteHex("90 2b 00 67 d0 2a 00 67", ROM, 0x00013D72)
            where = hexutil.findHex("3F01902A0067122B0067E201D001E201D001122b0075e301d001", ROM) #not whole hack string!
            if where > -1: 
                hexutil.overwriteHex("ff" * len(bytearray.fromhex("3F01902A0067122B0067E201D001E201D001122b0075e301d0010400000e321f4e75")), ROM, where)

    def apply( self, ROM ):
        #print(self.__class__.__name__ + "." + inspect.stack()[0][3])
        if self.toApply:
            wherespace = 4 + hexutil.findEmptyRomSpace(ROM) # +4 to leave some "empty" space in front of  each hack, so it's easier to see them individually.
            where = hexutil.overwriteHex("4e b9", ROM, 0x00013D72) # JSR
            where = hexutil.overwriteHex(hexutil.numToByteArray(wherespace,32), ROM, where)
            hexutil.overwriteHex("4e 71", ROM, where)
            hexutil.overwriteHex("3F01902A0067122B0067E201D001E201D001122b0075e301d0010400000e321f4e75", ROM, wherespace) # added code


