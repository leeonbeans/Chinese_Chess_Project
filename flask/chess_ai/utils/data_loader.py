import json
import os
import numpy as np
import pickle
import sys
from tqdm import tqdm

# 添加项目根目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, project_root)

from board_utils import initial_board, apply_move


test_file = 'wanzhen.json'

def get_test_file():
    return  test_file

def load_and_process_data(json_file_path):
    """加载并预处理棋局数据"""
    # 加载数据
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            games = json.load(f)
        print(f"已加载 {len(games)} 场棋局数据，文件路径：{json_file_path}")
    except json.JSONDecodeError as e:
        print(f"解析 JSON 文件时出错，文件路径：{json_file_path}，错误信息：{e}")
        return []

    processed = []
    invalid_move_details = []  # 用于记录无效走法的详细信息

    for game in tqdm(games, desc="处理棋局"):
        movelist = game['movelist']
        result = game.get('result', 'unknown')  # 假设结果字段存在，如果没有则默认为未知

        # 创建初始棋盘
        board_state = initial_board()
        board_history = [board_state]
        moves = []

        # 将走法字符串转换为每四个字符一组的列表
        game_moves = [movelist[i:i+4] for i in range(0, len(movelist), 4)]

        for move in game_moves:
            try:
                # 应用走法到棋盘
                new_board = apply_move(board_state, move)
                board_history.append(new_board)
                moves.append(move)
                board_state = new_board
            except ValueError as e:
                # 记录无效走法的详细信息
                invalid_move_details.append({
                    'move': move,
                    'movelist': movelist,  # 记录整个 movelist
                    'board_state': board_state,
                    'error': str(e)
                })
                print(f"跳过无效走法 {move}，原因：{e}")
                continue

        processed.append({
            'game_id': len(processed),  # 临时游戏ID
            'result': result,
            'board_states': board_history,
            'moves': moves
        })

    # 保存处理后的数据
    processed_data_path = os.path.join(os.path.dirname(json_file_path), 'processed_data.pkl')
    with open(processed_data_path, 'wb') as f:
        pickle.dump(processed, f)

    print(f"处理后的数据已保存，文件路径：{processed_data_path}")

    # 保存无效走法的详细信息
    invalid_moves_path = os.path.join(os.path.dirname(json_file_path), 'invalid_moves.json')
    with open(invalid_moves_path, 'w', encoding='utf-8') as f:
        json.dump(invalid_move_details, f, ensure_ascii=False, indent=4)

    print(f"无效走法的详细信息已保存，文件路径：{invalid_moves_path}")
    return processed


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, '..', 'data')
    json_file_path = os.path.join(data_dir, 'wanzhen.json')
    load_and_process_data(json_file_path)