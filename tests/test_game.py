from app.game import adjacent_counts,has_won,neighbours,place_mines,reveal_area,score_for_win

def test_neighbours_corner_and_center()->None:
    assert len(neighbours(9,9,0,0))==3
    assert len(neighbours(9,9,4,4))==8

def test_first_click_and_neighbours_are_safe()->None:
    mines=place_mines(9,9,10,4,4,seed=7)
    assert sum(map(sum,mines))==10
    assert all(mines[r][c]==0 for r,c in [(4,4),*neighbours(9,9,4,4)])

def test_adjacent_counts()->None:
    mines=[[1,0,0],[0,0,0],[0,0,1]]
    assert adjacent_counts(mines)==[[0,1,0],[1,2,1],[0,1,0]]

def test_reveal_cascade_respects_flags()->None:
    adjacent=[[0,0,0],[0,1,1],[0,1,0]]
    revealed=[[False]*3 for _ in range(3)]; flagged=[[False]*3 for _ in range(3)]; flagged[0][2]=True
    result=reveal_area(revealed,flagged,adjacent,0,0)
    assert result[0][0] and result[1][1] and not result[0][2]

def test_win_and_score()->None:
    mines=[[1,0],[0,0]]; revealed=[[False,True],[True,True]]
    assert has_won(mines,revealed)
    assert score_for_win(9,9,10,20)>score_for_win(9,9,10,40)
