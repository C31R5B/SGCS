#SGCS Steam Game Cartridge System
import requests
import os
import subprocess
import re

import json
from io import StringIO  
from io import BytesIO
import PIL
from PIL import Image


from PIL import Image as PILImage
import PIL.ImageOps 
import time
import serial

API_KEY='42ff83c071ec2ecb5c3bd4088a0d9f72'

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
    Games_string=requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v2/")
    if Games_string.status_code==200:
        Games_string=Games_string.text.removeprefix('{"applist":{"apps":[').removesuffix("]}}")
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


def Fill_GameID():
    GameID=Find_GameID(NameField.get(),GamesLists)
    KeyField.delete(0,END)
    KeyField.insert(0,GameID)

def Fill_GameName():
    GameID=Find_GameName(KeyField.get(),GamesLists)
    NameField.delete(0,END)
    NameField.insert(0,GameID)


#https://store.steampowered.com/app/1210320/Potion_Craft_Alchemist_Simulator/
#steam://rungameid/1637320
#"C:\Program Files (x86)\Steam\Steam.exe"
#https://store.steampowered.com/app/2749770/Galaxy_Burger/
#https://partner.steamgames.com/doc/webapi/ISteamApps#GetAppBuilds
#https://steamapi.xpaw.me/#ISteamApps
IsConnected=Connect_Check()
GamesLists=List_Games()

if Steam_running() == False:
    os.startfile("C:\Program Files (x86)\Steam\Steam.exe")

#os.startfile(f"C:\Program Files (x86)\Steam\Steam.exe")

def FetchImage():

    headers = {
            "Authorization": f"Bearer {API_KEY}"
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


# ======== CONFIG ========
#filename = "hornchen.jpg"
filename="apetrui.png"
width, height = 200, 200   # Displaygröße
output_name = "epd_image"  # Name des C-Arrays
port = "COM6"        # deinen COM-Port anpassen
Baudrate = 115200
Chunk_Size = 256     # Größe der Blöcke für STM32
# ========================



def SendImage():
    #---------------------------------------------------------------------------------------------------
    #---------------------------------------------------------------------------------------------------
    # Bild öffnen, in 1-bit konvertieren
    #img = Image.open(filename).convert('1')  
    #img = img.resize((width, height))  # sicherstellen, dass es passt

    # Bild öffnen, in Graustufen konvertieren
    #!img = Image.open(filename).convert('L')  # 'L' = 8-bit grayscale
    img=FetchImage()
    img = img.resize((width, height), PILImage.Resampling.LANCZOS)

    # Floyd-Steinberg Dithering auf 1-Bit anwenden
    img_dithered = img.convert('1')  # PIL macht automatisch FS-Dither

    img_dithered =PIL.ImageOps.invert(img_dithered)
    img_dithered=PIL.ImageOps.mirror(img_dithered)


    data = []

    for y in range(height):
        for x in range(0, width, 8):
            byte = 0
            for bit in range(8):
                px = img_dithered.getpixel((x + bit, y))
                # Pillow: 0 = schwarz, 255 = weiß
                if px == 0:
                    byte |= (1 << (7 - bit))  # MSB zuerst
            data.append(byte)

    epd_bytes = bytearray()
    for y in range(height):
        byte = 0
        bit_count = 0
        for x in range(width):
            pixel = img_dithered.getpixel((x, y))
            byte = (byte << 1) | (0 if pixel else 1)  # 0=weiß, 1=schwarz
            bit_count += 1
            if bit_count == 8:
                epd_bytes.append(byte)
                byte = 0
                bit_count = 0
        if bit_count != 0:  # Restbits auffüllen
            byte = byte << (8 - bit_count)
            epd_bytes.append(byte)

    print(f"Bytes für E-Ink: {len(epd_bytes)}")

    # ------------------------
    # Verbindung öffnen und senden
    # ------------------------
    ser = serial.Serial(port, Baudrate, timeout=1)
    time.sleep(2)  # STM bereit machen

    for i in range(0, len(epd_bytes), Chunk_Size):
        chunk = epd_bytes[i:i+Chunk_Size]
        ser.write(chunk)
        time.sleep(0.01)  # STM kann verarbeiten

    print("Bild gesendet!")
    ser.close()

    # Ausgabe als C-Array
    """print(f"const uint8_t {output_name}[] = {{")
    for i, b in enumerate(data):
        print(f"0x{b:02X}, ", end='')
        if (i + 1) % 16 == 0:
            print()
    print("\n};")"""""

    #---------------------------------------------------------------------------------------------------
    #---------------------------------------------------------------------------------------------------
from tkinter import *
from tkinter import ttk
from tkinter import Tk
from tkinter.filedialog import askopenfilename

def SelectImage():
    filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
    print(filename)
    #---------------------------------------------------------------------------------------------------
    #---------------------------------------------------------------------------------------------------
    # Bild öffnen, in 1-bit konvertieren
    #img = Image.open(filename).convert('1')  
    #img = img.resize((width, height))  # sicherstellen, dass es passt

    # Bild öffnen, in Graustufen konvertieren
    img = PILImage.open(filename).convert('L')  # 'L' = 8-bit grayscale
    img = img.resize((width, height), PILImage.Resampling.LANCZOS)
    # Floyd-Steinberg Dithering auf 1-Bit anwenden
    img_dithered = img.convert('1')  # PIL macht automatisch FS-Dither

    img_dithered =PIL.ImageOps.invert(img_dithered)
    img_dithered=PIL.ImageOps.mirror(img_dithered)

    data = []

    for y in range(height):
        for x in range(0, width, 8):
            byte = 0
            for bit in range(8):
                px = img_dithered.getpixel((x + bit, y))
                # Pillow: 0 = schwarz, 255 = weiß
                if px == 0:
                    byte |= (1 << (7 - bit))  # MSB zuerst
            data.append(byte)

    epd_bytes = bytearray()
    for y in range(height):
        byte = 0
        bit_count = 0
        for x in range(width):
            pixel = img_dithered.getpixel((x, y))
            byte = (byte << 1) | (0 if pixel else 1)  # 0=weiß, 1=schwarz
            bit_count += 1
            if bit_count == 8:
                epd_bytes.append(byte)
                byte = 0
                bit_count = 0
        if bit_count != 0:  # Restbits auffüllen
            byte = byte << (8 - bit_count)
            epd_bytes.append(byte)

    print(f"Bytes für E-Ink: {len(epd_bytes)}")

    # ------------------------
    # Verbindung öffnen und senden
    # ------------------------
    ser = serial.Serial(port, Baudrate, timeout=1)
    time.sleep(2)  # STM bereit machen

    for i in range(0, len(epd_bytes), Chunk_Size):
        chunk = epd_bytes[i:i+Chunk_Size]
        ser.write(chunk)
        time.sleep(0.01)  # STM kann verarbeiten

    print("Bild gesendet!")
    ser.close()

    # Ausgabe als C-Array
    """print(f"const uint8_t {output_name}[] = {{")
    for i, b in enumerate(data):
        print(f"0x{b:02X}, ", end='')
        if (i + 1) % 16 == 0:
            print()
    print("\n};")"""""

    #---------------------------------------------------------------------------------------------------
    #---------------------------------------------------------------------------------------------------
    


#print(Find_GameID("Portal",GamesLists))
#print(Find_GameName(400,GamesLists))
root = Tk()
root.title("SGCS 0.1")
root.attributes("-fullscreen", False)
FrameThing=ttk.Frame(root,padding=30)
FrameThing.pack()
ttk.Button(FrameThing, text="Quit", command=root.destroy).pack()
ttk.Button(FrameThing, text="Launch Game",command=Launch_Game).pack()
ttk.Label(FrameThing,text="GameID").pack()
ttk.Button(FrameThing, text="Get GameName",command=Fill_GameName).pack()
KeyField=ttk.Entry(FrameThing,text="GAMEID")
KeyField.pack()
IDThing=ttk.Frame(root,padding=30)
IDThing.pack()
ttk.Label(IDThing,text="GameID from Name").pack()
ttk.Button(IDThing, text="Get GameID",command=Fill_GameID).pack()
NameField=ttk.Entry(IDThing,text="GAMENAME")
NameField.pack()


ttk.Label(root,text="Image Selection/Sending").pack()
ttk.Button(root,text="Send Game Image",command=SendImage).pack()
ttk.Label(root,text="OR").pack()
ttk.Button(root,text="Select and Send Image from Disk",command=SelectImage).pack()
root.mainloop()



#New API:https://partner.steamgames.com/doc/webapi/IStoreService#GetAppList