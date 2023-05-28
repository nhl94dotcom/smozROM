#
#  Copyright 2010 Michael Capewell (smozoma)
#  Report bugs here:  http://forum.nhl94.com/index.php?showtopic=12074
#
#  This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

#-----------------------------
# TODO
"""
Needs refactoring (or .. any factoring)
A much nicer way to do this would be to pack up each hack into a class with 
detect(), remove(), apply(), question/configure(), info(), toapply() methods.
Buuuut some other time (plus some hacks have interdependencies, so it's a non-
trivial fix.. i know.. i tried! and this is all going to end up rewritten in 
the EARE editor, anyway!)
"""
#-----------------------------

from hexutil import *
import os
import sys

DEBUG = False

def debug(str):
    if DEBUG: print(str)

def printHeader():
    print("\n  SmozROM Hack Applier v1.0.2 - smozoma 2023-05\n")

def clearScreen(): 
    if os.name == 'nt':
        os.system('CLS')
    else:
        os.system('clear')

def wait_key():
    ''' Wait for a key press on the console and return it. '''
    result = None
    if os.name == 'nt':
        import msvcrt
        result = msvcrt.getch()
    else:
        import termios
        fd = sys.stdin.fileno()

        oldterm = termios.tcgetattr(fd)
        newattr = termios.tcgetattr(fd)
        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, newattr)

        try:
            result = sys.stdin.read(1)
        except IOError:
            pass
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)

    return result

def isNhl94Rom(romByteArray):
    #these bytes should be at the start of the file
    if  0 != findHex("00FF FFF6 0000 0200 0001 8BFC 0001 8BFC 0001 8C22 0001 8C4C", romByteArray):
        return False
    else: 
        return True

    
def removeChecksum(romByteArray):
    """
    does what NOSE does
    """
    checksumCode = "7000 91C8 223C 0003 FEB0 B0FC 018C 6604 5848 6002 D098 5381 6EF0 0C80 8AB9 F121 6602 4E75 287C 00C0 0004 38BC 8F02 38BC 8004 38BC 8700 38BC 8144 38BC C000 323C 003F 33FC 000E 00C0 0000 51C9 FFF6 60FE"
    checksumCodeLen = len(bytearray.fromhex(checksumCode)) #remember 2 chars per byte
    checksumCodeLocation = findHex(checksumCode, romByteArray)
    #print(checksumCodeLen)
    #print(checksumCodeLocation)
    if checksumCodeLocation > -1:
        overwriteHex("ff"*checksumCodeLen, romByteArray, checksumCodeLocation)
        overwriteHex("60FE", romByteArray, checksumCodeLocation)
    overwriteHex("4e71 4e71 4e71", romByteArray, 0x300)

    
def checkForAppliedHacks(romByteArray, hacks):
    """
    Returns names of found hacks in a list
    """
    hacksFound = []
    
    for hack in hacks:
        hack.detect(romByteArray)

    # remove checksum
    if matchHex("4e71", romByteArray, 0x300):
        hacksFound.append("remove checksum")
        
    # simple weight bug fix
    #if matchHex("902a 0067 d02b 0067", romByteArray, 0x00013D72):
        #hacksFound.append("simple weight bug fix") # += separates the string into characters in the list

    # weight bug fix
    #if matchHex("4eb9", romByteArray, 0x00013D72):
        #hacksFound.append("weight bug fix") # += separates the string into characters in the list

    # Bodycheck Statistics
    if matchHex("4eb9", romByteArray, 0x00014130):
        hacksFound.append("Bodycheck Statistics") # += separates the string into characters in the list

    # Second-assist bug fix
    if matchHex("4eb9", romByteArray, 0x00010188):
        hacksFound.append("Second-assist bug fix") # += separates the string into characters in the list

    # 0-15 player ratings scale
    if matchHex("4e71", romByteArray, 0xf711C) or matchHex("E343", romByteArray, 0xf711C):
        hacksFound.append("0-15 player ratings scale")
        hacksFound.append("New overall rating formulas for 0-15 ratings")

    # 2. Ratings Consistency Fix - bonuses disabled
    if matchHex("4201", romByteArray, 0x0f710a):
        hacksFound.append("Ratings Consistency Fix") # topic
        hacksFound.append("Ratings Consistency Fix - bonuses disabled")
    
    # 3. Ratings Consistency Fix - Don't show bonuses in Edit Lines (0-6)
    elif matchHex("4207", romByteArray, 0x0FAAB4):
        hacksFound.append("Ratings Consistency Fix") # topic
        hacksFound.append("Ratings Consistency Fix - Don't show bonuses in Edit Lines (0-6)")

    # 3. Ratings Consistency Fix - Don't show bonuses in Edit Lines (0-15)
    elif matchHex("4207", romByteArray, 0xFAAAC):
        hacksFound.append("Ratings Consistency Fix") # topic
        hacksFound.append("Ratings Consistency Fix - Don't show bonuses in Edit Lines (0-15)")

    # 4. Ratings Consistency Fix - players match edit lines
    elif matchHex("4eb9", romByteArray, 0xf710a):
        hacksFound.append("Ratings Consistency Fix") # topic
        hacksFound.append("Ratings Consistency Fix - Players match edit lines")

    # 5. Ratings Consistency Fix - edit lines match players
    elif matchHex("4E71", romByteArray, 0xfaa38):
        hacksFound.append("Ratings Consistency Fix") # topic
        if matchHex("1E14", romByteArray, 0xfaab4):
            hacksFound.append("Ratings Consistency Fix - Edit lines match players (0-6)")
        elif matchHex("1E2C", romByteArray, 0xFAAAC):
            hacksFound.append("Ratings Consistency Fix - Edit lines match players (0-15)")

    # Plus-Minus statistic
    if matchHex("4eb9", romByteArray, 0x1494a):
        hacksFound.append("Plus-Minus statistic")
        
    # Three Stars hack - line changes OFF
    if matchHex("4241", romByteArray, 0x18698) and matchHex("2AF8", romByteArray, 0x186be): #11000 goal value (2af8)
        hacksFound.append("Three Stars hack - line changes OFF")
            
    # Three Stars hack - line changes ON
    if matchHex("4241", romByteArray, 0x18698) and matchHex("37DC", romByteArray, 0x186be): #14300 goal value (37DC)
        hacksFound.append("Three Stars hack - line changes ON")
            
    return hacksFound   

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

            
def inputNumber(prompt, validNumbers = []):
    while True: #loop until good input
        val = input(prompt)
        try:
            val = int(val)
        except:
            print ("\n     That's not a number.")
            continue
        if (len(validNumbers) == 0) or (val in validNumbers):
            break #got a good value!
        else: 
            print ("\n     That's not a valid option."
                   "\n     Valid numbers are: ", str(validNumbers).replace('[', '').replace(']', ''))
    return val
    
def inputString(prompt, validInput, caseSensitive = False):
    #print(validInput)
    while True: #loop until good input
        val = input(prompt).strip()
        if not caseSensitive: #convert all to lower case
            validInput = [x for x in map(str.lower, validInput)]
            val = val.lower()
        if val in validInput:
            break #got a good value!
        else: 
            print ("\n     That's not a valid option."
                   "\n     Valid inputs are: ", str(validInput).replace('[', '').replace(']', '').replace("'", ''))
    return val
    
def getBaseWeight(romByteArray):
    return getNumValue(romByteArray, 0x8e92, 2)
    
# Startup code
if __name__ == '__main__':

    import sys
    import os # os.system('CLS')
    
    from hacks.WeightBugFix import WeightBugFix
    
    #print(sys.argv[0])
    #print(os.getcwd())
    
    
    # no arguments, give instructions
    if len(sys.argv) == 1:
        printHeader()
        print("\n\n\n    INSTRUCTIONS\n\n")
        print("    To use this program, simply drag-and-drop a ROM onto the .EXE file.")
        print("    You will then be prompted for which hacks to apply and an output file name.")
        print("\n\n\n\n    PRESS ANY KEY TO CLOSE THIS WINDOW.", end='')
        wait_key()
        
    else:
    
        infileName = sys.argv[1]
        
        ROM = bytearray(open(infileName, 'rb').read()) #bytearray is mutable.  bytes is not
        
        # exit if not a valid ROM
        if not isNhl94Rom(ROM):
            printHeader()
            print("\n\n  This does not appear to be an NHL'94 ROM!"
            "\n\n  Press any key to close this window.")
            wait_key()
            sys.exit(1)

        weightBugFix = WeightBugFix()
        
        hacks = []
        hacks.append(weightBugFix)

        # are any fixes already applied to this ROM?
        hacksFound = checkForAppliedHacks(ROM, hacks)
        
        #for hack in hacks:
        #    print(hack.name, hack.isDetected)
        
        if len(hacksFound) > 0:
            printHeader()
            print ("\n  The following hacks were detected in this ROM: \n")
            for hack in hacks:
                if hack.isDetected:
                    print ("   -", hack.name)
            for x in hacksFound:
                if x != "Ratings Consistency Fix":
                    print("   - " + x)
            print ("\n  You will be asked some questions about the ROM you are creating.")
            print ("\n  Press any key to continue.")
            wait_key()
            os.system('CLS')

        romOldBaseWeight = getBaseWeight(ROM)
            
        # Questions about the ROM:
        printHeader()
        
        for hack in hacks:
            print("-" * 79)
            hack.configure()
            print("\n")
            
        
        # Weight bug fix
        #print('-' * 79)
        #print("\n  Weight Bug Fix:" 
        #    "\n\n     Do you want to include the weight bug fix?"
        #    "\n     The original game has a bug that makes light players good at checking and"
        #    "\n     heavy players easy to knock over.  This hack reverses this and also"
        #    "\n     includes the players' checking rating when deciding if a check succeeds.\n")
        #weightBugFixOption = inputString("     Enter 'y' or 'n':  ", ['y', 'n'])

        # Weight
        print('\n', "-" * 79)
        print("  Weight Scale:" + "\n" + "\n"
            "     The average weight of players changed over the years.  What game year " + "\n"
            "     does your ROM represent?  Use the 4-digit year (e.g., \"1994\")\n")
        romYear = inputNumber("     Year:  ",range(1000,3000))
        romNewBaseWeight = 140
        # find appropriate base weight from lookup table file
        weightyears = {}
        try:
            #handle XP/7 difference.. 7 doesn't include the script's path in argv[0]
            if sys.argv[0].rfind("\\") > -1:
                pathToUse = sys.argv[0][0:sys.argv[0].rfind("\\")] + "\\"
            else:
                pathToUse = ""
            for line in open(pathToUse + 'weightscale.txt'):
                line = line.strip()
                if len(line) and line[0] != "#":
                    line = line.split()
                    if len(line) >= 2:
                        try:
                            line[0] = int(line[0])
                            line[1] = int(line[1])
                            if line[1] >= 102 and line[1] <= 152 and (0 == line[1] % 2):
                                # valid
                                weightyears[line[0]] = line[1]
                            else:
                                print("Invalid base weight found in weightscale.txt: " + str(line[1]) + ".  Base weights must be EVEN numbers from 102-152.")
                        except:
                            pass #ignore
            #[print(x, weightyears[x]) for x in weightyears.keys()]
        except Exception as inst:
            print('  Uh oh, there was an error.  Is the file "weightscale.txt" missing?')
            print(type(inst))    # the exception instance
            print(inst.args)     # arguments stored in .args
            print('\n\n  Press any key to close this window.')
            wait_key()
            sys.exit(1)
        lowerYear = int(sorted(weightyears.keys())[0])
        upperYear = int(sorted(weightyears.keys())[-1])
        if romYear not in weightyears.keys(): 
            if romYear < lowerYear:
                print("\n     Years earlier than", lowerYear, "will use the same weight scale as", lowerYear)
                romYear = lowerYear
            elif romYear > upperYear:
                print("\n     Years after", upperYear, "will use the same weight scale as", upperYear)
                romYear = upperYear
            else: #year missing
                print("\n     Weight data for year", romYear, "missing.")
                radius = 1
                while (romYear + radius) not in weightyears.keys() and (romYear - radius) not in weightyears.keys():
                    radius += 1
                if (romYear - radius) in weightyears.keys():
                    romYear = romYear - radius
                else:
                    romYear = romYear + radius
                print("\n     Using data for year", romYear, "instead.")
            romNewBaseWeight = int(weightyears[romYear])
            print("\n     The current base weight in the ROM is " + str(romOldBaseWeight) + ".")
            print("     The ROM will be set up to use a base weight of " + str(romNewBaseWeight) + ".")
            print("     The original NHL'94 game uses a base weight of 140.")
            print ("\n  Press any key to continue.")
            wait_key()
        else:
            romNewBaseWeight = int(weightyears[romYear])
            print("\n     The current base weight in the ROM is " + str(romOldBaseWeight) + ".")
            print("     The ROM will be set up to use a base weight of " + str(romNewBaseWeight) + ".")
            print("     The original NHL'94 game uses a base weight of 140.")        
        

        # Ratings Scale: Do you want to use the original 0-6 rating scale, or the new 0-15 rating scale?  Enter "6" or "15".
        print('\n' + '-' * 79)
        print("\n  Player Rating Scale:" + "\n" + "\n"
            "     Do you want to use the old 0-6 rating scale, or the new 0-15 rating scale? ")
        ratingScaleOption = inputNumber("     Enter 6 or 15:  ", [6, 15])
        
        # Three Stars Scale:  Will this ROM be used with line changes OFF or ON?  The Three Stars hack will give goalies extra credit with line changes off.  Enter "on" or "off".
        print('\n' + '-' * 79)
        print("\n  Three Stars Scale:" + "\n" + "\n"
            "     You can update the Three Stars formula so it gives more realistic results." + "\n"
            "     Do you want to add this hack?" + "\n")
        lineChangesOnOffOption = inputString("     Enter 'y' or 'n':  ", ['y', 'n'])
        if lineChangesOnOffOption == 'y':
            print("\n     Will this ROM be used primarily with line changes OFF or ON?" + "\n"
                "     The Three Stars formula needs to be adjusted to match." + "\n")
            lineChangesOnOffOption = inputString("     Enter 'off' or 'on':  ", ['off', 'on'])
                
        # Edit Lines Ratings 
        print('\n' + '-' * 79)
        print("\n  Edit Lines Ratings:" + "\n" + "\n"
            "     The game normally makes each player either hot or cold (or average).  " + "\n"
            "     However, the Edit Lines ratings are not accurate, so are misleading." + "\n"
            "     You can change this.  But Ron Barr will still be wrong!" + "\n" + "\n"
            "     There are 3 options:" + "\n" + "\n"
            "     1. [No hack] Use the original ratings.  The Edit Lines ratings will not" + "\n"
            "        be accurate, so you have to 'feel' which players are hot or cold." + "\n"
            "     2. Disable the bonuses, so the players are the same every game." + "\n"
            "     3. Leave the bonuses on the players, but remove them from Edit Lines," + "\n"
            "        so you have to 'feel' which players are hot or cold." + "\n"
            "     4. Make the players match the Edit Lines ratings.  Players will be hot" + "\n"
            "        or cold on each individual attribute (e.g., hot speed & cold agility)." + "\n"
            "     5. Make the Edit Lines ratings match the players.  Each player will be" + "\n"
            "        either hot on all his attributes or cold on all his attributes." + "\n"
            )
        playerRatingsFixOption = inputNumber("     Enter a number from 1-5:  ", [1, 2, 3, 4, 5])
        
        
        
        # list hacks:
        os.system('CLS')
        printHeader()
        hacknum = 1
        print('-' * 79)
        print("\n  The following hacks will be added, removed, updated, left in, or omitted:" + "\n")
        
        print("    ", str(hacknum) + ((hacknum<10) and ".  " or ". "), end='')
        hacknum += 1
        if "remove checksum" in hacksFound:
            print("LEAVE  - ", end='')
        else:
            print("ADD    - ", end='')
        print ("remove checksum")
        
        for hack in hacks:
            print("    ", str(hacknum) + ((hacknum<10) and ".  " or ". "), end='')
            hacknum += 1
            hack.toDo() #prints out if the hack will be ADDedd, OMITted, REMOVEd, or LEAVE...d...
        
            """
            if "weight bug fix" in hacksFound:
                if weightBugFix.toApply:
                    print("LEAVE  - ", end='')
                else:
                    print("REMOVE - ", end='')
            else:
                if weightBugFix.toApply:
                    print("ADD    - ", end='')
                else:
                    print("OMIT   - ", end='')
            print ("weight bug fix")
            """
            
        print("    ", str(hacknum) + ((hacknum<10) and ".  " or ". "), end='')
        hacknum += 1
        if "Bodycheck Statistics" in hacksFound:
            if weightBugFix.toApply == True: #uh oh.. interdependency between hacks
                print("LEAVE  - ", end='')
            else:
                print("REMOVE - ", end='')
        else:
            if weightBugFix.toApply == True:
                print("ADD    - ", end='')
            else:
                print("OMIT   - ", end='')
        print ("Bodycheck Statistics")

        print("    ", str(hacknum) + ((hacknum<10) and ".  " or ". "), end='')
        hacknum += 1
        if romNewBaseWeight != romOldBaseWeight:
            if romOldBaseWeight == 140:
                print("ADD    - ", end='')
            else:
                print("CHANGE - ", end='')
        else:
            if romOldBaseWeight == 140:
                print("OMIT   - ", end='')
            else:
                print("LEAVE  - ", end='')
        print ("Weight scale modification for different era")

        print("    ", str(hacknum) + ((hacknum<10) and ".  " or ". "), end='')
        hacknum += 1
        if "Second-assist bug fix" in hacksFound:
            print("LEAVE  - ", end='')
        else:
            print("ADD    - ", end='')
        print ("Second-assist bug fix")

        print("    ", str(hacknum) + ((hacknum<10) and ".  " or ". "), end='')
        hacknum += 1
        if "0-15 player ratings scale" in hacksFound and ratingScaleOption==15:
            print("LEAVE  - ", end='')
        elif "0-15 player ratings scale" in hacksFound and ratingScaleOption==6:
            print("REMOVE - ", end='')
        elif ratingScaleOption==15:
            print("ADD    - ", end='')
        else: #6
            print("OMIT   - ", end='')
        print ("0-15 player ratings scale")
        
        print("    ", str(hacknum) + ((hacknum<10) and ".  " or ". "), end='')
        hacknum += 1
        if "0-15 player ratings scale" in hacksFound and ratingScaleOption==15:
            print("LEAVE  - ", end='')
        elif "0-15 player ratings scale" in hacksFound and ratingScaleOption==6:
            print("REMOVE - ", end='')
        elif ratingScaleOption==15:
            print("ADD    - ", end='')
        else: #6
            print("OMIT   - ", end='')
        print ("New overall rating formulas for 0-15 ratings")

        print("    ", str(hacknum) + ((hacknum<10) and ".  " or ". "), end='')
        hacknum += 1
        if playerRatingsFixOption == 1: #(original)
            if "Ratings Consistency Fix" in hacksFound:
                print("REMOVE - ", end='')
            else:
                print("OMIT   - ", end='')

        elif playerRatingsFixOption == 2: # disable both
            s = "Ratings Consistency Fix - bonuses disabled"
            if s in hacksFound:
                print("LEAVE  - ", end='')
            elif "Ratings Consistency Fix" in hacksFound:
                print("CHANGE - ", end='')
            else:
                print("ADD    - ", end='')

        # 3. Ratings Consistency Fix - Don't show bonuses in Edit Lines (0-6 ratings)
        # 3. Ratings Consistency Fix - Don't show bonuses in Edit Lines (0-15 ratings)
        elif playerRatingsFixOption == 3:
        
            s1 = "Ratings Consistency Fix - Don't show bonuses in Edit Lines (0-6)"
            s2 = "Ratings Consistency Fix - Don't show bonuses in Edit Lines (0-15)"
            if s1 in hacksFound:
                if ratingScaleOption == 6:
                    print("LEAVE  - ", end='')
                else:
                    print("CHANGE - ", end='')
            elif s2 in hacksFound:
                if ratingScaleOption == 15:
                    print("LEAVE  - ", end='')
                else:
                    print("CHANGE - ", end='')
            elif "Ratings Consistency Fix" in hacksFound:
                print("CHANGE - ", end='')
            else:
                print("ADD    - ", end='')
                
                
        # 4. Ratings Consistency Fix - players match edit lines
        elif playerRatingsFixOption == 4:
        
            s = "Ratings Consistency Fix - players match edit lines"
            if s in hacksFound:
                print("LEAVE  - ", end='')
            elif "Ratings Consistency Fix" in hacksFound:
                print("CHANGE - ", end='')
            else:
                print("ADD    - ", end='')
            
        # 5. Ratings Consistency Fix - edit lines match players
        elif playerRatingsFixOption == 5:
        
            s1 = "Ratings Consistency Fix - Edit lines match players (0-6)"
            s2 = "Ratings Consistency Fix - Edit lines match players (0-15)"
            if s1 in hacksFound:
                if ratingScaleOption == 6:
                    print("LEAVE  - ", end='')
                else:
                    print("CHANGE - ", end='')
            elif s2 in hacksFound:
                if ratingScaleOption == 15:
                    print("LEAVE  - ", end='')
                else:
                    print("CHANGE - ", end='')
            elif "Ratings Consistency Fix" in hacksFound:
                print("CHANGE - ", end='')
            else:
                print("ADD    - ", end='')

        print("Ratings Consistency Fix")
                
        print("    ", str(hacknum) + ((hacknum<10) and ".  " or ". "), end='')
        hacknum += 1
        if "Plus-Minus statistic" in hacksFound:
            print("LEAVE  - ", end='')
        else:
            print("ADD    - ", end='')
        print ("Plus-Minus statistic")
            
        print("    ", str(hacknum) + ((hacknum<10) and ".  " or ". "), end='')
        hacknum += 1
        if "Three Stars hack - line changes OFF" in hacksFound or "Three Stars hack - line changes ON" in hacksFound:
            if lineChangesOnOffOption.lower() == "n":
                    print("REMOVE  - Three Stars hack")
            elif "Three Stars hack - line changes OFF" in hacksFound:
                if lineChangesOnOffOption.lower() == "off":
                    print("LEAVE  - Three Stars hack - line changes OFF")
                else:
                    print("CHANGE - Three Stars hack - line changes ON")
            elif "Three Stars hack - line changes ON" in hacksFound:
                if lineChangesOnOffOption.lower() == "on":
                    print("LEAVE  - Three Stars hack - line changes ON")
                else:
                    print("CHANGE - Three Stars hack - line changes OFF")
        else:
            if lineChangesOnOffOption.lower() == "n":
                print("OMIT   - Three Stars hack")
            elif lineChangesOnOffOption.lower() == "on":
                print("ADD    - Three Stars hack - line changes ON")
            else:
                print("ADD    - Three Stars hack - line changes OFF")


        print("    ", str(hacknum) + ((hacknum<10) and ".  " or ". "), end='')
        hacknum += 1
        
        if ("0-15 player ratings scale" in hacksFound and ratingScaleOption==6) \
                or ("0-15 player ratings scale" not in hacksFound and ratingScaleOption==15) \
                or (romNewBaseWeight != romOldBaseWeight):
            print("CHANGE - ", end='')
        else:
            print("LEAVE  - ", end='')
        print ("ROM Product Code so NOSE can show correct weights and ratings")

        #if "simple weight bug fix" in hacksFound:
         #   print("    ", str(hacknum) + ((hacknum<10) and ".  " or ". "), end='')
          #  hacknum += 1
           # print("REMOVE - simple weight bug fix")
            
        userOption = ''
        
        print("\n  Enter the number corresponding to a hack to get more information.")
        print("  Enter 'H' to apply the changes and save the ROM to a new file name.")
        print("  Enter 'X' to exit without changing the ROM.")
        options = list([str(x) for x in range(hacknum)])
        options.insert(0, "H")
        options.insert(1, "X")
        
        while userOption.lower() != 'x' and userOption.lower() != 'h' :

            userOption = inputString("  Enter your choice:  ", options)
            
            if userOption.lower() == 'x':
                print("\n  No changes were made to the ROM.")
                break
                
            elif userOption.lower() != 'h':
            
                print('\n')
                
                if userOption == '1':
                    print("\n     Remove Checksum:"
                          "\n\n     Removing the checksum routine is necessary for modded ROMs to run")
                
                elif userOption == '2':
                    print(weightBugFix.info())
                    #print("\n     Weight Bug Fix:"
                    #      "\n\n     The original game has a bug that makes light players good at checking and"
                    #      "\n     heavy players easy to knock over.  This hack reverses this and also"
                    #      "\n     includes the players' checking rating when deciding if a check succeeds."
                    #      )
                
                elif userOption == '3':
                    print("\n     Bodycheck Statistics:"
                          "\n\n     This hack replaces the PIM stat in Player Stats with Chk -- the number of"
                          "\n     successful checks that player delivered."
                          )
                
                elif userOption == '4':
                    print("\n     Weight scale modification for different eras"
                          "\n\n     Since player weights have increased over the years, this hack changed the"
                          "\n     base player weight to match the year the ROM represents so there is a good."
                          "\n     variation of player weights in the ROM."
                          "\n     This hack requires you to update the .ini files in NOSE so it can display."
                          "\n     the correct weights."
                          )
                
                elif userOption == '5':
                    print("\n     Second-Assist Bug Fix"
                          "\n\n     If two players pass back and forth and then score, the player who passed"
                          "\n     it to them does not get an assist.  This fixes that bug."
                          )
                
                elif userOption == '6':
                    print("\n     0-15 Player Ratings Scale"
                          "\n\n     This hack lets players be rated on a finer-grained scale."
                          "\n     The original game rates players from 0 to 6.  This lets them be rated from"
                          "\n     0 to 15."
                          "\n     This hack requires you to update the .ini files in NOSE so it can display."
                          "\n     the correct ratings."
                          )
                
                elif userOption == '7':
                    print("\n     New overall rating formulas for 0-15 ratings"
                          "\n\n     With the 0-15 rating scale, a new rating system was devised that rates"
                          "\n     players from 0-99 more accurately that in the original game.  More credit"
                          "\n     is given to the attributes that make players better at generating or"
                          "\n     preventing goals."
                          )
                
                elif userOption == '8':
                    print("\n     Ratings Consistency Fix"
                          "\n\n     In the original game, the ratings you see in Edit Lines are not accurate."
                          "\n     This hack lets you change the bonuses to either make the players match the"
                          "\n     Edit Lines ratings or the Edit lines ratings match the players."
                          "\n     You can also disable the bonuses, or have the Edit Lines screen not show."
                          "\n     bonuses."
                          )
                
                elif userOption == '9':
                    print("\n     Plus-Minus Statistic"
                          "\n\n     This hack adds an invisible +/- statistic to the game.  The values can be "
                          "\n     retrieved from the savestate file for use in leagues with stats tracking.."
                          )
                
                elif userOption == '10':
                    print("\n     Three Stars Hack"
                          "\n\n     The original game had a very simple way of generating the Three Stars."
                          "\n     This adds a more realistic evaluation scheme."
                          "\n     The formula is made to differ depending on if Line Changes are On or Off --."
                          "\n     skaters get a bit more credit with line changes on because they get less "
                          "\n     ice time."
                          )
                
                elif userOption == '11':
                    print("\n     ROM Product Code"
                          "\n\n     The NOSE editor can read this value and then change the way it displays"
                          "\n     player ratings and weights, to reflect the modified base weight or 0-15"
                          "\n     rating scale."
                          "\n     Note that you have to update NOSE's .ini files or it will not be able to"
                          "\n     open your ROM."
                          )
                
                elif userOption == '12':
                    print("\n     Simple Weight Bug Fix"
                          "\n\n     This was the original weight bug fix.  It didn't included the checking"
                          "\n     rating of the players' when deciding if a check succeeded or not.  This"
                          "\n     will be upgraded to the improved weight bug fix."
                          )
                          
                print('') # blank line
            
            
            else: # h - apply hacks!
            
                
                # ---------------------------------------------------------------
                # remove all hacks (reset the new code section)
                # ---------------------------------------------------------------
                
                for hack in hacks:
                    hack.remove(ROM)

                #if "weight bug fix" in hacksFound:
                #    overwriteHex("90 2b 00 67 d0 2a 00 67", ROM, 0x00013D72)
                #    where = findHex("3F01902A0067122B0067E201D001E201D001122b0075e301d001", ROM) #not whole hack string!
                #    if where > -1: 
                #        overwriteHex("ff" * len(bytearray.fromhex("3F01902A0067122B0067E201D001E201D001122b0075e301d0010400000e321f4e75")), ROM, where)
                        
                if "Bodycheck Statistics" in hacksFound:
                    overwriteHex("50 49 4D", ROM, 0x0000993F) #PIM
                    overwriteHex("50 65 6E 61 6C 74 79 20 4D 69 6E 75 74 65 73", ROM, 0x000099b4) # Penalty Minutes
                    overwriteHex("52 68 00 10 42 40 10 2B 00 66 D0 C0 52 28 01 1C", ROM, 0x00014130)
                    hackcode = "526800100839000000ffc2ea6600002a4240102b0066d0c05228010290c090fc0364b7ca6e000006d0fc06c84240102a0066d0c05228011C4e75"
                    where = findHex(hackcode, ROM)
                    if where > -1:
                        overwriteHex("ff" * len(bytearray.fromhex(hackcode)), ROM, where)
                    overwriteHex("D5 32 00 00", ROM, 0x00012302)
                

                # Second-assist bug fix
                if "Second-assist bug fix" in hacksFound:
                    overwriteHex("31 68 00 1A 00 1C", ROM, 0x00010188)
                    overwriteHex("31 68 00 1A 00 1C", ROM, 0x000F6CE4)
                    hackcode = "B068001A670000083168001A001C4E75"
                    where = findHex(hackcode, ROM)
                    if where > -1:
                        overwriteHex("ff" * len(bytearray.fromhex(hackcode)), ROM, where)

                # 0-15 player ratings scale
                if "0-15 player ratings scale" in hacksFound:
                    overwriteHex("3F03E543D65F", ROM, 0x0F711C)
                    overwriteHex("2F0E 4278 D6CE 4278 D6D0 2C7C 000F AB3C B8B9 0001 9420 6600 0008 2C7C 000F AB1C B8B9 0001 9582 6600 0008 2C7C 000F AB2C 206A 001E 49EA 01A2 4281 3200 E941 D9C1 D9FC 0000 0010 D0D0 D0D0 5048 51C8 FFFA 4240 4241 740F 4844 0504 6700 0092 3602 E24B 4443 1630 30FF 0802 0000 6700 0004 E84B 0243 000F B47C 000D 6600 0006 6000 0068 B47C 0006 6700 0060 48E7 0700 1A36 2000 4885 BA7C 0002 6700 0010 3F03 5545 D657 51CD FFFC E243 4A5F 4CDF 00E0 BDFC 000F AB3C 6700 001C 4442 3F07 1E34 20FF 4887 DF78 D6CE 5278 D6D0 3E1F 4442 6000 0018 3F03 E943 D657 D65F 4442 D634 20FF 6A00 0004 4203 4442 D043 0641 0064 51CA FF68 BDFC 000F AB3C 6700 001C 323C 0064 48E7 0300 3C38 D6CE 48C6 3E38 D6D0 8DC7 D046 4CDF 00C0 B041 6D00 0006 3200 5340 2C5F 4E75", ROM, 0x0FA9F8)
                    hackcode = "B068001A670000083168001A001C4E75"
                    where = findHex(hackcode, ROM)
                    if where > -1:
                        overwriteHex("ff" * len(bytearray.fromhex(hackcode)), ROM, where)


                # New overall rating formulas for 0-15 ratings
                if "New overall rating formulas for 0-15 ratings" in hacksFound:
                    overwriteHex("0202 0202 0406 0204 0204 0606 0402 0202 0202 0202 0202 0202 0909 0202 0902 0202 0202 0202 0202 0202 0202 0202 0202 0202", ROM, 0x0FAB1C)
                    overwriteHex("1FBA", ROM, 0x019420)
                    overwriteHex("130F", ROM, 0x019582)


                # Ratings Consistency Fix - players match edit lines
                if "Ratings Consistency Fix" in hacksFound:
                    # revert them all.. 
                    
                    # on-ice bonus
                    overwriteHex("D3FC 0000 01A2 1231 1000", ROM, 0x0f710a) 
                    hackcode = "D3FC 0000 01B2 3F02 3438 BF14 0442 0010 D441 1231 2000 341F 4E75"
                    where = findHex(hackcode, ROM)
                    if where > -1:
                        overwriteHex("ff" * len(bytearray.fromhex(hackcode)), ROM, where)

                    #Edit Lines Bonuses
                    overwriteHex("1E34 20FF", ROM, 0x0FAAB4) 
                    overwriteHex("D634 20FF", ROM, 0x0FAAD4) 
                
                #-----------------
                # Ratings Consistency Fix - players match edit lines
                if "Ratings Consistency Fix - players match edit lines" in hacksFound:
                    overwriteHex("D3FC 0000 01A2 1231 1000", ROM, 0x0f710a)
                    hackcode = "D3FC 0000 01B2 3F02 3438 BF14 0442 0010 D441 1231 2000 341F 4E75"
                    where = findHex(hackcode, ROM)
                    if where > -1:
                        overwriteHex("ff" * len(bytearray.fromhex(hackcode)), ROM, where)
                        
                # Ratings Consistency Fix - edit lines match players
                if "Ratings Consistency Fix - edit lines match players" in hacksFound:
                    overwriteHex("D9FC 0000 0010", ROM, 0xfaa38)
                    overwriteHex("1E34 20FF", ROM, 0xfaab4)
                    overwriteHex("D634 20FF", ROM, 0xfaad4)


                # Plus-Minus statistic
                if "Plus-Minus statistic" in hacksFound:
                    overwriteHex("0678 001E B8A2", ROM, 0x1494a)
                    overwriteHex("4CDF 0E00 203C 0000 0363 307C C6CE 4218 51C8 FFFC 307C CA32 303C 0363 4218 51C8 FFFC 48E7 0070", ROM, 0x017132)
                    hackcode = "0678 001E B8A2 48E7 E0C0 0838 0005 C2F4 6700 0010 0838 0000 C2FA 6600 0006 08C0 0006 B4FC C6CE 6700 0006 08C0 0007 307C DEF6 3210 D0F8 DEF4 5E78 DEF4 5E78 DEF4 3210 10C0 5248 700B 327C B04A 323C 0080 343C FF10 B451 6600 000A 10FC 00FF 6000 0006 10E9 0066 D2C1 51C8 FFEA 4CDF 0307 4E75"
                    where = findHex(hackcode, ROM)
                    if where > -1:
                        overwriteHex("ff" * len(bytearray.fromhex(hackcode)), ROM, where)
                        
                    
                # Three Stars hack - line changes OFF, Three Stars hack - line changes ON
                if "Three Stars hack - line changes OFF" in hacksFound or "Three Stars hack - line changes ON" in hacksFound:
                    overwriteHex("324A 362A 000C 966B 000C 48C3 7819 4EB9 0000 9F40 4440 D044 2883 B840 6200 003C 4241 122A 00B4 C2FC 2AF8 D394 4241 122A 00CE C2FC 2774 D394 4241 122A 00E8 C2FC 000A 4A43 6600 000E C2FC 0064 D394 4281 D269 0136 D394 6000 003A BA69 0136 6200 0032 4241 122A 00B4 C2FC 0064 4242 142A 00E8 6700 001E 82C2 B27C 0004 6200 0014 0694 0000 7D00 4A41 6600 0008 0694 0001 24F8 5449 524A 584C 51CC FF7E 4E75", ROM, 0x0001867e)

                # ROM Product Code
                if len(ROM) > 500*1024 and len(ROM) < 1500*1204: # roughly 1MB..
                    overwriteHex("202d 3030", ROM, 0x18a) # " -00"
                elif len(ROM) >= 1500*1024:
                    overwriteHex("202d 3330", ROM, 0x18a) # " -30"
                    
                
                #---------------------------------------------------------
                # Apply hacks
                #---------------------------------------------------------
                
                removeChecksum(ROM)

                for hack in hacks:
                    hack.apply(ROM)  #won't apply it if not configured to be applied
                
                # weight bug fix
                # Bodycheck Statistics
                if weightBugFix.toApply:
                    # weight bug fix
                    #wherespace = 4 + findEmptyRomSpace(ROM) # +4 to leave some "empty" space in front of  each hack, so it's easier to see them individually.
                    #where = overwriteHex("4e b9", ROM, 0x00013D72) # JSR
                    #where = overwriteHex(numToByteArray(wherespace,32), ROM, where)
                    #overwriteHex("4e 71", ROM, where)
                    #overwriteHex("3F01902A0067122B0067E201D001E201D001122b0075e301d0010400000e321f4e75", ROM, wherespace) # added code
                    # Bodycheck Statistics
                    overwriteHex("43 68 6B", ROM, 0x0000993F) # "Chk"
                    overwriteHex("20 20 20 43 68 65 63 6B 73 20 46 6F 72 20 20", ROM, 0x000099B4) # "   Checks For  "
                    wherespace = 4 + findEmptyRomSpace(ROM) # +4 to leave some "empty" space in front of  each hack, so it's easier to see them individually.
                    where = overwriteHex("4e b9", ROM, 0x00014130) # JSR
                    where = overwriteHex(numToByteArray(wherespace,32), ROM, where)
                    overwriteHex("4e714e714e714e714e71", ROM, where)
                    overwriteHex("526800100839000000ffc2ea6600002a4240102b0066d0c05228010290c090fc0364b7ca6e000006d0fc06c84240102a0066d0c05228011C4e75", ROM,wherespace)
                    overwriteHex("4E 71 4E 71", ROM, 0x00012302) # don't write PIM stat
                    
                # Weight Adjustment - Weights will match the era
                overwriteHex(numToByteArray(romNewBaseWeight,16), ROM, 0x8e92)
                    
                # Second-assist bug fix
                wherespace = 4 + findEmptyRomSpace(ROM) # +4 to leave some "empty" space in front of  each hack, so it's easier to see them individually.
                # JSR
                where = overwriteHex("4e b9", ROM, 0x00010188) 
                overwriteHex(numToByteArray(wherespace,32), ROM, where)
                # JSR
                where = overwriteHex("4e b9", ROM, 0x000F6CE4) 
                overwriteHex(numToByteArray(wherespace,32), ROM, where)
                # new code
                overwriteHex("B068001A670000083168001A001C4E75", ROM,wherespace)
                
                # 0-15 player ratings scale
                if ratingScaleOption == 15:
                    # change on-ice multiplier from 5 to 2
                    overwriteHex("4e71 E343 4e71", ROM, 0x0F711C) 
                    # rewrite ratings code
                    overwriteHex("48E7 0702 4278 D6CE 4278 D6D0 2C7C 000F AB3C B8B9 0001 9420 6600 0008 2C7C 000F AB1C B8B9 0001 9582 6600 0008 2C7C 000F AB2C 206A 001E 49EA 01A2 4281 3200 E941 D9C1 D9FC 0000 0010 D0D0 D0D0 5048 51C8 FFFA 4240 4241 740F 4844 0504 6700 0084 3602 E24B 4443 1630 30FF 0802 0000 6700 0004 E84B 0243 000F BDFC 000F AB3C 6600 0016 B47C 000D 6700 007C B47C 0006 6700 0074 6000 0034 1A36 2000 4885 3F03 5545 D657 51CD FFFC 4A5F BDFC 000F AB3C 6700 0018 4442 1E34 20FF 4887 DF78 D6CE 5278 D6D0 4442 6000 0016 3F03 E743 965F 4442 D634 20FF 6A00 0004 4203 4442 D043 0641 0064 51CA FF76 BDFC 000F AB3C 6700 001C E640 3C38 D6CE 48C6 3E38 D6D0 8DC7 D046 6000 0004 D043 323C 0064 B041 6D00 0006 3200 5340 4CDF 40E0 4E75 FFFF FFFF FFFF FFFF FFFF", ROM, 0x0FA9F8) 
                    # New overall rating formulas for 0-15 ratings
                    # multipliers
                    overwriteHex("0206 0202 0606 0204 0806 060A 0804 0202 0808 0707 0202 0202 0A04 0202 0C02 0202 0202 0202 0202 0202 0202 0202 0202 0202", ROM, 0x0FAB1C) 
                    overwriteHex("3FBA", ROM, 0x019420) # include weight
                    overwriteHex("1B0F", ROM, 0x019582) # include speed (for what it's worth)

                    
                    
                "     1. [No hack] Use the original ratings.  The Edit Lines ratings will not" + "\n"
                "        be accurate, so you have to 'feel' which players are hot or cold." + "\n"
                "     2. Disable the bonuses, so the players are the same every game." + "\n"
                "     3. Leave the bonuses on the players, but remove them from Edit Lines," + "\n"
                "        so you have to 'feel' which players are hot or cold." + "\n"
                "     4. Make the players match the Edit Lines ratings.  Players will be hot" + "\n"
                "        or cold on each individual attribute (e.g., hot speed & cold agility)." + "\n"
                "     5. Make the Edit Lines ratings match the players.  Each player will be" + "\n"
                "        either hot on all his attributes or cold on all his attributes." + "\n"
                "        This is recommended for 'for fun' ROMs. " + "\n"                    
                # 2. Ratings Consistency Fix - disable the bonuses
                # 3. Leave the bonuses on the players, but remove them from Edit Lines
                if playerRatingsFixOption == 2 or playerRatingsFixOption == 3:
                    if playerRatingsFixOption == 2:
                        overwriteHex("4201 4e71 4e71 4e71 4e71", ROM, 0x0f710a) #on ice
                    if ratingScaleOption == 6:
                        overwriteHex("4207 4e71", ROM, 0x0FAAB4) # edit lines/team rosters
                        overwriteHex("4e71 4a43", ROM, 0x0FAAD4) # edit lines/team rosters
                    else: # 0-15 ratings
                        overwriteHex("4207 4e71", ROM, 0xFAAAC) # edit lines/team rosters
                        overwriteHex("4e71 4a43", ROM, 0xFAAC8) # edit lines/team rosters

                # 4. Ratings Consistency Fix - players match edit lines
                if playerRatingsFixOption == 4:
                    # same for 0-6 and 0-15 ratings
                    wherespace = 4 + findEmptyRomSpace(ROM) # +4 to leave some "empty" space in front of  each hack, so it's easier to see them individually.
                    # JSR
                    where = overwriteHex("4e b9", ROM, 0x0f710a) 
                    where = overwriteHex(numToByteArray(wherespace,32), ROM, where)
                    overwriteHex("4e714e71", ROM, where)
                    # new code
                    overwriteHex("D3FC 0000 01B2 3F02 3438 BF14 0442 0010 D441 1231 2000 341F 4E75", ROM, wherespace)

                # 5. Ratings Consistency Fix - edit lines match players
                elif playerRatingsFixOption == 5:
                    if ratingScaleOption == 6:
                        overwriteHex("4E71 4E71 4E71", ROM, 0xfaa38)
                        overwriteHex("1E14 4e71", ROM, 0xfaab4)
                        overwriteHex("D634 0000", ROM, 0xfaad4)
                    else: #0-15
                        overwriteHex("4E71 4E71 4E71", ROM, 0xfaa38)
                        overwriteHex("1E2C 0000", ROM, 0xFAAAC)
                        overwriteHex("D62C 0000", ROM, 0xFAAC8)
                        
                
                # Plus-Minus statistic
                wherespace = 4 + findEmptyRomSpace(ROM) # +4 to leave some "empty" space in front of  each hack, so it's easier to see them individually.
                # JSR
                where = overwriteHex("4e b9", ROM, 0x1494a) 
                overwriteHex(numToByteArray(wherespace,32), ROM, where)
                # new code
                overwriteHex("0678 001E B8A2 48E7 E0C0 0838 0005 C2F4 6700 0010 0838 0000 C2FA 6600 0006 08C0 0006 B4FC C6CE 6700 0006 08C0 0007 307C DEF6 3210 D0F8 DEF4 5E78 DEF4 5E78 DEF4 3210 10C0 5248 700B 327C B04A 323C 0080 343C FF10 B451 6600 000A 10FC 00FF 6000 0006 10E9 0066 D2C1 51C8 FFEA 4CDF 0307 4E75", ROM, wherespace)
                # erase memory before game
                overwriteHex("4CDF 0E00 203C 0000 06C7 307C C6CE 4218 51C8 FFFC 307C DEF4 3010 5440 4218 51C8 FFFC 48E7 0070", ROM, 0x017132)
                
                # Three Stars hack - line changes OFF
                # Three Stars hack - line changes ON
                if lineChangesOnOffOption != 'n':
                    code = "324A 362A 000C 966B 000C 48C3 7819 4EB9 0000 9F40 4440 D044 2883 4241 122A 00CE C2FC {assist:04X} 4242 142A 00E8 B840 6200 0026 D394 C4FC {shot_for:04X} D594 4241 122A 00B4 C2FC {goal:04X} D394 4241 122A 0102 C2FC {check:04X} D394 6000 003A BA69 0136 6200 0032 4A42 6700 002C E281 D394 4241 122A 00B4 4A41 6600 0008 0694 0000 {shutout:04X} C3FC {goals_against:04X} D394 4A43 6A00 0004 5382 C4FC {shots_against:04X} D594 5449 524A 584C 51CC FF84 4E75 ffff ffff ffff"
                    if lineChangesOnOffOption == 'off':
                        #values must less than or equal to 65535
                        code = code.format(goal=11000, assist=7000, shot_for=500, check=500, goals_against=65536-11000, shots_against=4000, shutout=16000)
                    elif lineChangesOnOffOption == 'on':
                        code = code.format(goal=14300, assist=9100, shot_for=650, check=650, goals_against=65536-11000, shots_against=4500, shutout=20800)
                    overwriteHex(code, ROM, 0x1867E) 
                
                # ROM Product Code so NOSE can show correct weights and ratings      
                #use ROM size to decide to use -00 or -30
                #  -00 - plain 28-team ROM
                #  -30 - plain 30-team ROM
                #  -0t - should be  -00 (t means 140 base weight, which is normal)
                #  -3t - should be  -30 (t means 140 base weight, which is normal)
                #  -0a - 28-team ROM with 102 base weight
                #  -3v - 30-tean ROM with 144 base weight
                # -f0w - 0-15 ratings 28-team ROM with 146 base weight
                # -f3x - 0-15 ratings 30-team ROM with 148 base weight
                
                # 28 or 30-team ROM?
                if ratingScaleOption == 15:
                    ROM[0x18a] = ord('-')
                    ROM[0x18b] = ord('F')
                # base weight not default?
                if romNewBaseWeight != 140:
                    # convert base weights of 102-152 even numbers to 'A'-'Z'
                    ROM[0x18d] = (romNewBaseWeight-100)//2 + ord('A') - 1 

                if weightBugFix.toApply or ratingScaleOption == 15 or romNewBaseWeight != romOldBaseWeight:
                    print("\n  Before you save, please read this:" + "\n")
                    print("     If you are using the 0-15 ratings or different year base weight with NOSE," + "\n"
                        "     then you need to use NOSE version 1.2d or higher. See 'NOSE update.html'" + "\n")
                    print("     See 'Player Rating Guide.html' for information about player "+ "\n"
                        "     rating balances if you are going customize player ratings." + "\n")
                    print("     In particular, the Weight Bug Fix is calibrated to match the original " + "\n"
                        "     NHL'94 game's players.  This means that if you edit the players and you " + "\n"
                        "     drastically change the average checking value in the ROM, it will be " + "\n"
                        "     generally too hard or too easy to check." + "\n"
                        "     " + "\n"
                        "     So, you need to keep roughly the same average checking values as  " + "\n"
                        "     in the original game." + "\n" + "\n"
                        "     Most  forwards   should be rated 2-3 out of 6 (4-8 out of 15) in checking." + "\n"
                        "     Most defensemen  should be rated 2-4 out of 6 (4-11 out of 15)." + "\n"
                        "     Very few players should be rated 5-6 out of 6 (12-15 out of 15)." + "\n")
                    print("  Press a key to continue" + "\n")
                    wait_key()

                saveHex(ROM, sys.argv[1])
                
        
        print("\n  Press any key to close this window.")
        
        wait_key()
