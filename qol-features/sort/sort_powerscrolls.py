from AutoComplete import *
import re


BOOK_MELEE = 0x57BE5E26
BOOK_MAGIC = 0x5DE465B6
BOOK_BARD = 0x6FC163F0
BOOK_CRAFT = 0x402241A9
BOOK_TAMING = 0x6FC163F0
BOOK_ROGUE = 0x6FC163F0


scroll_map = {
    # Melee
    "Anatomy": BOOK_MELEE,
    "Archery": BOOK_MELEE,
    "Arms Lore": BOOK_MELEE,
    "Anatomy": BOOK_MELEE,
    "Fencing": BOOK_MELEE,
    "Focus": BOOK_MELEE,
    "Healing": BOOK_MELEE,
    "Mace Fighting": BOOK_MELEE,
    "Parrying": BOOK_MELEE,
    "Swordsmanship": BOOK_MELEE,
    "Tactics": BOOK_MELEE,
    "Throwing": BOOK_MELEE,
    "Wrestling": BOOK_MELEE,
    # Magic
    "Bushido": BOOK_MAGIC,
    "Chivalry": BOOK_MAGIC,
    "Evaluate Intelligence": BOOK_MAGIC,
    "Magery": BOOK_MAGIC,
    "Meditation": BOOK_MAGIC,
    "Necromancy": BOOK_MAGIC,
    "Ninjitsu": BOOK_MAGIC,
    "Resisting Spells": BOOK_MAGIC,
    "Spellweaving": BOOK_MAGIC,
    "Spirit Speak": BOOK_MAGIC,
    "Mysticism": BOOK_MAGIC,
    # Bard
    "Discordance": BOOK_BARD,
    "Musicianship": BOOK_BARD,
    "Peacemaking": BOOK_BARD,
    "Provocation": BOOK_BARD,
    # Craft
    "Alchemy": BOOK_CRAFT,
    "Blacksmithing": BOOK_CRAFT,
    "Fletching": BOOK_CRAFT,
    "Carpentry": BOOK_CRAFT,
    "Cooking": BOOK_CRAFT,
    "Cartography": BOOK_CRAFT,
    "Tailoring": BOOK_CRAFT,
    "Tinkering": BOOK_CRAFT,
    "Imbuing": BOOK_CRAFT,
    "Inscription": BOOK_CRAFT,
    "Fishing": BOOK_CRAFT,
    "Mining": BOOK_CRAFT,
    "Lumberjacking": BOOK_CRAFT,
    # Taming
    "Animal Lore": BOOK_TAMING,
    "Animal Taming": BOOK_TAMING,
    "Veterinary": BOOK_TAMING,
    "": BOOK_TAMING,
    # Rogue
    "Hiding": BOOK_ROGUE,
    "Lockpicking": BOOK_ROGUE,
    "Poisoning": BOOK_ROGUE,
    "Remove Trap": BOOK_ROGUE,
    "Stealing": BOOK_ROGUE,
    "Stealth": BOOK_ROGUE,
}


def sort_ps():
    while True:
        scrolls = Items.FindAllByID(0x14F0, 0x481, Player.Backpack.Serial, 2)
        if not scrolls:
            break
        ps = scrolls[0]
        matchres = re.match(r"^(?:a wondrous|an exalted|a mythical|a legendary) scroll of (.+) \((\d+) Skill\)", ps.Name)
        if not matchres:
            print(f"{ps.Name} -> Not matched")
            Misc.Pause(1000)
            continue
        book = scroll_map.get(matchres.group(1), None)
        if book is None:
            print(f"{ps.Name} -> No book found")
            Misc.Pause(1000)
            continue
        Misc.SendMessage(f"Moving PS: {matchres.group(2)} {matchres.group(1)}", 0x802)
        Items.Move(ps.Serial, book, -1)
        Misc.Pause(1000)


sort_ps()
