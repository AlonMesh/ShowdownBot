import random
from BattleBots.battle_bot import BattleBot
from constant_variable import ACTION


class RandomBot(BattleBot):
    """
    A test class for BattleBot that makes random battle actions.

    This class extends the functionality of the BattleBot class to make random battle actions, such as selecting
    random known_moves or switching Pokemon.
    """

    def __init__(self, battle_id: str, sender):
        super().__init__(battle_id, sender)

    @staticmethod
    async def pick_random_action():
        """
        Generate a random battle action.

        This function randomly selects between move and switch and returns the chosen action.
        """
        random_number = random.randint(1, 2)
        if random_number == 1:
            return ACTION.MOVE
        else:
            return ACTION.SWITCH

    async def make_action(self, sender, forced_action=ACTION.NONE):
        """
        Perform a battle action in response to a game event.

        This method makes battle actions based on a forced action or a random choice between move and switch.
        """
        if forced_action is ACTION.NONE:
            forced_action = await self.pick_random_action()

        if forced_action == ACTION.MOVE:
            # move
            while True:
                random_number = random.randint(0, 3)
                if self.move_validity(random_number):
                    # Exit the loop when a valid pick is found
                    break
            # await sender.send_message(self.battle_id, "I picked a move")
            await super().make_move(random_number)
        else:
            # switch
            while True:
                random_number = random.randint(0, 5)
                if self.switch_validity(random_number):
                    # Exit the loop when a valid pick is found
                    break
            # await sender.send_message(self.battle_id, "I picked a switch")
            await super().make_switch(random_number)
