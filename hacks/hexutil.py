
#print("hexutil!")

#ehh not really the right place for this since it's not a generic bytes operation
#not to mention this is about bytes more than hex and everything is named hex...
def findEmptyRomSpace(hexByteArray):
    """
    return the location where the empty "FFFF..." block at the end of the ROM starts
    """
    oldwhere = -1
    where = hexByteArray.find(b'\xff', len(hexByteArray) - 1)
    #print(where)
    while where != oldwhere:
        oldwhere = where
        where = hexByteArray.find(b'\xff', where - 1)
    return where



def findHex(hexString, hexByteArray):
    fix = bytearray.fromhex(hexString) #hex2bytes(hexString)
    #print ("\nFind this: " + str(fix))
    where = hexByteArray.find(fix)
    #print ("\nResult: " + hex(where))
    return where

    
def matchHex(hexString, hexByteArray, where):
    """
    Returns true if the passed in hexString matches the hexByteArray at where
    """
    hexString = bytearray.fromhex(hexString)
    #print(hexString)
    #print(hexByteArray[where:where+len(hexString)])
    return hexString == hexByteArray[where:where+len(hexString)]

def getNumValue(hexByteArray, where, size):
    # big endian (motorola)
    # TODO: allow little endian
    ret = 0
    hexByteArray = hexByteArray[where:where+size]
    #print(hexByteArray)
    for s in range(size):
        ret += ord(hexByteArray[s:s+1]) << (8 * (size-s-1))
    return ret

def numToByteArray(number, bits = 0, endian = 'big'):
    """
    takes number and converts it to a bytearray.  
    if bits!=0, pad with 00 to correct number of bits (valid numbers are multiples of 8)
    TODO: if bits!=0 and bits < bits to represent number, the value will be truncated
    """
    #don't change number!!
    numbertemp = number
    # build bytearray in little-endian format
    retval = bytearray(0)
    retval.append(numbertemp % 256)
    while numbertemp//256 != 0:
        numbertemp = numbertemp // 256
        retval.append(numbertemp % 256)

    # need to zero-pad?
    if (bits > 0):
        for i in range((bits//8) - len(retval)):
            retval.append(0x00)
        
    if endian == 'big':
        # reverse the bytearray
        for i in range(len(retval)//2):
            temp           = retval[i]
            retval[i]      = retval[-(i+1)]
            retval[-(i+1)] = temp
    return retval

def overwriteHex(hexString, hexByteArray, where):
    """
    modifies 'hexByteArray', overwriting 'hexString' into it at 'where'
    returns offset where it stopped writing to
    raises an exception if would write past end of hexByteArray
    """
    if type(hexString).__name__ == "str":
        hexStringBytes = bytearray.fromhex(hexString)
    else:
        hexStringBytes = hexString
    #print("where: " + str(where) + ", len(hexStringBytes): " + str(len(hexStringBytes)) + ", len(hexByteArray): " +  str(len(hexByteArray)))
    # don't write past end of hexByteArray
    if where+len(hexStringBytes) > len(hexByteArray):
        raise Exception('Tried to write data beyond end of ROM.  Kaboom!')
    for i in range(len(hexStringBytes)):
        hexByteArray[where + i] = hexStringBytes[i]
    #print("wrote", hexString, "\nto", where, "\nreturned", where + len(hexStringBytes),'\n')
    return where + len(hexStringBytes)
    
    #hexByteArray = hexByteArray[:where] + hexStringBytes + hexByteArray[where+len(hexStringBytes):]

    
def saveHex(hexByteArray, inputfilename):
    done = False
    while not done:
        print("\nYour input file was: \n    " + inputfilename)
        
        whereSlash = inputfilename.rfind('\\') + 1 #whereSlash points to after the slash, or is 0 if no slash present
        outfiledir = inputfilename[:whereSlash]
        outfilename = ""
        while outfilename == "":
            print("\nEnter output file name: \n    " + outfiledir, end='')
            outfilename = input("").strip()
        #debug(outfilename)
        if outfilename[-4:] != ".bin":
            outfilename += ".bin"
        #debug(outfilename)
        #debug ("save file")
        
        try:
            outfile = open(outfiledir + outfilename, 'wb')
            written = outfile.write(hexByteArray)
            closed = outfile.close()
        except IOError as err:
            print("\nThere was an error writing the file!")
            print("I/O error: {0}".format(err))
        except Exception as inst:
            print(type(inst))    # the exception instance
            print(inst.args)     # arguments stored in .args
        else:
            print("\nSaved file: \n    " + outfiledir + outfilename)
            print("\nDone!")
            done = True
        