import discord
import json
import random

from discord.ext import commands

PREFIX = "~"
NO_LOGS = ["156019409658314752", "660613170636914698"]
TICKET_CATEGORY_COMPLETE = 740635626373775480
TICKET_CATEGORY_CONTROL = 740608896997130292
TICKET_CATEGORY_USER = 740624628082540694
WELCOME_CHANNEL = 740323922096029696

def CREATECODE():
    b32 = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "2", "3", "4", "5", "6", "7"]
    out = ""
    for x in range(6): #pylint: disable=unused-variable
        out += random.choice(b32)
    return out 
    
def FILEREAD(fpath): 
    with open(f"local_Store/{fpath}", "r") as file:
        return file.read()

def JSONREAD(fpath):
    with open(f"local_Store/{fpath}", "r") as file:
        return json.load(file)
    
def JSONWRITE(fpath, data):
    with open(f"local_Store/{fpath}", "w") as file:
        json.dump(data, file)

def QUERY_CODE(code):
    userdata = JSONREAD("userdata.json")
    for key, value in userdata.items():
        for k, v in value.items():
            if k == "code" and v == code: return key
    return None

def QUERY_PAIR(channel):
    pairs = JSONREAD("channel_pairs.json")
    for element in pairs:
        if element[0] == channel: return element[1]
        elif element[1] == channel: return element[0]
    return None

def USERDATA_READ(user):
    full_data = JSONREAD("userdata.json")
    try:
        return full_data[str(user)]
    except:
        return full_data["default"]

def USERDATA_WRITE(user, data):
    full_data = JSONREAD("userdata.json")
    full_data[str(user)] = data
    JSONWRITE("userdata.json", full_data)
