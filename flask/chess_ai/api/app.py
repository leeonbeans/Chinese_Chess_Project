from flask import Flask, request, jsonify
from model.chess_model import ChessModel
import os
import sys

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)

# 加载模型
MODEL_TYPE = os.getenv('MODEL_TYPE', 'winrate')  # 默认使用胜率模型
if MODEL_TYPE == 'freq':
    model = ChessModel.load('../model/freq_model.pkl')
else:
    model = ChessModel.load('../model/winrate_model.pkl')

@app.route('/suggest/<board_state>', methods=['GET'])
def suggest_move(board_state):
    """API: 获取机器走法建议"""
    move = model.predict(board_state)
    if not move:
        return jsonify({"error": "No move found for this board state"}), 404
    return jsonify({"move": move})

@app.route('/move', methods=['GET'])
def make_move():
    """API: 执行人类走法"""
    board_state = request.args.get('board')
    action = request.args.get('action')
    
    if not board_state or not action:
        return jsonify({"error": "Missing board or action parameter"}), 400
    
    try:
        # 实际应用中应在此添加走法合法性检查
        from utils.board_utils import apply_move
        new_board = apply_move(board_state, action)
        return jsonify({"new_board": new_board})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/memorize', methods=['POST'])
def memorize_move():
    """API: 学习人类走法（可选）"""
    data = request.json
    board = data.get('board')
    move = data.get('move')
    result = data.get('result')  # 可选：该走法的结果
    
    # 在实际应用中，这里会将走法添加到训练数据中
    return jsonify({"status": "learned", "move": move})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)