from pathlib import Path
from collections.abc import Generator
import pytest
from fastapi.testclient import TestClient
from app import storage
from app.main import app

@pytest.fixture
def client(tmp_path:Path,monkeypatch:pytest.MonkeyPatch)->Generator[TestClient,None,None]:
    monkeypatch.setattr(storage,"DB_PATH",tmp_path/"test.db")
    with TestClient(app) as test_client: yield test_client

def test_health_and_config(client:TestClient)->None:
    assert client.get("/api/health").json()=={"status":"ok"}
    assert set(client.get("/api/config").json()["levels"])=={"beginner","intermediate","expert"}

def test_create_and_first_reveal(client:TestClient)->None:
    game=client.post("/api/games",json={"level":"beginner","player_name":"Guillaume"}).json()
    assert game["rows"]==9 and game["mine_count"]==10 and not game["started"]
    played=client.post(f'/api/games/{game["id"]}/actions',json={"row":4,"column":4,"action":"reveal"}).json()
    assert played["started"] and played["revealed"][4][4] and played["mines"][4][4]==0

def test_flag_toggle(client:TestClient)->None:
    game=client.post("/api/games",json={"level":"beginner"}).json(); url=f'/api/games/{game["id"]}/actions'
    assert client.post(url,json={"row":0,"column":0,"action":"flag"}).json()["flagged"][0][0]
    assert not client.post(url,json={"row":0,"column":0,"action":"flag"}).json()["flagged"][0][0]

def test_custom_validation_and_history(client:TestClient)->None:
    assert client.post("/api/games",json={"level":"custom","rows":5,"columns":5,"mines":25}).status_code==400
    game=client.post("/api/games",json={"level":"custom","rows":6,"columns":7,"mines":8}).json()
    assert (game["rows"],game["columns"],game["mine_count"])==(6,7,8)
    client.post(f'/api/games/{game["id"]}/give-up')
    assert len(client.get("/api/history").json())==1
    assert client.delete("/api/history").json()=={"deleted":1}
