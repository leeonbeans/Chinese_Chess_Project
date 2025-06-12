def custom_to_fen(custom_str):
    """将自定义格式转换为FEN"""
    # 棋子类型映射 (按顺序)
    piece_types = [
        'r', 'n', 'b', 'a', 'k', 'a', 'b', 'n', 'r',  # 黑方：车马象士将士象马车
        'c', 'c',  # 黑方：炮炮
        'p', 'p', 'p', 'p', 'p',  # 黑方：卒卒卒卒卒

        'R', 'N', 'B', 'A', 'K', 'A', 'B', 'N', 'R',  # 红方：车马相仕帅仕相马车
        'C', 'C',  # 红方：炮炮
        'P', 'P', 'P', 'P', 'P'  # 红方：兵兵兵兵兵
    ]

    # 创建空棋盘 (10行9列)
    board = [['.' for _ in range(9)] for _ in range(10)]

    # 解析字符串
    for i in range(0, len(custom_str), 2):
        # 提取位置编码
        pos_str = custom_str[i:i + 2]
        if not pos_str.isdigit():
            continue

        # 转换为行列坐标
        pos = int(pos_str)
        row = pos // 9
        col = pos % 9

        # 获取棋子类型 (按顺序)
        piece_idx = i // 2
        if piece_idx < len(piece_types):
            piece = piece_types[piece_idx]

            # 放置棋子到棋盘
            if 0 <= row <= 9 and 0 <= col <= 8:
                board[row][col] = piece

    # 将棋盘转换为FEN
    fen_rows = []
    for row in board:
        fen_row = ""
        empty_count = 0

        for cell in row:
            if cell == '.':
                empty_count += 1
            else:
                if empty_count > 0:
                    fen_row += str(empty_count)
                    empty_count = 0
                fen_row += cell

        if empty_count > 0:
            fen_row += str(empty_count)

        fen_rows.append(fen_row)

    # 默认红方先行
    return f"{'/'.join(fen_rows)} w - - 0 1"


def generate_fen(board, turn='b', half_moves=0, full_moves=1):
    """
    生成中国象棋FEN字符串
    :param board: 10x9的二维列表表示棋盘
    :param turn: 'w'红方/'b'黑方
    :param half_moves: 半回合计数
    :param full_moves: 回合数
    :return: FEN字符串
    """
    fen_rows = []
    for row in board:
        fen_row = ""
        empty_count = 0

        for piece in row:
            if piece == ".":
                empty_count += 1
            else:
                if empty_count > 0:
                    fen_row += str(empty_count)
                    empty_count = 0
                fen_row += piece

        if empty_count > 0:
            fen_row += str(empty_count)

        fen_rows.append(fen_row)

    return f"{'/'.join(fen_rows)} {turn}"# - - {half_moves} {full_moves}"


# 使用示例
initial_board = [
    ['r', 'n', 'b', 'a', 'k', 'a', 'b', 'n', 'r'],
    ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', 'c', '.', '.', '.', '.', '.', 'c', '.'],
    ['p', '.', 'p', '.', 'p', '.', 'p', '.', 'p'],
    ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
    ['P', '.', 'P', '.', 'P', '.', 'P', '.', 'P'],
    ['.', 'C', '.', '.', '.', '.', '.', 'C', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
    ['R', 'N', 'B', 'A', 'K', 'A', 'B', 'N', 'R']
]




def changetoFen(dp):
    initial_board = [
        ['r', 'n', 'b', 'a', 'k', 'a', 'b', 'n', 'r'],
        ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', 'c', '.', '.', '.', '.', '.', 'c', '.'],
        ['p', '.', 'p', '.', 'p', '.', 'p', '.', 'p'],
        ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['P', '.', 'P', '.', 'P', '.', 'P', '.', 'P'],
        ['.', 'C', '.', '.', '.', '.', '.', 'C', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['R', 'N', 'B', 'A', 'K', 'A', 'B', 'N', 'R']
    ]

    # 全部变成 “1” 意思是空棋盘
    for i in range(0,10):
        for j in range(0,9):
            initial_board[i][j] = str(1)

    # 棋子的顺序，前为黑，后为红#作废已经是乱套的错的了
    str_chess = "rnbakabnrccppppp"+"rnbakabnrccppppp".upper()
    sum = 0
    for i in range(0,64,2):
        sum += 1
        # print(f"dp:{len(dp)}")
        # print(f"i:{i}")
        x = int(dp[i])          #x,y是当前棋子的位置
        y = int(dp[i+1])
        #当前棋子的位置
        if(x == 9 & y == 9):
            continue

        char = str_chess[sum-1]     #当前棋子是什么
        # if(sum >= 17):
        #     char = str_chess[sum-1].upper()     #变成大写

        initial_board[y][x] = char

    s =  generate_fen(initial_board)
    s = s.replace("111111111", "9")
    s = s.replace('11111111', '8')
    s = s.replace('1111111', '7')
    s = s.replace('111111', '6')
    s = s.replace('11111', '5')
    s = s.replace('1111', '4')
    s = s.replace('111', '3')
    s = s.replace('11', '2')

    #错误补救措施
    s = s.replace('P', 'T')
    s = s.replace('p', 'P')
    s = s.replace('T', 'p')


    return s;

dp = "0010203040506070801272062646668609192939495969798917770323436383"
print(dp)
print(changetoFen(dp))