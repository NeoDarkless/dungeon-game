# imports
from time import sleep
from random import randint, choice, uniform
from tkinter import *
from tkinter import messagebox


## initial values

# 2D array of rooms
map = [
    ## Room types in the dungeon:
    # Entrance rooms - Usually have puzzles to unlock dungeons - Lit + Unlocked
    # Dungeon rooms - Lots of enemies and items - Unlit + Unlocked
    # Special rooms - Usually Unlit + Locked

    ## Name, Description (Regular), Room Connections, Lit?, Locked?
    # Starting rooms
    ["Gate", "A large, rusty metal gate. It's where you entered.", [1], True, False],
    ["Main Hall", "A long, dimly-lit corridor with cobwebs spanning the walls.", [0, 2, 5, 7], True, False],

    # East rooms
    ["East Entrance", "A small foyer with the entrance to the east dungeon.", [1, 3, 4], True, False],
    ["Shop", "A shop owned by a weary skeleton. He doesn't notice you're a human.", [2, 4], True, False],
    ["East Dungeon", "The long, dark prison is full of monsters guarding jail cells.", [2, 3, 8], False, False],

    # West rooms
    ["West Entrance", "A small foyer with the entrance to the west dungeon.", [1, 6, 9], True, False],
    ["West Dungeon", "The long, dark prison is full of monsters guarding jail cells. There is also a magnificent golden door.", [5, 10], False, False],

    # Locked rooms
    ["North Entrance", "A well-protected pathway with ominous, high-tech doors. It seems important.", [1, 8, 9], False, True],
    ["Vault", "The room is filled with shiny riches and sharp tools. You want to take it all, but there's way too much.", [4, 7], False, True],
    ["Library", "A twisting labyrinth of dusty shelves, all filled with ancient books. It hasn't been used in a long time.", [5, 7], False, True],
    ["Throne Room", "It's magnificent.", [6], True, True],
]

# 2D array of items
items = [
    # Item type 0 = Useless item
    # Item type 1 = Consumable item
    # Item type 2 = Key
    # Item type 3 = Torch

    # Room -1 = player's inventory
    # Room -2 = shop exclusive item
    # Room None = item has been consumed

    ## Name, Room, Item Type, Data (Room key, HP etc)
    ["Skeleton Plushie", 1, 0, None],
    ["Rotten Apple", 5, 1, 15],
    ["Torch", 3, 3, None],
    ["North Entrance Key", 4, 2, 7],
    ["Fake Key", 6, 2, None]
]

# 2D array of enemies
enemies = [
    ## Name, Attack, HP, Spells
    ["SKELLO", 4, 30, "BONETROUSLE"], # BONETROUSLE deals two hits of damage to the player at once
    ["XOMBI", 5, 35, "VENOM CURSE"], # VENOM CURSE deals half a hit of damage every turn
    ["FROHST", 1, 70, "SHADOW OF THE COLD"], # SHADOW OF THE COLD increases the chance of an encounter
    ["GOBBLIMP", 4, 45, "DESPERATION"] # DESPERATION skips one player turn
]

# the current room - game starts at the gate
room = map[0]
# max player hp is 100 hp
max_hp = 100
# player starts at 100 hp
hp = 100
# player starts with a full inventory
inventory_count = 0
coins = 0
# encounter chance starts at 1/4 (3)
encounter_chance = 3
# playing
in_game = True

# narrate speech word by word
def narrate(txt):
    for char in txt:
        print(char, end="", flush=True)
        sleep(0.07)
    print()

            
# choice menu - main loop
def menu():
    # globals
    global room, hp, inventory_count, encounter_chance, in_game

    while in_game:
        sleep(1)

        # check if the player has a torch
        check_torch()
        # print the room description
        describe_room()
        # check if hp is greater than max hp
        check_hp()
        # print player information
        player_stats()
        # run the RNG for an encounter
        handle_encounters()

        try:
            choice = int(input("────────────────────────\nWhat will you do?\n[0] Move\n[1] Items\n - "))
            # move
            if choice == 0:
                move_rooms()
            # open inventory
            elif choice == 1:
                inventory()
            else:
                print("[!] That is not an option. Please enter a valid option.")
        except ValueError:
            print("[!] Invalid input. Please enter an integer.")

# main loop for moving
def move_rooms():
    global room, hp, inventory_count, encounter_chance, in_game
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
                print(f"\nYou crawl through the gate and sprint outside, not looking back.\nCOINS: {coins}")
            else:
                print("\nYou decide to keep going.")
        
        else:
            # if the door is locked
            if map[next_room][4]:
                if not check_key(next_room):
                    print("\n[!] The door is locked.")
                else:
                    # move to the appropriate room
                    prev_room = room
                    room = map[next_room]
            else:
                # move to the appropriate room
                prev_room = room
                room = map[next_room]

    except ValueError:
        # if user enters an invalid input
        print("\n[!] Invalid input. Please enter an integer.")
    
    # go back to the select menu by ending the function
        

# run the RNG for an encounter
def handle_encounters():
    global room, hp, inventory_count, encounter_chance
    
    if randint(0,encounter_chance) == 0:
        # choose an enemy
        encounter = choice(enemies)
        # 25% chance of finding an enemy every move (by default)
        print(f"\nYou encountered the {encounter[0]}!")

        battle(encounter)

# enter battle state after an encounter
def battle(enemy):
    global hp, inventory_count, coins

    print("\nBATTLE:\n - Attack or cast a spell to defeat the enemy\n - Gain MP from attacking or defending\n - Use MP to cast spells\n - Remaining MP after a battle will turn into coins")

    # magic points (MP) are the points required to cast a spell. MP is gained from attacking or defending
    mp = 0

    # setup enemy vars
    enemy_name = enemy[0]
    enemy_atk = enemy[1]
    enemy_max_hp = enemy[2]
    enemy_hp = enemy_max_hp
    enemy_mp = 0

    # random hit strength
    player_hits = [
        [f"Weak hit. {name} dealt {round(enemy_max_hp/6)} damage.", round(enemy_max_hp/8)],
        [f"Moderate hit. {name} dealt {round(enemy_max_hp/5)} damage!", round(enemy_max_hp/6)],
        [f"Strong hit! {name} dealt {round(enemy_max_hp/4)} damage!", round(enemy_max_hp/4)],
        [f"CRITCAL HIT! {name} dealt {round(enemy_max_hp/2)} damage!", round(enemy_max_hp/2)]
    ]

    # start battle loop
    in_battle = True
    while in_battle:
        sleep(1)

        # check player hp
        check_hp()

        # enemy stats: name, attack, hp, spells
        print(f"\nENEMY: [{enemy_name} - HP: {enemy_hp} / {enemy_max_hp} - ATK: {enemy_atk} - MAGIC POINTS: {enemy_mp}]")
        print(f"\nPLAYER: [{name} - HP: {hp} / {max_hp} - MAGIC POINTS: {mp}]")

        try:
            battle_choice = int(input("────────────────────────\nWhat will you do?\n[0] Attack\n[1] Items\n[2] Magic\n[3] Defend\n - "))
            # handle options
            if battle_choice == 0:
                print(f"{name} attacked the {enemy_name}.")
                sleep(1)

                # choose a random attack strength and deal that damage
                attack = choice(player_hits)
                print(attack[0])
                enemy_hp -= attack[1]

                # gain magic points
                mp_gain = randint(7,13)
                mp += mp_gain
                print(f"{name} gained {mp_gain} MP.")
            elif battle_choice == 1:
                inventory()
            elif battle_choice == 2:
                print("magic placeholder")
            elif battle_choice == 3:
                print("defend placeholder")
            else:
                print("[!] That is not an option. Please choose one of the options.")
            
            # if a valid option was chosen, switch to enemy's turn
            if battle_choice == 0 or battle_choice == 1 or battle_choice == 2 or battle_choice == 3:
                # first check if enemy is dead
                if enemy_hp <= 0:
                    print(f"\nYou defeated the {enemy_name}!\nYou got {mp} coins.")
                    coins += mp
                    in_battle = False

                else:
                    # if enemy mp is over 25, there is a random chance to cast a spell
                    if enemy_mp > 25 and randint(0, 1) == 0:
                            print("Spells placeholder")
                    else:
                        print(f"\nThe {enemy_name} attacked {name}.")
                        sleep(1)

                        # enemy damage formula: random value * enemy attack
                        enemy_hit = round(0.6*(uniform(2,5) * enemy_atk))
                        hp -= enemy_hit
                        print(f"{enemy_name} dealt {enemy_hit} damage!")

                        # gain magic points
                        mp_gain = randint(7,13)
                        enemy_mp += mp_gain
                        print(f"{enemy_name} gained {mp_gain} MP.")

        except ValueError:
            print("[!] Invalid input. Please enter an integer.")


# print player stats
def player_stats():
    print(f"\n[{name} - HP: {hp} / {max_hp}]")

# check if hp is over max or 0
def check_hp():
    global hp

    # hp should not exceed max hp. this code caps hp at max
    if hp > max_hp:
        hp = max_hp

    # game over screen - if hp is 0 or under
    elif hp <= 0:
        print("\n\n[GAME OVER]")
        narrate("IT SEEMS YOU HAVE PERISHED...")
        narrate("WELL, THERE IS ALWAYS NEXT TIME.")
        narrate("IF YOU CHOOSE TO CONTINUE... I WISH YOU THE BEST OF LUCK.")
        exit()

# check if player holding torch, if yes then light up all rooms
# for now all rooms will be lit permanently and torch is undroppable
# a dropping torch system will (NOT) be implimented in v3
def check_torch():
    global map

    for i in items:
        # if item in inventory and datatype torch
        if i[1] == -1 and i[2] == 3:
            for x in range(len(map)):
                # if a room is dark, light it
                if not map[x][3]:
                    map[x][3] = True

# if a door is locked, check if the player has the correct key
def check_key(room_no):
    global map

    for i in items:
        # if item in inventory and datatype key
        if i[1] == -1 and i[2] == 2:
            # and matches correct room no
            if i[3] == room_no:
                # unlock the door permanently
                map[room_no][4] = False
                print(f"\nYou slit the {i[0]} into the lock. The door creaks open.")
                return True
            else:
                # if the key doesn't match the room no
                print(f"\nYou tried to budge the {i[0]} into the lock, but it's the wrong key.")

# open inventory
def inventory():
    global inventory_count

    print("\nINVENTORY:")
    if inventory_count != 0:
        for i in items:
            if i[1] == -1:
                print(f"{i[0]}")
        choice_item = int(input("\nWhat will you do with your items?\n[0] Use\n[1] Drop\n[2] Cancel\n - "))
        # use item
        if choice_item == 0:
            use_item()
        elif choice_item == 1:
            drop_item()
        else:
            print("[!] That is not an option. Please enter a valid option.")
    else:
        print("You're not carrying any items.")

def use_item():
    global inventory_count, hp

    print("Choose an item to use:")
    for i in items:
        if i[1] == -1:
            print(f"[{items.index(i)}] {i[0]}")
    choice_item_use = int(input(" - "))
    try:
        if items[choice_item_use][2] == 1:
            print(f"{name} ate the {items[choice_item_use][0]}.\n{name} recovered {items[choice_item_use][3]} HP!")
            hp += items[choice_item_use][3]
            items[choice_item_use][1] = None
            inventory_count -= 1
        else:
            print("[!] This item cannot be used.")
    except IndexError:
        print("[!] This item does not exist. Please enter a valid option.")

def drop_item():
    global room, inventory_count

    print("Choose an item to drop:")
    for i in items:
        if i[1] == -1:
            print(f"[{items.index(i)}] {i[0]}")
    choice_item_drop = int(input(" - "))
    if items[choice_item_drop][2] == 3:
        print("You'd rather not drop that.")
    else:
        try:
            items[choice_item_drop][1] = map.index(room)
            inventory_count -= 1
            print(f"You dropped the {items[choice_item_drop][0]}.")
        except IndexError:
            print("[!] This item does not exist. Please enter a valid option.")

# check if there are any items in the current room, and ask to pick them up
def handle_room_items():
    global inventory_count
    for i in items:
        if i[1] == map.index(room):
            if input(f"\nYou found the {i[0]}. Pick it up? (y/n) - ") == "y":
                items[items.index(i)][1] = -1
                inventory_count += 1
                print(f"You got the {i[0]}.")
            else:
                print(f"You left the {i[0]} in the room.")

# gives the name and description of the room
def describe_room():
    global connected_rooms

    print(f"\n────────────────────────\nYou are in the [{map.index(room)}] {room[0]}.")
    if room[3]:
        print(f"{room[1]}\n\nThe doors in this room lead to:")
        connected_rooms = room[2]
        for i in connected_rooms:
            print(f"[{i}] {map[i][0]}")
        handle_room_items()
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

    # enter main loop
    narrate(f"VERY WELL THEN. PLAYER... {name}... LET US BEGIN THE ADVENTURE...")
    sleep(3.5)

else:
    print("WE CALLED YOUR ADVENTURER: Neo. LET US BEGIN...")
    name = "Neo"

print("\nYou cautiously tread underneath the towering gate. The long hall ahead is dimly lit, and dusty cobwebs span the corners.")
menu()