import os
import pickle
import numpy as np
import sys
from tqdm import tqdm
from utils.data_loader import load_and_process_data
from model.chess_model import ChessModel
from utils.data_loader import get_test_file

def train_model():
    # 数据路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, 'data')
    json_file_path = os.path.join(data_dir, get_test_file())

    # 加载和预处理数据
    processed_data = load_and_process_data(json_file_path)

    if not processed_data:
        print("No valid data to train on.")
        return

    # 初始化模型
    model = ChessModel(model_type='winrate')  # 选择模型类型：'freq' 或 'winrate'

    # 训练模型
    model.train(processed_data)

    # 保存训练好的模型
    model_save_path = os.path.join(current_dir,  'model', 'chess_ai_model.pkl')
    model.save(model_save_path)

    print(f"模型训练完成，并已保存到 {model_save_path}")


if __name__ == "__main__":
    train_model()