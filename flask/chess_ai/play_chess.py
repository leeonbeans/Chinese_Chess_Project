import os
import pickle
import sys
from utils.board_utils import initial_board, apply_move, board_to_matrix
from model.chess_model import ChessModel

def main():
    # 加载模型
    model_path = os.path.join('model', 'chess_ai_model.pkl')
    # model_path = "./chess_ai/model/chess_ai_model.pkl"
    try:
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        print(f"已加载模型：{model_path}")
    except FileNotFoundError:
        print(f"模型文件未找到，请确保模型已训练并保存到 {model_path}")
        return

    # 从字典数据中重新构建ChessModel实例
    model = ChessModel(model_type=model_data['model_type'])
    model.move_stats = model_data['move_stats']
    model.win_stats = model_data['win_stats']

    # 初始化棋盘
    board_state = initial_board()
    print("初始棋盘状态：")
    print(board_state)

    # 游戏主循环
    while True:
        # 用户走棋
        user_move = input("请输入您的走法（格式：起始位置+目标位置，例如：1747）：")
        try:
            new_board_state = apply_move(board_state, user_move)
            board_state = new_board_state
            print(f"用户走法：{user_move}")
            print(f"当前棋盘状态：{board_state}")
        except ValueError as e:
            print(f"无效走法：{user_move}，原因：{e}")
            continue

        # AI走棋
        try:
            ai_move = model.predict(board_state)
            if ai_move is None:
                print("AI无法找到合法走法，游戏结束")
                break

            new_board_state = apply_move(board_state, ai_move)
            board_state = new_board_state
            print(f"AI走法：{ai_move}")
            print(f"当前棋盘状态：{board_state}")
        except ValueError as e:
            print(f"AI走法出错：{e}")
            break

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(current_dir, '..'))
    main()