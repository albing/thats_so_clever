from clever import GameBoard, Die, Color

gb = GameBoard()
gb.re_rolls = 2
gb.plus_ones = 1
gb.do_rolls()
gb.do_plus_one()


gb = GameBoard()
gb.score(Die(Color.YELLOW, 3))
gb.score(Die(Color.ORANGE, 3))

gb.dice.rolled_dice=[Die(Color.WHITE, 1), Die(Color.BLUE, 3)]


gb = GameBoard()
gb.total_score() == 0



gb.play_game()
