# imports
from time import sleep

# 2D array of rooms
map = [
    ## Room types in the dungeon:
    # Entrance rooms - Usually have puzzles to unlock dungeons - Lit + Unlocked
    # Dungeon rooms - Lots of enemies and items - Unlit + Unlocked
    # Special rooms - Usually Unlit + Locked

    ## Name, Description (Regular), Room Connections, Lit?, Locked?
    # Starting rooms
    ["Gate", "A large, rusty metal gate. It's where you entered.", [1], True, False],
    ["Main Hall", "", [0, 2, 5, 7], True, False],

    # East rooms
    ["East Entrance", "", [1, 3, 4], True, False],
    ["Shop", "", [2, 4], True, False],
    ["East Dungeon", "", [2, 3, 8], False, False],

    # West rooms
    ["West Entrance", "", [1, 6 ,9], True, False],
    ["West Dungeon", "", [5, 10], False, False],

    # Locked rooms
    ["North Entrance", "", [1, 8, 9], False, True],
    ["Vault", "", [4, 7], False, True],
    ["Library", "", [5, 7], False, True],
    ["Throne Room", "", [6], True, True],
]

# 2D array of items
items = [
    # Item type 0 = Useless item
    # Item type 1 = Key
    # Item type 2 = Torch

    # Room -1 = player's inventory
    ## Name, Room, Item Type
    ["Skeleton Plushie", 1, 0]
]

# narrate speech word by word
def narrate(txt):
    txt_split = txt.split()
    for word in txt_split:
        print(word, end=" ", flush=True)
        sleep(0.15)
    print()

            
# choice menu - main loop
def menu():
    # globals
    global in_game
    global room
    global prev_room
    global hp
        
    # the current room - game starts at the gate
    room = map[0]
    # player starts at 20 hp
    hp = 20
    # playing
    in_game = True

    while in_game:
        # print the room description
        describe_room()

        choice = int(input("\n────────────────────────\nWhat will you do?\n[0] Move\n[1] Items\n - "))
        # move
        if choice == 0:
            move_rooms()
        # open inventory
        elif choice == 1:
            print("\nINVENTORY:\n")
            for i in items:
                if i[1] == -1:
                    print(f"{i[0]}")


# main loop for moving
def move_rooms():
    global room
    try:
        next_room = int(input("\nWhich room would you like to move to? (room no.) - "))

        # if the user enters a non-existent room
        if next_room < 0 or next_room >= len(map):
            print("\n[!] This room doesn't exist. Please enter a different integer.")

        # if the user is already in that room
        elif map[next_room] == room:
            print("\n[!] You are already in that room.")

        # if the room is not connected through a door
        elif next_room not in connected_rooms:
            print("\n[!] That room is too far away. You can only go through doors in your current room.")
        
        # if the user leaves the house
        elif next_room == 0:
            confirm_leave = input("\nYou approach the Gate. Are you sure you want to leave the dungeon? (y/n) - ")
            # confirm?
            if confirm_leave == "y":
                in_game = False
                print("\nYou crawl through the gate and sprint outside, not looking back.")
            else:
                print("\nYou decide to keep going.")

        # if the door is locked
        elif map[next_room][4]:
            print("\n[!] The door is locked.")
        
        # if the room is valid
        else:
            # move to the appropriate room
            prev_room = room
            room = map[next_room]

    except ValueError:
        # if user enters an invalid input
        print("\n[!] Invalid input. Please enter an integer.")
    
    # go back to the select menu by ending the function

# gives the name and description of the room
def describe_room():
    global connected_rooms

    print(f"You are in the [{map.index(room)}] {room[0]}.\n")
    if room[3]:
        print(f"{room[1]}\nThe doors in this room lead to:")
        connected_rooms = room[2]
        for i in connected_rooms:
            print(f"[{i}] {map[i][0]}")
        for i in items:
            if i[1] == map.index(room):
                if input(f"\nYou found the {i[0]}. Pick it up? (y/n) - ") == "y":
                    items[items.index(i)][1] = -1
                    print(f"You got the {i[0]}.")
                else:
                    print(f"You left the {i[0]} in the room.")
    else:
        print("It's too dark to see anything.")

## start the game

print("""
▓█████▄  █    ██  ███▄    █   ▄████ ▓█████  ▒█████   ███▄    █ 
▒██▀ ██▌ ██  ▓██▒ ██ ▀█   █  ██▒ ▀█▒▓█   ▀ ▒██▒  ██▒ ██ ▀█   █ 
░██   █▌▓██  ▒██░▓██  ▀█ ██▒▒██░▄▄▄░▒███   ▒██░  ██▒▓██  ▀█ ██▒
░▓█▄   ▌▓▓█  ░██░▓██▒  ▐▌██▒░▓█  ██▓▒▓█  ▄ ▒██   ██░▓██▒  ▐▌██▒
░▒████▓ ▒▒█████▓ ▒██░   ▓██░░▒▓███▀▒░▒████▒░ ████▓▒░▒██░   ▓██░
 ▒▒▓  ▒ ░▒▓▒ ▒ ▒ ░ ▒░   ▒ ▒  ░▒   ▒ ░░ ▒░ ░░ ▒░▒░▒░ ░ ▒░   ▒ ▒ 
 ░ ▒  ▒ ░░▒░ ░ ░ ░ ░░   ░ ▒░  ░   ░  ░ ░  ░  ░ ▒ ▒░ ░ ░░   ░ ▒░
 ░ ░  ░  ░░░ ░ ░    ░   ░ ░ ░ ░   ░    ░   ░ ░ ░ ▒     ░   ░ ░ 
   ░       ░              ░       ░    ░  ░    ░ ░           ░       
                 ▄▄ •  ▄▄▄· • ▌ ▄ ·. ▄▄▄ .
                ▐█ ▀ ▪▐█ ▀█ ·██ ▐███▪▀▄.▀·
                ▄█ ▀█▄▄█▀▀█ ▐█ ▌▐▌▐█·▐▀▀▪▄
                ▐█▄▪▐█▐█ ▪▐▌██ ██▌▐█▌▐█▄▄▌
                ·▀▀▀▀  ▀  ▀ ▀▀  █▪▀▀▀ ▀▀▀ 
      """)

# skip cutscene
if input("Skip Cutscene? (y/n) - ") != "y":

    sleep(2)
    narrate("WELCOME, PLAYER.")
    sleep(1)
    narrate("I AM EXCITED TO MEET YOU.")
    sleep(1)

    # input name
    narrate("WHAT SHALL YOU NAME THE ADVENTURER?")
    name = input("> ")

    narrate(f"YOU HAVE CHOSEN: {name}...")
    narrate("THAT IS A GREAT NAME.")
    sleep(1)

    # input difficulty (how hard enemies will be)
    try:
        narrate(f"HOW DIFFICULT WILL THE QUEST BE FOR THEM? (0 = easy, 1 = hard, 2 = insane, 999 = debug mode)")
        difficulty = int(input("> "))
    except:
        difficulty = 0

    if difficulty == 1:
        difficulty = "hard"
    elif difficulty == 2:
        difficulty = "insane"
    elif difficulty == 999:
        difficulty = "debug mode"
    else:
        difficulty = "easy"

    narrate(f"THEIR JOURNEY WILL BE: {difficulty}")
    sleep(2)

    # enter main loop
    narrate(f"VERY WELL THEN. PLAYER... {name}... LET US BEGIN THE ADVENTURE...")
    sleep(3.5)

else:
    print("WE CALLED YOUR ADVENTURER: Neo. LET US BEGIN...")
    name = "Neo"
    difficulty = "Easy"

print("\n\nYou cautiously tread underneath the towering gate. The long hall ahead is dimly lit, and dusty cobwebs span the corners.\n")
menu()

