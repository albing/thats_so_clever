from dataclasses import dataclass
from random import randint
from enum import Enum
from typing import List

class Color(Enum):
    WHITE = 1
    YELLOW = 2
    BLUE = 3
    GREEN = 4
    ORANGE = 5
    PURPLE = 6

    def all():
        return Color.WHITE, Color.YELLOW, Color.BLUE, Color.GREEN, Color.ORANGE, Color.PURPLE

@dataclass
class Die:
    color: Color
    value: int

    def __repr__(self):
        return f"{self.color.name.title()} {self.value}"

    def __eq__(self, __o: Color) -> bool:
        return self.color.value == __o.value


class Dice:
    
    def __init__(self):
        self.reset()

    def __repr__(self):
        return f"Chosen: {self.chosen_dice}, plate: {self.plate_dice}, rolled: {self.rolled_dice}"

    def reset(self):
        self.chosen_dice = []
        self.plate_dice = []
        self.rolled_dice = []

    def roll(self):
        colors_to_roll = (c.color for c in self.rolled_dice) if self.rolled_dice else Color.all()

        self.rolled_dice = [
            Die(color=Color(color), value=randint(1,6))
            for color in colors_to_roll
        ]

    def choose(self, color: Color):
        """Given a color, move dice between lists"""

        if color not in self.rolled_dice:
            print(f"{color.name.title()} not available in rolled dice")
            return False

        # move die from rolled list to chosen list
        chosen_die = self.rolled_dice.pop(
            self.rolled_dice.index(color)
        )
        self.chosen_dice.append(chosen_die)

        # move all dice _strictly_ less than chosen die to public plate
        dice_to_move = [
            die for die in self.rolled_dice
            if die.value < chosen_die.value
        ]
        self.plate_dice += dice_to_move
        for die in dice_to_move:
            self.rolled_dice.remove(die.color)
        return True

    def find(self, *colors : List[Color]):
        ret = []
        for color in colors:
            possible_locations = [self.rolled_dice, self.chosen_dice, self.plate_dice]
            for location in possible_locations:
                if color in location:
                    ret.append(location[location.index(color)])
                    break
        return ret


class Effects:
    @staticmethod
    def NOTHING(gb: 'GameBoard', points: int):
        pass
        return points

    @staticmethod
    def ADD_REROLL(gb: 'GameBoard', points: int):
        gb.re_rolls += 1
        return points

    @staticmethod
    def ADD_PLUS_ONE(gb: 'GameBoard', points: int):
        gb.plus_ones += 1
        return points

    @staticmethod
    def POINT_x2(gb: 'GameBoard', points: int):
        return points * 2

    @staticmethod
    def POINT_x3(gb: 'GameBoard', points: int):
        return points * 3

    @staticmethod
    def ADD_FOX(gb: 'GameBoard', points: int):
        gb.foxes += 1
        return points

    @staticmethod
    def PURPLE_6(gb: 'GameBoard', points: int):
        gb.purplesection.score(gb, 6)
        return points

    @staticmethod
    def ORANGE_4(gb: 'GameBoard', points: int):
        gb.orangesection.score(gb, 4)
        return points

    @staticmethod
    def ORANGE_5(gb: 'GameBoard', points: int):
        gb.orangesection.score(gb, 5)
        return points

    @staticmethod
    def ORANGE_6(gb: 'GameBoard', points: int):
        gb.orangesection.score(gb, 6)
        return points

    @staticmethod
    def GREEN_X(gb: 'GameBoard', points: int):
        gb.greensection.score(gb, 6)
        return points

    @staticmethod
    def YELLOW_X(gb: 'GameBoard', points: int):
        while user_input := input("Yellow number to X over: "):
            try:
                user_input = int(user_input)
            except ValueError:
                continue
            if gb.yellowsection.valid_to_score(user_input):
                break
        gb.yellowsection.score(gb, user_input)
        return points

    @staticmethod
    def BLUE_X(gb: 'GameBoard', points: int):
        while user_input := input("Blue number to X over: "):
            try:
                user_input = int(user_input)
            except ValueError:
                continue
            if gb.bluesection.valid_to_score(user_input):
                break
        gb.bluesection.score(gb, user_input)
        return points

    @staticmethod
    def X_OR_6(gb: 'GameBoard', points: int):
        gb.board()
        while user_input := input("Section color to X or 6: ").upper():
            try:
                color = Color[user_input]
            except KeyError:
                continue
            if color == Color.WHITE:
                print("Can't pick white.")
                continue

            if color in (Color.BLUE, Color.YELLOW):
                try:
                    points = int(input(f"What number to X off in {color.name.lower()}?" ))
                except ValueError:
                    print(f"Can't parse '{points}'")
                    continue
            else:
                points = 6
            
            section = getattr(gb, f"{color.name.lower()}section")

            if not section.valid_to_score(points):
                print(f"Invalid to score {points} in {color.name.lower()} section")
            section.score(gb, points)
            break


class OrangeSection:        # anything
    LENGTH = 11
    effects = [
        Effects.NOTHING,
        Effects.NOTHING,
        Effects.ADD_REROLL,
        Effects.POINT_x2,
        Effects.YELLOW_X,
        Effects.ADD_PLUS_ONE,
        Effects.POINT_x2,
        Effects.ADD_FOX,
        Effects.POINT_x2,
        Effects.PURPLE_6,
        Effects.POINT_x3,
    ]

    def __init__(self):
        self._entries = []

    def __repr__(self):
        return f"Orange section: {len(self._entries)}/{OrangeSection.LENGTH}: {self._entries}"

    def valid_to_score(self, points):
        return len(self._entries) <= OrangeSection.LENGTH

    def score(self, gameboard, points):
        self._entries.append(
            OrangeSection.effects[len(self._entries)](gameboard, points)
        )

    def get_total_score(self):
        return sum(self._entries)


class GreenSection:         # [1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 6] (but that's not the points)
    LENGTH = 11
    effects = [
        Effects.NOTHING,
        Effects.NOTHING,
        Effects.NOTHING,
        Effects.ADD_PLUS_ONE,
        Effects.NOTHING,
        Effects.BLUE_X,
        Effects.ADD_FOX,
        Effects.NOTHING,
        Effects.PURPLE_6,
        Effects.ADD_REROLL,
        Effects.NOTHING,
    ]
    greaterthans = [1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 6]
    totalscores = [0, 1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 66]

    def __init__(self):
        self._entries = []

    def __repr__(self):
        return f"Green section: {len(self._entries)}/{GreenSection.LENGTH}: {self._entries}"

    def valid_to_score(self, points):
        return len(self._entries) <= GreenSection.LENGTH \
            and points >= GreenSection.greaterthans[len(self._entries)]

    def score(self, gameboard, points):
        self._entries.append(
            GreenSection.effects[len(self._entries)](gameboard, points)
        )

    def get_total_score(self):
        return GreenSection.totalscores[len(self._entries)]


class PurpleSection:        # increasing until 6
    LENGTH = 11
    effects = [
        Effects.NOTHING,
        Effects.NOTHING,
        Effects.ADD_REROLL,
        Effects.BLUE_X,
        Effects.ADD_PLUS_ONE,
        Effects.YELLOW_X,
        Effects.ADD_FOX,
        Effects.ADD_REROLL,
        Effects.GREEN_X,
        Effects.ORANGE_6,
        Effects.ADD_PLUS_ONE,
    ]

    def __init__(self):
        self._entries = []

    def __repr__(self):
        return f"Purple section: {len(self._entries)}/{PurpleSection.LENGTH}: {self._entries}"

    def valid_to_score(self, points):
        if len(self._entries) == 0:
            return True

        return len(self._entries) <= PurpleSection.LENGTH \
            and (points > self._entries[-1] or self._entries[-1] == 6)

    def score(self, gameboard, points):
        self._entries.append(
            PurpleSection.effects[len(self._entries)](gameboard, points)
        )

    def get_total_score(self):
        return sum(self._entries)


class BlueSection:
    
    scores = [0, 1, 2, 4, 7, 11, 16, 22, 29, 37, 46, 56]
    LENGTH = len(scores)
    effects = {
        (5, 9) : Effects.ADD_REROLL,
        (2, 6, 10): Effects.GREEN_X,
        (3, 7, 11): Effects.PURPLE_6,
        (4, 8, 12): Effects.ADD_PLUS_ONE,
        (2, 3, 4): Effects.ORANGE_5,
        (5, 6, 7, 8): Effects.YELLOW_X,
        (9, 10, 11, 12): Effects.ADD_FOX,
    }

    def __init__(self):
        self._entries = []

    def __repr__(self):
        return f"Blue section: {self._entries} crossed out"

    def valid_to_score(self, points):
        return points not in self._entries

    def score(self, gameboard, points):
        # First, add to entries.
        self._entries.append(points)

        # If we score this, we assume that valid_to_score = True, which means that the
        # value of 'points' is new to the section.  This means that checking if 'points'
        # is in 'number_combo' will not double-apply effects.
        # Also, don't break because you can score 2 effects with 1 number.
        for number_combo, effect in BlueSection.effects.items():
            if points in number_combo and all([x in self._entries for x in number_combo]):
                effect(gameboard, points)

    def get_total_score(self):
        return BlueSection.scores[len(self._entries)]


class YellowSection:
    
    DIMENSION = 4
    effects = {
        0: Effects.BLUE_X,
        1: Effects.ORANGE_4,
        2: Effects.GREEN_X,
        3: Effects.ADD_FOX,
        'diag': Effects.ADD_PLUS_ONE,
    }

    def __init__(self):
        self._entries = [
            [3, 6, 5, 0],
            [2, 1, 0, 5],
            [1, 0, 2, 4],
            [0, 3, 4, 6],
        ]
        self.done_diagonal_effect = False

    def __repr__(self):
        return f"Yellow section: {self._entries}"

    def valid_to_score(self, points):
        return (points != 0) and any([points in x for x in self._entries])

    def score(self, gameboard, points):
        # change board
        while user_input := input("Upper or lower? ").lower():
            if user_input[0] in "ul":
                break
        top_down = user_input[0] == "u"
        for i, row in enumerate(self._entries if top_down else reversed(self._entries)):
            if points in row:
                row_index = i if top_down else ((len(self._entries) - i) - 1)
                col_index = row.index(points)

                # "check off" the number
                self._entries[row_index][col_index] = 0

                # See if we've completd the row for an effect
                if sum(self._entries[row_index]) == 0:
                    YellowSection.effects[row_index](gameboard, points)
                
                # done; no need to keep looping
                break

        # check diagonal effect
        if 0 == self._entries[0][0] + self._entries[1][1] + self._entries[2][2] + self._entries[3][3] \
            and not self.done_diagonal_effect:

            self.done_diagonal_effect = True
            YellowSection.effects["diag"](gameboard, points)

    def get_total_score(self):
        total = 0

        rows = list(range(YellowSection.DIMENSION))
        if not any(sum([self._entries[r][0]]) for r in rows):
            total += 10
        if not any(sum([self._entries[r][1]]) for r in rows):
            total += 14
        if not any(sum([self._entries[r][2]]) for r in rows):
            total += 16
        if not any(sum([self._entries[r][3]]) for r in rows):
            total += 20

        return total


class GameBoard:
    round_effects = [
        Effects.ADD_REROLL,
        Effects.ADD_PLUS_ONE,
        Effects.ADD_REROLL,
        Effects.X_OR_6,
        Effects.NOTHING,
        Effects.NOTHING,
    ]

    def __init__(self):
        self.re_rolls = 0
        self.re_roll_max = 7

        self.plus_ones = 0
        self.plus_ones_max = 7

        self.foxes = 0

        self.dice = Dice()

        self.orangesection = OrangeSection()
        self.purplesection = PurpleSection()
        self.greensection = GreenSection()
        self.bluesection = BlueSection()
        self.yellowsection = YellowSection()

        self.die_section_mapper = {
            Color.YELLOW: self.yellowsection,
            Color.GREEN: self.greensection,
            Color.ORANGE: self.orangesection,
            Color.PURPLE: self.purplesection,
        }

    def play_game(self):
        for i in range(6):
            print(f"*** Round {i+1} ***")
            GameBoard.round_effects[i](self, 0)
            self.board()
            self.do_rolls()
            print("** Plate dice section **")
            self.dice.reset()
            self.dice.roll()
            smallest_three_dice = sorted(self.dice.rolled_dice, key=lambda die: die.value)[:3]
            print(f"({self.dice.rolled_dice}")
            while user_input := input(f"Color? {smallest_three_dice}").upper():
                try:
                    color = Color[user_input]
                    die = smallest_three_dice[smallest_three_dice.index(color)]
                except (KeyError, ValueError):
                    continue
                if self.score(die):
                    break



        print(self.total_score())

    def board(self):
        print(self.orangesection)
        print(self.purplesection)
        print(self.greensection)
        print(self.bluesection)
        print(self.yellowsection)

    def do_rolls(self):
        def roll_and_output():
            self.dice.roll()
            
            valid_dice = 0
            # print dice, but only if they're valid to use
            for die in self.dice.rolled_dice:
                if die.color == Color.WHITE:    # white is always valid actually probably not oh well
                    print(die, end=', ')
                elif die.color == Color.BLUE:   # blue needs a special valid function
                    bw_dice = self.dice.find(Color.BLUE, Color.WHITE)
                    if self.bluesection.valid_to_score(bw_dice[0].value + bw_dice[1].value):
                        print(die, end=', ')
                        valid_dice += 1
                    else:
                        print(f"({die})", end=', ')
                elif self.die_section_mapper[die.color].valid_to_score(die.value):
                    print(die, end=', ')
                    valid_dice += 1
                else:
                    print(f"({die})", end=', ')
            print()
            if self.re_rolls > 0:
                print(f"REROLL: {self.re_rolls}")
            if self.plus_ones > 0:
                print(f"PLUS ONE: {self.re_rolls}")

            return valid_dice

        self.dice.reset()

        for i in range(3):
            print(f"Roll number {i+1}/3")
            valid_dice = roll_and_output()
            if valid_dice == 0:
                print("No more valid moves; end of turn!")
                break
            while choice := input("Color: ").upper():
                if choice == "REROLL" and self.re_rolls > 0:
                    self.re_rolls -= 1
                    roll_and_output()
                    continue

                try:
                    color = Color[choice]
                except KeyError:
                    continue

                if not self.dice.choose(color):
                    continue

                # score the die just added
                if self.score(self.dice.chosen_dice[-1]):
                    break   # valid input and valid score; stop looping
                else:
                    print("Invalid")

            # stop rolling if there are no more dice to roll
            if len(self.dice.rolled_dice) == 0:
                break
        self.do_plus_one()

    def do_plus_one(self):
        if self.plus_ones == 0:
            return
        
        # TODO: when multiplayer, a plus-one can also take from another players' chosen dice
        plus_one_dice = self.dice.plate_dice.copy()
        plus_one_dice += self.dice.rolled_dice.copy()
        
        print(f"Available dice: {plus_one_dice}")
        use_plus_one = input("Use plus-one? y/(n) ")
        if use_plus_one.lower() != "y":
            return

        while raw_input := input("Color: ").upper():
            try:
                color_choice = Color[raw_input]
                idx = self.dice.plate_dice.index(color_choice)
            except KeyError:  # from Color[color]
                continue
            except ValueError:  # from plate_dice.index()
                continue

            if not self.score(self.dice.plate_dice[idx]):
                print("Invalid scoring")
                continue
            break
        self.plus_ones -= 1

    def do_blue_white(self, die: Die):
        # choose the other die color
        other_color = Color.WHITE if die.color == Color.BLUE else Color.BLUE

        # find the other die
        other_die_value = self.dice.find(other_color)[0].value

        if not self.bluesection.valid_to_score(die.value + other_die_value):
            return False
        self.bluesection.score(self, die.value + other_die_value)
        return True

    def score(self, die: Die):
        print(f"Scoring a {die}")

        if die.color == Color.WHITE:
            while choice := input("What color should it be instead? ").upper():
                if choice == "WHITE":
                    continue
                try:
                    white_die_color = Color[choice]
                except KeyError:
                    continue

                if white_die_color == Color.BLUE:
                    # do_blue_white will also call bluesection.score()
                    return self.do_blue_white(die)   # pass in white die; it'll find the blue one
                break   # valid input; stop looping
        elif (die.color == Color.BLUE):
            # do_blue_white will also call bluesection.score()
            return self.do_blue_white(die)     # pass in blue die; it'll find the white one
        elif die.color not in self.die_section_mapper:
            print(f"Cannot score a {die}; probably unsupported.")
            return False

        section = self.die_section_mapper[die.color if die.color != Color.WHITE else white_die_color]
        if not section.valid_to_score(die.value):
            print(f"Invalid to score a {die}")
            print(section)
            return False

        section.score(self, die.value)
        return True

    def total_score(self):
        # sort ascending, multiply lowest by foxes, and sum all sections
        sections = sorted([section.get_total_score() for section in [
            self.yellowsection,
            self.bluesection,
            self.greensection,
            self.orangesection,
            self.purplesection,
        ]])
        sections[0] *= (self.foxes or 1)
        return sum(sections)

