import random
import chomp_learning
import chomp_report_generator
import numpy as np
from typing import Tuple, Optional
import argparse
from rich import print as rprint

#region: konstansok
NUMBER_OF_ROWS = 3
NUMBER_OF_COLUMNS = 4
MEMO_SET_NAME = "alfa"
#endregion

def print_board(current_board: np.ndarray) -> None:
    """Megrajzolja az aktuális táblát"""
    for r in range(NUMBER_OF_ROWS):
        for c in range(NUMBER_OF_COLUMNS):
            if r==0 and c == 0:
                print("🟦", end="")
            elif c==NUMBER_OF_COLUMNS-1:
                if current_board[r, c] == 1:
                    print("🟩")
                else:
                    print("🟥")
            else:
                if current_board[r, c] == 1:
                    print("🟩", end="")
                else:
                    print("🟥", end="")

def validate_player_step(board: np.ndarray, row_n: int, col_n: int) -> Tuple[bool, np.ndarray]:
    """Validálja a játékos lépését, visszatérített változók/értékek: érvényes volt-e a lépés -> `True`/`False` | aktuális állás a táblán -> `np.array`"""
    if (row_n > 0 and row_n <= board.shape[0]) and (col_n > 0 and col_n <= board.shape[1]) and not (row_n == 1 and col_n == 1):
        if board[row_n-1,col_n-1]==0:
            return False, board
        else:
            #region: recording and appending event
            rows, cols = np.where(board == 1)
            options = tuple(zip(rows, cols))[1:]
            event = chomp_learning.Event(
                computer = False,
                options = options,
                choice = (row_n-1, col_n-1)
            )
            chomp_learning.append_event(event)
            #endregion

            board[row_n-1:,col_n-1: ] = 0
            return True, board
    else:
        return False, board
   
def computer_step(board: np.ndarray, computer: Optional[bool] = True) -> Tuple[tuple, np.ndarray]:
    """A számítógépet léptető funkció, visszatérített értékek: a választott mező indexei | az aktuális állás a táblán"""
    rows, cols = np.where(board == 1)
    choices = tuple(zip(rows, cols))[1:]
    if choices in chomp_learning.memories.keys():
        choice = random.choices(choices, weights=chomp_learning.memories[choices].weights, k=1)[0]
    else:
        choice = random.choice(choices)

    #region: recording and appending event
    event = chomp_learning.Event(
        computer = computer,
        options = choices,
        choice = choice
    )
    chomp_learning.append_event(event)
    #endregion

    board[choice[0]:, choice[1]:] = 0
    return choice, board


def computer_step_as_player(board: np.ndarray) -> Tuple[tuple, np.ndarray]:
    rows, cols = np.where(board == 1)
    choices = list(zip(rows, cols))[1:]
    choice = random.choice(choices)

    #region: recording and appending event
    event = chomp_learning.Event(
        computer = False,
        options = tuple(choices),
        choice = choice
    )
    chomp_learning.append_event(event)
    #endregion

    board[choice[0]:, choice[1]:] = 0
    return choice, board

def train(number_of_games: int, computer_starts: Optional[bool] = False) -> None:
    """A bemeneti paraméter által meghatározott számú játékot játszik a számítógép ellen random lépésekkel"""
    for _ in range(1,number_of_games+1):
        game(autommated=True, computer_starts=computer_starts)

def game(computer_starts: Optional[bool] = False, autommated: Optional[bool] = False) -> None:
    chomp_learning.init_memory(MEMO_SET_NAME)
    board = np.ones((NUMBER_OF_ROWS, NUMBER_OF_COLUMNS))
    
    print("__________________________________________")
    print(f"Ki indulási tábla:")
    print_board(board)
    print("__________________________________________")

    players = ["Játékos", "Számítógép"]
    computer_plays: bool = computer_starts

    while np.sum(board==1) != 1:
        if not computer_plays:
            if not autommated:
                #region: emberi játékos esetén
                try:
                    row_n = int(input("\nAdja meg a kiválasztott kocka SORÁNAK számát: "))
                    col_n = int(input("Adja meg a kiválasztott kocka OSZLOP számát: "))
                    was_valid, board = validate_player_step(board, row_n, col_n)
                    if not was_valid:
                        print("Invalid lépés! Próbálja újra!")
                        continue
                except:
                    print("Invalid lépés! Próbálja újra!")
                    continue
                #endregion
            else:
                #region: robot játékos esetén
                choice, board = computer_step_as_player(board)
                #choice, board = computer_step(board, computer=False)
                #endregion
            print("__________________________________________")
            print(f"A {players[int(computer_plays)]} lépése:")
            print_board(board)
            print("------------------------------------------")
        else:
            choice, board = computer_step(board)
            print("__________________________________________")
            print(f"A {players[int(computer_plays)]} a {choice[0]+1}, {choice[1]+1} mezőt válaszotta:")
            print_board(board)
            print("------------------------------------------")
        computer_plays = not computer_plays

    chomp_learning.evaluate_events(computer_won=not computer_plays, memory_file_name=MEMO_SET_NAME)
    chomp_learning.save_memory(MEMO_SET_NAME)

    if not computer_plays:
        print("🟥🟥🟥🟥🟥🟥  VESZTETTÉL!  🟥🟥🟥🟥🟥🟥")
    else:
        print("🟩🟩🟩🟩🟩🟩    GYŐZTÉL!   🟩🟩🟩🟩🟩🟩")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Chomp játék © Orbán Gábor (github.com/GaborOrbanDev)')
    parser.add_argument("-m", "--memo_set_name", action="store", help="Megadhatja, hogy melyik memória/tudás szettet használja a program. Ha még nem létezik, akkor létrehozza.")
    parser.add_argument("-t", "--train", action="store", type=int, help="Ezzel a paraméterrel tanulási módra állíthatja a programot, és meghatározza, hogy hány meccset játsszon gyakorlásként.")
    parser.add_argument("-s", "--show_memory", action="store_true", help="Ezzel a címkével megjelenítheti a használt memória szett tartalmát. Ilyenkor a játék nem indul el.")
    parser.add_argument("-sl", "--show_logs", action="store_true", help="Ezzel a címkével megjelenítheti a használt memória szetthez tartozó logok tartalmát. Ilyenkor a játék nem indul el.")
    parser.add_argument("-r", "--report", action="store_true", help="Ezzel a címkével megjelenítheti az adott memória szetthez tartozó tanulási görbéket. Ilyenkor a játék nem indul el.")
    args = parser.parse_args()

    if args.memo_set_name is not None:
        MEMO_SET_NAME = args.memo_set_name

    if args.show_memory:
        chomp_learning.init_memory(MEMO_SET_NAME)
        rprint(f"[bold green]Elmentett lehetőségek száma: [blue]{len(chomp_learning.memories)}[/blue][/bold green]")
        rprint(chomp_learning.memories)
        exit()

    if args.show_logs:
        chomp_learning.init_logs(MEMO_SET_NAME)
        rprint(f"[bold green]Logok - Elmentett lehetőségek száma: [blue]{len(chomp_learning.logs)}[/blue][/bold green]")
        print(chomp_learning.logs)
        exit()

    if args.report:
        chomp_report_generator.make_report(MEMO_SET_NAME)
        exit()

    if args.train is None:
        game()
    else:
        try:
            if args.train > 0:
                chomp_learning.init_logs(MEMO_SET_NAME)
                train(args.train)
        except Exception as ex:
            print(ex)
            chomp_learning.save_logs(MEMO_SET_NAME)