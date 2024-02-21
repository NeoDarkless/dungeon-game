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
    ["Main Hall", "", [2, 5, 7], True, False],

    # East rooms
    ["East Entrance", "", [1, 3, 4], True, False],
    ["Shop", "", [2, 4], True, False],
    ["East Dungeon", "", [2, 3, 8], False, False],

    # West rooms
    ["West Entrance", "", [1, 6 ,9], True, False],
    ["West Dungeon", "", [5, 10], False, False],

    # Locked rooms
    ["North Entrance", "", [1, 8, 9], False, False],
    ["Vault", "", [4, 7], False, True],
    ["Library", "", [5, 7], False, True],
    ["Throne Room", "", [6], True, True],
]

# narrate descriptions word by word
def narrate(txt):
    txt_split = txt.split()
    for word in txt_split:
        print(word, end=" ", flush=True)
        sleep(0.15)
    print()

# main loop
def move_rooms():
    global room
    in_game = True
    while in_game:
        # print the room description before moving
        describe_room()

        try:
            next_room = int(input("Which room would you like to move to? (room no.) - "))
        except:
            # if user enters an invalid input
            print("\nInvalid input. Please enter an integer.")
            continue
        
        # if the user enters a non-existent room
        if next_room < 0 or next_room >= len(map):
            print("\nThis room doesn't exist. Please enter a different integer.")
            continue

        # if the user leaves the house
        if next_room == 0:
            confirm_leave = input("\nYou approach the Gate. Are you sure you want to leave the dungeon? (y/n) - ")
            # confirm?
            if confirm_leave == "y":
                in_game = False
                print("\nYou creak open the door and sprint outside, not looking back.")
            else:
                print("\nYou decide to keep going from the porch.")

        # move to the appropriate room, regardless of choice
        room = map[next_room]

# gives the name and description of the room
def describe_room():
    narrate(f"You are in the {room[0]}.")
    if room[3]:
        narrate(room[1])
        narrate("The doors in the room lead to: ")
    else:
        narrate("It's too dark to see anything.")

# the current room - game starts at the gate
room = map[0]

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
    difficulty == "debug mode"
else:
    difficulty = "easy"

narrate(f"THEIR JOURNEY WILL BE: {difficulty}")
sleep(2)

# enter main loop
narrate(f"VERY WELL THEN. PLAYER... LET US BEGIN THE ADVENTURE OF: {name} ...")
sleep(3.5)

print("\n\nYou cautiously tread underneath the towering gate. The long hall ahead is dimly lit, and dusty cobwebs span the corners.\n")
move_rooms()

