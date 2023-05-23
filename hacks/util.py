
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
    