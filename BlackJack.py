"""Black Jack 21 by Stanley Cunningham stan61285@msn.com
Play and bet against the computer in a game of Single Deck Black Jack in the terminal.
"""
import random
import time
import os


class Deck:
    deck = []
    suit_dict = {'h': '\u2665', 'd': '\u2666', 'c': '\u2663',  's': '\u2660'}
    face_down = False  # All references to face_down are cosmetic only and does not affect any game logic.
    turn = 0  # All references affect game logic

    def __init__(self, name):
        self.name = name
        self.hand = []
        self.render = []
        self.sum = []
        self.ace = 0

    def generate_deck(self):
        self.reset_deck()
        for suit in 'scdh':
            for value in range(1, 14):
                self.deck.append(str(value) + '-' + suit)

    def reset_deck(self):
        self.ace, Deck.turn = 0, 0
        self.hand, self.hand, self.render, self.sum, Deck.deck = [], [], [], [], []
        Deck.face_down = False

    def draw_card(self):
        card_index = self.deck.index(random.choice(self.deck))
        card = self.deck.pop(card_index)
        self.hand.append(card)
        self.update_render(card)
        self.eval_sum()

    def update_render(self, card):
        count, suit = card.split('-')
        s = self.suit_dict[suit]

        if count == '1':
            self.ace += 1
        card = [[f' _____  '],
                [f'|{s}    | '],
                [f'|     | '],
                [f'| {str(count).rjust(2)}  | '],
                [f'|     | '],
                [f'|____{s}| ']]

        if not self.render:
            self.render = card
        else:
            for idx, held in enumerate(self.render):
                held.extend(card[idx])

    def render_hand(self):
        if not self.render:  # Spacing for dealer when dealing first hand
            print('\n' * 5)
        else:
            if self.name == 'Computer' and Deck.face_down:
                count, suit = self.hand[1].split('-')
                r = '#' if int(count) <= 9 else " #"
                for index, x in enumerate(self.render):
                    print(x[0].replace('11', ' J').replace('12', ' Q').replace('13', ' K').replace('1 ', 'A ')
                          + "".join([y for y in x[1]]).replace(self.suit_dict[suit], "#").replace(count, r))
            else:
                for index, x in enumerate(self.render):
                    print(''.join(x).replace('11', ' J').replace('12', ' Q').replace('13', ' K').replace('1 ', 'A '))

    def eval_sum(self):
        user_sum = sum([min(int(x.split('-')[0]), 10) for x in self.hand])
        user_ace = self.ace
        self.sum = [user_sum]

        while user_ace > 0:
            if user_sum + 10 <= 21:
                user_ace -= 1
                self.sum.append(user_sum + 10)
            else:
                break

    def eval_first(self):
        first_c = int(self.hand[0].split("-")[0])
        if first_c == 1 or first_c >= 10:
            return True

    def eval_natural(self):
        if max(self.sum) == 21:
            return True

    def dealer_play(self):
        if 17 > max(self.sum):
            return True


class Bank(Deck):
    def __init__(self, name, balance):
        super().__init__(name)
        self.balance = balance
        self.wins, self.loses = 0, 0

    def withdraw(self, amount):
        if amount > self.balance:
            print(f'Insufficient Funds! Try a different amount, only ${self.balance} remains in your account.')
            return False
        else:
            print(f'\n${amount} has been deducted from your balance, your new balance is ${self.balance}.')
            self.balance -= amount
            return True

    def deposit(self, amount):
        self.balance += amount
        print(f'\n${amount} has been added to your balance, your new balance is ${self.balance}.')
        return True


def main():
    new_game(player_turn=True, player_stay=False)


def new_game(player_turn, player_stay, win=None):
    """Main logic for game"""
    player1.generate_deck()
    cpu.generate_deck()

    bet = betting()
    while bet:
        Deck.turn += 1
        if Deck.turn == 4:
            Deck.face_down = True
        if Deck.turn > 4:
            natural = None
            if Deck.turn == 5:
                natural = naturals()
            win = win_condition(player_stay, natural)
            if win is None:
                if player_stay:
                    if cpu.dealer_play():
                        time.sleep(1.75)
                        deal_card(False)
                    else:
                        break
                else:
                    if max(player1.sum) < 21:
                        player_turn = hit_me()
                    else:
                        player_stay = True
                        continue  # Player is at 21, do not hit_me()
                    if player_turn is False:
                        Deck.face_down = False
                        player_stay = True
                        if cpu.dealer_play():
                            deal_card(player_turn)
                    else:
                        deal_card(player_turn)
            else:
                break
        else:
            time.sleep(1)
            player_turn = deal_card(player_turn)
            if Deck.turn < 4:
                print('\nDealing Cards...')

    Deck.face_down = False
    display_board()
    resolve_bet(win, bet)


def hit_me():
    choice_list = ['Enter [1] to Hit', 'Enter [2] to Stay']
    choice = multi_list_prompt('Would you like to Hit or Stay?', choice_list)
    if choice == choice_list[0]:
        return True
    else:
        return False


def win_condition(player_stay, natural=None):
    if any(x > 21 for x in player1.sum):
        return False
    elif any(x > 21 for x in cpu.sum):
        return True
    elif max(cpu.sum) == max(player1.sum) and natural == 'push':
        return 'push'
    elif natural == player1.name and any(x == 21 for x in player1.sum):
        return 'blackjack'
    elif natural == cpu.name and any(x == 21 for x in cpu.sum):
        return False
    else:
        if player_stay and not cpu.dealer_play():
            if max(cpu.sum) == max(player1.sum):
                return 'push'
            elif max(cpu.sum) > max(player1.sum):
                return False
            else:
                return True


def deal_card(player_turn):
    if player_turn:
        player1.draw_card()
        display_board()  # Never have card face down
        return False  # Player turn
    else:
        cpu.draw_card()
        display_board()
        return True


def resolve_bet(win, bet):
    if win == 'blackjack':
        print('\nYou win!')
        player1.deposit(bet * 1.5)
    elif win is False:
        print('\nYou Lose!')
        player1.withdraw(bet)
    elif win is True:
        print('\nYou win!')
        player1.deposit(bet)
    else:
        print('\nPush...')
    input('\nPress [Enter] if you wish to play another hand...')
    main()


def betting():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f'Current balance:  ${player1.balance}')

    if player1.balance < 2:
        print('\nYou are all out of money, better luck next time!')
        input('\nPress [Enter] to close the script...')
        raise SystemExit

    print(f'\nHow much would you like to bet this game?')
    print(f'You may bet between $2 and $500 but not exceed your current balance of ${player1.balance}')

    while True:
        try:
            bet = int(input(f'>> '))
            if 2 > bet or bet > player1.balance or bet > 500:
                print(f'You must bet at least $2 and not more than your current balance of ${player1.balance}.')
            else:
                print(f'\nYou are betting ${bet}. Good luck!')
                return bet
        except ValueError:
            print(f'You must choose a whole number between 2 and .')


def display_board():
    # print('\n' * 100)
    os.system('cls' if os.name == 'nt' else 'clear')

    print(f'Dealer - {cpu.name}')
    cpu.render_hand()
    cpu_show = f'{str(min(int(cpu.hand[0].split("-")[0]), 10))}' if Deck.face_down is True else \
        str(cpu.sum).replace("[", "").replace("]", "")
    if cpu_show == '1':
        cpu_show = cpu_show.replace("1", "1 or 11")
    print(f'The dealer is currently at {"".join(cpu_show)}')

    print(f'\n\nPlayer - {player1.name}')
    player1.render_hand()
    print(f'{player1.name} is currently at {" or ".join([str(x) for x in player1.sum])}')


def naturals():
    if cpu.eval_first():
        Deck.face_down = False
        display_board()
        print("\nThe dealer's face-up card is a ten-card or an ace.")

    if cpu.eval_natural() and player1.eval_natural():
        display_board()
        return 'push'
    elif cpu.eval_natural():
        display_board()
        print('\nThe dealer has the only natural and immediately collects all bets!')
        return cpu.name
    elif player1.eval_natural():
        display_board()
        print(f'\nYou have a natural 21 and immediately collect your bet with a bonus!')
        return player1.name


def multi_list_prompt(prompt, prompt_lst):
    print(f'\n{prompt}')
    valid = [x for x in range(1, len(prompt_lst) + 1)]
    for index, x in enumerate(prompt_lst, 1):
        print(f' {index}: {x}')

    while True:
        try:
            selection = int(input('>> '))
            if selection in valid:
                break
            else:
                print('You may only select an option available above.')
        except ValueError:
            print('You may only enter a number...\n')

    return prompt_lst[selection - 1]


def init_prompt():
    os.system('cls' if os.name == 'nt' else 'clear')
    print('Welcome to Black Jack 21!')
    print('\nOBJECT OF THE GAME')
    print('Attempt to beat the dealer by getting a count as close to 21 as possible, without going over 21.')

    name = input('\nWhat is your name Player 1?\n>> ').title()
    if name == "":
        name = "Player"

    print('\nBETTING')
    print('Before the deal begins, place a bet. Minimum and maximum limits are established on the betting, '
          'and the general limits are from $2 to $500.')

    print(f'\nHowdy {name}, how much money would you like start with in your betting pool? '
          f'Select a numeric option below:')
    while True:
        balance = [100, 500, 1000]
        for index, x in enumerate(balance, 1):
            print(f' {index}: ${x}')
        try:
            selection = int(input('>> '))
            if selection in [1, 2, 3]:
                break
            else:
                print('You must select a numeric option above.')
        except ValueError:
            print('You must select a numeric option above.')

    print(f'\nYou have ${balance[selection - 1]} to bet with, use it wisely and good luck!')

    print('\nTHE DEAL')
    print('The dealer gives one card face up to the player, and then one card face up to themselves. '
          'Another card is then dealt face up to the player, but the dealer takes the second card face down. '
          'Thus, the dealer receives one card face up and one card face down.')
    input('\nPress [Enter] to continue...')
    return name, balance[selection - 1]


player1 = Bank(*init_prompt())
# player1 = Bank('Stanley', 100)
cpu = Deck('Computer')

if __name__ == '__main__':
    main()
