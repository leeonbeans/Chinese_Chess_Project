import numpy as np

def initial_board():
    """生成初始棋盘状态"""
    # 黑方棋子位置（横坐标在前，纵坐标在后）
    black_pieces = [
        00, 10, 20, 30, 40, 50, 60, 70, 80,  # 车马象士将士象马车（横坐标0-8，纵坐标0）
        12, 72,  # 炮（横坐标1和7，纵坐标2）
        6, 26, 46, 66, 86  # 卒（横坐标0,2,4,6,8，纵坐标6）
    ]

    # 红方棋子位置（横坐标在前，纵坐标在后）
    red_pieces = [
        9, 19, 29, 39, 49, 59, 69, 79, 89,  # 车马相士帅士相马车（横坐标0-8，纵坐标9）
        17, 77,  # 炮（横坐标1和7，纵坐标7）
        3, 23, 43, 63, 83  # 兵（横坐标0,2,4,6,8，纵坐标3）
    ]

    # 构建棋盘状态字符串
    board = ""
    for pos in black_pieces + red_pieces:
        board += f"{pos:02d}"

    return board


def apply_move(board_state, action):
    """应用走法到棋盘"""
    start = int(action[:2])  # 起始位置（横坐标在前，纵坐标在后）
    end = int(action[2:4])   # 目标位置（横坐标在前，纵坐标在后）

    # 将棋盘转为列表便于修改
    board_list = list(board_state)

    # 查找要移动的棋子
    moved = False
    move_reason = ""  # 用于记录走法无效的原因
    for i in range(0, len(board_list), 2):
        # 检查当前位置是否有效
        if i + 1 >= len(board_list):
            continue

        pos_str = board_list[i] + board_list[i + 1]
        if pos_str == "99":
            continue  # 跳过无效位置

        pos = int(pos_str)
        if pos == start:
            # 移动棋子
            board_list[i] = f"{end // 10}"  # 更新横坐标
            board_list[i + 1] = f"{end % 10}"  # 更新纵坐标
            moved = True

            # 检查是否吃子
            for j in range(0, len(board_list), 2):
                if j == i:
                    continue  # 跳过自身
                if j + 1 >= len(board_list):
                    continue

                target_pos_str = board_list[j] + board_list[j + 1]
                if target_pos_str == "99":
                    continue

                target_pos = int(target_pos_str)
                if target_pos == end:
                    # 吃掉对方棋子（将其位置设为99）
                    board_list[j] = "9"
                    board_list[j + 1] = "9"
            break

    if not moved:
        # 检查起始位置是否有棋子
        has_piece = False
        for i in range(0, len(board_list), 2):
            if i + 1 >= len(board_list):
                continue
            pos_str = board_list[i] + board_list[i + 1]
            if pos_str != "99":
                current_pos = int(pos_str)
                if current_pos == start:
                    has_piece = True
                    break

        if not has_piece:
            move_reason = "起始位置没有棋子"
        else:
            move_reason = "目标位置被其他棋子占据且未吃子"

        raise ValueError(f"无效走法: {action}，原因：{move_reason}，当前棋盘状态：{board_state}")

    return "".join(board_list)


def board_to_matrix(board_state):
    """将棋盘状态转为矩阵表示（可选）"""
    matrix = np.full((10, 9), -1)  # 10行（纵坐标0-9）9列（横坐标0-8）

    for i in range(0, len(board_state), 2):
        if i + 1 >= len(board_state):
            continue

        pos_str = board_state[i:i + 2]
        if pos_str == "99":
            continue

        pos = int(pos_str)
        col = pos // 10  # 横坐标（列）
        row = pos % 10   # 纵坐标（行）

        # 棋子类型由索引位置决定（这里可能需要更复杂的映射逻辑）
        piece_index = i // 2
        matrix[row][col] = piece_index  # 简单映射，实际可能需要调整

    return matrix


def generate_legal_moves(board_state):
    """优化的合法走法生成器"""
    legal_moves = []
    pieces = []

    # 提取所有棋子位置
    for i in range(0, len(board_state), 2):
        pos_str = board_state[i:i + 2]
        if pos_str != "99":
            pieces.append(int(pos_str))

    # 针对每个棋子生成可能的目标位置（减少尝试次数）
    for start in pieces:
        start_x, start_y = start // 10, start % 10

        # 根据棋子类型生成可能移动范围（简化版）
        possible_moves = []
        if start_y < 9: possible_moves.append(start + 1)  # 上
        if start_y > 0: possible_moves.append(start - 1)  # 下
        if start_x < 8: possible_moves.append(start + 10)  # 右
        if start_x > 0: possible_moves.append(start - 10)  # 左

        # 对角线移动（士、象等）
        if start_x > 0 and start_y < 9: possible_moves.append(start - 9)  # 左上
        if start_x < 8 and start_y < 9: possible_moves.append(start + 11)  # 右上
        if start_x > 0 and start_y > 0: possible_moves.append(start - 11)  # 左下
        if start_x < 8 and start_y > 0: possible_moves.append(start + 9)  # 右下

        for end in possible_moves:
            move_str = f"{start:02d}{end:02d}"
            try:
                apply_move(board_state, move_str)
                legal_moves.append(move_str)
            except ValueError:
                continue

    return legal_moves