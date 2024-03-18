from abc import ABC
from functools import total_ordering
from random import Random
from typing import Optional, Any

from enums import Race, Condition, Type, Orders, Courage, Feature, Object, Fear, Direction, Area, Status
from maps import mainMap, referenceDescriptionMap, routes


class Time:
    DAWN = 16
    NIGHT = 0

    def __init__(self, time: int = 16) -> None:
        self.time = time

    def dawn(self) -> None:
        self.time = self.DAWN

    def night(self) -> None:
        self.time = self.NIGHT

    def __str__(self):
        if self.time == self.NIGHT:
            return "It is night"
        if self.time == self.DAWN:
            return "It is dawn"
        if self.time % 2 == 1:
            return f"Less than {self.time / 2 + 1} {'hour of the day remains' if self.time < 3 else 'hours of the day remain'}"
        return f"{self.time / 2} {'hour of the day remains' if self.time < 3 else 'hours of the day remain'}"

    def increase(self, increment: int) -> None:
        self.time += increment
        if self.time > self.DAWN:
            self.time = self.DAWN

    def decrease(self, decrement: int) -> None:
        self.time -= decrement
        if self.time < self.NIGHT:
            self.time = self.NIGHT

    def is_night(self) -> bool:
        return self.time == self.NIGHT

    def is_dawn(self) -> bool:
        return self.time == self.DAWN

    def get_time(self) -> int:
        return self.time


class Unit(ABC):
    condition: Optional[Condition]  # !!
    location: Optional['Location']
    MAX_ENERGY = 127

    def __init__(self, game: 'Midnight', race: Race, energy: int) -> None:
        self.enemy_killed = 0
        self.energy = 0
        self.condition = None
        self.location = None
        self.game = game
        self.race = race
        self.set_energy(energy)

    def get_game(self) -> 'Midnight':
        return self.game

    def get_race(self) -> Race:
        return self.race

    def set_race(self, race: Race) -> None:
        self.race = race

    def get_location(self) -> 'Location':
        return self.location

    def set_location(self, location: 'Location') -> None:
        self.location = location

    def get_condition(self) -> Condition:
        return self.condition

    def get_energy(self) -> int:
        return self.energy

    def set_energy(self, energy: int) -> None:
        if energy < 0:
            energy = 0
        elif energy > self.MAX_ENERGY:
            energy = self.MAX_ENERGY
        self.energy = energy
        self.condition = Condition.get_condition(energy >> 4)

    def increment_energy(self, increment: int) -> None:
        self.set_energy(self.get_energy() + increment)

    def decrement_energy(self, decrement: int) -> None:
        self.set_energy(self.get_energy() - decrement)

    def get_enemy_killed(self) -> int:
        return self.enemy_killed

    def set_enemy_killed(self, enemy_killed: int) -> None:
        self.enemy_killed = enemy_killed


class Army(Unit):

    def __init__(self, game: 'Midnight', race: Race, how_many: int, type: Type) -> None:
        super().__init__(game, race, 88)
        self.success_chance = 0
        self.casualties = 0
        self.how_many = how_many
        self.type = type

    def get_how_many(self) -> int:
        return self.how_many

    def set_how_many(self, how_many: int) -> None:
        self.how_many = how_many

    def get_type(self) -> Type:
        return self.type

    def increase_numbers(self, increase: int) -> None:
        self.how_many += increase

    def decrease_numbers(self, decrease: int) -> None:
        if decrease > self.how_many:
            decrease = self.how_many
        self.how_many -= decrease

    def append_casualties(self, number: int) -> None:
        self.decrease_numbers(number)
        self.casualties += number

    def get_casualties(self) -> int:
        return self.casualties

    def set_casualties(self, lost: int) -> None:
        self.casualties = lost

    def dawn(self) -> None:
        pass
        # self.enemy_killed=0
        # self.casualties=0

    def get_success_chance(self) -> int:
        return self.success_chance

    def set_success_chance(self, success_chance: int) -> None:
        self.success_chance = success_chance

    def increment_energy(self, increment: int) -> None:
        if self.type == Type.RIDERS:
            super().increment_energy(6 + increment)
        else:
            super().increment_energy(4 + increment)

    def guard(self, x, y: int = -1):
        if isinstance(x, int):
            location = self.get_game().get_map().get_location(x, y)
        else:
            location = x
        self.set_location(location)
        self.get_location().set_guard(self)

    def switch_sides(self) -> None:
        if self.get_race() == Race.FOUL:
            self.set_race(Race.FREE)
            self.how_many = 200
        else:
            self.set_race(Race.FOUL)
            self.how_many = 250

    def __str__(self):
        if self.how_many != 0:
            return f"{self.how_many} {self.type}"
        return f"no {self.type}"

    def save(self):
        raise NotImplementedError()

    @staticmethod
    def load():
        raise NotImplementedError()


class Battle:
    characters: set['Character']
    foul: list[Army]
    free: list[Army]

    def __init__(self, location: 'Location', winner: Optional[Race] = None) -> None:
        self.free = []
        self.foul = []
        self.characters = set()
        self.location = location
        if winner is None:
            self.winner = winner
        else:
            self.winner = None
            self.game = location.get_game()
            self.append_guard()

            for character in location.get_characters():
                if character.is_alive() and not character.is_hidden():
                    self.append_character(character)

            for army in location.get_armies():
                self.append_foul_army(army)

    def append_guard(self) -> None:
        guard = self.location.get_guard()
        if guard is None or guard.get_how_many() == 0:
            return

        if guard.get_race() == Race.FOUL:
            self.append_foul_army(guard)
        else:
            guard.set_success_chance(0x60 if guard.get_type() == Type.RIDERS else 0x40)
            self.free.append(guard)

    def append_character(self, character: 'Character') -> None:
        self.characters.add(character)
        character.set_battle(self)
        if character.get_riders().get_how_many() > 0:
            self.append_free_army(character.get_riders(), character)
        if character.get_warriors().get_how_many() > 0:
            self.append_free_army(character.get_warriors(), character)

    def append_foul_army(self, army: Army) -> None:
        fear_factor = self.location.get_ice_fear() // (4 if army.get_type() == Type.RIDERS else 5)
        success_chance = fear_factor

        if self.location.get_guard() is not None and self.location.get_guard().get_race() == Race.FOUL:
            success_chance += 0x20 if self.location.get_feature() == Feature.CITADEL else 0x10

        army.set_success_chance(success_chance)
        self.foul.append(army)

    def append_free_army(self, army: Army, character: 'Character'):
        if army is None or army.get_how_many() == 0:
            return

        success_chance = army.get_energy()

        if self.location.get_guard() is not None and self.location.get_guard().get_race() != Race.FOUL:
            success_chance += 0x20 if self.location.get_feature() == Feature.CITADEL else 0x10

        if army.get_type() == Type.RIDERS:
            success_chance += self.location.riders_battle_bonus()

        if self.location.get_feature() == Feature.FOREST and character.get_race() == Race.FEY and character.is_on_horse():
            success_chance += 0x40

        success_chance = success_chance // 2 + 0x18

        army.set_success_chance(success_chance)
        self.free.append(army)

    def run(self) -> None:
        for character in self.characters:
            character.set_enemy_killed(
                self.skirmish(character.get_strength(), character.get_energy() + 0x80, self.foul))

        for army in self.free:
            army.set_enemy_killed(self.skirmish(army.get_how_many() // 5, army.get_success_chance(), self.foul))

        for army in self.foul:
            army.set_enemy_killed(self.skirmish(army.get_how_many() // 5, army.get_success_chance(), self.free))

        self.determine_result()

    def skirmish(self, hits: int, success_chance: int, enemies: list[Army]) -> int:
        enemy_killed = 0
        for i in range(len(enemies)):
            if self.game.random(256) < success_chance:
                enemy_index = self.game.random(len(enemies))
                enemy = enemies[enemy_index]

                if self.game.random(256) > enemy.get_success_chance():
                    enemy_killed += 5

                    enemy.append_casualties(5)
                    if enemy.get_how_many() == 0:
                        enemies.pop(enemy_index)
            if i >= hits:
                break
        return enemy_killed

    def determine_result(self) -> None:
        if len(self.foul) == 0:
            self.winner = Race.FREE
        elif len(self.free) == 0:
            self.winner = Race.FOUL
        else:
            self.winner = None

        for army in self.free:
            army.decrement_energy(0x18)

        if self.location.get_guard() is not None:
            if self.winner is not None:
                if (self.winner == Race.FOUL and self.location.get_guard().get_race() != Race.FOUL) or (
                        self.winner != Race.FOUL and self.location.get_guard().get_race() == Race.FOUL):
                    self.location.get_guard().switch_sides()
            elif self.location.get_guard().get_how_many() == 0:
                self.location.get_guard().increase_numbers(20)

        for character in self.characters:
            character.decrement_energy(0x14)

        if self.winner == Race.FOUL:
            self.what_happened_to_free_lords()

    def what_happened_to_free_lords(self) -> None:
        for character in self.characters:
            character.maybe_lose()
            if character.is_alive():
                while True:
                    direction = Direction.get_direction(self.game.random(8))
                    destination = self.location.get_map().get_in_front(character.get_location(), direction)
                    if destination.get_feature() != Feature.FROZEN_WASTE:
                        break
                character.set_location(destination)

    def get_location(self) -> 'Location':
        return self.location

    def get_winner(self) -> Race:
        return self.winner

    def __str__(self):
        return f"A battle in the domain of {self.location.get_domain()}"


@total_ordering
class Character(Unit):
    killed: Optional[Object]
    found: Optional[Object]
    battle: Optional[Battle]
    courage: Optional[Courage]

    def __init__(self, game: 'Midnight', id: int, name: str, title: str, race: Race, x: int, y: int, life: int,
                 energy: int, strength: int, courage_base: int, recruiting_key: int, recruited_by_key: int, riders: int,
                 warriors: int) -> None:
        super().__init__(game, race, energy)
        self.killed = None
        self.found = None
        self.battle = None
        self.recruited = False
        self.hidden = False
        self.strength = strength
        self.courage = None
        self.id = id
        self.name = name
        self.title = title
        self.life = life
        self.courage_base = courage_base
        self.recruiting_key = recruiting_key
        self.recruited_by_key = recruited_by_key
        self.warriors = Army(game, race, warriors, Type.WARRIORS)
        self.riders = Army(game, race, riders, Type.RIDERS)
        self.set_location(self.get_game().get_map().get_location(x, y))
        self.direction = Direction.NORTH
        self.time = Time()
        self.object = Object.NOTHING
        self.on_horse = race not in [Race.DRAGON, Race.SKULKRIN]

    def __hash__(self):
        return hash(self.id)

    def get_id(self) -> int:
        return self.id

    def get_name(self) -> str:
        return self.name

    def get_full_title(self) -> str:
        return self.title

    def get_life(self) -> int:
        return self.life

    def get_courage_base(self) -> int:
        return self.courage_base

    def get_courage(self) -> Courage:
        self.calculate_courage()
        return self.courage

    def calculate_courage(self) -> None:
        fear = (self.courage_base - self.get_location().get_ice_fear() // 7)
        self.courage = Courage.get_courage(fear // 8)

    def set_location(self, location: 'Location') -> None:
        if self.get_location() is not None:
            self.get_location().remove_character(self)
        super().set_location(location)
        self.get_location().append_character(self)

    def get_direction(self) -> Direction:
        return self.direction

    def set_direction(self, direction: Direction) -> None:
        self.direction = direction

    def is_alive(self) -> bool:
        return self.life > 0

    def die(self) -> None:
        self.life = 0

    def get_strength(self) -> int:
        return self.strength

    def set_strength(self, strength: int) -> None:
        self.strength = strength

    def is_hidden(self) -> bool:
        return self.hidden

    def can_hide(self) -> bool:
        return self != self.get_game().MORKIN and self.get_warriors().get_how_many() == 0 and self.get_riders().get_how_many() == 0

    def set_hidden(self, hidden: bool) -> None:
        self.hidden = hidden

    def can_walk_forward(self) -> bool:
        destination = self.get_game().get_map().get_in_front(self.get_location(), self.direction)
        return self.can_leave() and not self.time.is_night() and self.get_condition() != Condition.UTTERLY_TIRED and destination.get_feature() != Feature.FROZEN_WASTE and len(
            destination.get_characters()) < 29 and len(destination.get_armies()) == 0 and (
                destination.get_guard() is None or destination.get_guard().get_race() != Race.FOUL)

    def can_leave(self) -> bool:
        object = self.get_location().get_object()
        guard = self.get_location().get_guard()
        return self.is_alive() and not self.is_hidden() and (self.time.is_dawn() or (
                len(self.get_location().get_armies()) == 0 and (
                guard is None or guard.get_race() != Race.FOUL))) and (
                object not in [Object.DRAGONS, Object.ICE_TROLLS, Object.SKULKRIN, Object.WOLVES])

    def walk_forward(self) -> None:
        destination = self.get_game().get_map().get_in_front(self.get_location(), self.direction)
        self.set_location(destination)

        drain = 2
        if self.direction.is_diagonal():
            drain += 1
        if not self.on_horse:
            drain *= 2
        if destination.get_feature() == Feature.DOWNS:
            drain += 1
        elif destination.get_feature() == Feature.MOUNTAIN:
            drain += 4
        elif destination.get_feature() == Feature.FOREST and self.get_race() == Race.FEY:
            drain += 3

        if self == self.get_game().FARFLAME:
            drain = 1

        self.time.decrease(drain)
        self.set_energy(self.get_energy() - drain)
        self.riders.set_energy(self.riders.get_energy() - drain)
        self.warriors.set_energy(self.warriors.get_energy() - drain)
        self.set_battle(None)
        self.clear_killed()
        self.clear_found()

    def get_recruited_by_key(self) -> int:
        return self.recruited_by_key

    def get_recruiting_key(self) -> int:
        return self.recruiting_key

    def can_recruit(self, c: 'Character') -> bool:
        return not c.is_recruited() and c.get_location() == self.get_location() and (
                self.recruiting_key & c.recruited_by_key) != 0 and (
                len(self.get_location().get_armies()) == 0 or self == self.get_game().MORKIN)

    def recruit(self, c: 'Character') -> bool:
        if self.can_recruit(c):
            c.set_recruited(True)
            return True
        return False

    def is_recruited(self) -> bool:
        return self.recruited

    def set_recruited(self, recruited: bool) -> None:
        self.recruited = recruited

    def get_riders(self) -> Army:
        return self.riders

    def get_warriors(self) -> Army:
        return self.warriors

    def can_recruit_men(self) -> bool:
        guards = self.get_location().get_guard()
        return guards is not None and guards.get_race() == self.get_race() and guards.get_how_many() > 125 and (
                (guards.get_type() == Type.RIDERS and self.get_riders().get_how_many() < 1175) or (
                guards.get_type() == Type.WARRIORS and self.get_warriors().get_how_many() < 1175)) and (
                len(self.get_location().get_armies()) == 0 or self == self.get_game().MORKIN)

    def recruit_men(self) -> bool:
        if not self.can_recruit_men():
            return False

        guards = self.get_location().get_guard()
        guards.decrease_numbers(100)
        if guards.get_type() == Type.RIDERS:
            self.get_riders().increase_numbers(100)
        elif guards.get_type() == Type.WARRIORS:
            self.get_warriors().increase_numbers(100)

        return True

    def can_stand_on_guard(self) -> bool:
        guards = self.get_location().get_guard()
        return guards is not None and guards.get_race() == self.get_race() and guards.get_how_many() < 1175 and (
                (guards.get_type() == Type.RIDERS and self.get_riders().get_how_many() >= 100) or (
                guards.get_type() == Type.WARRIORS and self.get_warriors().get_how_many() >= 100)) and (
                len(self.get_location().get_armies()) == 0 or self == self.get_game().MORKIN)

    def stand_on_guard(self) -> bool:
        if not self.can_stand_on_guard():
            return False

        guards = self.get_location().get_guard()
        guards.increase_numbers(100)
        if guards.get_type() == Type.RIDERS:
            self.get_riders().decrease_numbers(100)
        elif guards.get_type() == Type.WARRIORS:
            self.get_warriors().decrease_numbers(100)

        return True

    def get_time(self) -> Time:
        return self.time

    def set_time(self, time: Time) -> None:
        self.time = time

    def is_on_horse(self) -> bool:
        return self.on_horse

    def set_on_horse(self, on_horse: bool) -> None:
        self.on_horse = on_horse

    def can_attack(self) -> bool:
        destination = self.get_game().get_map().get_in_front(self.get_location(), self.direction)

        return self.can_leave() and (len(destination.get_armies()) > 0 or (
                destination.get_guard() is not None and destination.get_guard().get_race() == Race.FOUL)) and self.get_courage() != Courage.UTTERLY_AFRAID

    def get_battle(self) -> Battle:
        return self.battle

    def set_battle(self, battle: Optional[Battle]) -> None:
        self.battle = battle

    def describe_battle(self) -> str:
        sb = f"In the battle of {self.battle.get_location().get_domain()} "
        if self.riders.get_casualties() != 0 or self.warriors.get_casualties() != 0:
            sb += f"{self.get_name()} lost "
            if self.riders.get_casualties() != 0:
                sb += f"{self.riders.get_casualties()} riders"
            if self.riders.get_casualties() != 0 and self.warriors.get_casualties() != 0:
                sb += " and "
            if self.warriors.get_casualties() != 0:
                sb += f"{self.warriors.get_casualties()} warriors"
            sb += ". "

        sb += f"{self.get_name()} alone slew {self.enemy_killed} of the Enemy. "
        if self.riders.get_enemy_killed() != 0:
            sb += f"His riders killed {self.riders.get_enemy_killed()} of the enemy. "
        if self.warriors.get_enemy_killed() != 0:
            sb += f"His warriors killed {self.warriors.get_enemy_killed()} of the enemy. "

        if self.battle.get_winner() is not None:
            sb += f"Victory went to the {self.battle.get_winner()}!"
        else:
            sb += "The battle continues!"

        return sb

    def increment_energy(self, increment: int) -> None:
        super().increment_energy(9 + increment)
        if self.warriors is not None:
            self.warriors.increment_energy(increment)
        if self.riders is not None:
            self.riders.increment_energy(increment)

    def dawn(self) -> None:
        self.time.dawn()
        if self.is_alive():
            if self.riders is not None:
                self.riders.dawn()
            if self.warriors is not None:
                self.warriors.dawn()
        self.clear_found()
        self.clear_killed()

    def get_object(self) -> Object:
        return self.object

    def set_object(self, object: Object) -> None:
        self.object = object

    def get_found(self) -> Object:
        return self.found

    def clear_found(self):
        self.found = None

    def seek(self) -> Object:
        object = self.get_location().get_object()
        self.found = object

        if object in [Object.DRAGONSLAYER, Object.WOLFSLAYER]:
            if self.get_object() not in [Object.ICE_CROWN, Object.MOON_RING]:
                self.get_location().set_object(self.get_object())
                self.set_object(object)
        elif object == Object.WILD_HORSES:
            if self.get_race() in [Race.FREE, Race.FEY, Race.TARG, Race.WISE]:
                self.set_on_horse(True)
        elif object == Object.SHELTER:
            self.increment_energy(0x10)
            self.get_location().set_object(Object.NOTHING)
        elif object == Object.HAND_OF_DARK:
            self.time.night()
            self.get_location().set_object(Object.NOTHING)
        elif object == Object.CUP_OF_DREAMS:
            self.time.dawn()
            self.get_location().set_object(Object.NOTHING)
        elif object == Object.WATERS_OF_LIFE:
            self.set_energy(0x78)
            self.warriors.set_energy(0x78)
            self.riders.set_energy(0x78)
            self.get_location().set_object(Object.NOTHING)
        elif object == Object.SHADOWS_OF_DEATH:
            self.set_energy(0)
            self.warriors.set_energy(0)
            self.riders.set_energy(0)
            self.get_location().set_object(Object.NOTHING)
        elif object in [Object.ICE_CROWN, Object.MOON_RING]:
            if self == self.get_game().MORKIN:
                self.get_location().set_object(self.get_object())
                self.set_object(object)
            else:
                return Object.NOTHING
        return object

    def drop_object(self) -> None:
        self.get_location().set_object(self.get_object())
        self.set_object(Object.NOTHING)

    def can_fight(self) -> bool:
        object = self.get_location().get_object()
        return not self.is_hidden() and (
                object in [Object.DRAGONS, Object.ICE_TROLLS, Object.SKULKRIN, Object.WOLVES]) and (
                len(self.get_location().get_armies()) == 0 or self == self.get_game().MORKIN)

    def fight(self) -> None:
        object = self.get_location().get_object()

        self.killed = object
        for character in self.get_location().get_characters():
            if character.get_warriors().get_how_many() != 0 or character.get_riders().get_how_many() != 0:
                self.get_location().set_object(Object.NOTHING)
                return
        if (object == Object.WOLVES and self.get_object() == Object.WOLFSLAYER) or (
                object == Object.DRAGONS and self.get_object() == Object.DRAGONSLAYER):
            self.get_location().set_object(Object.NOTHING)
            return
        self.maybe_lose()
        self.get_location().set_object(Object.NOTHING)

    def maybe_lose(self):
        if self.is_on_horse():
            self.set_on_horse(self.get_game().random(2) == 0)
        if (self.get_energy() / 2 - 0x40 + self.life) < self.get_game().random(256):
            self.die()

    def get_killed(self) -> Object:
        return self.killed

    def set_killed(self, killed: Object) -> None:
        self.killed = killed

    def clear_killed(self) -> None:
        if self.is_alive():
            self.killed = None

    def __str__(self):
        return self.get_full_title()

    def __lt__(self, __value):
        return self.id < __value.id

    def __eq__(self, __value):
        return self.id == __value.id

    def save(self):
        raise NotImplementedError()

    @staticmethod
    def load():
        raise NotImplementedError()

    def update(self):
        raise NotImplementedError


class Doomguard(Army):
    MAX_MOVE_COUNT = 6
    next_id = 0

    def __init__(self, game: 'Midnight', energy: int, how_many: int, type: Type, orders: Orders, target: Any) -> None:
        super().__init__(game, Race.FOUL, how_many, type)
        self.move_count = 0
        self.orders = orders
        self.target = target
        self.id = Doomguard.next_id
        Doomguard.next_id += 1

    def __str__(self):
        return f"{self.id} Doomguard ({super.__str__(self)} at {self.get_location()}): {self.orders} {self.target if self.target is not None else ''})"

    def set_location(self, x, y: int = -1) -> None:
        if isinstance(x, int):
            location = self.get_game().get_map().get_location(x, y)
        else:
            location = x
        if self.get_location() is not None:
            self.get_location().remove_army(self)
        super().set_location(location)
        self.get_location().append_army(self)

    def get_orders(self) -> Orders:
        return self.orders

    def get_target(self) -> Any:
        return self.target

    def decrease_numbers(self, decrease: int) -> None:
        super().decrease_numbers(decrease)
        if self.get_how_many() == 0:
            self.get_location().remove_army(self)
            self.get_game().remove_doomguard(self)

    def execute_move(self) -> None:
        if self.get_location().is_special():
            self.stop_moving()

        direction = Direction.NORTH
        for i in range(8):
            location = self.get_game().get_map().get_in_front(self.get_location(), direction)
            if location.is_special():
                self.move_to(self.get_game().get_map().get_in_front(self.get_location(), direction))
                return
            direction = direction.turn_right()

        if self.orders == Orders.FOLLOW:
            self.follow_character()
        elif self.orders == Orders.GOTO:
            self.follow_goto()
        elif self.orders == Orders.ROUTE:
            self.follow_route()
        elif self.orders == Orders.WANDER:
            self.wander()

    def follow_character(self) -> None:
        character: Character = self.target
        if not character.is_alive():
            if self.get_game().LUXOR.is_alive():
                character = self.get_game().LUXOR
            else:
                character = self.get_game().MORKIN
            self.target = character
        self.move_towards(character.get_location())

    def follow_goto(self) -> None:
        location: Location = self.target
        if location.is_special():
            self.move_towards(self.target)
        else:
            self.stop_moving()

    def follow_route(self) -> None:
        destination: Location = self.target
        if self.get_location() == destination:
            if self.get_game().random(2) == 0:
                destination = self.get_game().get_map().get_next_node_a(destination)
            else:
                destination = self.get_game().get_map().get_next_node_b(destination)
            self.target = destination
        self.move_towards(destination)

    def wander(self) -> None:
        while True:
            location = self.get_game().get_map().get_in_front(self.get_location(),
                                                              Direction.get_direction(self.get_game().random(8)))
            if location.get_feature() != Feature.FROZEN_WASTE:
                break
        self.move_to(location)

    def move_towards(self, location: 'Location') -> None:
        if self.get_location() != location:
            direction = Map.calc_direction(self.get_location(), location)
            for i in range(8):
                rnd = self.get_game().random(4)
                if rnd in [0, 1]:
                    destination = self.get_game().get_map().get_in_front(self.get_location(), direction)
                elif rnd == 2:
                    destination = self.get_game().get_map().get_in_front(self.get_location(), direction.turn_left())
                elif rnd == 3:
                    destination = self.get_game().get_map().get_in_front(self.get_location(), direction.turn_right())
                if destination.get_feature() not in [Feature.FOREST, Feature.MOUNTAIN, Feature.FROZEN_WASTE]:
                    break
            if destination.get_feature() != Feature.FROZEN_WASTE:
                self.move_to(destination)
            else:
                self.stop_moving()
        else:
            self.stop_moving()

    def stop_moving(self) -> None:
        self.move_count = self.MAX_MOVE_COUNT

    def get_move_count(self) -> int:
        return self.move_count

    def reset_move_count(self) -> None:
        self.move_count = 0

    def move_to(self, location: 'Location') -> None:
        if len(location.get_armies()) > 0x1f:
            self.stop_moving()
            return
        cost = 8 if location.get_feature() in [Feature.FOREST, Feature.MOUNTAIN] else 2
        if self.get_type() == Type.RIDERS:
            cost /= 2
        self.move_count += cost
        self.set_location(location)

    def save(self):
        raise NotImplementedError()

    @staticmethod
    def load():
        raise NotImplementedError()


class Location:
    characters: set[Character]
    armies: set[Army]
    guard: Optional[Army]

    def __init__(self, game: Optional['Midnight'], x: int, y: int, feature: Feature, object: Object, area: Area,
                 domain: bool,
                 special: bool) -> None:
        self.ice_fear = 0
        self.characters = set()
        self.armies = set()
        self.guard = None
        self.game = game
        self.x = x
        self.y = y
        self.feature = feature
        self.object = object
        self.area = area
        self.domain = domain
        self.special = special

    def get_coordinates(self) -> str:
        return f" [{self.x}, {self.y}]"

    def __str__(self):
        if self.domain:
            return f"{self.get_article(self.feature)}{self.feature} in the Domain of {self.area}"
        if self.feature == Feature.HENGE:
            return f"{self.area}Henge"
        if self.feature == Feature.LAKE:
            return f"Lake {self.area}"
        if self.feature == Feature.FROZEN_WASTE:
            return "the Frozen Wastes"

        name = f"the {self.capitalize(self.feature)} of {self.area}"
        return name

    def get_x(self) -> int:
        return self.x

    def get_y(self) -> int:
        return self.y

    def get_map(self) -> 'Map':
        return self.game.get_map()

    def get_game(self) -> 'Midnight':
        return self.game

    @staticmethod
    def get_article(feature: Feature) -> str:
        if feature in [Feature.MOUNTAIN, Feature.DOWNS, Feature.FROZEN_WASTE, Feature.ARMY, Feature.PLAINS]:
            return " "
        return "a "

    def get_feature(self) -> Feature:
        return self.feature

    def get_domain(self) -> Area:
        return self.area

    def get_domain_flag(self) -> bool:
        return self.domain

    def get_object(self) -> Object:
        return self.object

    def set_object(self, object: Object) -> None:
        self.object = object

    def is_special(self) -> bool:
        return self.special

    def set_special(self, special: bool) -> None:
        self.special = special

    def get_guard(self) -> Army:
        return self.guard

    def set_guard(self, guard: Army) -> None:
        if self.feature in [Feature.KEEP, Feature.CITADEL]:
            self.guard = guard

    def get_armies(self) -> set[Army]:
        return self.armies

    def append_army(self, army: Army) -> None:
        self.armies.add(army)
        if self.feature == Feature.PLAINS:
            self.feature = Feature.ARMY

    def remove_army(self, army: Army) -> None:
        self.armies.remove(army)
        if self.feature == Feature.ARMY and len(self.armies) == 0:
            self.feature = Feature.PLAINS

    def get_characters(self) -> set[Character]:
        return self.characters

    def append_character(self, character: Character) -> None:
        self.characters.add(character)
        if self.feature == Feature.PLAINS and (
                character.get_riders().get_how_many() > 0 or character.get_warriors().get_how_many() > 0):
            self.feature = Feature.ARMY

    def remove_character(self, character: Character) -> None:
        self.characters.remove(character)
        if self.feature == Feature.ARMY:
            for c in self.characters:
                if c.get_warriors().get_how_many() > 0 or c.get_riders().get_how_many() > 0:
                    return
            self.feature = Feature.PLAINS

    def riders_battle_bonus(self) -> int:
        return 0x20 if self.feature == Feature.MOUNTAIN else 0x40

    @staticmethod
    def capitalize(o: Any) -> str:
        return str(o).capitalize()

    def save(self):
        raise NotImplementedError()

    @staticmethod
    def load():
        raise NotImplementedError()

    def get_ice_fear(self) -> int:
        if self.game.MORKIN.is_alive():
            if Map.calc_distance(self, self.game.MORKIN.get_location()) == 0:
                self.ice_fear = 0x1ff - Map.calc_distance(self, self.get_map().TOWER_OF_DESPAIR) * 4
                return self.ice_fear
            fear = Map.calc_distance(self.game.MORKIN.get_location(), self.get_map().TOWER_OF_DESPAIR)
        else:
            fear = 0x7f

        fear += Map.calc_distance(self, self.game.LUXOR.get_location()) if self.game.LUXOR.is_alive() else 0x7f

        fear += 0x30
        fear += self.game.get_doom_darks_citadels()

        self.ice_fear = fear
        return self.ice_fear

    def describe_fear(self) -> Fear:
        return Fear.get_fear(7 - self.ice_fear // 0x40)


class FrozenWaste(Location):
    instance: 'FrozenWaste'

    def __init__(self) -> None:
        super().__init__(None, -1, -1, Feature.FROZEN_WASTE, Object.NOTHING, Area.NOTHING, False, False)

    @staticmethod
    def get_instance() -> Location:
        if FrozenWaste.instance is None:
            FrozenWaste.instance = FrozenWaste()
        return FrozenWaste.instance


class Map:
    routeNodes: dict[Location, int]
    locations: list[list[Optional[Location]]]
    TOWER_OF_DESPAIR: Location

    def __init__(self, game: 'Midnight') -> None:
        self.game = game
        self.locations = [[None for _ in range(61)] for _ in range(64)]
        i = 0
        for y in range(self.height()):
            for x in range(self.width()):
                feature = Feature.get_feature(mainMap[i] & 0x0f)
                object = Object.get_object(mainMap[i] >> 4)

                area = Area.get_area(referenceDescriptionMap[i] & 0x3f)
                domain = (referenceDescriptionMap[i] & 0x40) != 0
                special = (referenceDescriptionMap[i] & 0x80) != 0
                self.locations[x][y] = Location(game, x, y, feature, object, area, domain, special)
                i += 1
        self.TOWER_OF_DESPAIR = self.get_location(26, 4)
        self.XAJORKITH = self.get_location(45, 59)
        self.USHGARAK = self.get_location(29, 7)
        self.LAKE_MIRROW = self.get_location(9, 17)

        self.routeNodes = {}
        for i in range(len(routes)):
            self.routeNodes[self.locations[routes[i][0]][routes[i][1]]] = i

    def width(self) -> int:
        return len(self.locations)

    def height(self) -> int:
        return len(self.locations[0])

    def get_location(self, x: int, y: int) -> Location:
        if x < 0 or y < 0 or x >= self.width() or y >= self.height():
            return FrozenWaste.get_instance()
        return self.locations[x][y]

    def set_location(self, l: Location) -> None:
        self.locations[l.get_x()][l.get_y()] = l

    def get_in_front(self, location: Location, direction: Direction) -> Location:
        x = location.get_x() + direction.get_x_adjustment()
        y = location.get_y() + direction.get_y_adjustment()
        if x < 0 or x >= self.width() or y < 0 or y >= self.height():
            return FrozenWaste.get_instance()
        return self.locations[x][y]

    def get_looking_towards(self, location: Location, direction: Direction) -> Location:
        for i in range(3):
            location = self.get_in_front(location, direction)
            if location.get_feature() != Feature.PLAINS or location.is_special():
                break

        return location

    @staticmethod
    def calc_distance(a: Location, b: Location) -> int:
        return abs(a.get_x() - b.get_x()) + abs(a.get_y() - b.get_y())

    @staticmethod
    def calc_direction(origin: Location, target: Location) -> Direction:
        if origin.get_x() > target.get_x():
            if origin.get_y() > target.get_y():
                return Direction.NORTHWEST
            if origin.get_y() < target.get_y():
                return Direction.SOUTHWEST
            return Direction.WEST

        if origin.get_x() < target.get_x():
            if origin.get_y() > target.get_y():
                return Direction.NORTHEAST
            if origin.get_y() < target.get_y():
                return Direction.SOUTHEAST
            return Direction.EAST
        if origin.get_y() > target.get_y():
            return Direction.NORTH
        if origin.get_y() < target.get_y():
            return Direction.SOUTH
        assert False

    def load(self):
        raise NotImplementedError()

    def save(self):
        raise NotImplementedError()

    def get_route_node(self, index: int) -> Location:
        return self.locations[routes[index][0]][routes[index][1]]

    def get_node_index(self, node: Location) -> int:
        return self.routeNodes[node]

    def get_next_node_a(self, location: Location) -> Location:
        next_node = routes[self.get_node_index(location)][2]
        return self.locations[routes[next_node][0]][routes[next_node][1]]

    def get_next_node_b(self, location: Location) -> Location:
        next_node = routes[self.get_node_index(location)][3]
        return self.locations[routes[next_node][0]][routes[next_node][1]]


class Midnight:
    instance = None
    status: Optional[Status]
    battles: dict[Location, Battle]
    armies: list[Army]
    characters: list[Character]
    doomguard: list[Doomguard]
    LUXOR: Character
    MORKIN: Character
    FARFLAME: Character
    FAWKRIN: Character
    LORGRIM: Character

    def __init__(self, random: Random = Random()):
        self.status = None
        self.doom_darks_citadels = 0
        self.ice_crown_destroyed = False
        self.armies = []
        self.characters = []
        self.game_over = False
        self.doomguard = []
        self.random_generator = random
        self.map = Map(self)
        self.day = 0
        self.moon_ring_controlled = True
        self.battles = dict()
        self.initialize_characters()
        self.initialize_armies()
        self.initialize_doomguard()

    def get_map(self) -> Map:
        return self.map

    def set_map(self, map: Map) -> None:
        self.map = map

    def remove_doomguard(self, army: Doomguard) -> None:
        self.doomguard.remove(army)

    def get_day(self) -> int:
        return self.day

    def is_controllable(self, character: Character) -> bool:
        if character != self.LUXOR and character != self.MORKIN:
            return character.is_recruited() and self.is_moon_ring_controlled()
        return True

    def is_moon_ring_controlled(self) -> bool:
        return self.moon_ring_controlled

    def night(self) -> None:
        self.check_special_conditions()
        if not self.game_over:
            self.day += 1
            self.calc_doom_darks_citadels()
            self.calc_night_activity()

    def dawn(self) -> None:
        for character in self.characters:
            character.dawn()
        for army in self.armies:
            army.dawn()
        for army in self.doomguard:
            army.dawn()


    def check_special_conditions(self)->None:
        if not self.LUXOR.is_alive() and self.LUXOR.get_object() == Object.MOON_RING:
            self.LUXOR.drop_object()
            self.moon_ring_controlled = False

        if self.MORKIN.is_alive():
            if self.MORKIN.get_object() == Object.MOON_RING:
                self.moon_ring_controlled = True
            elif self.MORKIN.get_object() == Object.ICE_CROWN:
                if self.MORKIN.get_location() in [self.map.LAKE_MIRROW, self.FAWKRIN.get_location(),
                                                  self.LORGRIM.get_location(), self.FARFLAME.get_location()]:
                    self.ice_crown_destroyed = True

        self.check_game_over()

    def calc_doom_darks_citadels(self):
        self.doom_darks_citadels = 0
        for army in self.armies:
            if army.get_race() == Race.FOUL:
                self.doom_darks_citadels += 5 if army.get_location().get_feature() == Feature.CITADEL else 2

    def calc_night_activity(self):
        self.battles.clear()
        for character in self.characters:
            character.increment_energy(character.get_time().get_time() // 2)
            if character.is_alive() and not character.is_hidden():
                character.get_location().set_special(True)
                character.set_battle(None)
                character.set_enemy_killed(0)
                character.get_riders().set_casualties(0)
                character.get_riders().set_enemy_killed(0)
                character.get_warriors().set_casualties(0)
                character.get_warriors().set_enemy_killed(0)

        for army in self.armies:
            if army.get_race() != Race.FOUL:
                army.get_location().set_special(True)

        for doomguard in self.doomguard:
            while doomguard.get_move_count() < Doomguard.MAX_MOVE_COUNT:
                doomguard.execute_move()
            doomguard.reset_move_count()

        for character in self.characters:
            location = character.get_location()
            location.set_special(False)
            if (len(location.get_armies()) > 0 or (
                    location.get_guard() is not None and location.get_guard().get_race() == Race.FOUL)) and location not in self.battles:
                self.battles[location] = Battle(location)

        for army in self.armies:
            if army.get_race() != Race.FOUL:
                army.get_location().set_special(False)
                if len(army.get_location().get_armies()) > 0 and army.get_location() not in self.battles:
                    self.battles[army.get_location()] = Battle(army.get_location())

        for battle in self.battles.values():
            battle.run()

    def check_game_over(self) -> None:
        if not self.MORKIN.is_alive():
            if not self.LUXOR.is_alive():
                self.game_over = True
                self.status = Status.LUXOR_MORKIN_DEAD
            elif self.map.XAJORKITH.get_guard().get_race() == Race.FOUL:
                self.game_over = True
                self.status = Status.MORKIN_XAJORKITH
        if self.map.USHGARAK.get_guard().get_race() == Race.FREE:
            self.game_over = True
            self.status = Status.USHGARAK
        elif self.ice_crown_destroyed:
            self.game_over = True
            self.status = Status.ICE_CROWN

    @staticmethod
    def get_instance() -> 'Midnight':
        if Midnight.instance is None:
            Midnight.instance = Midnight()
        return Midnight.instance

    def get_battles(self) -> list[Battle]:
        return list(self.battles.values())

    def get_battle_domains(self) -> set[Area]:
        return {battle.get_location().get_domain() for battle in self.battles.values()}

    def get_doom_darks_citadels(self) -> int:
        return self.doom_darks_citadels

    def is_game_over(self) -> bool:
        return self.game_over

    def get_status(self) -> Status:
        return self.status

    def load(self):
        raise NotImplementedError()

    def save(self):
        raise NotImplementedError()

    def initialize_characters(self) -> None:
        self.LUXOR = Character(self, 0, "Luxor", "Luxor the Moonprince", Race.FREE, 12, 40, 180, 127, 25, 80, 0x17,
                               0x00, 0, 0)
        self.LUXOR.set_direction(Direction.SOUTHEAST)

        self.MORKIN = Character(self, 1, "Morkin", "Morkin", Race.MORKIN, 12, 40, 200, 127, 5, 127, 0x7e, 0x00, 0, 0)
        self.MORKIN.set_direction(Direction.SOUTHEAST)

        self.CORLETH = Character(self, 2, "Corleth", "Corleth the Fey", Race.FEY, 12, 40, 180, 127, 20, 96, 0x6b, 0x00,
                                 0, 0)
        self.CORLETH.set_direction(Direction.EAST)

        self.ROTHRON = Character(self, 3, "Rothron", "Rothron the Wise", Race.WISE, 12, 40, 220, 127, 40, 80, 0x7f,
                                 0x00, 0, 0)
        self.ROTHRON.set_direction(Direction.NORTHEAST)

        self.GARD = Character(self, 4, "Gard", "the Lord of Gard", Race.FREE, 10, 55, 150, 64, 10, 64, 0x01, 0x01, 500,
                              1000)
        self.GARD.set_direction(Direction.EAST)

        self.MARAKITH = Character(self, 5, "Marakith", "the Lord of Marakith", Race.FREE, 43, 32, 150, 64, 10, 64, 0x01,
                                  0x01, 500, 1000)
        self.MARAKITH.set_direction(Direction.WEST)

        self.XAJORKITH = Character(self, 6, "Xajorkith", "the Lord of Xajorkith", Race.FREE, 45, 59, 150, 64, 15, 64,
                                   0x01, 0x01, 800, 1200)
        self.XAJORKITH.set_direction(Direction.NORTH)

        self.GLOOM = Character(self, 7, "Gloom", "the Lord of Gloom", Race.FREE, 8, 0, 150, 64, 15, 56, 0x01, 0x01, 500,
                               1000)
        self.GLOOM.set_direction(Direction.EAST)

        self.SHIMERIL = Character(self, 8, "Shimeril", "the Lord of Shimeril", Race.FREE, 28, 42, 150, 64, 15, 64, 0x01,
                                  0x01, 800, 1000)
        self.SHIMERIL.set_direction(Direction.NORTHWEST)

        self.KUMAR = Character(self, 9, "Kumar", "the Lord of Kumar", Race.FREE, 57, 29, 150, 64, 10, 64, 0x01, 0x01,
                               700, 1000)
        self.KUMAR.set_direction(Direction.NORTH)

        self.ITHRORN = Character(self, 10, "Ithrorn", "the Lord of Ithrorn", Race.FREE, 57, 15, 150, 64, 15, 64, 0x09,
                                 0x01, 1000, 1200)
        self.ITHRORN.set_direction(Direction.NORTHWEST)

        self.DAWN = Character(self, 11, "Dawn", "the Lord of Dawn", Race.FREE, 44, 45, 150, 64, 8, 48, 0x01, 0x01, 500,
                              800)
        self.DAWN.set_direction(Direction.NORTH)

        self.DREAMS = Character(self, 12, "Dreams", "the Lord Of Dreams", Race.FEY, 42, 16, 180, 64, 20, 90, 0x1f, 0x08,
                                800, 1200)
        self.DREAMS.set_direction(Direction.NORTH)

        self.DREGRIM = Character(self, 13, "Dregrim", "the Lord Of Dregrim", Race.FEY, 59, 43, 150, 64, 15, 80, 0x1f,
                                 0x08, 400, 1000)
        self.DREGRIM.set_direction(Direction.NORTH)

        self.THIMRATH = Character(self, 14, "Thimrath", "Thimrath the Fey", Race.FEY, 33, 60, 130, 64, 12, 90, 0x1a,
                                  0x02, 600, 400)
        self.THIMRATH.set_direction(Direction.WEST)

        self.WHISPERS = Character(self, 15, "Whispers", "the Lord Of Whispers", Race.FEY, 57, 20, 150, 64, 12, 80, 0x1a,
                                  0x02, 300, 600)
        self.WHISPERS.set_direction(Direction.NORTHWEST)

        self.SHADOWS = Character(self, 16, "Shadows", "the Lord Of Shadows", Race.FEY, 11, 37, 130, 64, 12, 70, 0x1a,
                                 0x02, 0, 1000)
        self.SHADOWS.set_direction(Direction.NORTH)
        self.SHADOWS.set_on_horse(False)

        self.LOTHORIL = Character(self, 17, "Lothoril", "the Lord Of Lothoril", Race.FEY, 11, 10, 100, 64, 8, 60, 0x1a,
                                  0x02, 200, 500)
        self.LOTHORIL.set_direction(Direction.EAST)

        self.KORINEL = Character(self, 18, "Korinel", "Korinel the Fey", Race.FEY, 23, 21, 120, 64, 12, 60, 0x1a, 0x02,
                                 0, 1000)
        self.KORINEL.set_direction(Direction.NORTH)
        self.KORINEL.set_on_horse(False)

        self.THRALL = Character(self, 19, "Thrall", "the Lord Of Thrall", Race.FEY, 33, 38, 150, 64, 10, 70, 0x1a, 0x02,
                                300, 600)
        self.THRALL.set_direction(Direction.NORTHWEST)

        self.BRITH = Character(self, 20, "Brith", "Lord Brith", Race.FREE, 21, 49, 100, 64, 8, 40, 0x01, 0x01, 500, 300)
        self.BRITH.set_direction(Direction.NORTHEAST)

        self.RORATH = Character(self, 21, "Rorath", "Lord Rorath", Race.FREE, 23, 60, 100, 64, 8, 50, 0x01, 0x01, 800,
                                400)
        self.RORATH.set_direction(Direction.NORTH)

        self.TRORN = Character(self, 22, "Trorn", "Lord Trorn", Race.FREE, 54, 50, 100, 64, 8, 35, 0x01, 0x01, 400, 800)
        self.TRORN.set_direction(Direction.NORTHWEST)

        self.MORNING = Character(self, 23, "Morning", "the Lord Of Morning", Race.FREE, 39, 51, 120, 64, 8, 40, 0x01,
                                 0x01, 300, 800)
        self.MORNING.set_direction(Direction.NORTH)

        self.ATHORIL = Character(self, 24, "Athoril", "Lord Athoril", Race.FREE, 54, 38, 120, 64, 8, 50, 0x01, 0x01,
                                 800, 300)
        self.ATHORIL.set_direction(Direction.NORTH)

        self.BLOOD = Character(self, 25, "Blood", "Lord Blood", Race.FREE, 21, 36, 150, 64, 15, 80, 0x01, 0x01, 1200, 0)
        self.BLOOD.set_direction(Direction.NORTH)

        self.HERATH = Character(self, 26, "Herath", "Lord Herath", Race.FREE, 45, 26, 130, 64, 8, 40, 0x01, 0x01, 500,
                                600)
        self.HERATH.set_direction(Direction.NORTHEAST)

        self.MITHARG = Character(self, 27, "Mitharg", "Lord Mitharg", Race.FREE, 29, 46, 130, 64, 8, 50, 0x01, 0x01,
                                 500, 600)
        self.MITHARG.set_direction(Direction.NORTH)

        self.UTARG = Character(self, 28, "Utarg", "the Utarg Of Utarg", Race.TARG, 59, 34, 180, 64, 20, 80, 0x00, 0x04,
                               1000, 0)
        self.UTARG.set_direction(Direction.WEST)

        self.FAWKRIN = Character(self, 29, "Fawkrin", "Fawkrin the Skulkrin", Race.SKULKRIN, 1, 10, 200, 64, 1, 30,
                                 0x00, 0x20, 0, 0)
        self.FAWKRIN.set_direction(Direction.EAST)

        self.LORGRIM = Character(self, 30, "Lorgrim", "Lorgrim the Wise", Race.WISE, 62, 0, 200, 64, 20, 70, 0x7f, 0x10,
                                 0, 0)
        self.LORGRIM.set_direction(Direction.SOUTH)

        self.FARFLAME = Character(self, 31, "Farflame", "Farflame the Dragonlord", Race.DRAGON, 12, 23, 200, 64, 100,
                                  127, 0x00, 0x40, 0, 0)
        self.FARFLAME.set_direction(Direction.SOUTHEAST)

        self.LUXOR.set_recruited(True)
        self.LUXOR.set_object(Object.MOON_RING)
        self.MORKIN.set_recruited(True)
        self.CORLETH.set_recruited(True)
        self.ROTHRON.set_recruited(True)
        self.characters.append(self.LUXOR)
        self.characters.append(self.MORKIN)
        self.characters.append(self.CORLETH)
        self.characters.append(self.ROTHRON)
        self.characters.append(self.GARD)
        self.characters.append(self.MARAKITH)
        self.characters.append(self.XAJORKITH)
        self.characters.append(self.GLOOM)
        self.characters.append(self.SHIMERIL)
        self.characters.append(self.KUMAR)
        self.characters.append(self.ITHRORN)
        self.characters.append(self.DAWN)
        self.characters.append(self.DREAMS)
        self.characters.append(self.DREGRIM)
        self.characters.append(self.THIMRATH)
        self.characters.append(self.WHISPERS)
        self.characters.append(self.SHADOWS)
        self.characters.append(self.LOTHORIL)
        self.characters.append(self.KORINEL)
        self.characters.append(self.THRALL)
        self.characters.append(self.BRITH)
        self.characters.append(self.RORATH)
        self.characters.append(self.TRORN)
        self.characters.append(self.MORNING)
        self.characters.append(self.ATHORIL)
        self.characters.append(self.BLOOD)
        self.characters.append(self.HERATH)
        self.characters.append(self.MITHARG)
        self.characters.append(self.UTARG)
        self.characters.append(self.FAWKRIN)
        self.characters.append(self.LORGRIM)
        self.characters.append(self.FARFLAME)

    def initialize_armies(self):
        army = Army(self, Race.FREE, 600, Type.WARRIORS)
        army.guard(8, 0) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 200, Type.RIDERS)
        army.guard(46, 3) 
        self.armies.append(army)
        
        army = Army(self, Race.FOUL, 400, Type.WARRIORS)
        army.guard(28, 4) 
        self.armies.append(army)
        
        army = Army(self, Race.FOUL, 1000, Type.WARRIORS)
        army.guard(22, 5) 
        self.armies.append(army)
        
        army = Army(self, Race.FOUL, 300, Type.RIDERS)
        army.guard(32, 6) 
        self.armies.append(army)
        
        army = Army(self, Race.FOUL, 500, Type.WARRIORS)
        army.guard(23, 7) 
        self.armies.append(army)
        
        army = Army(self, Race.FOUL, 1200, Type.RIDERS)
        army.guard(29, 7) 
        self.armies.append(army)
        
        army = Army(self, Race.FOUL, 1100, Type.WARRIORS)
        army.guard(37, 7) 
        self.armies.append(army)
        
        army = Army(self, Race.FOUL, 400, Type.RIDERS)
        army.guard(40, 8) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 300, Type.WARRIORS)
        army.guard(57, 8) 
        self.armies.append(army)
        
        army = Army(self, Race.FOUL, 500, Type.WARRIORS)
        army.guard(39, 9) 
        self.armies.append(army)
        
        army = Army(self, Race.FEY, 200, Type.WARRIORS)
        army.guard(11, 10) 
        self.armies.append(army)
        
        army = Army(self, Race.FOUL, 300, Type.WARRIORS)
        army.guard(21, 11) 
        self.armies.append(army)
        
        army = Army(self, Race.FOUL, 250, Type.WARRIORS)
        army.guard(25, 11) 
        self.armies.append(army)
        
        army = Army(self, Race.FOUL, 1000, Type.RIDERS)
        army.guard(29, 12) 
        self.armies.append(army)
        
        army = Army(self, Race.FOUL, 300, Type.RIDERS)
        army.guard(36, 12) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 200, Type.RIDERS)
        army.guard(51, 12) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 150, Type.WARRIORS)
        army.guard(62, 12) 
        self.armies.append(army)
        
        army = Army(self, Race.FOUL, 200, Type.WARRIORS)
        army.guard(16, 13) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 300, Type.WARRIORS)
        army.guard(55, 13) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 700, Type.WARRIORS)
        army.guard(57, 15) 
        self.armies.append(army)
        
        army = Army(self, Race.FOUL, 250, Type.WARRIORS)
        army.guard(14, 16) 
        self.armies.append(army)
        
        army = Army(self, Race.FOUL, 500, Type.WARRIORS)
        army.guard(27, 16) 
        self.armies.append(army)
        
        army = Army(self, Race.FOUL, 200, Type.WARRIORS)
        army.guard(34, 16) 
        self.armies.append(army)
        
        army = Army(self, Race.FEY, 550, Type.WARRIORS)
        army.guard(42, 16) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 150, Type.RIDERS)
        army.guard(52, 16) 
        self.armies.append(army)
        
        army = Army(self, Race.FOUL, 250, Type.WARRIORS)
        army.guard(19, 17) 
        self.armies.append(army)
        
        army = Army(self, Race.FOUL, 150, Type.WARRIORS)
        army.guard(22, 18) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 250, Type.WARRIORS)
        army.guard(54, 18) 
        self.armies.append(army)
        
        army = Army(self, Race.FOUL, 100, Type.WARRIORS)
        army.guard(14, 20) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 300, Type.WARRIORS)
        army.guard(49, 20) 
        self.armies.append(army)
        
        army = Army(self, Race.FEY, 150, Type.WARRIORS)
        army.guard(57, 20) 
        self.armies.append(army)
        
        army = Army(self, Race.FOUL, 900, Type.WARRIORS)
        army.guard(18, 21) 
        self.armies.append(army)
        
        army = Army(self, Race.FOUL, 100, Type.WARRIORS)
        army.guard(42, 21) 
        self.armies.append(army)
        
        army = Army(self, Race.FOUL, 350, Type.WARRIORS)
        army.guard(31, 22) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 400, Type.RIDERS)
        army.guard(46, 22) 
        self.armies.append(army)
        
        army = Army(self, Race.FOUL, 250, Type.WARRIORS)
        army.guard(39, 23) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 200, Type.WARRIORS)
        army.guard(56, 24) 
        self.armies.append(army)
        
        army = Army(self, Race.FOUL, 200, Type.WARRIORS)
        army.guard(32, 25) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 300, Type.WARRIORS)
        army.guard(45, 26) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 150, Type.RIDERS)
        army.guard(54, 26) 
        self.armies.append(army)
        
        army = Army(self, Race.FOUL, 200, Type.RIDERS)
        army.guard(34, 27) 
        self.armies.append(army)
        
        army = Army(self, Race.FOUL, 250, Type.WARRIORS)
        army.guard(17, 28) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 250, Type.WARRIORS)
        army.guard(42, 28) 
        self.armies.append(army)
        
        army = Army(self, Race.FOUL, 1000, Type.WARRIORS)
        army.guard(24, 29) 
        self.armies.append(army)
        
        army = Army(self, Race.FOUL, 150, Type.WARRIORS)
        army.guard(30, 29) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 150, Type.RIDERS)
        army.guard(51, 29) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 600, Type.RIDERS)
        army.guard(57, 29) 
        self.armies.append(army)
        
        army = Army(self, Race.TARG, 200, Type.RIDERS)
        army.guard(55, 31) 
        self.armies.append(army)
        
        army = Army(self, Race.FOUL, 300, Type.WARRIORS)
        army.guard(21, 32) 
        self.armies.append(army)
        
        army = Army(self, Race.FOUL, 300, Type.WARRIORS)
        army.guard(23, 32) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 700, Type.WARRIORS)
        army.guard(43, 32) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 250, Type.WARRIORS)
        army.guard(13, 33) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 150, Type.WARRIORS)
        army.guard(34, 33) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 100, Type.RIDERS)
        army.guard(30, 34) 
        self.armies.append(army)
        
        army = Army(self, Race.TARG, 350, Type.RIDERS)
        army.guard(59, 34) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 400, Type.WARRIORS)
        army.guard(21, 36) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 150, Type.WARRIORS)
        army.guard(54, 38) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 200, Type.WARRIORS)
        army.guard(27, 39) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 200, Type.WARRIORS)
        army.guard(22, 40) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 200, Type.WARRIORS)
        army.guard(25, 40) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 100, Type.WARRIORS)
        army.guard(48, 40) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 150, Type.RIDERS)
        army.guard(42, 41) 
        self.armies.append(army)
        
        army = Army(self, Race.FEY, 100, Type.RIDERS)
        army.guard(55, 41) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 250, Type.RIDERS)
        army.guard(17, 42) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 750, Type.WARRIORS)
        army.guard(28, 42) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 100, Type.RIDERS)
        army.guard(37, 43) 
        self.armies.append(army)
        
        army = Army(self, Race.FEY, 500, Type.WARRIORS)
        army.guard(59, 43) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 550, Type.WARRIORS)
        army.guard(44, 45) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 150, Type.WARRIORS)
        army.guard(29, 46) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 100, Type.RIDERS)
        army.guard(42, 46) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 150, Type.WARRIORS)
        army.guard(7, 47) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 250, Type.WARRIORS)
        army.guard(10, 47) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 200, Type.WARRIORS)
        army.guard(48, 48) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 150, Type.RIDERS)
        army.guard(21, 49) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 250, Type.RIDERS)
        army.guard(45, 49) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 150, Type.WARRIORS)
        army.guard(54, 50) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 200, Type.WARRIORS)
        army.guard(39, 51) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 150, Type.WARRIORS)
        army.guard(42, 51) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 150, Type.WARRIORS)
        army.guard(50, 51) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 200, Type.WARRIORS)
        army.guard(46, 52) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 250, Type.WARRIORS)
        army.guard(12, 54) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 250, Type.WARRIORS)
        army.guard(25, 54) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 200, Type.WARRIORS)
        army.guard(44, 54) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 150, Type.WARRIORS)
        army.guard(55, 54) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 100, Type.RIDERS)
        army.guard(7, 55) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 600, Type.RIDERS)
        army.guard(10, 55) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 250, Type.WARRIORS)
        army.guard(17, 56) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 150, Type.WARRIORS)
        army.guard(21, 56) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 150, Type.WARRIORS)
        army.guard(37, 56) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 150, Type.WARRIORS)
        army.guard(8, 57) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 200, Type.WARRIORS)
        army.guard(12, 57) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 200, Type.WARRIORS)
        army.guard(39, 58) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 250, Type.WARRIORS)
        army.guard(56, 58) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 150, Type.RIDERS)
        army.guard(63, 58) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 300, Type.WARRIORS)
        army.guard(42, 59) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 750, Type.RIDERS)
        army.guard(45, 59) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 50, Type.RIDERS)
        army.guard(4, 60) 
        self.armies.append(army)
        
        army = Army(self, Race.FEY, 300, Type.RIDERS)
        army.guard(33, 60) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 250, Type.RIDERS)
        army.guard(23, 60) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 250, Type.WARRIORS)
        army.guard(59, 60) 
        self.armies.append(army)
        
        army = Army(self, Race.FREE, 200, Type.WARRIORS)
        army.guard(14, 60) 
        self.armies.append(army)

    def initialize_doomguard(self):
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.FOLLOW, self.LUXOR)
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.FOLLOW, self.LUXOR)
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.FOLLOW, self.LUXOR)
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.FOLLOW, self.LUXOR)
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.FOLLOW, self.LUXOR)
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.FOLLOW, self.LUXOR)
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.FOLLOW, self.LUXOR)
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.FOLLOW, self.LUXOR)
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.FOLLOW, self.LUXOR)
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.FOLLOW, self.LUXOR)
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.FOLLOW, self.MORKIN)
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.FOLLOW, self.CORLETH)
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.FOLLOW, self.ROTHRON)
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.FOLLOW, self.GARD)
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.FOLLOW, self.MARAKITH)
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.FOLLOW, self.XAJORKITH)
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.FOLLOW, self.SHIMERIL)
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.FOLLOW, self.KUMAR)
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.FOLLOW, self.ITHRORN)
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.FOLLOW, self.DAWN)
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.FOLLOW, self.DREGRIM)
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.FOLLOW, self.THIMRATH)
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.FOLLOW, self.SHADOWS)
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.FOLLOW, self.THRALL)
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.FOLLOW, self.BRITH)
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.FOLLOW, self.RORATH)
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.FOLLOW, self.TRORN)
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.FOLLOW, self.MORNING)
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.FOLLOW, self.ATHORIL)
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.FOLLOW, self.BLOOD)
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.FOLLOW, self.HERATH)
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.FOLLOW, self.MITHARG)
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.RIDERS, Orders.ROUTE, self.get_map().get_route_node(6))
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.RIDERS, Orders.ROUTE, self.get_map().get_route_node(6))
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.RIDERS, Orders.ROUTE, self.get_map().get_route_node(6))
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.RIDERS, Orders.ROUTE, self.get_map().get_route_node(6))
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.RIDERS, Orders.ROUTE, self.get_map().get_route_node(6))
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.RIDERS, Orders.ROUTE, self.get_map().get_route_node(6))
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.RIDERS, Orders.ROUTE, self.get_map().get_route_node(6))
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.RIDERS, Orders.ROUTE, self.get_map().get_route_node(6))
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(3))
        army.set_location(22, 5)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(3))
        army.set_location(22, 5)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(3))
        army.set_location(22, 5)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(3))
        army.set_location(22, 5)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(7))
        army.set_location(37, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(7))
        army.set_location(37, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(7))
        army.set_location(37, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(7))
        army.set_location(37, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.FOLLOW, self.MORKIN)
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.FOLLOW, self.MORKIN)
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(14))
        army.set_location(29, 12)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(14))
        army.set_location(29, 12)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(14))
        army.set_location(29, 12)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(14))
        army.set_location(29, 12)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(14))
        army.set_location(29, 12)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(14))
        army.set_location(29, 12)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(14))
        army.set_location(29, 12)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(14))
        army.set_location(29, 12)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(14))
        army.set_location(29, 12)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(14))
        army.set_location(29, 12)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(14))
        army.set_location(29, 12)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(14))
        army.set_location(29, 12)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(14))
        army.set_location(29, 12)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(14))
        army.set_location(29, 12)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.RIDERS, Orders.ROUTE, self.get_map().get_route_node(14))
        army.set_location(29, 12)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.RIDERS, Orders.ROUTE, self.get_map().get_route_node(14))
        army.set_location(29, 12)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.RIDERS, Orders.ROUTE, self.get_map().get_route_node(14))
        army.set_location(29, 12)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.RIDERS, Orders.ROUTE, self.get_map().get_route_node(14))
        army.set_location(29, 12)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.RIDERS, Orders.ROUTE, self.get_map().get_route_node(14))
        army.set_location(29, 12)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.RIDERS, Orders.ROUTE, self.get_map().get_route_node(14))
        army.set_location(29, 12)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.RIDERS, Orders.ROUTE, self.get_map().get_route_node(14))
        army.set_location(29, 12)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.RIDERS, Orders.ROUTE, self.get_map().get_route_node(14))
        army.set_location(29, 12)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(32))
        army.set_location(18, 21)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(32))
        army.set_location(18, 21)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(32))
        army.set_location(18, 21)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(32))
        army.set_location(18, 21)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(32))
        army.set_location(18, 21)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(32))
        army.set_location(18, 21)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(32))
        army.set_location(18, 21)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(32))
        army.set_location(18, 21)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(32))
        army.set_location(18, 21)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(32))
        army.set_location(18, 21)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(32))
        army.set_location(18, 21)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(32))
        army.set_location(18, 21)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(32))
        army.set_location(18, 21)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(32))
        army.set_location(18, 21)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(32))
        army.set_location(18, 21)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(32))
        army.set_location(18, 21)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.RIDERS, Orders.ROUTE, self.get_map().get_route_node(32))
        army.set_location(18, 21)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.RIDERS, Orders.ROUTE, self.get_map().get_route_node(32))
        army.set_location(18, 21)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.RIDERS, Orders.ROUTE, self.get_map().get_route_node(32))
        army.set_location(18, 21)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.RIDERS, Orders.ROUTE, self.get_map().get_route_node(32))
        army.set_location(18, 21)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(44))
        army.set_location(24, 29)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(44))
        army.set_location(24, 29)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(44))
        army.set_location(24, 29)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.ROUTE, self.get_map().get_route_node(44))
        army.set_location(24, 29)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.WANDER, None)
        army.set_location(7, 21)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.WANDER, None)
        army.set_location(27, 16)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.WANDER, None)
        army.set_location(40, 8)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.WANDER, None)
        army.set_location(39, 23)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.WANDER, None)
        army.set_location(21, 32)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.WANDER, None)
        army.set_location(23, 32)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.WARRIORS, Orders.WANDER, None)
        army.set_location(17, 28)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.WARRIORS, Orders.WANDER, None)
        army.set_location(18, 3)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.WARRIORS, Orders.WANDER, None)
        army.set_location(30, 29)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.WARRIORS, Orders.WANDER, None)
        army.set_location(16, 13)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.WARRIORS, Orders.WANDER, None)
        army.set_location(31, 22)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.WARRIORS, Orders.WANDER, None)
        army.set_location(6, 37)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.GOTO, self.get_map().get_route_node(6))
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.GOTO, self.get_map().get_route_node(6))
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.GOTO, self.get_map().get_route_node(6))
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.GOTO, self.get_map().get_route_node(6))
        army.set_location(29, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.GOTO, self.get_map().get_route_node(6))
        army.set_location(29, 12)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.GOTO, self.get_map().get_route_node(6))
        army.set_location(22, 5)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.GOTO, self.get_map().get_route_node(6))
        army.set_location(37, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.GOTO, self.get_map().get_route_node(6))
        army.set_location(23, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.GOTO, self.get_map().get_route_node(6))
        army.set_location(28, 4)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.GOTO, self.get_map().get_route_node(14))
        army.set_location(25, 11)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.GOTO, self.get_map().get_route_node(7))
        army.set_location(36, 12)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.GOTO, self.get_map().get_route_node(7))
        army.set_location(40, 8)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.GOTO, self.get_map().get_route_node(7))
        army.set_location(39, 9)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.GOTO, self.get_map().get_route_node(6))
        army.set_location(32, 6)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1200, Type.WARRIORS, Orders.GOTO, self.get_map().get_route_node(3))
        army.set_location(21, 11)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.GOTO, self.get_map().get_route_node(6))
        army.set_location(29, 9)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.GOTO, self.get_map().get_route_node(6))
        army.set_location(33, 7)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.GOTO, self.get_map().get_route_node(6))
        army.set_location(30, 6)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.GOTO, self.get_map().get_route_node(6))
        army.set_location(27, 6)
        self.doomguard.append(army)
        
        army = Doomguard(self, 0, 1000, Type.RIDERS, Orders.GOTO, self.get_map().get_route_node(6))
        army.set_location(26, 7)
        self.doomguard.append(army)


    def random(self, n: int) -> int:
        return self.random_generator.randint(0,n)
