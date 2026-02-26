#SGCS Steam Game Cartridge System
import requests
import os
import subprocess
import re

import json
import urllib
from io import StringIO  
from io import BytesIO


from PIL import Image as PILImage

try:
    with open("C:/Users/thecr/Nextcloud/AAA_SCGS/Key.txt") as f:
        key_data = f.readlines()
except Exception as e:
    with open("C:/Users/user/Nextcloud/AAA_SCGS/Key.txt") as f:
        key_data = f.readlines()
        
        
key_data=key_data[0].split()

API_KEY_Steam=key_data[1]
API_KEY_SteamGrid=key_data[3]
USER_ID_Steam=key_data[5]
key_data=""


def Connect_Check():
    try:
        requests.get("https://store.steampowered.com/",timeout=1)
        print("Internetverbindung erfolgreich!")
        return True         
    except requests.ConnectionError as e:
        print("Internetverbindung fehlgeschlagen", e)
        return False
def Steam_running():
    tasks = subprocess.check_output("tasklist").decode("utf-8").lower()
    return "steam.exe" in tasks
def Run_Game(GameID:int):
    os.startfile(f"steam://rungameid/{GameID}")

def Launch_Game():
    global AppID_v
    GameID=int(AppID_v)
    Run_Game(GameID)

def List_Games():
    
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

    try:
        print(f"🔄 Rufe Seite ab mit last_appid = {last_appid}...")
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Die Struktur der Antwort: Die Apps sind in 'response' -> 'apps'
        apps = data.get('response', {}).get('apps', [])
        print(f"   ✅ {len(apps)} Apps auf dieser Seite erhalten.")

        
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Fehler: {e}")
    
  
    #print(response.headers)
    #print(response.text)
    if response.status_code==200:

        Resp=json.loads(response.text)
        Games=Resp["response"]
        Gamecount=Games["game_count"]
        Games=Games["games"]
        
        
        # with open('Games.txt', 'w') as filehandle:
        #     json.dump(Resp, filehandle)    
        return Games
    else:
        return {}

def List_Owned_Client_Games():
    try:
        with open("Games.txt") as f:
                Resp = f.read()
        Resp=json.loads(Resp)
        Games=Resp["response"]
        Gamecount=Games["game_count"]
        Games=Games["games"] 
        
        return Games
    except Exception as e:
            
        
        url="https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
        
        #DLC Fetching? https://api.steampowered.com/IStoreBrowseService/GetDLCForApps/v1/
        
        
        params = {
            "key": API_KEY_Steam,
            "steamid":USER_ID_Steam,
            "include_played_free_games":True,
            "include_appinfo":True,
            "include_extended_appinfo":True,
            "include_free_sub":True
            
        }
        #Returns like this IF "include_extended_appinfo":False :
        #{"appid":210970,"name":"The Witness","playtime_forever":1896,"img_icon_url":"5406b4e33862420abfb60a23e581cad2a1ec85f7","has_community_visible_stats":true,"playtime_windows_forever":363,"playtime_mac_forever":0,"playtime_linux_forever":0,"playtime_deck_forever":0,"rtime_last_played":1639273581,"playtime_disconnected":0}
        #{"appid":8190,"name":"Just Cause 2","playtime_forever":49,"img_icon_url":"73582e392a2b9413fe93b011665a5b9cf26ff175","has_community_visible_stats":true,"playtime_windows_forever":0,"playtime_mac_forever":0,"playtime_linux_forever":0,"playtime_deck_forever":0,"rtime_last_played":1508424672,"playtime_disconnected":0}
        #use IMG url as follows:
        #http://media.steampowered.com/steamcommunity/public/images/apps/APPID/IMG_ICON_URL.jpg, replacing "APPID" and "IMG_ICON_URL" as necessary.
        #http://media.steampowered.com/steamcommunity/public/images/apps/APPID/IMG_LOGO_URL.jpg, replacing "APPID" and "IMG_LOGO_URL" as necessary.
        
        #Source: https://wiki.teamfortress.com/wiki/WebAPI/GetOwnedGames
        
        #sonst mit =True:
        #{"appid":220200,"name":"Kerbal Space Program","playtime_forever":28444,"img_icon_url":"6dc8c1377c6b0ffedaeaec59c253f8c33fb3e62b","playtime_windows_forever":17874,"playtime_mac_forever":0,"playtime_linux_forever":0,"playtime_deck_forever":0,"rtime_last_played":1736608738,"capsule_filename":"library_600x900.jpg","has_workshop":true,"has_market":false,"has_dlc":true,"playtime_disconnected":0}
            
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            #print(response.text)
            
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Fehler: {e}")
            print(response.text)
        
    
        #print(response.headers)
        #print(response.text)
        if response.status_code==200:

            Resp=json.loads(response.text)
            Games=Resp["response"]
            Gamecount=Games["game_count"]
            Games=Games["games"]
            
            with open('Games.txt', 'w') as filehandle:
                json.dump(Resp, filehandle)    
            return Games
        else:
            return {}

def List_Installed_Client_Games():
    #Actually Returns a Set!
    with open(f"C:/Program Files (x86)/Steam/steamapps/libraryfolders.vdf") as f:
        library = f.read()
    libraryFolderHeader='"libraryfolders"\n{\n\t"0"\n\t{\n\t\t"path"\t\t"C:\\\\Program Files (x86)\\\\Steam"\n\t\t"label"\t\t""\n\t\t"contentid"\t\t"1611306386609458316"\n\t\t"totalsize"\t\t"0"\n\t\t"update_clean_bytes_tally"\t\t"2148087031"\n\t\t"time_last_update_verified"\t\t"1771937665"\n\t\t'
    library =library.removeprefix(libraryFolderHeader)
    Regex=re.compile(r'(?<="apps"\s{3}{\s{4})((\s*"\d+")*)')
    GameID_Locations_List=Regex.findall(library)
    GameID_set=set()
    Regex=re.compile(r'\d+')
    for i in range (0,len(GameID_Locations_List)):
        List=GameID_Locations_List[i]
        List=List[0]
        List=Regex.findall(List)
        for data in List:
            GameID_set.add(data)
    return GameID_set


#1988540=ZSC
def Find_GameID(GameName:str,GamesLists):
#    if IsConnected == True:
#        headers = {
#            "Authorization": f"Bearer {API_KEY}"
#        }
#        Query=requests.get(f"https://@www.steamgriddb.com/api/v2/search/autocomplete/{GameName}",headers=headers)
#        print(Query.headers)
#        print(Query.text)'
#    else:
        GameIDs=list(GamesLists["ID_L"])
        GameNames=list(GamesLists["Name_L"])
        return GameIDs[GameNames.index(GameName)]

def Find_GameName(GameID:int,GamesLists):
#    if IsConnected == True:
#        Query=requests.get(f"https://www.steamgriddb.com/api/v2/games/id/{GameID}")
#    else:
        GameIDs=list(GamesLists["ID_L"])
        GameNames=list(GamesLists["Name_L"])
        return GameNames[GameIDs.index(str(GameID))]

def GUI_FindGameID():
        global GamesList
        global AppID_v
        global GName_v
        global Playtime_v
        global Installed_v
        global Achievement_Rate_v
        Name=NameField.get()
        GameID=0
        for i in range(0,len(GamesList)):
            Data=GamesList[i]
            if Name == Data["name"]:
                GameID= Data["appid"]
                Playtime_v=Data["playtime_forever"]
                break
        if GameID ==0:
            AppID.configure(text="Not Found")
            GName.configure(text="Check Spelling?")
            Playtime.configure(text="N/A")
            Installed.configure(text="N/A")
            AppID_v=0
            GName_v=""
            Installed_v=False
            Achievement_Rate_v=0
            Achievement_Rate.configure(text="N/A")
        else:
            AppID.configure(text=GameID)
            AppID_v=GameID
            GName.configure(text=NameField.get())
            GName_v=NameField.get()
            Playtime.configure(text=str(round(Playtime_v/60,1)))
            Find_GameStats(GameID)
            Installed_v=Fetch_Install_State(GameID)
            Installed.configure(text=str(Installed_v))
            
        
def Fetch_Install_State(AppID):
    Installed_GamesSet=List_Installed_Client_Games()
    if AppID in Installed_GamesSet:
        return True
    else:
        return False
       
        
def Find_GameStats(AppID):
    global Achievement_Rate_v
# Takes the AppID from the Currently "selected" Game
#Not Called from GUI, only from other Functions


#! Damit kann man sowohl die Achievement Completion Rate als auch sowas wie Rarest Achievement fetchen, Man kriegt sogar n link für die Bilder der Achievements!

#Global Achievements Percentages

    url="https://api.steampowered.com/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v2/"
    params = {
        "gameid":AppID
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        #print(response.text)
        
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Fehler: {e}")
        print(response.text)
    

    #print(response.headers)
    #print(response.text)
    if response.status_code==200:
        GameAchievements_G=json.loads(response.text)
        print(response.text)
        with open('Achievements_Global.txt', 'w') as filehandle:
            json.dump(response.text, filehandle)   
        
        


#Game Stats and Achievements


    url="https://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/"
    params = {
        "key": API_KEY_Steam,
        "steamid":USER_ID_Steam,
        "appid":AppID
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        #print(response.text)
        
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Fehler: {e}")
        print(response.text)
    

    #print(response.headers)
    #print(response.text)
    if response.status_code==200:
        GameAchievements=json.loads(response.text)
        #print(response.text)
        with open('Achievements.txt', 'w') as filehandle:
            json.dump(response.text, filehandle)   
        
        
        
#User Achievements
    url="https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v1/"
    params = {
        "key": API_KEY_Steam,
        "steamid":USER_ID_Steam,
        "appid":AppID
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        #print(response.text)
        
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Fehler: {e}")
        print(response.text)
    

    #print(response.headers)
    #print(response.text)
    if response.status_code==200:
        UserAchievements=json.loads(response.text)
        # print(response.text)
        Achievement_List=UserAchievements["playerstats"]
        Achievement_List=Achievement_List["achievements"]
        Achievement_Nr=len(Achievement_List)
        Achieved_Nr=0
        for i in range(0,Achievement_Nr):
            Achievement=Achievement_List[i]
            if Achievement["achieved"]==1:
                Achieved_Nr+=1
                
        Achievement_Rate_v=round(Achieved_Nr/Achievement_Nr*100,2)
        Achievement_Rate.configure(text=str(Achievement_Rate_v)+"%")
        
        
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
        
    # except requests.exceptions.RequestException as e:
    #     print(f"   ❌ Fehler: {e}")
    #     print(response.text)
    

    # #print(response.headers)
    # #print(response.text)
    # if response.status_code==200:
    #     UserStats=json.loads(response.text)
    #     print(response.text)




def FetchImage():

    headers = {
            "Authorization": f"Bearer {API_KEY_SteamGrid}"
        }
    params = {
        'styles':'official',
        }
    IconQuery=requests.get(f"https://www.steamgriddb.com/api/v2/icons/steam/{AppID.get()}",headers=headers,params=params)
    IconURL=re.findall((r'(?<="url":")[^"]*'),IconQuery.text)
    print(IconQuery.status_code)
    url = IconURL[0].encode("utf-8").decode("unicode_escape").replace("\\/", "/")
    response = requests.get(url)
    img = PILImage.open(BytesIO(response.content)).convert('L')
    return img 


#https://store.steampowered.com/app/1210320/Potion_Craft_Alchemist_Simulator/
#steam://rungameid/1637320
#"C:\Program Files (x86)\Steam\Steam.exe"
#https://store.steampowered.com/app/2749770/Galaxy_Burger/
#https://partner.steamgames.com/doc/webapi/ISteamApps#GetAppBuilds
#https://steamapi.xpaw.me/#ISteamApps
IsConnected=Connect_Check()
GamesList=List_Owned_Client_Games()


if Steam_running() == False:
    path="C:/Program Files (x86)/Steam/Steam.exe"
    os.startfile(path)

#os.startfile(f"C:\Program Files (x86)\Steam\Steam.exe")



#BitMap-Processing. maybe even for dithering and the likes
#todo: Build small Interface. Build Way to save to External Flash Chip, then see how to get the Data Back again? Way to boot booth funcs?



from tkinter import *
from tkinter import ttk
from tkinter import Tk
from tkinter.filedialog import askopenfilename

#print(Find_GameID("Portal",GamesLists))
#print(Find_GameName(400,GamesLists))
root = Tk()
root.title("SGCS 0.1")
root.attributes("-fullscreen", False)
FrameThing=ttk.Frame(root,padding=30,relief="groove")
FrameThing.pack(side="left")
ttk.Button(FrameThing, text="Quit", command=root.destroy).pack()
ttk.Label(FrameThing,text="\n").pack()
ttk.Label(FrameThing,text="GameName").pack()
NameField=ttk.Entry(FrameThing)
NameField.pack()
ttk.Label(FrameThing,text="\n").pack()
ttk.Button(FrameThing, text="Find OWNED Game",command=GUI_FindGameID).pack()

DiagnoseField=ttk.Frame(root,padding=30,relief="groove")
DiagnoseField.pack(side="left")
ttk.Label(DiagnoseField,text="App-ID:").pack()
AppID=ttk.Label(DiagnoseField,text="xxxxxx")
AppID.pack()
AppID_v=0


ttk.Label(DiagnoseField,text="\nGame Name:").pack()
GName=ttk.Label(DiagnoseField,text="xxxxxx")
GName.pack()
GName_v=""



ttk.Label(DiagnoseField,text="\nPlaytime [h]:").pack()
Playtime=ttk.Label(DiagnoseField,text="xxxxxx")
Playtime.pack()
Playtime_v=0

ttk.Label(DiagnoseField,text="\nInstalled [True/False]:").pack()
Installed=ttk.Label(DiagnoseField,text="xxxxxx")
Installed.pack()
Installed_v=False

ttk.Label(DiagnoseField,text="\nAchievement Rate [%]:").pack()
Achievement_Rate=ttk.Label(DiagnoseField,text="xxxxxx")
Achievement_Rate.pack()
Achievement_Rate_v=0

ttk.Label(DiagnoseField,text="\n").pack()
ttk.Button(DiagnoseField, text="Launch Game",command=Launch_Game).pack()


root.mainloop()



#New API:https://partner.steamgames.com/doc/webapi/IStoreService#GetAppList

# For Finding out stuff Like Achievement Completion Rate
# https://partner.steamgames.com/doc/webapi/ISteamUserStats
