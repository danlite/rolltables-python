import os
import sys
import math
import random
import colorama
from prettytable import PrettyTable
from glob import glob
from termcolor import colored
import config

# sys.path.append(os.path.dirname(__file__))

from dice import Modifier
from roll_table import get_table, load_table

MAX_LEVEL = 10
colorama.init()


def a_an(next_word):
    return 'an' if next_word[0] in ['a', 'e', 'i', 'o', 'u'] else 'a'


def show_roll(d):
    print(d.description(), d.roll())


class TableRollDisplayElement():
    def __init__(self, values=[], header=[], level=0):
        self.values = values
        self.header = header
        self.level = level


def gather_table_roll_displays(t,
                               ref_opts={},
                               unique_rolls=None,
                               modifier=None,
                               row=None,
                               level=0,
                               elements=None):
    if level > MAX_LEVEL:
        return (elements, None, None)

    if type(t) is str:
        t = get_table(t)

    if row is None:
        ignore = ref_opts.get('ignore')
        while True:
            row = t.roll(modifier)
            number = row[0].number
            valid = True

            if type(ignore) == int:
                valid = number != ignore
            elif type(ignore) == list:
                valid = number not in ignore

            if valid and unique_rolls is not None:
                valid = number not in unique_rolls
                unique_rolls.add(number)

            if valid:
                break

    roll, text, references, result_modifier = row

    if elements is None:
        elements = []

    elements.append(TableRollDisplayElement([roll, text],
                                            [str(t.dice), t.title],
                                            level))

    if references is not None:
        for ref in references:
            unique = ref.opts.get('unique', False)
            unique_rolls = set() if unique else None
            if config.DEBUG:
                print(ref.count)
            for _ in range(ref.count):
                gather_table_roll_displays(ref.identifier,
                                           ref_opts=ref.opts,
                                           unique_rolls=unique_rolls,
                                           elements=elements,
                                           level=level + 1)

    return (elements, roll, result_modifier)


def print_table_roll(t, modifier=None, row=None, starting_level=0):
    (
        elements,
        roll,
        result_modifier
    ) = gather_table_roll_displays(t, modifier=modifier, row=row, level=starting_level)
    grouped_elements = []

    current_level = -1
    current_header = None
    current_grouped_values = None

    def add_current():
        if current_header and current_grouped_values:
            grouped_elements.append((current_header,
                                     current_grouped_values,
                                     current_level))

    for el in elements:
        if current_level != el.level:
            add_current()
            current_grouped_values = [el.values]
            current_header = el.header
            current_level = el.level

        elif current_header != el.header:
            add_current()
            current_grouped_values = [el.values]
            current_header = el.header

        else:
            current_grouped_values.append(el.values)

    add_current()

    current_level = starting_level
    for el in grouped_elements:
        header, values, level = el
        pt = PrettyTable(header)
        for v in values:
            pt.add_row(v)

        output = '\n'.join(['    ' * level + r for r in str(pt).split('\n')])

        if level > current_level:
            arrow = '    ' * (level - 1) + '╚═══'
            output = arrow + output[len(arrow):]

        current_level = level

        print(output)

    return (roll, result_modifier)


dirname = os.path.dirname(__file__)

for f in glob(os.path.join(dirname, '../tables/**'), recursive=True):
    if os.path.isfile(f):
        load_table(f)

# config.DEBUG = True

# print(get_table('dmg/dungeons/location').description())
# print(get_table('dmg/dungeons/exotic-location').description())

# show_roll(Die(4))
# show_roll(Dice([Die(6, 3)]))
# show_roll(Dice([Die(8), Die(12)]))

# die = Die(6, 3)
# roll = die.roll()
# range = RollRange(10, 12)
# print(die.description(), roll)
# print(range.description(), range.matches(roll))


def ask(prompt):
    print(prompt)
    return input('>> ')


def ask_int(prompt):
    r = ask(prompt)
    try:
        return int(r)
    except (ValueError, TypeError):
        return None


def header(header):
    def header_decorator(func):
        def func_wrapper():
            print('')
            first_line = ('╔════════════════   ' +
                          header +
                          '   ════════════════╗')
            print(first_line)
            print('')
            func()
            print('')
            print('╚' + ('═' * (len(first_line) - 2)) + '╝')
            print('')
        return func_wrapper
    return header_decorator


@header('Building a Dungeon')
def make_dungeon():
    dungeon_list = [
        'location',
        'creator',
        'purpose',
        'history'
    ]

    for name in dungeon_list:
        print_table_roll('dmg/dungeons/' + name)


@header('This Is Your Life')
def make_life():
    races = {
        'he': 'Half-elf',
        'ho': 'Half-orc',
        't': 'Tiefling',
        'd': 'Dwarf',
        'e': 'Elf',
    }
    race = ask(colored('What is your race?\n', 'magenta') +
               '\n'.join(['{}: {}'.format(k, v) for k, v in races.items()]))

    race = None if race not in races else race
    sibling_modifier = Modifier(-2) if race in ('e', 'd') else None

    if race:
        print(colored('Your race is: {}'.format(races[race]), 'green'))

    if race == 'ho':
        print_table_roll('xgte/life/origins/half-orc-parents')
    if race == 'he':
        print_table_roll('xgte/life/origins/half-elf-parents')
    if race == 't':
        print_table_roll('xgte/life/origins/tiefling-parents')

    print_table_roll('xgte/life/origins/birthplace')
    r, m = print_table_roll('xgte/life/origins/siblings',
                            modifier=sibling_modifier)
    number_of_siblings = m
    for i in range(number_of_siblings):
        print(colored('Sibling {}'.format(i + 1), 'yellow'))
        print_table_roll('xgte/life/origins/birth-order', starting_level=1)
        print_table_roll('xgte/life/supplemental/occupation', starting_level=1)
        print_table_roll('xgte/life/supplemental/alignment', starting_level=1)
        print_table_roll('xgte/life/supplemental/status', starting_level=1)
        print_table_roll('xgte/life/supplemental/relationship',
                         starting_level=1)

    print_table_roll('xgte/life/origins/family')
    r, m = print_table_roll('xgte/life/origins/family-lifestyle')
    lifestyle_modifier = Modifier(m)
    print_table_roll('xgte/life/origins/childhood-home',
                     modifier=lifestyle_modifier)

    backgrounds = [
        ('acolyte', 'Acolyte'),
        ('charlatan', 'Charlatan'),
        ('criminal', 'Criminal'),
        ('entertainer', 'Entertainer'),
        ('folk-hero', 'Folk hero'),
        ('guild-artisan', 'Guild artisan'),
        ('hermit', 'Hermit'),
        ('noble', 'Noble'),
        ('outlander', 'Outlander'),
        ('sage', 'Sage'),
        ('sailor', 'Sailor'),
        ('soldier', 'Soldier'),
        ('urchin', 'Urchin'),
    ]
    bg_choice = ask_int(colored('What is your background?\n', 'magenta') +
                        '\n'.join(['{}: {}'.format(i, b[1])
                                   for i, b in enumerate(backgrounds)]
                                  )
                        )
    if isinstance(bg_choice, int) and bg_choice in range(len(backgrounds)):
        background = backgrounds[bg_choice]
    else:
        background = None

    if background:
        print(colored(
            'Your background is: {}'.format(background[1]),
            'green'
        ))

        print_table_roll('xgte/life/decisions/background/' + background[0])

    classes = [
        ('barbarian', 'Barbarian'),
        ('bard', 'Bard'),
        ('cleric', 'Cleric'),
        ('druid', 'Druid'),
        ('fighter', 'Fighter'),
        ('monk', 'Monk'),
        ('paladin', 'Paladin'),
        ('ranger', 'Ranger'),
        ('rogue', 'Rogue'),
        ('sorcerer', 'Sorcerer'),
        ('warlock', 'Warlock'),
        ('wizard', 'Wizard'),
    ]
    class_choice = ask_int(colored('What is your class?\n', 'magenta') +
                           '\n'.join(['{}: {}'.format(i, b[1])
                                      for i, b in enumerate(classes)]
                                     )
                           )
    if isinstance(class_choice, int) and class_choice in range(len(classes)):
        class_ = classes[class_choice]
    else:
        class_ = None

    if class_:
        print(colored(
            'Your class is: {}'.format(class_[1]),
            'green'
        ))

        print_table_roll('xgte/life/decisions/class/' + class_[0])

    print_table_roll('xgte/life/events/age')


@header('Treasure Hoards')
def treasure():
    table = get_table('dmg/treasure/hoard-4-loot')
    # print(table.evaluate_text())
    print_table_roll(table)
    # print_table_roll('dmg/treasure/magic-item-g')


@header('White Plume Mountain')
def mountain_loot():
    table_1 = get_table('dmg/treasure/hoard-1-loot')
    table_2 = get_table('dmg/treasure/hoard-2-loot')

    print_table_roll(table_1)
    print_table_roll(table_1)
    print_table_roll(table_1)
    print_table_roll(table_1)
    print_table_roll(table_1)
    print_table_roll(table_1)
    print_table_roll(table_1)

    print_table_roll(table_2)
    print_table_roll(table_2)
    print_table_roll(table_2)
    print_table_roll(table_2)
    print_table_roll(table_2)
    print_table_roll(table_2)
    print_table_roll(table_2)
    print_table_roll(table_2)
    print_table_roll(table_2)


@header('Spells')
def spells():
    table = get_table('spells/level/0')
    print(table.description())


@header('Random Dungeon')
def random_dungeon():
    table = get_table('dmg/dungeons/random/starting-area')
    print_table_roll(table)
    # print(table.roll())


@header('Universal NPC Emulator')
def une():
    nn_table = get_table('une/npc-noun')
    nm_table = get_table('une/npc-modifier')
    mv_table = get_table('une/npc-motivation-verb')
    mn_table = get_table('une/npc-motivation-noun')

    npc_noun = nm_table.roll()[1]
    npc_modifier = nn_table.roll()[1]

    npc_description = 'The NPC is {} {} {}'.format(
        a_an(npc_noun),
        npc_noun,
        npc_modifier,
    )

    print(npc_description)

    noun_columns = []
    motivations = []
    while len(noun_columns) < 3:
        verb = mv_table.roll()[1]
        noun_roll, noun = mn_table.roll()[0:2]
        column = math.floor((noun_roll.number - 1) / 20)
        if column not in noun_columns:
            noun_columns.append(column)
            motivations.append((verb, noun))

    print('\nwho wants to...\n')

    for verb, noun in motivations:
        print('{} {}'.format(verb, noun))

    ideals = ['good', 'evil', 'lawful', 'chaotic', 'neutral', 'other']

    tables = [
        'appearance',
        'ability-high',
        'talent',
        'mannerism',
        'interaction',
        'ideal-{}'.format(random.choice(ideals)),
        'bond',
        'flaw-secret',
    ]

    [print_table_roll('dmg/npcs/{}'.format(table)) for table in tables]


@header('Villain')
def villain():
    for t in ('objective', 'method', 'weakness'):
        table = get_table('dmg/villains/{}'.format(t))
        print_table_roll(table)


@header('Settlement')
def settlement():
    for t in ('race-relations', 'ruler-status', 'notable-traits', 'known-for', 'current-calamity'):
        table = get_table('dmg/settlements/{}'.format(t))
        print_table_roll(table)

@header('NPC')
def npc():
    ideal = 'ideal-' + random.choice(('chaotic', 'evil', 'good', 'lawful', 'neutral', 'other'))
    for t in ('appearance', 'ability-high', 'talent', 'mannerism', 'interaction', ideal, 'bond', 'flaw-secret'):
        table = get_table('dmg/npcs/{}'.format(t))
        print_table_roll(table)



if __name__ == '__main__':
    args = list(sys.argv)
    args.pop(0)

    # make_dungeon()
    make_life()
    # treasure()
    # spells()
    # random_dungeon()
    # une()
    # mountain_loot()
    # villain()
    # settlement()
    # npc()

    for table_name in args:
        print_table_roll(table_name)
