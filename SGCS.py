#SGCS Steam Game Cartridge System
from PIL.Image import Image
import requests
import os
import subprocess
import re
import json
import urllib
import urllib.request
from urllib.parse import urlparse
from io import BytesIO
import time

from PIL import Image as PILImage
from PIL import ImageTk
try:
    with open("C:/Users/thecr/Nextcloud/AAA_SCGS/Key.txt") as f:
        key_data = f.readlines()
except Exception as e:
    with open("C:/Users/user/Nextcloud/AAA_SCGS/Key.txt") as f:
        key_data = f.readlines()
        
        
key_data=key_data[0].split()

API_KEY_Steam=key_data[1]
API_KEY_SteamGrid=key_data[3]
USER_ID_Steam_Standard=key_data[5]
USER_ID_Steam=USER_ID_Steam_Standard


def Connect_Check() -> bool:
    try:
        _=requests.get(url="https://store.steampowered.com/",timeout=1)
        print("Internetverbindung erfolgreich!")
        return True         
    except requests.ConnectionError as e:
        print("Internetverbindung fehlgeschlagen", e)
        return False


def Steam_running():
    tasks = subprocess.check_output("tasklist").decode(encoding="utf-8").lower()
    return "steam.exe" in tasks


def Run_Game(GameID:int):
    os.startfile(f"steam://rungameid/{GameID}")

def Launch_Game() -> None:
    global AppID_v
    GameID: int=int(AppID_v)
    Register_Changes(appid=GameID)
    Run_Game(GameID)

def List_Games() -> list[dict[str, int | str]]:
    last_appid=0 
    max_results=50000
    url="https://api.steampowered.com/IStoreService/GetAppList/v1/"
    params = {
        "key": API_KEY_Steam,
        # "include_games": True,        # Nur Spiele (default)
        # "include_dlc": False,         # Keine DLCs
        # "include_software": False,    # Keine Software
        # "include_videos": False,       # Keine Videos
        # "include_hardware": False,     # Keine Hardware
        "max_results": max_results,    # Maximal 50.000 pro Seite
        # "last_appid": last_appid       # Startpunkt für die nächste Seite
    }
    print(f"🔄 Rufe Seite ab mit last_appid = {last_appid}...")
    response = requests.get(url, params=params)
    try:
        response.raise_for_status()
        data = response.json()  # pyright: ignore[reportAny]
        
        # Die Struktur der Antwort: Die Apps sind in 'response' -> 'apps'
        apps = data.get('response', {}).get('apps', [])  # pyright: ignore[reportAny]
        print(f"   ✅ {len(apps)} Apps auf dieser Seite erhalten.")  # pyright: ignore[reportAny]
        #print(response.headers)
        #print(response.text)
        if response.status_code==200:

            Resp=json.loads(response.text)  # pyright: ignore[reportAny]
            Games: list[dict[str, int | str]]=Resp["response"]["games"]  # pyright: ignore[reportAny]
            
            
            # with open('Games.txt', 'w') as filehandle:
            #     json.dump(Resp, filehandle)    
            return Games
        else:
            return [{"appid":int(),"name":"","playtime_forever":int()}]
        
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Fehler: {e}")
        print(response.text)
        return [{"appid":int(),"name":"","playtime_forever":int()}]

#! Still not fully functional. with every Registry it Forces a new Call, possibilty to Save the GamesList-owner in the Json Block as well, would be cool!
def List_Owned_Client_Games(force_get:bool)  -> list[dict[str, int | str]]:
    Games: list[dict[str, int | str]]
    try:
        if force_get ==False:
            with open("Games.txt") as f:
                    Resp = f.read()
        Resp=json.loads(Resp)  # pyright: ignore[reportAny, reportPossiblyUnboundVariable]
        Games=Resp["response"]["games"]   # pyright: ignore[reportAny]

        return Games
    except Exception as e:
            
        
        url="https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
        
        #DLC Fetching? https://api.steampowered.com/IStoreBrowseService/GetDLCForApps/v1/
        
        
        params = {
            "key": API_KEY_Steam,
            "steamid":USER_ID_Steam,
            "include_played_free_games":True,
            "include_appinfo":True,
            "include_extended_appinfo":False,
            "include_free_sub":True
            
        }
        #use IMG url as follows:
        #http://media.steampowered.com/steamcommunity/public/images/apps/APPID/IMG_ICON_URL.jpg, replacing "APPID" and "IMG_ICON_URL" as necessary.
        #http://media.steampowered.com/steamcommunity/public/images/apps/APPID/IMG_LOGO_URL.jpg, replacing "APPID" and "IMG_LOGO_URL" as necessary.
        
        #Source: https://wiki.teamfortress.com/wiki/WebAPI/GetOwnedGames

        response = requests.get(url, params=params)
        try:
            response.raise_for_status()
            #print(response.text)
            #print(response.headers)
            #print(response.text)
            if response.status_code==200:

                Resp=json.loads(response.text)  # pyright: ignore[reportAny]
                Games=Resp["response"]["games"]  # pyright: ignore[reportAny]
                
                with open('Games.txt', 'w') as filehandle:
                    json.dump(Resp, filehandle)    
                return Games
            else:
                return[{"appid":int(),"name":"","playtime_forever":int()}]

        except requests.exceptions.RequestException as e:
            print(f"   ❌ Fehler: {e}")
            print(response.text)
            return [{"appid":int(),"name":"","playtime_forever":int()}]


def List_Installed_Client_Games() -> set[int]:
    #Actually Returns a Set!
    with open(f"C:/Program Files (x86)/Steam/steamapps/libraryfolders.vdf") as f:
        library = f.read()
    Regex=re.compile(r'(?<="apps"\s{3}{\s{4})((\s*"\d+")*)')
    GameID_Locations_List: list[tuple[str]]=Regex.findall(library)
    GameID_set: set[int]=set[int]()
    Regex=re.compile(r'\d+')
    for i in range (0,len(GameID_Locations_List)):
        lib_content:str=str(GameID_Locations_List[i][0])
        List: list[int]=Regex.findall(lib_content)
        for data in List:  
            GameID_set.add(int(data))
    return GameID_set


#1988540=ZSC

def GUI_FindGameID() -> None:
        global GamesList
        global AppID_v
        global GName_v
        global Playtime_v
        global Installed_v
        global Achievement_Rate_v
        global Logo_Icon_URL
        GamesList=List_Owned_Client_Games(force_get=False)
        Name=NameField.get()
        GameID:int=0
        Data=GamesList[0]
        for i in range(0,len(GamesList)):
            Data=GamesList[i]
            if Name == Data["name"]:
                GameID= int(Data["appid"])
                Playtime_v=int(Data["playtime_forever"])
                break
        if GameID ==0:
            _=AppID.configure(text="Not Found")
            _=GName.configure(text="Check Spelling?")
            _=Playtime.configure(text="N/A")
            _=Installed.configure(text="N/A")
            AppID_v=0
            GName_v=""
            Installed_v=False
            Achievement_Rate_v=0
            _=Achievement_Rate.configure(text="N/A")
            _=GameIcon.configure(image=steam_pic)
            Logo_Icon_URL=""
        else:
            _=AppID.configure(text=GameID)
            AppID_v=GameID
            _=GName.configure(text=NameField.get())
            GName_v=NameField.get()
            _=Playtime.configure(text=str(round(Playtime_v/60,1)))
            Find_GameStats(GameID)
            Installed_v=Fetch_Install_State(GameID)
            _=Installed.configure(text=str(Installed_v))
            photo=FetchImage(Game=Data,use_SteamGrid=False,use_BlackWhite=True)             #? Switch the use_BlackWhite to get the normal Color 
            photo = ImageTk.PhotoImage(photo)
            _=GameIcon.configure(image=photo)
            GameIcon.image = photo   # pyright: ignore[reportAttributeAccessIssue]
            url=Data["img_icon_url"]
            Logo_Icon_URL=f"http://media.steampowered.com/steamcommunity/public/images/apps/{AppID_v}/{url}.jpg"
            # Logo_Icon_URL=""


def Fetch_Install_State(AppID:int) -> bool:
    Installed_GamesSet=List_Installed_Client_Games()
    if AppID in Installed_GamesSet:
        return True
    else:
        return False   


def Find_GameStats(AppID:int):
    global Achievement_Rate_v
    # Takes the AppID from the Currently "selected" Game
    #Not Called from GUI, only from other Functions


    #! Damit kann man sowohl die Achievement Completion Rate als auch sowas wie Rarest Achievement fetchen, Man kriegt sogar n link für die Bilder der Achievements!

    #Global Achievements Percentages

    # url="https://api.steampowered.com/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v2/"
    # params = {
    #     "gameid":AppID
    # }
    # try:
    #     response = requests.get(url, params=params)
    #     response.raise_for_status()
    #     #print(response.text)
        
    # except requests.exceptions.RequestException as e:
    #     print(f"   ❌ Fehler: {e}")
    #     print(response.text)
    

    # #print(response.headers)
    # #print(response.text)
    # if response.status_code==200:
    #     GameAchievements_G=json.loads(response.text)
    #     print(response.text)
    #     with open('Achievements_Global.txt', 'w') as filehandle:
    #         json.dump(response.text, filehandle)   
        
        


    #Game Stats and Achievements


    # url="https://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/"
    # params = {
    #     "key": API_KEY_Steam,
    #     "steamid":USER_ID_Steam,
    #     "appid":AppID
    # }
    # response: Response = requests.get(url, params=params)
    # try:
    #     response.raise_for_status()
    #     #print(response.text)
    #     #print(response.headers)
    #     #print(response.text)
    #     if response.status_code==200:
    #         GameAchievements=json.loads(response.text) 
    #         #print(response.text)
    #         with open('Achievements.txt', 'w') as filehandle:
    #             json.dump(response.text, filehandle)   
    # except requests.exceptions.RequestException as e:
    #     print(f"   ❌ Fehler: {e}")
    #     print(response.text)
    


        
        
        
    #User Achievements
    url="https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v1/"
    params = {
        "key": API_KEY_Steam,
        "steamid":USER_ID_Steam,
        "appid":AppID
    }
    response = requests.get(url, params=params)
    try:
        response.raise_for_status()
        #print(response.text)
        #print(response.headers)
        #print(response.text)
        if response.status_code==200:
            UserAchievements=json.loads(response.text)# pyright: ignore[reportAny]
            # print(response.text)
            Achievement_List=UserAchievements["playerstats"]["achievements"]# pyright: ignore[reportAny]
            Achievement_Nr=len(Achievement_List)# pyright: ignore[reportAny]
            Achieved_Nr=0
            for i in range(0,Achievement_Nr):
                Achievement=Achievement_List[i]# pyright: ignore[reportAny]
                if Achievement["achieved"]==1:
                    Achieved_Nr+=1
                    
            Achievement_Rate_v=round(Achieved_Nr/Achievement_Nr*100,2)
            _=Achievement_Rate.configure(text=str(Achievement_Rate_v)+"%")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Fehler: {e}")
        print(response.text)
        _=Achievement_Rate.configure(text="Not Public!")
    


        
        
    #User Stats

    # url="https://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v2/"
    # params = {
    #     "key": API_KEY_Steam,
    #     "steamid":USER_ID_Steam,
    #     "appid":AppID
    # }
    # try:
    #     response = requests.get(url, params=params)
    #     response.raise_for_status()
    #     #print(response.text)
        # #print(response.headers)
        # #print(response.text)
        # if response.status_code==200:
        #     UserStats=json.loads(response.text)
        #     print(response.text)
    # except requests.exceptions.RequestException as e:
    #     print(f"   ❌ Fehler: {e}")
    #     print(response.text)


def FetchImage(Game,use_SteamGrid:bool,use_BlackWhite:bool) -> Image:  # pyright: ignore[reportUnknownParameterType, reportMissingParameterType]
    """Types possible are Grids, Logos, Icons.\n
    Returns a PIL"""

    headers = {
            "Authorization": f"Bearer {API_KEY_SteamGrid}"
        }
    params = {
        'styles':'official',
        'dimensions':'256',
    }
    if use_SteamGrid==True:
        aID=AppID["text"]  # pyright: ignore[reportAny]
        if False:
            Query=requests.get(f"https://www.steamgriddb.com/api/v2/icons/steam/{aID}",headers=headers,params=params)  # pyright: ignore[reportUnreachable]
            requrl=re.findall((r'(?<="url":")[^"]*'),Query.text)
        Query=requests.get(f"https://www.steamgriddb.com/api/v2/icons/steam/{aID}",headers=headers,params=params)
        requrl=re.findall((r'(?<="url":")[^"]*'),Query.text)

        print(Query.status_code)
        url:str =  requrl[0].encode("utf-8").decode("unicode_escape").replace("\\/", "/")  # pyright: ignore[reportAny, reportRedeclaration]
    else:
        aID=Game["appid"]  # pyright: ignore[reportUnknownVariableType]
        iconURl=Game["img_icon_url"]  # pyright: ignore[reportUnknownVariableType]
        url:str =f"http://media.steampowered.com/steamcommunity/public/images/apps/{aID}/{iconURl}.jpg"
    response = requests.get(url)
    img = PILImage.open(BytesIO(response.content))#.convert('L')
    if use_BlackWhite ==True:
        img=img.convert(mode='L')
    return img 


#https://store.steampowered.com/app/1210320/Potion_Craft_Alchemist_Simulator/
#"C:\Program Files (x86)\Steam\Steam.exe"
#https://store.steampowered.com/app/2749770/Galaxy_Burger/
#https://partner.steamgames.com/doc/webapi/ISteamApps#GetAppBuilds
#https://steamapi.xpaw.me/#ISteamApps

#os.startfile(f"C:\Program Files (x86)\Steam\Steam.exe")
def GUI_FindSteamUser():
    #sets the USER_ID_Steam variable and Displays a connection status alongside the Nickname
    global USER_ID_Steam
    global USER_ID_Steam_Standard

    global ComboValues
    Steam_URL=UserNameField.get()
    path = urlparse(Steam_URL).path.rstrip('/')  # Remove trailing slash if any
    # Path will be something like '/profiles/76561197960435530' or '/id/gabeloganewell'
    parts = path.split('/')
    if len(parts)>3:
        _=Status_User.configure(text="Unable to resolve from Input, Check Input!")
        return
    print(path)
    if len(parts)>1:
        PathType=parts[1]
        id=parts[2]
        if PathType=="id":
            url="https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/"
            params = {
                "key": API_KEY_Steam,
                "vanityurl":id,
                "url_type":1
            }
            response = requests.get(url, params=params)
            try:
                response.raise_for_status()
                #print(response.text)
                #print(response.headers)
                #print(response.text)
                if response.status_code==200:
                    UserID=json.loads(response.text)  # pyright: ignore[reportAny]
                    USER_ID_Steam=UserID["response"]["steamid"]  # pyright: ignore[reportAny]
                    print(response.text)
            except requests.exceptions.RequestException as e:
                print(f"   ❌ Fehler: {e}")
                print(response.text)
            

        else:
            USER_ID_Steam=id
    elif len(parts)==1 and parts[0]=='':
        print("Falling Back to Standard ID!")
        USER_ID_Steam=USER_ID_Steam_Standard
    else:
        PathType=""
        id=parts[0]
        if len(id)==17 and id[0:2]=="765":
            USER_ID_Steam=id
        else:
            url="https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/"
            params = {
                "key": API_KEY_Steam,
                "vanityurl":id,
                "url_type":1
            }
            response = requests.get(url, params=params)
            try:
                response.raise_for_status()
                #print(response.text)
                            
                #print(response.headers)
                #print(response.text)
                if response.status_code==200:
                    UserID=json.loads(response.text)  # pyright: ignore[reportAny]
                    USER_ID_Steam=UserID["response"]["steamid"]  # pyright: ignore[reportAny]
                    print(response.text)
                    
            except requests.exceptions.RequestException as e:
                print(f"   ❌ Fehler: {e}")
                print(response.text)
    url="https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"
    params = {
        "key": API_KEY_Steam,
        "steamids":USER_ID_Steam
    }
    response = requests.get(url, params=params)
    try:
        response.raise_for_status()
        #print(response.text)
            #print(response.headers)
        #print(response.text)
        if response.status_code==200:
            UserInfo=json.loads(response.text)# pyright: ignore[reportAny]
            Nickname=UserInfo["response"]["players"][0]["personaname"]# pyright: ignore[reportAny]
            ProfileURL=UserInfo["response"]["players"][0]["profileurl"]# pyright: ignore[reportAny]
            ProfileAvatarURL=UserInfo["response"]["players"][0]["avatarfull"]# pyright: ignore[reportAny]
            print(response.text)
        else:
            Nickname=""
            ProfileURL=""
            ProfileAvatarURL=""
        Status="User "+ str(Nickname)+" registered under URL:\n"+str(ProfileURL)
        _=Status_User.configure(text=Status)    
        with urllib.request.urlopen(ProfileAvatarURL) as u:# pyright: ignore[reportAny]
            raw_data = u.read()  # pyright: ignore[reportAny]

        image = PILImage.open(BytesIO(raw_data))  # pyright: ignore[reportAny]
        photo = ImageTk.PhotoImage(image)
        _=Picture.configure(image=photo)
        Picture.image = photo   # pyright: ignore[reportAttributeAccessIssue]
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Fehler: {e}")
        print(response.text)
    tempList=List_Owned_Client_Games(force_get=True)
    temp: list[str]=[]
    for i in range (0,len(tempList)):  
        name=tempList[i]["name"]
        temp.append(str(name))
    ComboValues=sorted(temp)
    NameField['values']=ComboValues 


def PackageStats() -> dict[str, int | str | float]:
    global AppID_v
    global GName_v
    global Playtime_v
    global Installed_v
    global Achievement_Rate_v
    GameStats={"appid":AppID_v,"name":GName_v,"playtime_forever":Playtime_v,"achievement_rate":Achievement_Rate_v}
    return GameStats

def SendGameStats():
    GameStats=PackageStats()
    try:
        with open(f'{GameStats["appid"]}.txt', 'w') as filehandle:
            json.dump(GameStats, filehandle) 
            aID=GameStats["appid"]
            SendStatus["text"]=f"Success! Sent FileID {aID}"
            return True
    except Exception as e: 
        SendStatus["text"]=f"Error! Encounterd {e}"
        return False   


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





#BitMap-Processing. maybe even for dithering and the likes
#todo: Build small Interface. Build Way to save to External Flash Chip, then see how to get the Data Back again? Way to boot booth funcs?






from tkinter import ttk
from tkinter import Tk
#from tkinter.filedialog import askopenfilename



WIDTH, HEIGHT = 1000, 800  # Defines aspect ratio of window.

def maintain_aspect_ratio(event, aspect_ratio):  # pyright: ignore[reportUnknownParameterType, reportMissingParameterType]
    """ Event handler to override root window resize events to maintain the
        specified width to height aspect ratio.
    """
    if event.widget.master:  # Not root window?  # pyright: ignore[reportUnknownMemberType]
        return  # Ignore.

    # <Configure> events contain the widget's new width and height in pixels.
    new_aspect_ratio = event.width / event.height  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]

    # Decide which dimension controls.
    if new_aspect_ratio > aspect_ratio:
        # Use width as the controlling dimension.
        desired_width = event.width  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
        desired_height = int(event.width / aspect_ratio)   # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
    else:
        # Use height as the controlling dimension.
        desired_height = event.height  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
        desired_width = int(event.height * aspect_ratio)  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType]

    # Override if necessary.
    if event.width != desired_width or event.height != desired_height:  # pyright: ignore[ reportUnknownMemberType]
        # Manually give it the proper dimensions.
        event.widget.geometry(f'{desired_width}x{desired_height}') # pyright: ignore[ reportUnknownMemberType]
        return "break"  # Block further processing of this event.



IsConnected=Connect_Check()
GamesList=List_Owned_Client_Games(force_get=False)


if Steam_running() == False:
    path="C:/Program Files (x86)/Steam/Steam.exe"
    os.startfile(path)

#print(Find_GameID("Portal",GamesLists))
#print(Find_GameName(400,GamesLists))
root = Tk()
root.title("SGCS 0.1")

img = PILImage.open("Steam.png")
img=img.resize(size=[256,256])  # pyright: ignore[reportUnknownMemberType]
steam_pic=ImageTk.PhotoImage(img)
# root.geometry(f'{WIDTH}x{HEIGHT}')
# _=root.bind('<Configure>', lambda event: maintain_aspect_ratio(event, WIDTH/HEIGHT))


_=root.attributes('-fullscreen',False)  # pyright: ignore[reportUnknownMemberType]
base=ttk.Frame(root,padding=30,relief="groove")
base.pack(fill="both")
FrameThing=ttk.Frame(base,padding=30,relief="groove")
FrameThing.pack(side="left")

ttk.Button(FrameThing, text="Quit", command=root.destroy).pack()
Picture=ttk.Label(FrameThing,padding=10)
Picture.pack()
ttk.Label(FrameThing,text="\n").pack()

ttk.Label(FrameThing,text="Input your Steam URL, SteamID or Custom ID here").pack()
UserNameField=ttk.Entry(FrameThing)
UserNameField.pack()
ttk.Button(FrameThing, text="Find Steam Profile",command=GUI_FindSteamUser).pack()
Status_User=ttk.Label(FrameThing,text="\n")
Status_User.pack()


ttk.Label(FrameThing,text="\n").pack()
ttk.Label(FrameThing,text="Game Name").pack()
NameField=ttk.Combobox(FrameThing)
NameField.pack()
ComboValues=[]
ttk.Button(FrameThing, text="Find OWNED Game",command=GUI_FindGameID).pack()
ttk.Label(FrameThing,text="\n").pack()
ttk.Button(FrameThing, text="Send found Game-Stats",command=SendGameStats).pack()
SendStatus=ttk.Label(FrameThing,text="\n")
SendStatus.pack()

DiagnoseField=ttk.Frame(base,padding=30,relief="groove")
DiagnoseField.pack(side="left")
GameIcon=ttk.Label(DiagnoseField)
GameIcon.pack()
_=GameIcon.configure(image=steam_pic)

ttk.Label(DiagnoseField,text="App-ID:").pack()
AppID=ttk.Label(DiagnoseField,text="xxxxxx")
AppID.pack()
AppID_v:int=0


ttk.Label(DiagnoseField,text="\nGame Name:").pack()
GName=ttk.Label(DiagnoseField,text="xxxxxx")
GName.pack()
GName_v:str=""

Logo_Icon_URL:str=""

ttk.Label(DiagnoseField,text="\nPlaytime [h]:").pack()
Playtime=ttk.Label(DiagnoseField,text="xxxxxx")
Playtime.pack()
Playtime_v:int=0

ttk.Label(DiagnoseField,text="\nInstalled [True/False]:").pack()
Installed=ttk.Label(DiagnoseField,text="xxxxxx")
Installed.pack()
Installed_v:bool=False

ttk.Label(DiagnoseField,text="\nAchievement Rate [%]:").pack()
Achievement_Rate=ttk.Label(DiagnoseField,text="xxxxxx")
Achievement_Rate.pack()
Achievement_Rate_v:float=0

ttk.Label(DiagnoseField,text="\n").pack()
ttk.Button(DiagnoseField, text="Launch Game",command=Launch_Game).pack()

root.mainloop()



#New API:https://partner.steamgames.com/doc/webapi/IStoreService#GetAppList

# For Finding out stuff Like Achievement Completion Rate
# https://partner.steamgames.com/doc/webapi/ISteamUserStats
