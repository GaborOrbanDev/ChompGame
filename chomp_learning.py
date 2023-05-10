from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import pickle
import os.path
import numpy as np

A = 2
B = -1 / 3.5
START_WEIGHT = A / 2

@dataclass
class Event:
    computer: bool 
    options: Tuple[tuple]
    choice: tuple

events: List[Event] = []

@dataclass
class Memory:
    options: List[tuple]
    weights: List[float]
    counter: List[int]

memories: Dict[Tuple[tuple], Memory] = {}
"""
`memories: Dict[Tuple[tuple], Memory]` tartalmazza a különböző esetekhez tartozó választási lehetőségek bekövetkezési valószínűségének a súlyát
- key: `Memory.options | Event.options` :: az adott helyzetben választható lépések indexei
- value: `Memory` :: egy emlék, ami tartalmazza a válaztható lépéseket, és azok súlyát, illetve a súlyok kiszámításához szükséges számlálót
"""
logs: Dict[Tuple[tuple], List[Memory]] = {}

def init_memory(file_name: str) -> None:
    """A `pickle` modul segítségével betölti egy .pkl file-ban tárolt memories változó értékét"""
    file_name_w_format = f"{file_name}.pkl"
    if os.path.isfile(f"./{file_name_w_format}"):
        # print("Van file")
        with open(file_name_w_format, "rb") as f:
            _memories = pickle.load(f)
            for key in _memories:
                memories[key] = _memories[key]
    else:
        pass

def init_logs(file_name: str) -> None:
    """A `pickle` modul segítségével betölti egy .pkl file-ban tárolt log dictionary változó értékét"""
    file_name_w_format = f"logs_{file_name}.pkl"
    if os.path.isfile(f"./{file_name_w_format}"):
        # print("Van file")
        with open(file_name_w_format, "rb") as f:
            _logs = pickle.load(f)
            for key in _logs:
                logs[key] = _logs[key]
    else:
        pass

def append_event(event: Event) -> None:
    """Hozzáadja az `events` listához a paraméterként megadott eseményt"""
    events.append(event)

def clear_events() -> None:
    """Kitörli az `events` lista elemeit"""
    events.clear()

def evaluate_events(computer_won: bool, memory_file_name: str) -> None:
    """
    Ez a funkió kiértékeli a játék során szerzett tapasztalatokat és a tapasztalatokból emlékeket készít, illetve szerkeszt.
    Az emlékek elkészítése után hozzáadja azokat a `logs` dictionary-hoz.

    Egy for ciklus segítségével végig iterál a játék eseményein, és megnézi, hogy az adott helyzettel találkozott-e valaha a számítógép:
    - ha igen: akkor szerkeszti a létező emlékhez tartozó súlyokat
    - ha nem: akkor létrehozza először az eméket, majd a játék kimenete alapján meghatározza a súlyokat a választási lehetőségekhez

    Az események kiértékelése után törli az `events` lista elemeit a `clear_events()` funkció segítégével
    """
    for event in events:
        if event.options in memories.keys():
            choice_index = memories[event.options].options.index(event.choice)
            if event.computer == computer_won:
                memories[event.options].counter[choice_index] += 1
            else:
                memories[event.options].counter[choice_index] -= 1
            memories[event.options].weights[choice_index] = A / (1 + np.exp(B * memories[event.options].counter[choice_index]))
        else:
            memory = Memory(
                options = event.options,
                weights = [START_WEIGHT] * len(event.options),
                counter = [0] * len(event.options)
            )
            choice_index = memory.options.index(event.choice)
            if event.computer == computer_won:
                memory.counter[choice_index] += 1
            else:
                memory.counter[choice_index] -= 1
            memory.weights[choice_index] = A / (1 + np.exp(B * memory.counter[choice_index]))
            memories[memory.options] = memory
    
    # init_logs(file_name=memory_file_name)
    for event in events:
        if event.options in logs.keys():
            logs[event.options].append(memories[event.options])
        else:
            logs.update({event.options: [memories[event.options]]})
    # save_logs(file_name=memory_file_name)

    clear_events()

def save_memory(file_name: str) -> None:
    """A `pickle` modul segítségével elmenti egy file-ba a `memories` változót"""
    with open(f"{file_name}.pkl", "wb") as f:
        pickle.dump(memories, f)

def save_logs(file_name: str) -> None:
    """A `pickle` modul segítségével elmenti egy file-ba a `logs` változót"""
    with open(f"logs_{file_name}.pkl", "wb") as f:
        pickle.dump(logs, f)

if __name__ == "__main__":
    memo_name = "btest100000"
    init_memory(memo_name)
    print(memories)    