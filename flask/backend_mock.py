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
