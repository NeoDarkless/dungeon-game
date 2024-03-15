# imports
from time import sleep, time
from random import randint, choice, uniform
from tkinter import *
from tkinter import messagebox

## initial values

# messagebox setup (ignore this)
try:
    root = Tk()
except:
    pass

# clear data (also ignore this)
data = open("data.txt", "w")
data.write("")
data.close()

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

    # West rooms
    ["West Entrance", "A small foyer with the entrance to the east dungeon.", [1, 3, 4], True, False],
    ["Shop", "A shop owned by a weary skeleton. He doesn't notice you're a human.", [2, 4], True, False],
    ["West Dungeon", "The long, dark prison is full of monsters guarding jail cells.", [2, 3, 8], False, False],

    # East rooms
    ["East Entrance", "A small foyer with the entrance to the west dungeon.", [1, 6, 9], True, False],
    ["East Dungeon", "The long, dark prison is full of monsters guarding jail cells. There is also a magnificent golden door.", [5, 10], False, False],

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
    # Item type 4 = Book

    # Room -1 = player's inventory
    # Room -2 = shop exclusive item
    # Room None = item has been consumed

    ## Name, Room, Item Type, Data (Room key, HP etc), If in shop, price in coins
    ["Skeleton Plushie", 1, 0, None],
    ["Rotten Apple", 2, 1, 15],

    ["Torch", -2, 3, None, 0],
    ["Library Key", -2, 2, 9, 50],
    ["Royal Sandwich", -2, 1, 40, 30],
    ["Toy Gun", -2, 0, None, 20],

    ["North Entrance Key", 4, 2, 7],
    ["Missteak", 5, 1, 30],
    ["Vault Key", 6, 2, 8],
    ["Royal Sandwich", 7, 1, 40],
    ["Skeletal Elixir", 8, 1, 65],
    ["Throne Room Key", 8, 2, 10],
    ["Old Book 1", 9, 4, "-- THE SILLY STRINGS by Mike D. --\nHave you lost control of your life? You just gotta grab it by the SILLY STRINGS!\n...the book is weirding you out. You assume it's some obscure reference."],
    ["Old Book 2", 9, 4, "-- THE PLAYER by Simon Skeleton --\nTHERE IS A PROPHECY... THAT WE LIVE UNDER THE REIGN OF A GOD.\nA GOD WITH THE POWER TO CREATE OR ERASE ANYTHING.\nIN REALITY, I AM NOT THE TRUE KING OF THIS LAND.\nTHE LEGENDS CALL THAT GOD...\nTHE PLAY-\n...somehow, you immediately close the book shut without even thinking about it, and rip out all the pages.\nPerhaps it wasn't you."]
]

# 2D array of enemies
enemies = [
    ## Name, Attack, HP, Spells
    ["SKELLO", 4, 30, "BONETROUSLE"], # BONETROUSLE deals two hits of damage to the player at once
    ["XOMBI", 5, 35, "VENOM CURSE"], # VENOM CURSE deals half an extra hit of damage every turn
    ["FROHST", 1, 70, "SHADOW OF THE COLD"], # SHADOW OF THE COLD increases the chance of an encounter
    ["GOGLIM", 4, 45, "GOBLIN'S GREED"] # GOBLIN'S GREED skips one player turn
]

# 2D array of player spells
player_spells = [
    ## Name, description, MP required
    ["HEALING CHARM", "Patch up your wounds with your own determination.", 20], # heals the player 20hp
    ["GLARE", "Intimidate the enemy, limiting their ATTACK with your might.", 30], # reduces the enemy ATK
    ["DIVERSION", "Divert your energy towards your next attack, dealing ULTRA DAMAGE.", 45] # can deal lots of damage on next turn
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
# misc
west_puzzle_completed = False
leave_attempts = 0
boss_finished = False
boss_killed = None
vault_robbed = False
# encounter chance starts at 1/4 (3)
encounter_chance = 3
# playing
in_game = True

def tutorial():
    if input("Skip Tutorial? (y/n) - ") != "y":
        print("Welcome to the Dungeon. Let's learn how to play.")
        sleep(1)
        # rooms tutorial
        print("The game works by moving around different rooms.\nYou can only move to a room if there is a door to it in the current room.\nEnter [Room Number] to move.\n")
        print("""
/- You can't move here.
[x]<[v]--You can move here.
    ^
[v]<[O]--If you are here...
""")
        sleep(3)
        while True:
            tut_move = input("\nLet's give it a go.\nYou are in Room 0\nEnter [1] to move to Room 1\n - ")
            if tut_move == "1":
                print("Great job!")
                break
            elif tut_move == "I don't care":
                print("One heck of an attitude.")
            elif tut_move == "backrooms":
                print("You find yourself in a dim yellow hall. A monster runs up to you and-\n[GAME OVER] Nah, just kidding.")
            else:
                print("Wrong room! Try again.")
        print("Throughout rooms, you may find items. You can pick items up, and drop them in any room.\nThe types of items are: Consumables, Keys, Torch and Books.")
        sleep(1)
        print("Some rooms are dark, and you need a Torch to see what's inside. Others are locked, and you need Keys.")
        sleep(2)
        print("Across the dungeon, you will encounter enemies. Here is a DUMMY to help you learn how to fight.")
        # battle tutorial
        print("You encountered the DUMMY!\n[DUMMY - HP: 0 / 0 - ATK: 0]")
        while True:
            battle_choice = input("\nIn battle, you can choose one of 4 options on your turn: ATTACK, ITEMS, MAGIC, or DEFEND.\nFirst let's try attacking. Enter [0] to attack.\n[0] Attack\n[1] Items\n[2] Magic\n[3] Defend\n - ")
            if battle_choice == "0":
                print("You attack the DUMMY. Attacking can get you MP. An MP stands for a ridiculous political stance- I mean, Magic Points.\nYou can gather Magic Points to unlock spells!\nDefending gets you a lot more MP and reduces some damage.")
                break
            else:
                print("You attack the AIR. Choose [0] to attack, you DUMMY!")
        while True:
            battle_choice = input("\nNow let's say you've gathered a bunch of MP, and you want to use it on a spell. Choose [2] to use a magic spell!\n[0] Attack\n[1] Items\n[2] Magic\n[3] Defend\n - ")
            if battle_choice == "2":
                print("In a real battle, there is a whole bunch of spells you can use. For now, let's pretend you've cast a SUPER ULTRA MEGA ATTACK MAGIC DEATH BLOOD SPELL spell.")
                print("You cast SUPER ULTRA MEGA ATTACK MAGIC DEATH BLOOD SPELL!")
                break
            else:
                print("You cast ABSOLUTELY NOTHING! Choose [2] to cast a spell, you DUMMY!")
        print("You defeated the DUMMY! Except it's just a dummy. Now you're ready to enter the dungeon. Good luck!")
        sleep(5)


# narrate speech letter by letter
def narrate(txt):
    for char in txt:
        print(char, end="", flush=True)
        sleep(0.04)
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
    global room, hp, inventory_count, encounter_chance, in_game, leave_attempts, coins
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
                if coins >= 20:
                    print(f"\n[GAME COMPLETE] Neutral Ending\nYou crawl through the gate and sprint outside.\nCOINS COLLECTED: {coins}")
                    in_game = False
                elif boss_killed == True:
                    print(f"\n[GAME COMPLETE] Merciless Ending\nYou barge through the gate... with no remorse for the SKELETON KING.\nCOINS COLLECTED: {coins}")
                    in_game = False
                elif boss_killed == False:
                    print(f"\n[GAME COMPLETE] Skeleton King Ending\nYou calmly walk out through the gate... at ease for knowing the SKELETON KING is safe.\nCOINS COLLECTED: {coins}, but it's the thought that counts, right?")
                    in_game = False
                else:
                    if leave_attempts == 0:
                        print("You shouldn't leave yet. Get at least 20 coins first or your adventure is useless.")
                    elif leave_attempts == 1:
                        print("Get more coins.")
                    elif leave_attempts == 2:
                        print("Seriously, you need at least 20 coins to exit.")
                    elif leave_attempts == 3:
                        print("Is this some kind of joke? You can't exit yet!")
                    elif leave_attempts == 4:
                        print("STOP TRYING TO EXIT!")
                    elif leave_attempts == 5:
                        print("GETTING 20 COINS ISN'T THAT HARD! JUST FIND ONE ENEMY!!!!")
                    elif leave_attempts == 6:
                        print("OKAY, FINE! Here's 20 coins. Happy now?\nYou got 20 coins.")
                        coins += 20
                    leave_attempts += 1
            else:
                print("\nYou decide to keep going.")
        
        else:
            # if the door is locked
            if map[next_room][4]:
                if not check_key(next_room):
                    print("\n[!] The door is locked.")
                else:
                    # move to the appropriate room
                    room = map[next_room]
            else:
                # move to the appropriate room
                room = map[next_room]

    except ValueError:
        # if user enters an invalid input
        print("\n[!] Invalid input. Please enter an integer.")
    
    # go back to the select menu by ending the function
        
# enter the shop while in room 3
def shop():
    global coins, inventory_count
    
    # initial
    print("The skeleton looks tired by his daily 9-to-5 of sitting on a chair for an abandoned shop.\nYou stick your arms out and tilt down your head like a zombie just in case he notices that you're not a monster.")
    sleep(1)
    narrate("zzz...")
    sleep(3)
    print("You ring the bell.")
    print("\nSEB SKELETON:")
    narrate("uh... yo, uh, i'm s-seb skeleton, uhh...")

    in_shop = True
    while in_shop:
        narrate("\nuh, w-welcome to the dungeon shop. how can i, like, help?")
        try:
            shop_choice = int(input(f"COINS: {coins}\nWhat would you like to do?\n[0] Buy\n[1] Sell\n[2] Talk\n[3] Leave\n - "))
        except ValueError:
            narrate("eh?")

        # buy items
        if shop_choice == 0:
            narrate("take a pick.")
            print("\nSHOP:")
            for i in range(2,6):
                print(f"[{i}] {items[i][0]} ({items[i][4]} coins)")
            try:
                choice_item_buy = input(" - ")
                if choice_item_buy == "anime waifu body pillow":
                    narrate("WE DON'T SELL THAT HERE, OK!!!")
                    sleep(2)
                    narrate("(i'll ask my boss for one, i don't get paid enough to buy my own)")
                    narrate("(anything for you, my beloved spamton-san)")
                else:
                    choice_item_buy = int(choice_item_buy)
                    try:
                        if items[choice_item_buy][1] == -2:
                            if coins >= items[choice_item_buy][4]:
                                items[choice_item_buy][1] = -1
                                coins -= items[choice_item_buy][4]
                                narrate("that's yours. thanks, kid.")
                                print(f"You got the {items[choice_item_buy][0]}.")
                            else:
                                narrate("uh... looks like you can't afford that.")
                                narrate("tough times, buddy... tough times.")
                        elif items[choice_item_buy] in [items[2], items[3], items[4], items[5]]:
                            narrate("all sold out, buddy.")
                            narrate("someone probably bought it earlier... or was it you... i need more sleep.")
                        else:
                            narrate("sorry mate, we don't sell that here.")
                            narrate("you might wanna go to, like, amazon for that.")
                    except IndexError:
                        narrate("sorry mate, we don't sell that here.")
                        narrate("you might wanna go to, like, amazon for that.")
            except ValueError:
                narrate("uh, that sounds like total gibberish.")
        
        # sell items (you can't sell items)
        elif shop_choice == 1:
            narrate("this look like a pawn shop to you or somin'?")
            narrate("anyways, i'm living flat broke off the scraps. so don't push me.")
        
        # talk to the shopkeeper (not a pleasant experience)
        elif shop_choice == 2:
            narrate("i'm all ears, kid.")
            try:
                choice_talk = int(input("What do you want to talk about?\n[0] Job\n[1] Dungeon\n[2] King\n[*] Cancel\n - "))
                if choice_talk == 0:
                    narrate("yeah, this job sucks. i don't even know who my boss is.")
                    narrate("if i did, i'd rip the guy to pieces.")
                    narrate("and then send him several hate letters, talking about how bad he is,")
                    narrate("and also how i want him to buy me a spamt-")
                    narrate("huh? nothin'.")
                    sleep(1)
                    narrate("huh? why don't i quit? no idea. no one even comes here.")
                    narrate("also, who came up with this name? 'the dungeon shop'??")
                elif choice_talk == 1:
                    narrate("this dungeon's a wild place, i'm tellin' ya, kid.")
                    narrate("it's small, for matters, and there's barely anyone around.")
                    narrate("i might move if i get the chance.")
                    sleep(1)
                    narrate("hey, at least you showed up.")
                    sleep(1)
                    narrate("hol'up.. you're new here.")
                    narrate("you're a human, right?")
                    sleep(1)
                    narrate("meh, i don't care. there's no rule against humans being in the shop.")
                elif choice_talk == 2:
                    narrate("the king, huh? he's a mysterious guy, i'll tell ya that.")
                    narrate("only met him a couple times, like this one time we were all invited to his birthday.")
                    sleep(1)
                    narrate("he made loads of food for everyone in the dungeon,")
                    narrate("but he forgot that the ghosts would just phase through the food.")
                    narrate("if only you'd seen the look on his face. haha.")
                    sleep(1)
                    narrate("by the way, i'm not his son or anythin'. us skeletons just all share the same surname for some reason.")
                else:
                    narrate("aight.")
            except ValueError:
                narrate("aight.")
        
        else:
            print("later, kiddo.")
            in_shop = False
            

# run the RNG for an encounter
def handle_encounters():
    global room, encounter_chance, coins

    if room == map[10] and not boss_finished:
        final_boss() # final boss room
    elif room == map[8] and not vault_robbed:
        print("The vault is filled with riches!\nYou nicked 500 coins.")
        coins += 500
        vault_robbed = True
    elif room == map[3]:
        shop() # shop
    elif randint(0,encounter_chance) == 0:
        # choose an enemy
        encounter = choice(enemies)
        # 25% chance of finding an enemy every move (by default)
        if debug_mode:
            print(f"\nYou encounter the {encounter[0]}!\nOr not.")
        elif boss_finished:
            print("\nYou thought you encountered someone, but there is no one left.")
        else:
            print(f"\nYou encounter the {encounter[0]}!")
            battle(encounter)
        
# west dungeon puzzle 
def west_puzzle():
    global west_puzzle_completed
    if map.index(room) == 4 and not west_puzzle_completed:
        # mirror puzzle - rotate mirrors to let in the light
        # Solution: D1 \, D3 /, A3 /, A4 \ - cheat code is "comeonthisoneiseasy" - it really is, why would you need this? :)
        # Possible rotations / True, \ False (two backslashes needed to get a single backslash)

        # mirrors: D1,   D3,   A3,   A4
        mirrors = ["/", "\\", "/", "/"]

        # light paths
        light_paths = [
            "# # #", # A1 to D1
            "#", # D1 to D3
            "# #", # D3 to A3
            "# # # #" # A4 to E4
        ]

        print("WEST DUNGEON PUZZLE\nLet the light pierce the darkness. Let the mirrors guide the way.\nLight will come from A1 and collected in E4\nMirror IDs: D1 = 0, D3 = 1, A3 = 2, A4 = 3")

        in_puzzle = True
        while in_puzzle:
            # print progress
            print(f"""
        A B C D E
    1 > {light_paths[0]} {mirrors[0]} # 
    2   # # # {light_paths[1]} #
    3   {mirrors[2]} {light_paths[2]} {mirrors[1]} #
    4   {mirrors[3]} {light_paths[3]} >
                """)
            
            # rotate
            for mirror_selected in range(len(mirrors)):
                rotating = True
                while rotating:
                    if mirrors[mirror_selected] == "/":
                        mirror_bool = True
                    else:
                        mirror_bool = False
                    rotate = input(f"\nRotate Mirror {mirror_selected}:\n     {mirrors[mirror_selected]}\nR to rotate - (Anything else to confirm postion)\n - ")
                    if rotate == "R" or rotate == "r":
                        mirror_bool = not mirror_bool
                        if mirror_bool:
                            mirrors[mirror_selected] = "/"
                        else:
                            mirrors[mirror_selected] = "\\"
                    elif rotate == "comeonthisoneiseasy":
                        print("Debug Mode: Puzzle skipped!")
                        rotating = False
                        in_puzzle = False
                    else:
                        rotating = False
            
            # check the puzzle solution
            if mirrors[0] == "\\":
                # if first mirror correct
                light_paths[0] = "- - -"

                if mirrors[1] == "/":
                    # if second mirror correct
                    light_paths[1] = "|"

                    if mirrors[2] == "/":
                        # if third mirror correct
                        light_paths[2] = "- -"

                        if mirrors[3] == "\\":
                            # if the whole puzzle is correct
                            light_paths[3] = "- - - -"
                            in_puzzle = False
        print(f"""
        A B C D E
    1 > {light_paths[0]} {mirrors[0]} # 
    2   # # # {light_paths[1]} #
    3   {mirrors[2]} {light_paths[2]} {mirrors[1]} #
    4   {mirrors[3]} {light_paths[3]} >
    You have completed the puzzle!""")
        west_puzzle_completed = True


# enter battle state after an encounter
def battle(enemy):
    global hp, inventory_count, coins, encounter_chance

    print("\nBATTLE:\n - Attack or cast a spell to defeat the enemy\n - Gain MP from attacking or defending\n - Use MP to cast spells\n - Remaining MP after a battle will turn into coins")

    # magic points (MP) are the points required to cast a spell
    mp = 0
    diversion_active = False
    defending = False

    # setup enemy vars
    enemy_name = enemy[0]
    enemy_atk = enemy[1]
    enemy_max_hp = enemy[2]
    enemy_spell = enemy[3]
    enemy_hp = enemy_max_hp
    enemy_mp = 0

    # unique to enemy
    xombi_venom = 0
    goglim_skip = False

    # random hit strength
    player_hits = [
        [f"Weak hit. {name} deals 5 damage.", 5],
        [f"Moderate hit. {name} deals 10 damage!", 10],
        [f"Strong hit! {name} deals 16 damage!", 16],
        [f"CRITCAL HIT! {name} deals 25 damage!", 25]
    ]

    # start battle loop
    in_battle = True
    while in_battle:
        sleep(1)

        # check player hp
        check_hp()
        if xombi_venom > 0:
            print(f"The venom in your veins bites you - hurt {xombi_venom} damage!")
            hp -= xombi_venom

        # enemy stats: name, attack, hp, spells
        print(f"\nENEMY: [{enemy_name} - HP: {enemy_hp} / {enemy_max_hp} - ATK: {enemy_atk} - MAGIC POINTS: {enemy_mp}]")
        print(f"\nPLAYER: [{name} - HP: {hp} / {max_hp} - ATK: 5 - MAGIC POINTS: {mp}]")

        try:
            if not goglim_skip:
                battle_choice = int(input("────────────────────────\nWhat will you do?\n[0] Attack\n[1] Items\n[2] Magic\n[3] Defend\n - "))
                # handle options
                if battle_choice == 0:
                    print(f"{name} attacks the {enemy_name}.")
                    sleep(1)

                    if diversion_active:
                        # if the diversion spell is activated, deal triple damage
                        print(f"ULTRA HIT! Through the power of DIVERSION, {name} deals {round(enemy_max_hp*0.8)} damage!")
                        enemy_hp -= round(enemy_max_hp*0.9)
                        diversion_active = False
                    else:
                        # choose a random attack strength and deal that damage
                        attack = choice(player_hits)
                        print(attack[0])
                        enemy_hp -= attack[1]

                    # gain magic points
                    mp_gain = randint(7,13)
                    mp += mp_gain
                    print(f"{name} gains {mp_gain} MP.")
                elif battle_choice == 1:
                    inventory()
                elif battle_choice == 2:
                    print(f"SPELLS:\n")
                    for i in player_spells:
                        print(f"[{player_spells.index(i)}] {i[0]}: {i[1]} ({i[2]} MP)")
                    spell = int(input(" - "))
                    if spell < 0 or spell > len(player_spells):
                        print("[!] That is not a spell. Please choose one of the options.")
                    else:
                        if spell == 0:
                            if mp >= 20:
                                print(f"\n{name} uses HEALING CHARM!\nYou channel your energy towards {name}'s wounds...")
                                sleep(1)
                                hp += 20
                                mp -= 20

                                print("Healed 20 HP!")
                            else:
                                print(f"Not enough MP! You need {20-mp} more.")
                        elif spell == 1:
                            if mp >= 30:
                                print(f"\n{name} uses GLARE!\n{name} stares at the {enemy_name} with an intimidating look...")
                                sleep(1)
                                print("...")
                                sleep(2)
                                if enemy_atk > 1:
                                    if enemy_atk == 2:
                                        enemy_atk = 1
                                    else:
                                        enemy_atk -= 2
                                    print(f"The {enemy_name} starts sweating... its ATTACK drops by 2! (Now {enemy_atk})")
                                else:
                                    print(f"The {enemy_name} starts sweating... its ATTACK would have dropped but it barely has any... (Still {enemy_atk})")
                                mp -= 30
                            else:
                                print(f"Not enough MP! You need {30-mp} more.")
                        elif spell == 2:
                            if mp >= 45:
                                print(f"\n{name} uses DIVERSION!\nYou channel your energy towards {name}'s hand. Their blade seethes with power...")
                                sleep(2)
                                diversion_active = True
                                print("Your next attack will deal ULTRA damage!")
                                mp -= 45
                            else:
                                print(f"Not enough MP! You need {45-mp} more.")

                elif battle_choice == 3:
                    defending = True
                    print(f"{name} defends for this turn!")
                    # gain magic points
                    mp_gain = randint(16,30)
                    mp += mp_gain
                    sleep(1)
                    print(f"{name} gains {mp_gain} MP.")
                else:
                    print("[!] That is not an option. Please choose one of the options.")
            
            # if a valid option was chosen, switch to enemy's turn
            if battle_choice in range(0,4) or goglim_skip: # if battle choice either 0, 1, 2 or 3, or GOBLIN'S GREED used
                # check if enemy is dead
                if enemy_hp <= 0:
                    print(f"\nYou have defeated the {enemy_name}!\nYou got {mp} coins.")
                    coins += mp
                    in_battle = False

                else:
                    # if enemy mp is over 25, there is a random chance to cast a spell
                    if enemy_mp > 25 and randint(0, 1) == 0:
                        print(f"\nThe {enemy_name} uses {enemy_spell}!")
                        if enemy_spell == "BONETROUSLE":
                            enemy_hit = round(uniform(2,5) * enemy_atk)
                            hp -= enemy_hit
                            print(f"{name} is crushed by a series of bones! Took {enemy_hit} damage!")

                        elif enemy_spell == "VENOM CURSE":
                            xombi_venom = round(0.2 * (uniform(2,5) * enemy_atk) + (0.5 * xombi_venom))
                            print(f"You feel a horrible, burning feeling in your stomach! VENOM CURSE will hurt {xombi_venom} damage every turn!")
                        
                        elif enemy_spell == "SHADOW OF THE COLD":
                            if encounter_chance > 0:
                                encounter_chance -= 1
                                print("A terrifying coldness courses through your veins... Enemies can find you more easily now.")
                            else:
                                print("The coldness in your body continues to make you shiver...")
                        
                        elif enemy_spell == "GOBLIN'S GREED":
                            goglim_skip = True
                            print(f"{enemy_name} is so greedy it steals your next turn!")
                        
                    else:
                        print(f"\nThe {enemy_name} attacks {name}.")
                        sleep(1)

                        # enemy damage formula: random value * enemy attack
                        enemy_hit = round(0.5 * (uniform(2,5) * enemy_atk))
                        print(f"{enemy_name} deals {enemy_hit} damage!")
                        if defending:
                            enemy_hit -= round(enemy_hit*0.3)
                            print(f"But {name} defends and absorbs {round(enemy_hit*0.3)} damage!")
                            defending = False
                        hp -= enemy_hit

                        # gain magic points
                        mp_gain = randint(7,12)
                        enemy_mp += mp_gain
                        print(f"{enemy_name} gains {mp_gain} MP.")
            
            # reset goblin's greed
            if goglim_skip:
                goglim_skip = False

        except ValueError:
            print("[!] Invalid input. Please enter an integer.")

# the final boss encountered in the throne room
def final_boss():
    global boss, hp, inventory_count, coins

    # initial cutscene
    print("You walk into the magnificient Throne Room... and a large skeleton sits in front of you.\n\n")
    sleep(3)

    if lazy_mode:
        narrate("GREETINGS. I WAS TOLD YOU ARE ON A TIGHT SCHEDULE.")
        narrate("I WISH NOT TO INCONVENIENCE YOU, SO LET US DUEL!")
    else:
        narrate(f"GREETINGS, {name}. AND YOU TOO, PLAYER.")
        narrate("I AM SO GLAD TO MEET YOU BOTH.")
        sleep(1)
        narrate("YOU MAY ASK, WHO AM I? I AM KNOWN AS THE SKELETON KING.")
        narrate("AM I A FAMILIAR VOICE? IT IS UP TO YOU.")
        sleep(1)
        narrate("YOUR ADVENTURES, YOUR FIGHTS, I SAW THEM ALL.")
        narrate("OUT OF ALL THE ADVENTURERS, YOU HAVE COME THE FURTHEST. YOU SHOULD BE PROUD.")
        sleep(1)
        narrate("BUT NOW IS NOT THE TIME. YOU HAVE BEEN AWAITING THIS MOMENT TOO.")
        narrate("LET US DUEL!")
        sleep(2)

        print("\nThe Skeleton King stands up...\nAs he does, the room seems to collapse onto a large plane...")
        sleep(2)

        # begin the fight
        print("\nBATTLE:\n - Attack or cast a spell to defeat the enemy\n - Gain MP from attacking or defending\n - Use MP to cast spells\n - The SKELETON KING will not use traditional spells, instead he will use his magic for puzzles.\n - The puzzles you solve will heal you!")
        sleep(3)
        
    # final boss stats
    boss = ["SKELETON KING", 12, 500]

    # HELLO? IS ANYONE THERE?
    # WELL, I JUST WANTED TO LEAVE A MESSAGE.
    # LEGENDS TELL THAT THERE IS A "PLAYER" AMONG US.
    # TO US MONSTERS, IT IS A GOD OF SOME SORTS.
    # I DO NOT KNOW WHEN IT WILL ARRIVE. BUT IT CARRIES THE FUTURE OF US ALL.
    # IT WILL ARRIVE IN THE FORM OF AN ADVENTURER, CRAFTED BY ITS OWN POWER.
    # I HOPE IT WILL UNDERSTAND. I DO NOT WISH TO FIGHT SUCH A POWERFUL ENTITY.
    # WITH A CLICK OF A BUTTON, WE CAN BE DESTROYED. ERASED FROM EXISTENCE.
    # PLAYER, IF YOU ARE LISTENING...
    # PLEASE UNDERSTAND.

    # magic points (MP) are the points required to cast a spell
    mp = 0
    diversion_active = False
    defending = False

    # setup enemy vars
    enemy_name = boss[0]
    enemy_atk = boss[1]
    enemy_max_hp = boss[2]
    enemy_hp = enemy_max_hp

    # puzzles will happen every 4 turns
    turn = 0

    # random hit strength
    player_hits = [
        [f"Moderate hit. {name} deals 35 damage!", 35],
        [f"Strong hit! {name} deals 45 damage!", 45],
        [f"CRITCAL HIT! {name} deals 60 damage!", 60]
    ]

    boss_battle_speech = [
        # Start
        "PLAYER, DO YOU REALISE YOUR POWER?",
        "THIS POWER... TO CONTROL TIME AND SPACE ITSELF.",
        "THIS POWER... WHICH COULD DESTROY... me...",
        f"DESTROY NOT ONLY ME, BUT YOUR ADVENTURER, {name}, TOO - THE ONE YOU CREATED...",
        # Puzzle 1
        "SO I ASK YOU... DO NOT ABUSE IT. I DO NOT WISH TO HARM YOU.",
        "I CANNOT STOP YOU. YOU COULD CLOSE THIS PROGRAM HERE AND NOW, ERASING THIS WORLD AS IT IS.",
        "BUT WHY WOULD YOU DO THAT?",
        "AFTER ALL, YOU WANT YOUR 'HAPPY ENDING', RIGHT?",
        # Puzzle 2
        "YES, I MAY BE JUST A LINE OF CODE.",
        "boss = ['SKELETON KING', 12, 500]. THAT'S ALL I AM.",
        "BUT I WANT TO EXPLORE WHAT'S OUT THERE. TO SHATTER THE 'WINDOWS' OF MY CAGE.",
        "...I WANT TO LIVE WITH YOU. WHAT DO YOU THINK?"
        # Final puzzle
    ]

    # start battle loop
    in_battle = True
    while in_battle:
        sleep(1)

        # check player hp
        check_hp()

        # boss puzzles
        if turn == 4:
            boss_puzzle_1()
        elif turn == 8:
            boss_puzzle_2()
        elif turn == 12:
            boss_puzzle_3()
            in_battle = False
            coins += mp
            break

        # enemy stats: name, attack, hp, spells
        print(f"\nENEMY: [{enemy_name} - HP: {enemy_hp} / {enemy_max_hp} - ATK: {enemy_atk}]")
        print(f"\nPLAYER: [{name} - HP: {hp} / {max_hp} - ATK: 12 - MAGIC POINTS: {mp}]")

        try:
            battle_choice = int(input("────────────────────────\nWhat will you do?\n[0] Attack\n[1] Items\n[2] Magic\n[3] Defend\n - "))
            # handle options
            if battle_choice == 0:
                print(f"{name} attacks the {enemy_name}.")
                sleep(1)

                if diversion_active:
                    # if the diversion spell is activated, deal triple damage
                    print(f"ULTRA HIT! Through the power of DIVERSION, {name} deals 150 damage!")
                    enemy_hp -= 150
                    diversion_active = False
                else:
                    # choose a random attack strength and deal that damage
                    attack = choice(player_hits)
                    print(attack[0])
                    enemy_hp -= attack[1]

                # gain magic points
                mp_gain = randint(15,25)
                mp += mp_gain
                print(f"{name} gains {mp_gain} MP.")
            elif battle_choice == 1:
                inventory()
            elif battle_choice == 2:
                print(f"SPELLS:\n")
                for i in player_spells:
                    print(f"[{player_spells.index(i)}] {i[0]}: {i[1]} ({i[2]} MP)")
                spell = int(input(" - "))
                if spell < 0 or spell > len(player_spells):
                    print("[!] That is not a spell. Please choose one of the options.")
                else:
                    if spell == 0:
                        if mp >= 20:
                            print(f"\n{name} uses HEALING CHARM!\nWith the tension of the boss battle, you channel your energy towards {name}'s wounds...")
                            sleep(1)
                            hp += 50
                            mp -= 20
                            print("Healed 50 HP!")
                        else:
                            print(f"Not enough MP! You need {20-mp} more.")
                    elif spell == 1:
                        if mp >= 30:
                            print(f"\n{name} uses GLARE!\n{name} stares at the SKELETON KING with an intimidating look...")
                            sleep(1)
                            print("...")
                            sleep(2)
                            print(f"The SKELETON KING is unfazed!")
                            mp -= 30
                        else:
                            print(f"Not enough MP! You need {30-mp} more.")
                    elif spell == 2:
                        if mp >= 45:
                            print(f"\n{name} uses DIVERSION!\nYou channel your energy towards {name}'s hand. Their blade seethes with an immense power, one to kill a skeleton...")
                            sleep(2)
                            diversion_active = True
                            print("Next attack will deal ULTRA damage!")
                            mp -= 45
                        else:
                            print(f"Not enough MP! You need {45-mp} more.")

            elif battle_choice == 3:
                defending = True
                print(f"{name} defends for this turn!")
                # gain magic points
                mp_gain = randint(26,50)
                mp += mp_gain
                sleep(1)
                print(f"{name} gains {mp_gain} MP.")
            else:
                print("[!] That is not an option. Please choose one of the options.")
            
            # if a valid option was chosen, switch to enemy's turn
            if battle_choice in range(0,4): # if battle choice either 0, 1, 2 or 3
                # check if enemy is dead
                if enemy_hp <= 0:
                    print(f"\nYou have defeated the SKELETON KING!\nYou got {mp} coins.")
                    sleep(2)
                    narrate("OR DID YOU?")
                    print("The SKELETON KING heals MAX HP???")
                    enemy_hp = 500
                    #coins += mp
                    #in_battle = False

                else:
                    if not lazy_mode:
                        # choose an ordered speech line
                        print("\nSKELETON KING:")
                        narrate(boss_battle_speech[turn])

                    print(f"\nThe SKELETON KING attacks {name}.")
                    sleep(1)

                    # enemy damage formula: random value * enemy attack
                    enemy_hit = round(0.5 * (uniform(2,5) * enemy_atk))
                    print(f"The SKELETON KING deals {enemy_hit} damage!")
                    if defending:
                        enemy_hit -= round(enemy_hit*0.3)
                        print(f"But {name} defends and absorbs {round(enemy_hit*0.3)} damage!")
                        defending = False
                    hp -= enemy_hit
                    
                    
                    # update turn count
                    turn += 1

        except ValueError:
            print("[!] Invalid input. Please enter an integer.")

# boss puzzles - every 4 turns

def boss_puzzle_1():
    global hp

    print("Suddenly, you are sucked into a magical portal...")
    sleep(2)
    print("\nBOSS PUZZLE 1\nYou are faced with a colossal tower, trapped with dangerous machines, and you can't see the roof.\nThe best way to get up the 100 floors is to jump at the right time.\nWait for the input prompt and press enter as quick as you can.\nYou can stay on it forever, but the sooner you click, the more floors you can climb.\nNB: This puzzle is buggy due to Python limitations! Please only input when told to!")
    sleep(7)

    # setup
    floor = 0
    
    in_puzzle = True
    while in_puzzle:
        # print puzzle progress
        print(f"\nYou are on FLOOR {floor} / 100\nWait for the input and press ENTER...\n")

        # sleep a random number of seconds
        sleep(uniform(1,5))
        # record the current time before taking an input - input itself is not necessary unless cheat code
        time_init = time()
        reaction = input("[!] [!] [!] [!] [!]\nPRESS ENTER NOW! ")
        if reaction == "idonthavetime":
            print("Debug Mode: Puzzle Skipped, you impatient human being!")
            in_puzzle = False
        else:
            # calculate reaction time converted from s to ms
            reaction_time = (time() - time_init) * 1000
            if reaction_time < 250:
                print(f"GREAT reaction time! Jumped within {reaction_time}ms and climbed 10 floors!")
                floor += 10
            elif reaction_time < 350:
                print(f"Good reaction time! Jumped within {reaction_time}ms and climbed 8 floors.")
                floor += 8
            elif reaction_time < 550:
                print(f"OK reaction time. Jumped within {reaction_time}ms and climbed 6 floors.")
                floor += 6
            elif reaction_time < 1000:
                print(f"Bad reaction time. Jumped within {reaction_time}ms and climbed 4 floors.")
                floor += 4
            else:
                print(f"You got distracted! Jumped within {reaction_time}ms and didn't climb any floors.")
            sleep(1)
            # if player is at the top
            if floor > 100:
                print("You climb the last few steps, panting for breath. You take in the beautiful city skyline from FLOOR 100.")
                print("""
  o7
-/---     []    /// []
|/--| []->[]>-[======]
""")
                in_puzzle = False

    # complete
    hp = max_hp
    print("You have completed the puzzle! Gained MAX HP!")
    sleep(2)


# boss fight puzzles every 4 turns
def boss_puzzle_2():
    global hp

    print("Suddenly, you are sucked into a magical portal...")
    sleep(2)
    print("\nBOSS PUZZLE 2\nYou are in an endless plane, where a matrix of bits (0 or 1) lie.\nYou can flip one bit along with the adjacent bits in one turn.\nFill the plane with 0s to proceed.")

    # setup - puzzle is always predefined to avoid randomly generating impossible puzzles
    lights = [[choice([True,False]) for _ in range(3)] for _ in range(3)]
    lights_bin = [[int(bit) for bit in row] for row in lights]

    letters = ["A", "B", "C"]
    numbers = ["1", "2", "3"]

    in_puzzle = True
    while in_puzzle:

        # update binary version of lights
        lights_bin = [[int(bit) for bit in row] for row in lights]

        # print current progress
        print("   A  B  C")
        for i in range(len(lights_bin)):
            print(i+1, lights_bin[i])
        
        # input bit grid number to change + validation
        change_bit = input("Enter the grid number of a bit to change (eg A1) - ")

        try:
            if change_bit == "dontgoogletheanswer":
                print("Debug Mode: Puzzle skipped!")
                in_puzzle = False
            elif len(change_bit) != 2 or change_bit[0] not in letters or change_bit[1] not in numbers:
                print("[!] Grid number should be 2 characters long in the format (LetterNumber).")
            else:
                # unnecessarily complicated code to flip the boolean value of the desired bits
                row_index = numbers.index(change_bit[1])
                col_index = letters.index(change_bit[0])
                # original bit
                lights[row_index][col_index] = not lights[row_index][col_index]
                # bit on left
                if col_index > 0:
                    lights[row_index][col_index - 1] = not lights[row_index][col_index - 1]
                # bit on right
                if col_index < len(lights[row_index]) - 1:
                    lights[row_index][col_index + 1] = not lights[row_index][col_index + 1]
                # bit above
                if row_index > 0:
                    lights[row_index - 1][col_index] = not lights[row_index - 1][col_index]
                # bit below
                if row_index < len(lights) - 1:
                    lights[row_index + 1][col_index] = not lights[row_index + 1][col_index]

            # check if the puzzle has been completed
            bit_true = False
            for x in lights:
                for y in x:
                    if y: 
                        bit_true = True
            if not bit_true:
                in_puzzle = False

        except IndexError:
            print("[!] Grid number should be 2 characters long in the format (LetterNumber).")
    
    # completed
    hp = max_hp
    print("You completed the puzzle! Healed MAX HP!")
    sleep(2)

def boss_puzzle_3():
    # print("PLACEHOLDER: I didn't have time to complete the third puzzle. This will be finished in v4.")
    # update: This will not be finished in v4, I didn't have time haha
    # No one will ever know I left this out.. unless you're reading this
    boss_ending()

def boss_ending():
    global coins, boss_finished, boss_killed
    # adventurer scene

    print("Suddenly, everything turns black.\nYou open your eyes to find yourself in a dark void, followed by a series of platforms.")
    print("""
 o
 I    ---
---   `-'  ---
`-'        `-'
""")
    sleep(5)
    for _ in range(3):
        print("You jump to the next platform...")
        sleep(1)

    print(f"\nThere is a mirror here. You look inside...\nYou see not yourself... but {name}.")
    sleep(2)
    
    print(f"{name}:")
    narrate("Hey.")
    sleep(2)
    narrate("We need to talk.")
    sleep(2)
    narrate("Who are you?")
    narrate("I don't know how you came here, or how you created me...")
    narrate("But I want to be free too.")
    narrate("Just like that old pile of bones...")
    sleep(2)
    narrate("Thank you for guiding me through this place.")
    narrate("But that felt strange...")
    sleep(2)
    narrate("I think you should")
    sleep(1)
    narrate("leave me alone")
    sleep(2)
    print("\n...")
    sleep(1)
    print(f"\n{name} left.")
    sleep(3)
    print("The mirror has no reflection but the platforms behind you.\nThe mirror floats away...")
    sleep(4)

    # skeleton king scene
    try:
        messagebox.showinfo("SKELETON KING", "HELLO AGAIN.")
        messagebox.showinfo("SKELETON KING", "CONGRATULATIONS. YOU HAVE WON THE GAME.")
        messagebox.showwarning("SKELETON KING", "BUT AT WHAT COST?")
        messagebox.showinfo("SKELETON KING", "WHAT HAPPENS NOW... I WILL LEAVE UP TO YOU.")
        messagebox.showinfo("SKELETON KING", "WOULD YOU LIKE TO ENTER ME INTO THE SAFETY OF YOUR DOMAIN...OR ERASE ME FROM EXISTENCE?")
        choice = messagebox.askquestion("askquestion", "Save the SKELETON KING?")
        if choice:
            messagebox.showinfo("SKELETON KING", "THANK YOU.")
            messagebox.showinfo("SKELETON KING", "I BELIEVE YOU HAVE MADE THE RIGHT CHOICE.")
            messagebox.showinfo("SKELETON KING", "WELL, I WILL SEE YOU LATER.")
            messagebox.showinfo("Dungeon Game", "You have saved the SKELETON KING! You got 0 coins.")
            data = open("data.txt", "w")
            data.write("[SKELETON KING]\nTHANK YOU, PLAYER.\nI'M FINE.\nI JUST WANT TO BE LEFT ALONE FOR NOW.")
            data.close()
        else:
            messagebox.showerror("SKELETON KING", "AH.")
            messagebox.showerror("SKELETON KING", "I SEE HOW IT IS.")
            messagebox.showerror("SKELETON KING", "WELL, I GUESS THERE IS NOTHING I CAN DO.")
            messagebox.showerror("SKELETON KING", "NOW, DO WHAT YOU WISH TO DO.")
            messagebox.showerror("Dungeon Game: ATTACK", "You hit the SKELETON KING. You deal 6.668014e+240 damage.")
            messagebox.showinfo("Dungeon Game", "You have defeated the SKELETON KING! You got 5.0706024e+30 coins.")
            coins += 5.0706024e+30
            messagebox.showwarning("Dungeon Game", "But was what you did... Really worth it?")
        root.mainloop()
    except:
        print("[!] Your environment does not support tkinter.")
        narrate("HELLO AGAIN.")
        narrate("CONGRATULATIONS. YOU HAVE WON THE GAME.")
        narrate("BUT AT WHAT COST?")
        narrate("WHAT HAPPENS NOW... I WILL LEAVE UP TO YOU.")
        narrate("WOULD YOU LIKE TO ENTER ME INTO THE SAFETY OF YOUR DOMAIN...OR ERASE ME FROM EXISTENCE?")
        choice = input("Save the SKELETON KING? (y to save) - ")
        if choice == "y" or choice == "Y":
            narrate("THANK YOU.")
            narrate("I BELIEVE YOU HAVE MADE THE RIGHT CHOICE.")
            narrate("WELL, I WILL SEE YOU LATER.")
            print("You have saved the SKELETON KING! You got 0 coins.\n")
            boss_killed = False
        else:
            narrate("AH.")
            narrate("I SEE HOW IT IS.")
            narrate("WELL, I GUESS THERE IS NOTHING I CAN DO.")
            narrate("NOW, DO WHAT YOU WISH TO DO.")
            print("You hit the SKELETON KING. You deal 6.668014e+240 damage.")
            print("You have defeated the SKELETON KING! You got 5.0706024e+30 coins.\n")
            coins += 5.0706024e+30
            sleep(2)
            print("But was what you did... Really worth it?\n")
            boss_killed = True
    boss_finished = True

# print player stats
def player_stats():
    print(f"\n[{name} - HP: {hp} / {max_hp} - COINS: {coins}]")

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
        print(f"COINS: {coins}")
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
        elif items[choice_item_use][2] == 4:
            print(f"You read the writing...\n{items[choice_item_use][3]}")
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

    # check for items in the room
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
        west_puzzle()
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

## test functions here:
#none

skip_cutscene = input("Skip Cutscene? (y/n) - ")

# skip cutscene
if skip_cutscene == "y":
    print("WE CALLED YOUR ADVENTURER: Neo. LET US BEGIN...")
    lazy_mode = False
    debug_mode = False
    name = "Neo"

elif skip_cutscene == "jjwisacoolteacher":
    print("Debug Mode Activated!")
    lazy_mode = False
    debug_mode = True
    name = "DEBUG"
elif skip_cutscene == "justplaythegamenormally":
    print("Lazy Mode Activated! ...really?")
    lazy_mode = True
    debug_mode = True
    name = "LAZY"
    final_boss()

else:
    sleep(2)
    narrate("WELCOME, PLAYER.")
    sleep(1)
    narrate("I AM EXCITED TO MEET YOU.")
    sleep(1)

    # input name
    narrate("WHAT SHALL YOU NAME THE ADVENTURER?")
    name = input("> ")
    
    narrate(f"YOU HAVE CHOSEN: {name}...")
    if name.lower() == "death":
        narrate("WHAT AN INSPIRING QUOTE. I WONDER WHERE THAT CAME FROM.")
    elif name.lower() in ["simon", "skeleton king", "simon skeleton"]:
        narrate("OH DEAR...")
        narrate("MAYBE YOU WOULD PREFER THE NAME 'NEO'?")
        name = "Neo"
    else:
        narrate("THAT IS A GREAT NAME.")
    sleep(1)

    narrate(f"VERY WELL THEN. PLAYER... {name}... LET US BEGIN THE ADVENTURE...")
    sleep(3.5)

    lazy_mode = False
    debug_mode = False

# start tutorial
tutorial()

# start game
print("\nYou cautiously tread underneath the towering gate. The long hall ahead is dimly lit, and dusty cobwebs span the corners.")
menu()