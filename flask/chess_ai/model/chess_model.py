import pickle
from collections import defaultdict
import numpy as np
import random
from tqdm import tqdm
from chess_ai.utils.board_utils import generate_legal_moves  # 新增函数


class ChessModel:
    def __init__(self, model_type='freq'):
        self.model_type = model_type
        self.move_stats = defaultdict(lambda: defaultdict(int))
        self.win_stats = defaultdict(lambda: defaultdict(list))

    def augment_board_state(board_state):
        """通过对称变换增强棋盘状态"""
        augmented = []

        # 原始状态
        augmented.append(board_state)

        # 水平翻转
        flipped = ""
        for i in range(0, len(board_state), 2):
            pos_str = board_state[i:i + 2]
            if pos_str == "99":
                flipped += "99"
            else:
                x, y = int(pos_str[0]), int(pos_str[1])
                flipped += f"{8 - x}{y}"  # 水平翻转
        augmented.append(flipped)

        return augmented

    def train(self, games):
        """训练模型"""
        print(f"Training {self.model_type} model with {len(games)} games...")

        for game in tqdm(games, desc="Processing games"):
            result = game['result']
            boards = game['board_states']
            moves = game['moves']

            # 红方胜率: 1=红胜, 0=黑胜, 0.5=平局
            outcome = 1 if result == 'red_win' else 0 if result == 'black_win' else 0.5

            for i, move in enumerate(moves):
                board_state = boards[i]

                # 使用数据增强
                for augmented_state in self.augment_board_state():
                    self.move_stats[augmented_state][move] += 1
                    self.win_stats[augmented_state][move].append(outcome)

                # 记录走法频率
                self.move_stats[board_state][move] += 1

                # 记录胜率
                self.win_stats[board_state][move].append(outcome)

    def predict(self, board_state):
        """预测下一步走法"""
        # 首先尝试统计模型
        if board_state in self.move_stats:
            if self.model_type == 'freq':
                moves = self.move_stats[board_state]
                return max(moves, key=moves.get)
            elif self.model_type == 'winrate':
                best_move, best_winrate = None, -1
                for move, outcomes in self.win_stats[board_state].items():
                    winrate = np.mean(outcomes)
                    if winrate > best_winrate:
                        best_winrate = winrate
                        best_move = move
                return best_move

        # 如果统计模型中没有记录，使用基于规则的回退策略
        return self.fallback_strategy(board_state)

    def fallback_strategy(self, board_state):
        """基于规则的回退策略"""
        # 1. 尝试生成所有合法走法并随机选择
        legal_moves = generate_legal_moves(board_state)
        if legal_moves:
            return random.choice(legal_moves)

        # 2. 极端情况：没有合法走法（将死局面）
        return None

    def save(self, filename):
        """保存模型"""
        with open(filename, 'wb') as f:
            pickle.dump({
                'model_type': self.model_type,
                'move_stats': dict(self.move_stats),
                'win_stats': dict(self.win_stats)
            }, f)

    @classmethod
    def load(cls, filename):
        """加载模型"""
        with open(filename, 'rb') as f:
            data = pickle.load(f)
            model = cls(data['model_type'])
            model.move_stats = defaultdict(lambda: defaultdict(int),
                                           {k: defaultdict(int, v) for k, v in data['move_stats'].items()})
            model.win_stats = defaultdict(lambda: defaultdict(list),
                                          {k: defaultdict(list, v) for k, v in data['win_stats'].items()})
            return model