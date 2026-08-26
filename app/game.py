"""Règles pures du Démineur."""
from collections import deque
from random import Random
from typing import TypedDict

class Level(TypedDict):
    label: str
    description: str
    rows: int
    columns: int
    mines: int

LEVELS: dict[str, Level] = {
    "beginner": {"label":"Débutant","description":"Grille 9 × 9 avec 10 mines.","rows":9,"columns":9,"mines":10},
    "intermediate": {"label":"Intermédiaire","description":"Grille 16 × 16 avec 40 mines.","rows":16,"columns":16,"mines":40},
    "expert": {"label":"Expert","description":"Grille 16 × 30 avec 99 mines.","rows":16,"columns":30,"mines":99},
}

def neighbours(rows:int,columns:int,row:int,column:int)->list[tuple[int,int]]:
    return [(r,c) for r in range(max(0,row-1),min(rows,row+2)) for c in range(max(0,column-1),min(columns,column+2)) if (r,c)!=(row,column)]

def place_mines(rows:int,columns:int,count:int,safe_row:int,safe_column:int,seed:int|None=None)->list[list[int]]:
    """Place les mines après le premier clic, qui est toujours sécurisé."""
    protected={(safe_row,safe_column),*neighbours(rows,columns,safe_row,safe_column)}
    candidates=[(r,c) for r in range(rows) for c in range(columns) if (r,c) not in protected]
    if count>len(candidates): candidates=[(r,c) for r in range(rows) for c in range(columns) if (r,c)!=(safe_row,safe_column)]
    chosen=set(Random(seed).sample(candidates,count))
    return [[1 if (r,c) in chosen else 0 for c in range(columns)] for r in range(rows)]

def adjacent_counts(mines:list[list[int]])->list[list[int]]:
    rows,columns=len(mines),len(mines[0])
    return [[sum(mines[r][c] for r,c in neighbours(rows,columns,row,column)) for column in range(columns)] for row in range(rows)]

def reveal_area(revealed:list[list[bool]],flagged:list[list[bool]],adjacent:list[list[int]],row:int,column:int)->list[list[bool]]:
    result=[line[:] for line in revealed]
    if flagged[row][column]: return result
    queue=deque([(row,column)])
    while queue:
        r,c=queue.popleft()
        if result[r][c] or flagged[r][c]: continue
        result[r][c]=True
        if adjacent[r][c]==0: queue.extend(neighbours(len(result),len(result[0]),r,c))
    return result

def has_won(mines:list[list[int]],revealed:list[list[bool]])->bool:
    return all(mines[r][c] or revealed[r][c] for r in range(len(mines)) for c in range(len(mines[0])))

def score_for_win(rows:int,columns:int,mines:int,duration_seconds:int)->int:
    return max(100,rows*columns*20+mines*50-duration_seconds*5)
