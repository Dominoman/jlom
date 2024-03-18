from functools import total_ordering


class Race:
    MORKIN:'Race'
    WISE: 'Race'
    TARG: 'Race'
    FEY: 'Race'
    SKULKRIN: 'Race'
    DRAGON: 'Race'
    FREE: 'Race'
    FOUL: 'Race'

    def __init__(self, description: str) -> None:
        self.description = description

    def __str__(self):
        return self.description

    def get_index(self) -> int:
        return Race.values.index(self)

    @staticmethod
    def get_race(index: int) -> 'Race':
        return Race.values[index]


Race.FREE = Race("Free")
Race.FEY = Race("Fey")
Race.WISE = Race("Wise")
Race.TARG = Race("Targ")
Race.SKULKRIN = Race("Skulkrin")
Race.DRAGON = Race("Dragon")
Race.FOUL = Race("Foul")
Race.MORKIN = Race("Morkin")
Race.values = (Race.FOUL, Race.FREE, Race.FEY, Race.TARG, Race.WISE, Race.MORKIN, Race.SKULKRIN, Race.DRAGON)


@total_ordering
class Condition:
    UTTERLY_TIRED: 'Condition'
    values = []

    def __init__(self, description: str) -> None:
        self.description = description
        self.ordinal = len(Condition.values)
        Condition.values.append(self)

    def __str__(self):
        return self.description

    def __lt__(self, __value):
        return self.ordinal < __value.ordinal

    def __eq__(self, __value):
        return self.values == __value.ordinal

    @staticmethod
    def get_condition(index: int) -> 'Condition':
        return Condition.values[index]


Condition.UTTERLY_TIRED = Condition("utterly tired and cannot continue")
Condition.VERY_TIRED = Condition("very tired")
Condition.TIRED = Condition("tired")
Condition.QUITE_TIRED = Condition("quite tired")
Condition.SLIGHTLY_TIRED = Condition("slightly tired")

Condition.INVIGORATED = Condition("invigorated")
Condition.VERY_INVIGORATED = Condition("very invigorated")
Condition.UTTERLY_INVIGORATED = Condition("utterly invigorated")


class Type:
    WARRIORS: 'Type'
    RIDERS: 'Type'

    def __init__(self, description: str) -> None:
        self.description = description

    def __str__(self):
        return self.description


Type.WARRIORS = Type("warriors")
Type.RIDERS = Type("riders")


class Orders:
    ROUTE: 'Orders'
    WANDER: 'Orders'
    GOTO: 'Orders'
    FOLLOW: 'Orders'

    def __init__(self, description: str) -> None:
        self.description = description

    def __str__(self):
        return self.description

    def get_index(self) -> int:
        return Orders.values.index(self)

    @staticmethod
    def get_orders(index: int) -> 'Orders':
        return Orders.values[index]


Orders.FOLLOW = Orders("Follow")
Orders.GOTO = Orders("Go to")
Orders.ROUTE = Orders("Route")
Orders.WANDER = Orders("Wander")
Orders.values = (Orders.GOTO, Orders.WANDER, Orders.FOLLOW, Orders.ROUTE)


@total_ordering
class Courage:
    UTTERLY_AFRAID: 'Courage'
    values = []

    def __init__(self, description: str) -> None:
        self.description = description
        self.ordinal = len(Courage.values)
        Courage.values.append(self)

    def __str__(self):
        return self.description

    @staticmethod
    def get_courage(index: int) -> 'Courage':
        if index < 0:
            index = 0
        elif index > len(Courage.values) - 1:
            index = len(Courage.values) - 1
        return Courage.values[index]

    def get_index(self) -> int:
        return self.ordinal

    def __lt__(self, __value):
        return self.ordinal < __value.ordinal

    def __eq__(self, __value):
        return self.ordinal == __value.ordinal


Courage.UTTERLY_AFRAID = Courage("utterly afraid")
Courage.VERY_AFRAID = Courage("very afraid")
Courage.AFRAID = Courage("afraid")
Courage.QUITE_AFRAID = Courage("quite afraid")
Courage.SLIGHTLY_AFRAID = Courage("slightly afraid")

Courage.BOLD = Courage("bold")
Courage.VERY_BOLD = Courage("very bold")
Courage.UTTERLY_BOLD = Courage("utterly bold")


class Feature:
    KEEP: 'Feature'
    PLAINS: 'Feature'
    ARMY: 'Feature'
    HENGE: 'Feature'
    LAKE: 'Feature'
    CITADEL: 'Feature'
    DOWNS: 'Feature'
    MOUNTAIN: 'Feature'
    FOREST: 'Feature'
    FROZEN_WASTE: 'Feature'

    def __init__(self, description: str) -> None:
        self.description = description

    @staticmethod
    def get_feature(index: int) -> 'Feature':
        return Feature.values[index]

    def get_index(self) -> int:
        return Feature.values.index(self)

    def __str__(self):
        return self.description


Feature.MOUNTAIN = Feature("mountains")
Feature.CITADEL = Feature("citadel")
Feature.FOREST = Feature("forest")
Feature.HENGE = Feature("henge")
Feature.TOWER = Feature("tower")
Feature.VILLAGE = Feature("village")
Feature.DOWNS = Feature("downs")
Feature.KEEP = Feature("keep")
Feature.SNOWHALL = Feature("snowhall")
Feature.LAKE = Feature("lake")
Feature.FROZEN_WASTE = Feature("frozen wastes")
Feature.RUIN = Feature("ruin")
Feature.LITH = Feature("lith")
Feature.CAVERN = Feature("cavern")
Feature.ARMY = Feature("plains")
Feature.PLAINS = Feature("plains")
Feature.values = (
    Feature.MOUNTAIN, Feature.CITADEL, Feature.FOREST, Feature.HENGE, Feature.TOWER, Feature.VILLAGE, Feature.DOWNS,
    Feature.KEEP, Feature.SNOWHALL, Feature.LAKE, Feature.FROZEN_WASTE, Feature.RUIN, Feature.LITH, Feature.CAVERN,
    Feature.ARMY, Feature.PLAINS)


class Object:
    SHADOWS_OF_DEATH: 'Object'
    WATERS_OF_LIFE: 'Object'
    CUP_OF_DREAMS: 'Object'
    HAND_OF_DARK: 'Object'
    SHELTER: 'Object'
    WILD_HORSES: 'Object'
    MOON_RING: 'Object'
    ICE_CROWN: 'Object'
    WOLFSLAYER: 'Object'
    DRAGONSLAYER: 'Object'
    WOLVES: 'Object'
    SKULKRIN: 'Object'
    ICE_TROLLS: 'Object'
    DRAGONS: 'Object'
    NOTHING: 'Object'

    def __init__(self, description: str) -> None:
        self.description = description

    def is_beast(self) -> bool:
        return self in [Object.WOLVES, Object.DRAGONS, Object.SKULKRIN, Object.ICE_TROLLS]

    @staticmethod
    def get_object(index: int) -> 'Object':
        return Object.values[index]

    def get_index(self) -> int:
        return Object.values.index(self)

    def to_string(self, location) -> str:
        if self != Object.GUIDANCE:
            return self.description

        message = "guidance. A voice says: '"
        rnd = location.get_game().random(32)
        if rnd >= 4:
            i = 0
            for character in location.game.characters():
                if i > rnd:
                    break
            message += f"Looking for {character} you must seek {character.get_location()}'"
        else:
            who = self.get_object(rnd + 16)
            message += f"{who.to_string(location)} can destroy the Ice Crown'"
        return message


Object.NOTHING = Object("nothing")
Object.WOLVES = Object("wolves")
Object.DRAGONS = Object("dragons")
Object.ICE_TROLLS = Object("ice trolls")
Object.SKULKRIN = Object("Skulkrin")
Object.WILD_HORSES = Object("wild horses")
Object.SHELTER = Object("shelter and is refreshed")
Object.GUIDANCE = Object("guidance. A voice calls, ")
Object.SHADOWS_OF_DEATH = Object("the Shadows of Death which drain him of vigour")
Object.WATERS_OF_LIFE = Object("the Waters of Life which fill him with vigour")
Object.HAND_OF_DARK = Object("the Hand of Dark which brings death to the day")
Object.CUP_OF_DREAMS = Object("the Cup of Dreams which brings welcome")
Object.WOLFSLAYER = Object("the sword Wolfslayer")
Object.DRAGONSLAYER = Object("the sword Dragonslayer")
Object.ICE_CROWN = Object("the Ice Crown")
Object.MOON_RING = Object("the Moon Ring")
Object.FAWKRIN = Object("Fawkrin the Skulkrin")
Object.FARFLAME = Object("Farflame the Dragonlord")
Object.LAKE_MIRROW = Object("Lake Mirrow")
Object.LORGRIM = Object("Lorgrim the Wise")
Object.values = (
    Object.NOTHING, Object.WOLVES, Object.DRAGONS, Object.ICE_TROLLS, Object.SKULKRIN, Object.WILD_HORSES,
    Object.SHELTER,
    Object.GUIDANCE, Object.SHADOWS_OF_DEATH, Object.WATERS_OF_LIFE, Object.HAND_OF_DARK, Object.CUP_OF_DREAMS,
    Object.WOLFSLAYER, Object.DRAGONSLAYER, Object.ICE_CROWN, Object.MOON_RING, Object.FAWKRIN, Object.FARFLAME,
    Object.LAKE_MIRROW, Object.LORGRIM)


@total_ordering
class Fear:
    values = []

    def __init__(self, description: str) -> None:
        self.description = description
        self.ordinal = len(Fear.values)
        Fear.values.append(self)

    def __str__(self):
        return self.description

    @staticmethod
    def get_fear(index: int) -> 'Fear':
        return Fear.values[index]

    def __lt__(self, __value):
        return self.ordinal < __value.ordinal

    def __eq__(self, __value):
        return self.ordinal == __value.ordinal


Fear.UTTERLY_COLD = Fear("utterly cold")
Fear.VERY_COLD = Fear("very cold")
Fear.COLD = Fear("cold")
Fear.QUITE_COLD = Fear("quite cold")
Fear.SLIGHTLY_COLD = Fear("slightly cold")

Fear.MILD = Fear("mild")
Fear.VERY_MILD = Fear("very mild")
Fear.UTTERLY_MILD = Fear("utterly mild")


class Direction:
    NORTHWEST: 'Direction'
    WEST: 'Direction'
    SOUTHWEST: 'Direction'
    SOUTH: 'Direction'
    SOUTHEAST: 'Direction'
    EAST: 'Direction'
    NORTHEAST: 'Direction'
    NORTH: 'Direction'

    def __init__(self, description: str, x_adjustment: int, y_adjustment: int) -> None:
        self.description = description
        self.x_adjustment = x_adjustment
        self.y_adjustment = y_adjustment

    def __str__(self):
        return self.description

    def get_x_adjustment(self) -> int:
        return self.x_adjustment

    def get_y_adjustment(self) -> int:
        return self.y_adjustment

    def get_index(self) -> int:
        return Direction.values.index(self)

    @staticmethod
    def get_direction(index: int) -> 'Direction':
        return Direction.values[index]

    def turn_right(self) -> 'Direction':
        return Direction.values[(self.get_index() + 1) % len(Direction.values)]

    def turn_left(self) -> 'Direction':
        return Direction.values[(len(Direction.values) + self.get_index()) % len(Direction.values)]

    def is_diagonal(self) -> bool:
        return self.x_adjustment != 0 and self.y_adjustment != 0


Direction.NORTH = Direction("North", 0, -1)
Direction.NORTHEAST = Direction("Northeast", 1, -1)
Direction.EAST = Direction("East", 1, 0)
Direction.SOUTHEAST = Direction("Southeast", 1, 1)
Direction.SOUTH = Direction("South", 0, 1)
Direction.SOUTHWEST = Direction("Southwest", -1, 1)
Direction.WEST = Direction("West", -1, 0)
Direction.NORTHWEST = Direction("Northwest", -1, -1)
Direction.values = (
    Direction.NORTH, Direction.NORTHEAST, Direction.EAST, Direction.SOUTHEAST, Direction.SOUTH, Direction.SOUTHWEST,
    Direction.WEST, Direction.NORTHWEST)


class Area:
    NOTHING: 'Area'

    def __init__(self, description: str) -> None:
        self.description = description

    @staticmethod
    def get_area(index: int) -> 'Area':
        return Area.values[index]

    def get_index(self) -> int:
        return Area.values.index(self)

    def __str__(self):
        return self.description


Area.NOTHING = Area("Nothing")
Area.LOTHORIL = Area("Lothoril")
Area.GLOOM = Area("Gloom")
Area.MOON = Area("Moon")
Area.MIRROW = Area("Mirrow")
Area.GLORIM = Area("Glorim")
Area.KORKITH = Area("Korkith")
Area.LOST = Area("the Lost")
Area.DEAD = Area("Dead")
Area.WEIRD = Area("Weird")
Area.UGRAK = Area("Ugrak")
Area.DEATH = Area("Death")
Area.DOOM = Area("Doom")
Area.DESPAIR = Area("Despair")
Area.VORGATH = Area("Vorgath")
Area.USHGARAK = Area("Ushgarak")
Area.UGRORN = Area("Ugrorn")
Area.KOR = Area("Kor")
Area.TOOMOG = Area("Toomog")
Area.OGRIM = Area("Ogrim")
Area.DODRAK = Area("Dodrak")
Area.GORGRATH = Area("Gorgrath")
Area.VALETHOR = Area("Valethor")
Area.COROTH = Area("Coroth")
Area.ASHIMAR = Area("Ashimar")
Area.ITHRIL = Area("Ithril")
Area.SHADOWS = Area("Shadows")
Area.BLOOD = Area("Blood")
Area.THRALL = Area("Thrall")
Area.TORKREN = Area("Torkren")
Area.GARD = Area("Gard")
Area.MITHARG = Area("Mitharg")
Area.MOON2 = Area("the Moon")
Area.ISERATH = Area("Iserath")
Area.SHIMERIL = Area("Shimeril")
Area.ODRARK = Area("Odrark")
Area.ISHMALAY = Area("Ishmalay")
Area.BRITH = Area("Brith")
Area.SILENCE = Area("Silence")
Area.ELENIL = Area("Elenil")
Area.RORATH = Area("Rorath")
Area.MORNING = Area("Morning")
Area.THIMRATH = Area("Thimrath")
Area.CORELAY = Area("Corelay")
Area.RATHORN = Area("Rathorn")
Area.LORGRIM = Area("Lorgrim")
Area.LOR = Area("Lor")
Area.FADRATH = Area("Fadrath")
Area.DROON = Area("Droon")
Area.GRARG = Area("Grarg")
Area.DREAMS = Area("Dreams")
Area.ITHRORN = Area("Ithrorn")
Area.WHISPERS = Area("Whispers")
Area.XAJORKITH = Area("Xajorkith")
Area.HERATH = Area("Herath")
Area.KUMAR = Area("Kumar")
Area.MARAKITH = Area("Marakith")
Area.TARG = Area("the Targ")
Area.UTARG = Area("Utarg")
Area.ATHORIL = Area("Athoril")
Area.DREGRIM = Area("Dregrim")
Area.DAWN = Area("Dawn")
Area.TRORN = Area("Trorn")
Area.COOM = Area("Coom")

Area.values = (
    Area.NOTHING, Area.LOTHORIL, Area.GLOOM, Area.MOON, Area.MIRROW, Area.GLORIM, Area.KORKITH, Area.LOST, Area.DEAD,
    Area.WEIRD, Area.UGRAK, Area.DEATH, Area.DOOM, Area.DESPAIR, Area.VORGATH, Area.USHGARAK, Area.UGRORN, Area.KOR,
    Area.TOOMOG, Area.OGRIM, Area.DODRAK, Area.GORGRATH, Area.VALETHOR, Area.COROTH, Area.ASHIMAR, Area.ITHRIL,
    Area.SHADOWS, Area.BLOOD, Area.THRALL, Area.TORKREN, Area.GARD, Area.MITHARG, Area.MOON2, Area.ISERATH,
    Area.SHIMERIL,
    Area.ODRARK, Area.ISHMALAY, Area.BRITH, Area.SILENCE, Area.ELENIL, Area.RORATH, Area.MORNING, Area.THIMRATH,
    Area.CORELAY, Area.RATHORN, Area.LORGRIM, Area.LOR, Area.FADRATH, Area.DROON, Area.GRARG, Area.DREAMS, Area.ITHRORN,
    Area.WHISPERS, Area.XAJORKITH, Area.HERATH, Area.KUMAR, Area.MARAKITH, Area.TARG, Area.UTARG, Area.ATHORIL,
    Area.DREGRIM, Area.DAWN, Area.TRORN, Area.COOM)


class Status:
    ICE_CROWN: 'Status'
    USHGARAK: 'Status'
    MORKIN_XAJORKITH: 'Status'
    LUXOR_MORKIN_DEAD: 'Status'

    def __init__(self, winner: Race, description: str) -> None:
        self.winner = winner
        self.description = description

    def get_winner(self) -> Race:
        return self.winner

    def __str__(self):
        return self.description

    def get_index(self) -> int:
        return Status.values.index(self)

    def get_status(self, index: int) -> 'Status':
        return Status.values[index]


Status.LUXOR_MORKIN_DEAD = Status(Race.FOUL, "Luxor is dead and Morkin is dead.")
Status.MORKIN_XAJORKITH = Status(Race.FOUL, "Xajorkith has fallend and Morkin is dead.")
Status.USHGARAK = Status(Race.FREE, "Ushgarak has fallen.")
Status.ICE_CROWN = Status(Race.FREE, "The Ice Crown has been destroyed.")

Status.values = (Status.LUXOR_MORKIN_DEAD, Status.MORKIN_XAJORKITH, Status.USHGARAK, Status.ICE_CROWN)
