"""Structures typées partagées par le Démineur."""
from typing_extensions import TypedDict

class Action(TypedDict):
    number: int
    row: int
    column: int
    action: str
    created_at: str

class Game(TypedDict):
    id: str
    level: str
    rows: int
    columns: int
    mine_count: int
    mines: list[list[int]]
    adjacent: list[list[int]]
    revealed: list[list[bool]]
    flagged: list[list[bool]]
    actions: list[Action]
    status: str
    started: bool
    started_at: str
    ended_at: str | None
    duration_seconds: int
    score: int
    player_name: str

class Stats(TypedDict):
    games_total: int
    wins: int
    losses: int
    total_score: int
    best_score: int
    best_time: int | None
