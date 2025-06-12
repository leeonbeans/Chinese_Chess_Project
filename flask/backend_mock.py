# backend_mock.py
import this

from flask import Flask, jsonify
from flask_cors import CORS
import random # 用于随机选择走法
import requests
from sympy.physics.units import action

from chess_ai import invertToFen
from chess_ai import movesChange
from chess_ai.utils.board_utils import initial_board, apply_move, board_to_matrix
from chess_ai.model.chess_model import ChessModel

import chess_ai.invertToFen
import chess_ai.movesChange

import pickle



app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
# AI (黑方) 的预设走法序列
# 格式: "起始列起始行目标列目标行" (0-indexed)
# (x,y) 对应 (列,行)。(0,0)是黑方左车，(8,9)是红方右车。
# AI 是黑方，所以它的棋子 y 坐标通常较小 (0-4)，兵/卒前进是 y 增加。

# 合规的黑方开局回应示例
# 假设红方常见的开局:
# 1. 炮二平五 (红炮从 (1,7) -> (4,7)) -> 后端表示 "1747" (如果红炮是R_PAO1)
#    或 (红炮从 (1,2) -> (4,2) 如果按棋盘数组顺序，红炮在第2行)
#    你需要确认你的棋盘字符串中红炮的初始位置。
#    假设红方 R_PAO1 (id=9) 的初始位置是 (1,7) -> 字符串 "17"
#    红方 R_PAO2 (id=10) 的初始位置是 (7,7) -> 字符串 "77"
#    黑方 B_PAO1 (id=25) 的初始位置是 (1,2) -> 字符串 "12"
#    黑方 B_PAO2 (id=26) 的初始位置是 (7,2) -> 字符串 "72"

# 黑方棋子初始位置 (0-indexed, (列, 行))
# B_CAR1: (0,0), B_HORSE1: (1,0), B_XIANG1: (2,0), B_SHI1: (3,0), B_JIANG: (4,0), B_SHI2: (5,0), B_XIANG2: (6,0), B_HORSE2: (7,0), B_CAR2: (8,0)
# B_PAO1: (1,2), B_PAO2: (7,2)
# B_ZU1: (0,3), B_ZU2: (2,3), B_ZU3: (4,3), B_ZU4: (6,3), B_ZU5: (8,3)

# ai_opening_moves_black = [
#     # 针对红方 "炮二平五" (假设红中炮)
#     {"name": "黑 马8进7 (应对红中炮)", "move": "7062"}, # B_HORSE2 (7,0) -> (6,2)
#     {"name": "黑 左中炮 (屏风马常见)", "move": "1242"}, # B_PAO1 (1,2) -> (4,2)
#     # 针对红方 "仙人指路" (兵七进一 或 兵三进一)
#     {"name": "黑 卒7进1 (应对红兵七进一)", "move": "6353"}, # B_ZU4 (6,3) -> (5,3) (错误，卒不能后退，应为 6373) -> 改为 6373 (卒7进1)
#     {"name": "黑 卒3进1 (应对红兵三进一)", "move": "2333"}, # B_ZU2 (2,3) -> (3,3)
#     # 其他一些常见开局
#     {"name": "黑 象3进5", "move": "2042"}, # B_XIANG1 (2,0) -> (4,2)
#     {"name": "黑 士4进5", "move": "3041"}, # B_SHI1 (3,0) -> (4,1)
#     {"name": "黑 炮8平5 (右中炮)", "move": "7242"}, # B_PAO2 (7,2) -> (4,2)
#     {"name": "黑 车9平8", "move": "8070"}, # B_CAR2 (8,0) -> (7,0)
# ]
#
# # 故意的不合规走法 (用于测试前端校验)
# ai_invalid_moves_black = [
#     {"name": "黑 卒7横走 (不合规，未过河)", "move": "6353"}, # B_ZU4 (6,3) -> (5,3)
#     {"name": "黑 马不别腿 (不合规，假设(1,1)有子)", "move": "0021"}, # B_HORSE1 (1,0) 尝试蹩腿跳到 (2,1) 如果(0,1)有子
#     {"name": "黑 象过河 (不合规)", "move": "2044"}, # B_XIANG1 (2,0) -> (4,4)
#     {"name": "黑 士出宫 (不合规)", "move": "3022"}, # B_SHI1 (3,0) -> (2,2)
#     {"name": "黑 将出宫 (不合规)", "move": "4043"}, # B_JIANG (4,0) -> (4,3)
#     {"name": "黑 车吃己方马 (不合规，假设马在(0,1))", "move": "0001"}, # B_CAR1 (0,0) 吃 B_HORSE1 (假设在(0,1))
# ]
#
# # 合并所有可能的测试走法
# all_test_moves = ai_opening_moves_black + ai_invalid_moves_black
# random.shuffle(all_test_moves) # 随机打乱顺序，增加测试多样性
#
# move_history_log = [] # 记录后端已经给出的走法，避免重复或简单循环
#
# @app.route('/api/suggest/<current_board_status>')
# def suggest_move_mock(current_board_status):
#     # global move_index # 不再使用简单的 move_index
#     print(f"后端收到棋盘状态 (status): {current_board_status}")
#     print(f"后端已走历史: {move_history_log}")
#
#     response_payload = {}
#     chosen_move_info = None
#
#     # 尝试从 all_test_moves 中选择一个之前没走过的
#     available_moves = [m for m in all_test_moves if m["move"] not in move_history_log]
#
#     if available_moves:
#         chosen_move_info = random.choice(available_moves) # 随机选一个可用的
#         ai_action = chosen_move_info["move"]
#         move_history_log.append(ai_action) # 记录已选择的走法
#
#         response_payload = {
#             "code": 200,
#             "data": ai_action
#         }
#         print(f"后端回应AI走法: {ai_action} (描述: {chosen_move_info['name']})")
#     else:
#         # 所有预设走法都用完了
#         print("所有预设测试走法已用完，AI无棋可走或返回错误")
#         response_payload = {
#             "code": 404,
#             "data": None,
#             "message": "AI没有可建议的走法 (测试序列结束)"
#         }
#         move_history_log.clear() # 可以选择清空历史，以便下次重新开始序列
#
#     return jsonify(response_payload)
a = ''

def load_model():
    model_path = "./chess_ai/model/chess_ai_model.pkl"
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
    global a
    board_state = initial_board()
    a = board_state
    print("初始棋盘状态：")
    print(board_state)

    @app.route('/api/suggest/<current_board_status>')
    def model_move_mock(current_board_status):
        print(f"用户走法：{current_board_status}")
        global a
        print('走之前棋盘状态：',a)
        board_state = apply_move(a,current_board_status)
        a = board_state
        response_payload = {}
        try:
            ai_move = model.predict(board_state)
            print(ai_move)
            if ai_move is None:
                print("AI无法找到合法走法，游戏结束")
                response_payload = {
                    "code": 404,
                    "data": None,
                    "message": "AI没有可建议的走法 (测试序列结束)"
                }
            print(f"AI走法：{ai_move}")
            response_payload = {
                "code": 200,
                "data": ai_move
            }
        except ValueError as e:
            print(f"AI走法出错：{e}")
            response_payload = {
                "code": 404,
                "data": None,
                "message": "AI没有可建议的走法 (测试序列结束)"
            }

        return jsonify(response_payload)

    @app.route('/api/suggest/restart')
    def restart():
        global a
        a = initial_board()
        return jsonify({"code": 200, "data": "restart"})

    @app.route('/api/suggest/current_apply_ai_step')
    def apply_ai_step():
        global a
        current_apply_ai_step = request.args.get('move')
        a = apply_move(a, current_apply_ai_step)
        return jsonify({"code": 200, "data": "applyOK"})

    api = "https://www.chessdb.cn/chessdb.php"

    from flask import request, jsonify
    import requests

    @app.route('/api/suggest/getApiMove')
    def getApiMove():
        # 1. 获取前端传来的 board 参数(传回来的是走步，不是棋局状态)
        board_dp = request.args.get('board')  # 这个就是前端传过来的 currentBoardString
        if not board_dp:
            return jsonify({"code": 400, "error": "缺少 board 参数"}), 400

        print(board_dp)

        # # 改变棋盘状态
        # chess_from = board_dp[0] + board_dp[1]
        # chess_to = board_dp[2] + board_dp[3]
        # # 对棋子位置进行处理
        # a.replace(str(chess_from), str(chess_to))

        global  a

        print(a)


        # 2. 使用这个 board_dp 作为输入的东萍棋局状态
        b = invertToFen.changetoFen(a)  # 东萍转 FEN 格式
        b = b + " "
        # 3. 构造 AI 查询参数
        params = {
            "action": "querybest",
            "board": b
        }
        print(f"[DEBUG] 接收到的 board 字符串: {board_dp}")
        print(f"[DEBUG] 转换后的 FEN 格式: {b}")

        # 4. 发送请求给 AI API
        try:
            ai_api_url = api  # 替换为实际的 AI 接口地址
            response = requests.get(ai_api_url, params=params)
            response.raise_for_status()

            res = response.text
            parts = res.split(':')
            print(parts)
            move_part = parts[1] if len(parts) > 1 else None
            if move_part is None:
                response = requests.get("https://www.chessdb.cn/chessdb.php?action=queryall&board="+b)
                res = response.text
                parts = res.split(':')
                move_part = parts[1] if len(parts) > 1 else None

            if move_part is None:
                return jsonify({
                    "code": 400,
                    "data": '9999'
                })

            best_move = movesChange.movesToDP(move_part[0:4])

            print(f"[DEBUG] 接收到的 board 字符串: {board_dp}")
            print(f"[DEBUG] 转换后的 FEN 格式: {b}")
            print(f"[DEBUG] AI 返回的原始结果: {res}")
            print(f"[DEBUG] 最终返回的东萍走法: {best_move}")

            # 5. 返回东萍格式的走法给前端
            return jsonify({
                "code": 200,
                "data": best_move
            })

        except requests.exceptions.RequestException as e:
            return jsonify({"code": 500, "error": str(e)})


if __name__ == '__main__':
    load_model()
    app.run(host='0.0.0.0', port=8080, debug=True)
