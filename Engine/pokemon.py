from abc import ABC
import json
import requests
from Engine.move import create_move

MAX_MOVES = 4


class Pokemon(ABC):
    def __init__(self, name, level, condition):
        self.name = make_name_in_format(name)
        self.url = "https://pokeapi.co/api/v2/" + "pokemon/" + name.lower().replace(" ", "-")
        self.types = self.set_types()
        self.level = level
        if '/' in condition:
            self.max_health = condition.split('/')[1]
            self.curr_health = condition.split('/')[0]
        else:  # Pokemon has fainted
            self.max_health = 0
            self.curr_health = 0

    def get_field_from_api(self, singular: str, plural: str):
        print("URL: ", self.url)
        # print("JSN: ", requests.get(self.url).json())
        try:
            response = requests.get(self.url).json()
            field_info_json = response.get(plural, [])
            wished_list = [field_info[singular]["name"] for field_info in field_info_json]
            return wished_list
        except ValueError:
            print("There is a problem with the name", self.name)

    def set_types(self) -> list[str]:
        ans = self.get_field_from_api("type", "types")
        if ans is None:
            raise ValueError("Pokemon must have type")
        return ans

    def __str__(self) -> str:
        return f"Name: {self.name}\nLevel: {self.level}\nCondition: {self.curr_health}/{self.max_health}"

    def is_alive(self) -> bool:
        return 0 < int(self.curr_health)


class BotPokemon(Pokemon):
    def __init__(self, name, level, condition, active, stats, moves, ability, item, terastall_type):
        super().__init__(name, level, condition)
        self.active = active
        self.stats = stats
        self.moves = moves
        self.ability = ability
        self.item = item
        self.terastall_type = terastall_type

    def __str__(self):
        return f"{super().__str__()}\nActive: {self.active}\nStats: {self.stats}\nMoves: {', '.join(self.moves)}\nAbility: {self.ability}\nItem: {self.item}\nTerastall Type: {self.terastall_type}"

    def get_moves(self):
        return self.moves

    def get_stats(self):
        return self.stats

    def get_ability(self):
        return self.ability

    def get_item(self):
        return self.item

    def get_terastall_type(self):
        return self.terastall_type


def create_pokemon_objects_from_json(json_data) -> list[BotPokemon]:
    """This function gets a json and create pokemons"""
    # TODO: Right now, this function create 6 pokemons every turn. It might be more eff to create only the changed.
    pokemon_objects = []

    # Load JSON data
    data = json.loads(json_data.replace("|request|", ""))

    if 'side' in data and 'pokemon' in data['side']:
        for pokemon_info in data['side']['pokemon']:
            name = pokemon_info.get('details', '').split(',')[0]
            level = pokemon_info.get('details', '').split(',')[1][-2:]
            condition = pokemon_info.get('condition', '')
            active = pokemon_info.get('active', False)
            stats = pokemon_info.get('stats', {})  # Extracted stats data
            moves = pokemon_info.get('known_moves', [])  # Extracted known_moves data
            ability = pokemon_info.get('ability', '')  # Extracted ability data
            item = pokemon_info.get('item', '')  # Extracted item data
            terastall_type = pokemon_info.get('teraType', '')  # Extracted terastall_type data

            # Create a BotPokemon object and append it to the list
            bot_pokemon = BotPokemon(name, level, condition, active, stats, moves, ability, item, terastall_type)
            pokemon_objects.append(bot_pokemon)

    return pokemon_objects


def make_name_in_format(given_name: str) -> str:
    """This function get a Pokemon name and adapt to the API name requirements. Mostly edge cases"""
    if given_name[-1] == 'F':
        given_name.replace('-F', '-female')
    if given_name[-1] == 'M':
        given_name.replace('-M', '-male')

    if given_name in ['Toxtricity', 'toxtricity']:
        given_name = "toxtricity-amped"

    if given_name == 'Giratina':
        given_name = "giratina-altered"

    if given_name == 'eiscue':
        given_name = "eiscue-ice"

    # if given_name == 'urshifu':
    #     given_name = "eiscue-ice"

    return given_name.lower()


class EnemyPokemon(Pokemon):
    def __init__(self, name, level, condition):
        super().__init__(name, level, condition)
        self.active = False  # By default
        self.stats = self.set_stats()
        self.abilities = self.set_potential_abilities()
        self.potential_moves = self.set_potential_moves()
        self.known_moves = []

    def set_stats(self):
        response = requests.get(self.url).json()["stats"]

        # Initialize an empty dictionary
        stat_dict = {}

        # Iterate through the list of dictionaries
        for stat_info in response:
            # Extract the "name" and "base_stat" values
            stat_name = stat_info["stat"]["name"]
            base_stat = stat_info["base_stat"]

            # Add the stat to the dictionary
            stat_dict[long_to_short_key_mapping[stat_name]] = base_stat

        # return the resulting dictionary
        return stat_dict

    def set_potential_moves(self):
        return super().get_field_from_api("move", "known_moves")

    def set_potential_abilities(self):
        return super().get_field_from_api("ability", "abilities")

    def update_enemy_moves(self, move_name: str):
        """Get the name of an attack used. If the enemy didn't use it yet, att it to the least"""
        for move in self.known_moves:
            if move.name == move_name:
                move.pp = str(int(move.pp) - 1)
                return

        self.known_moves.append(create_move(move_name))


# Define the mapping of long keys to short keys
long_to_short_key_mapping = {
    'hp': 'hp',
    'attack': 'atk',
    'defense': 'def',
    'special-attack': 'spa',
    'special-defense': 'spd',
    'speed': 'spe'
}
