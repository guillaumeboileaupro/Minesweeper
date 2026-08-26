"""Persistance SQLite des parties de Démineur."""
import json,os,sqlite3
from pathlib import Path
from typing import cast
from uuid import uuid4
from .types import Action,Game,Stats

def _default_db_path()->Path:
    return Path(os.getenv("XDG_DATA_HOME",Path.home()/".local"/"share"))/"demineur"/"demineur.db"
DB_PATH=Path(os.getenv("DEMINEUR_DB",_default_db_path()))

def _connect()->sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True,exist_ok=True); db=sqlite3.connect(DB_PATH); db.row_factory=sqlite3.Row; return db

def init_db()->None:
    with _connect() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS games(id TEXT PRIMARY KEY,level TEXT NOT NULL,rows INTEGER NOT NULL,columns_count INTEGER NOT NULL,mine_count INTEGER NOT NULL,mines_json TEXT NOT NULL,adjacent_json TEXT NOT NULL,revealed_json TEXT NOT NULL,flagged_json TEXT NOT NULL,actions_json TEXT NOT NULL,status TEXT NOT NULL,started INTEGER NOT NULL,started_at TEXT NOT NULL,ended_at TEXT,duration_seconds INTEGER NOT NULL,score INTEGER NOT NULL,player_name TEXT NOT NULL)""")

def create_game(level:str,rows:int,columns:int,mine_count:int,started_at:str,player_name:str)->Game:
    game_id=str(uuid4()); empty_int=[[0]*columns for _ in range(rows)]; empty_bool=[[False]*columns for _ in range(rows)]
    with _connect() as db:
        db.execute("""INSERT INTO games VALUES(?,?,?,?,?,?,?,?,?,'[]','active',0,?,NULL,0,0,?)""",(game_id,level,rows,columns,mine_count,json.dumps(empty_int),json.dumps(empty_int),json.dumps(empty_bool),json.dumps(empty_bool),started_at,player_name))
    game=get_game(game_id)
    if game is None: raise RuntimeError("Partie créée introuvable")
    return game

def get_game(game_id:str)->Game|None:
    with _connect() as db: row=db.execute("SELECT * FROM games WHERE id=?",(game_id,)).fetchone()
    return _decode(row) if row else None

def get_current_game()->Game|None:
    with _connect() as db: row=db.execute("SELECT * FROM games WHERE status='active' ORDER BY started_at DESC LIMIT 1").fetchone()
    return _decode(row) if row else None

def save_game(game:Game)->None:
    with _connect() as db:
        db.execute("""UPDATE games SET mines_json=?,adjacent_json=?,revealed_json=?,flagged_json=?,actions_json=?,status=?,started=?,ended_at=?,duration_seconds=?,score=? WHERE id=?""",(json.dumps(game["mines"]),json.dumps(game["adjacent"]),json.dumps(game["revealed"]),json.dumps(game["flagged"]),json.dumps(game["actions"]),game["status"],int(game["started"]),game["ended_at"],game["duration_seconds"],game["score"],game["id"]))

def abandon_active_games(ended_at:str)->None:
    with _connect() as db: db.execute("UPDATE games SET status='abandoned',ended_at=? WHERE status='active'",(ended_at,))
def list_history(limit:int=50)->list[Game]:
    with _connect() as db: rows=db.execute("SELECT * FROM games WHERE status!='active' ORDER BY started_at DESC LIMIT ?",(limit,)).fetchall()
    return [_decode(row) for row in rows]
def reset_scores()->int:
    with _connect() as db: cursor=db.execute("DELETE FROM games WHERE status!='active'")
    return max(0,cursor.rowcount)
def get_stats()->Stats:
    with _connect() as db: row=db.execute("""SELECT COUNT(*) games_total,SUM(status='won') wins,SUM(status='lost') losses,COALESCE(SUM(score),0) total_score,COALESCE(MAX(score),0) best_score,MIN(CASE WHEN status='won' THEN duration_seconds END) best_time FROM games WHERE status!='active'""").fetchone()
    return {"games_total":int(row["games_total"] or 0),"wins":int(row["wins"] or 0),"losses":int(row["losses"] or 0),"total_score":int(row["total_score"] or 0),"best_score":int(row["best_score"] or 0),"best_time":int(row["best_time"]) if row["best_time"] is not None else None}

def _decode(row:sqlite3.Row)->Game:
    return {"id":str(row["id"]),"level":str(row["level"]),"rows":int(row["rows"]),"columns":int(row["columns_count"]),"mine_count":int(row["mine_count"]),"mines":cast(list[list[int]],json.loads(row["mines_json"])),"adjacent":cast(list[list[int]],json.loads(row["adjacent_json"])),"revealed":cast(list[list[bool]],json.loads(row["revealed_json"])),"flagged":cast(list[list[bool]],json.loads(row["flagged_json"])),"actions":cast(list[Action],json.loads(row["actions_json"])),"status":str(row["status"]),"started":bool(row["started"]),"started_at":str(row["started_at"]),"ended_at":str(row["ended_at"]) if row["ended_at"] else None,"duration_seconds":int(row["duration_seconds"]),"score":int(row["score"]),"player_name":str(row["player_name"])}
