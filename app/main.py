"""API FastAPI du Démineur."""
from contextlib import asynccontextmanager
from datetime import datetime,timezone
from pathlib import Path
from typing import AsyncIterator,Literal
from fastapi import FastAPI,HTTPException,Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel,Field
from .game import LEVELS,adjacent_counts,has_won,place_mines,reveal_area,score_for_win
from .storage import abandon_active_games,create_game,get_current_game,get_game,get_stats,init_db,list_history,reset_scores,save_game
from .types import Action,Game,Stats

BASE_DIR=Path(__file__).resolve().parent.parent; STATIC_DIR=BASE_DIR/"static"
def utc_now()->datetime: return datetime.now(timezone.utc)
def elapsed(game:Game,now:datetime|None=None)->int:
    if not game["started"]: return 0
    if game["status"]!="active": return game["duration_seconds"]
    return max(0,int(((now or utc_now())-datetime.fromisoformat(game["started_at"])).total_seconds()))
@asynccontextmanager
async def lifespan(_:FastAPI)->AsyncIterator[None]: init_db(); yield
app=FastAPI(title="Démineur API",version="1.0.0",lifespan=lifespan); app.mount("/static",StaticFiles(directory=STATIC_DIR),name="static")

class NewGameRequest(BaseModel):
    level:str="beginner"; rows:int|None=Field(default=None,ge=5,le=30); columns:int|None=Field(default=None,ge=5,le=40); mines:int|None=Field(default=None,ge=1); player_name:str=Field(default="",max_length=20)
class ActionRequest(BaseModel):
    row:int; column:int; action:Literal["reveal","flag"]

@app.get("/")
def home()->FileResponse: return FileResponse(STATIC_DIR/"index.html")
@app.get("/api/health")
def health()->dict[str,str]: return {"status":"ok"}
@app.get("/api/config")
def config()->dict[str,object]: return {"levels":LEVELS,"custom":{"min_rows":5,"max_rows":30,"min_columns":5,"max_columns":40}}
@app.get("/api/games/current")
def current_game()->Game|None: return public_game(get_current_game())

def public_game(game:Game|None)->Game|None:
    if game is None: return None
    result=game.copy()
    if game["status"]=="active": result["mines"]=[[0]*game["columns"] for _ in range(game["rows"])]
    return result

@app.post("/api/games",status_code=201)
def new_game(payload:NewGameRequest)->Game:
    if payload.level=="custom":
        if payload.rows is None or payload.columns is None or payload.mines is None: raise HTTPException(400,"Dimensions personnalisées incomplètes")
        rows,columns,mines=payload.rows,payload.columns,payload.mines
        if mines>=rows*columns: raise HTTPException(400,"Il faut au moins une case sans mine")
    elif payload.level in LEVELS:
        level=LEVELS[payload.level]; rows,columns,mines=level["rows"],level["columns"],level["mines"]
    else: raise HTTPException(400,"Niveau inconnu")
    now=utc_now(); abandon_active_games(now.isoformat())
    return public_game(create_game(payload.level,rows,columns,mines,now.isoformat(),payload.player_name.strip() or "Joueur"))  # type: ignore[return-value]

@app.post("/api/games/{game_id}/actions")
def play(game_id:str,payload:ActionRequest)->Game:
    game=get_game(game_id)
    if not game: raise HTTPException(404,"Partie introuvable")
    if game["status"]!="active": raise HTTPException(409,"Cette partie est terminée")
    if not (0<=payload.row<game["rows"] and 0<=payload.column<game["columns"]): raise HTTPException(400,"Case invalide")
    row,column=payload.row,payload.column; now=utc_now()
    if payload.action=="flag":
        if game["revealed"][row][column]: raise HTTPException(400,"Une case révélée ne peut pas être marquée")
        game["flagged"][row][column]=not game["flagged"][row][column]
    else:
        if game["flagged"][row][column]: raise HTTPException(400,"Retirez d’abord le drapeau")
        if not game["started"]:
            game["mines"]=place_mines(game["rows"],game["columns"],game["mine_count"],row,column)
            game["adjacent"]=adjacent_counts(game["mines"]); game["started"]=True; game["started_at"]=now.isoformat()
        if game["mines"][row][column]:
            game["revealed"]=[[bool(game["mines"][r][c]) or game["revealed"][r][c] for c in range(game["columns"])] for r in range(game["rows"])]; game["status"]="lost"
        else:
            game["revealed"]=reveal_area(game["revealed"],game["flagged"],game["adjacent"],row,column)
            if has_won(game["mines"],game["revealed"]): game["status"]="won"; game["flagged"]=[[bool(game["mines"][r][c]) for c in range(game["columns"])] for r in range(game["rows"])]
    action:Action={"number":len(game["actions"])+1,"row":row,"column":column,"action":payload.action,"created_at":now.isoformat()}; game["actions"].append(action)
    if game["status"]!="active": game["ended_at"]=now.isoformat(); game["duration_seconds"]=elapsed(game,now); game["score"]=score_for_win(game["rows"],game["columns"],game["mine_count"],game["duration_seconds"]) if game["status"]=="won" else 0
    save_game(game); result=public_game(game)
    if result is None: raise RuntimeError("Partie introuvable")
    return result

@app.post("/api/games/{game_id}/give-up")
def give_up(game_id:str)->Game:
    game=get_game(game_id)
    if not game: raise HTTPException(404,"Partie introuvable")
    if game["status"]!="active": raise HTTPException(409,"Cette partie est terminée")
    now=utc_now(); game["status"]="abandoned"; game["ended_at"]=now.isoformat(); game["duration_seconds"]=elapsed(game,now); save_game(game); return game
@app.get("/api/history")
def history(limit:int=Query(50,ge=1,le=200))->list[Game]: return list_history(limit)
@app.get("/api/stats")
def stats()->Stats: return get_stats()
@app.delete("/api/history")
def clear_history()->dict[str,int]: return {"deleted":reset_scores()}
