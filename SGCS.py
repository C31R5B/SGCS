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
    GameID=int(KeyField.get())
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
        Games_string=response.text.removeprefix('{"applist":{"apps":[').removesuffix("]}}")
        #Games_List=Games_List.removeprefix('{"applist":{"apps":[')
        #Games_List=Games_List.removesuffix("]}}")
        #,{"appid":400,"name":"Portal"},{"appid":410,"name":"Portal: First Slice"},
        #Games_List=re.search('"appid":',Games_List)
        test=re.findall(r'\b4[0-9]*,', Games_string)
        EntryR = re.compile(r"\{[^}]*\}", re.IGNORECASE)
        Games_List=EntryR.findall(Games_string)
        GameIDR=re.compile(r'(?<="appid":)[0-9]+')
        GameID_List=GameIDR.findall(Games_string)
        GameNameR=re.compile(r'(?<="name":")(?:[^"]|"")*')
        GameName_List=GameNameR.findall(Games_string)
        
        #Games_Dict=dict(zip(GameID_List, GameName_List))
            
        return {"GIDL":GameID_List, "GNL":GameName_List}
    else:
        return {"GIDL":[],"GNL":[]}

def List_Client_Games():
    
    last_appid=0 
    max_results=50000
    
    url="https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
    params = {
        "key": API_KEY_Steam,
        "steamid":USER_ID_Steam,
        "include_played_free_games":True,
        "include_appinfo":True,
        "include_extended_appinfo":True
        
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
        data = response.json()
        print(response.text)
        
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Fehler: {e}")
        print(response.text)
    
  
    #print(response.headers)
    #print(response.text)
    if response.status_code==200:
        Games_string=response.text.removeprefix('{"applist":{"apps":[').removesuffix("]}}")
        #Games_List=Games_List.removeprefix('{"applist":{"apps":[')
        #Games_List=Games_List.removesuffix("]}}")
        #,{"appid":400,"name":"Portal"},{"appid":410,"name":"Portal: First Slice"},
        #Games_List=re.search('"appid":',Games_List)
        test=re.findall(r'\b4[0-9]*,', Games_string)
        EntryR = re.compile(r"\{[^}]*\}", re.IGNORECASE)
        Games_List=EntryR.findall(Games_string)
        GameIDR=re.compile(r'(?<="appid":)[0-9]+')
        GameID_List=GameIDR.findall(Games_string)
        GameNameR=re.compile(r'(?<="name":")(?:[^"]|"")*')
        GameName_List=GameNameR.findall(Games_string)
        
        #Games_Dict=dict(zip(GameID_List, GameName_List))
            
        return {"GCIDL":GameID_List, "GCNL":GameName_List}
    else:
        return {"GCIDL":[],"GCNL":[]}

def List_Installed_Client_Games():
    with open(f"C:/Program Files (x86)/Steam/steamapps/libraryfolders.vdf") as f:
        library = f.readlines()
    library =library[10:]
    GameIDR=re.compile(r'[0-9]+')
    GameID_List=GameIDR.findall(library)
    GameID_List=[]
    GameName_List=[]
    if True:
        return {"GICIDL":GameID_List, "GICNL":GameName_List}
    else:
        return {"GICIDL":[],"GICNL":[]}


def Find_GameID(GameName:str,GamesLists):
#    if IsConnected == True:
#        headers = {
#            "Authorization": f"Bearer {API_KEY}"
#        }
#        Query=requests.get(f"https://@www.steamgriddb.com/api/v2/search/autocomplete/{GameName}",headers=headers)
#        print(Query.headers)
#        print(Query.text)'
#    else:
        GameIDs=list(GamesLists["GIDL"])
        GameNames=list(GamesLists["GNL"])
        return GameIDs[GameNames.index(GameName)]

def Find_GameName(GameID:int,GamesLists):
#    if IsConnected == True:
#        Query=requests.get(f"https://www.steamgriddb.com/api/v2/games/id/{GameID}")
#    else:
        GameIDs=list(GamesLists["GIDL"])
        GameNames=list(GamesLists["GNL"])
        return GameNames[GameIDs.index(str(GameID))]




#https://store.steampowered.com/app/1210320/Potion_Craft_Alchemist_Simulator/
#steam://rungameid/1637320
#"C:\Program Files (x86)\Steam\Steam.exe"
#https://store.steampowered.com/app/2749770/Galaxy_Burger/
#https://partner.steamgames.com/doc/webapi/ISteamApps#GetAppBuilds
#https://steamapi.xpaw.me/#ISteamApps
IsConnected=Connect_Check()
GamesLists=List_Client_Games()
IGamesList=List_Installed_Client_Games()

if Steam_running() == False:
    os.startfile(f"C:\Program Files (x86)\Steam\Steam.exe")

#os.startfile(f"C:\Program Files (x86)\Steam\Steam.exe")

def FetchImage():

    headers = {
            "Authorization": f"Bearer {API_KEY_SteamGrid}"
        }
    params = {
'styles':'official',
}
    IconQuery=requests.get(f"https://www.steamgriddb.com/api/v2/icons/steam/{KeyField.get()}",headers=headers,params=params)
    IconURL=re.findall((r'(?<="url":")[^"]*'),IconQuery.text)
    print(IconQuery.status_code)
    url = IconURL[0].encode("utf-8").decode("unicode_escape").replace("\\/", "/")
    response = requests.get(url)
    img = PILImage.open(BytesIO(response.content)).convert('L')
    return img 



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
FrameThing=ttk.Frame(root,padding=30)
FrameThing.pack()
ttk.Button(FrameThing, text="Quit", command=root.destroy).pack()
ttk.Button(FrameThing, text="Launch Game",command=Launch_Game).pack()
ttk.Label(FrameThing,text="AppID").pack()
KeyField=ttk.Entry(FrameThing)
KeyField.pack()

root.mainloop()



#New API:https://partner.steamgames.com/doc/webapi/IStoreService#GetAppList