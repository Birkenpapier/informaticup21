import json



#Method to get the bodylocations for each player
def getPlayersBodyLocationsFromJson(jsonText):
    info_dict = json.loads(jsonTxt)
    cells = info_dict['cells']

    #Get and save the location of all playerbodys
    allPlayerBodyCords = []

    playerNr = 1
    #Check for each player the location and save as a list (0-58 rows, 0-76 columns in this example)
    while playerNr < 7:
        playerBodyCords = []

        rowNr = -1
        for cellRow in cells:
            rowNr = rowNr + 1
            columNr = 0
            for cell in cellRow:
                if(cell == playerNr):
                    playerBodyCords.append((columNr, rowNr))
                columNr = columNr + 1


        allPlayerBodyCords.append(playerBodyCords)
        playerNr = playerNr + 1


    return allPlayerBodyCords # Tuplelist with player locations
        

#Read JSON Textfile
jsonTxt = ""
with open("JSON Logs//singleState.txt","r") as f:
    jsonTxt = f.read()

#Get Locations
locations = getPlayersBodyLocationsFromJson(jsonTxt)
print(locations)

##################
info_dict = json.loads(jsonTxt)
#Get own Id
ownId = info_dict["you"]
print(ownId)
