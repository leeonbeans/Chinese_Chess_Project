## **Just a simple Chinese chess game owing to the lesson.**

Due to the limit, the ai model in /flask/chess_ai/model is not uploaded.  
So are training data in /flask/chess_ai/data.

* * *

We also use an api (https://www.chessdb.cn/chessdb.php) to assist.

At first, we hoped that the player play with our ai-model.  
But our trained ai-model went something wrong, and often robbed the player's chess.  
After trying all means, we decided to give up re-training ai-model and asked the outer api for help.

However, we found out we couldn't finish a whole game though using the api......  
So when the ai-model and api all abandon the game, the tip---"AI从未看见过如此逆天的对局，轮到您走棋。" will show up the top of the game.

* * *

## We use Dongping and Fen format across the project.

Dongping format (东萍格式) source *www.dpxq.com* (东萍象棋网), it can describe the current chess situation and movement.

###   \*The current chess situation by Dongping format  
64 numbers, and each 2 numbers stands for one chess.  
The order is:  
1st 红车 2nd 红马 3rd 红相 4th 红仕 5th 红帅 6th 红仕 7th 红相 8th 红马  
9th 红车 10th 红炮 11th 红炮 12th 红兵 13th 红兵 14th 红兵 15th 红兵 16th 红兵  
17th 黑车 18th 黑马 19th 黑相 20th 黑士 21st 黑将 22nd 黑士 23rd 黑相 24th 黑马  
25th 黑车 26th 黑炮 27th 黑炮 28th 黑卒 29th 黑卒 30th 黑卒 31st 黑卒 32nd 黑卒

The initial game is like 8979695949392919097717866646260600102030405060708012720323436383.  
89 means '红车' is at col 8 row 9 (starting with 0)  
79 means '红马' is at col 7 row 9  
and so on...

### \*The movement by Dongping format  
4 numbers, and each 2 numbers stands for a position  
For example, '8987' means the chess current at col 8 row 9 moves to col 8 row 7  
By the way, the movelist in *www.dpxq.com* is just a movement collection in a whole game, you can just split every four numbers to get the all movement in this game.

* * *
###   \*The current chess situation by Fen format  
Fen format can describe the current chess situation.  
The initial game is like

> \['r', 'n', 'b', 'a', 'k', 'a', 'b', 'n', 'r'\],  
> \['.', '.', '.', '.', '.', '.', '.', '.', '.'\],  
> \['.', 'c', '.', '.', '.', '.', '.', 'c', '.'\],  
> \['p', '.', 'p', '.', 'p', '.', 'p', '.', 'p'\],  
> \['.', '.', '.', '.', '.', '.', '.', '.', '.'\],  
> \['.', '.', '.', '.', '.', '.', '.', '.', '.'\],  
> \['P', '.', 'P', '.', 'P', '.', 'P', '.', 'P'\],  
> \['.', 'C', '.', '.', '.', '.', '.', 'C', '.'\],  
> \['.', '.', '.', '.', '.', '.', '.', '.', '.'\],  
> \['R', 'N', 'B', 'A', 'K', 'A', 'B', 'N', 'R'\]

describe it with Fen format is  
rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR r  
The numbers of Fen means the blank.  
The letter of the end means whose turn. 'r' means red (红方), 'b' means black (黑方).

In the project, we team confuse the Dongping format. Thus, we had to add remedial measures to make Dongping format convert correctly to Fen format. If you use the right Dongping format, please delete "错误补救措施" in 'invertToFen.py' (/flask/chess_ai/)

* * *
In the end, I sincerely hope nobody knows this rubbish. (To many errors and bugs as well as bad moods)