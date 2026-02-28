# Test Space to Work on Implementations without accidentally breaking stuff in the main File
import re

import time

#todo Implement API-Less Achievement Updates
#todo Implement Periodic Checking of the Actual Game-Time against the API
#todo Implement Way of Checking who the last owner of the program was so nothing is pulled if its not needed - done
#todo Keep User from Inputting or Launching Stuff when he isnt supposed to - done
#todo Implement Listing for a Game Launch(API-Less) -WIP
#todo Implement Library-location catching for ACF files -done
#todo Start thinking about Connection Between Backend-PC-Raspberry-Cartridge
    #todo Start working with Flash Chip and E-Ink (Connection)
    #todo Start Working on interface between PC and Raspberry
    #todo Start Thinking about how the Backend should work

#todo: Fix Error with Registering Launches Properly. maybe give an Arbitrary Time Delay before looking for changes
#todo: Add Force-Refresh to Library

def Get_Libary_Locations() -> list[str]:
    with open(f"C:/Program Files (x86)/Steam/steamapps/libraryfolders.vdf") as f:
        library = f.read()
    Regex=re.compile(r'(?<="\d"\s{2}{\s{3}"path"\s{2}")[^"]*')
    Libary_Loactions=Regex.findall(library)
    return Libary_Loactions
    
def Get_acf(appid:int) -> str:
    Locations: list[str]=Get_Libary_Locations()
    acf=""
    for i in range(0,len(Locations)):
        try:
            with open(f"{Locations[i]}/steamapps/appmanifest_{appid}.acf") as f:
                acf = f.read()
                #print(f"Found under Location: {Locations[i]}/steamapps/appmanifest_{appid}.acf")
                return acf
        except FileNotFoundError:
            #print(f"not Found under Location: {Locations[i]}/steamapps/")
            #print("Searching Next Location")
            continue
        except Exception as e:
            print(e)
            break
    return acf

def Get_LastPlayed(appid:int) -> int: 
    acf: str=Get_acf(appid)
    Regex=re.compile(r'(?<="LastPlayed"\s{2}")[^"]*')
    timestamp=int(Regex.findall(acf)[0])  # pyright: ignore[reportAny]
    return timestamp  

def Get_Name_from_Acf(appid:int):
    acf: str=Get_acf(appid)
    Regex=re.compile(r'(?<="name"\s{2}")[^"]*')
    Name=str(Regex.findall(acf)[0])  # pyright: ignore[reportAny]
    return Name  


def Register_Changes(appid:int):
    is_running=True
    Old_time=Get_LastPlayed(appid=appid)  
    New_time=Old_time 
    Change:bool=False
    has_launched=False
    has_closed=False
    Launch_Date=0
    Close_Date=0
    print("Starting Montoring")
    print(f'Game:   "{Get_Name_from_Acf(appid=appid)}"')
    print("----------------------------------------")
    while is_running:
        try:
            New_time=Get_LastPlayed(appid=appid) 
            timeUsed=int(round(time.time(),0))
            if New_time!=Old_time:
                Change=True
                if has_launched ==False:
                    has_launched =True
                    Launch_Date=New_time
                else:
                    has_closed=True
                    Close_Date=New_time
                    print(f"{timeUsed}:    {New_time}  | Changed:  {Change}")
                    print("Second Event Registered, Closing!")
                    break
            else:
                Change=False
            print(f"{timeUsed}:    {New_time}  | Changed:  {Change}")
            Old_time=New_time 
            time.sleep(1)
        except KeyboardInterrupt:
            is_running=False
            print("Aborting")
    if has_closed ==True:
        Playtime_seconds: int=Close_Date-Launch_Date
        Playtime_minutes: float=round(Playtime_seconds/60,1)
        print(f'Summary: Game "{Get_Name_from_Acf(appid=appid)}" was played for {Playtime_minutes} Minutes')
    else:
        print("No Activity detected")

Register_Changes(appid=int(input("please input appid to Listen for Changes:")))
#print(Get_Libary_Locations())
#print(Get_acf(appid=620))