<template>
  <div id="game-container">
    <div class="game-header">
      <div id="currActiveDisplay" :class="displayMessageClass">{{ currentPlayerText }}</div>
      <button @click="resetGame" class="reset-button">重新开始</button>
    </div>
    <div class="game-layout">
      <ChessBoard
        ref="chessBoardRef"
        :pieces="boardStatePieces"
        :current-player="currentPlayer"
        @piece-moved="handlePlayerMove"
      />
      <div id="moveHistoryPanel">
        <h3>走法记录:</h3>
        <ul ref="moveHistoryUlRef">
          <li v-for="(step, index) in moveHistory" :key="index">{{ step }}</li>
        </ul>
      </div>
    </div>
    <div v-if="gameOverMessage" class="game-over-message">{{ gameOverMessage }}</div>
    <div v-if="isLoadingAI" class="loading-ai">AI 正在思考，请稍候...</div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue';
import ChessBoard from './components/ChessBoard.vue';
import type { Piece, MovedPayload, ChessBoardExposed, AISuggestionResponseSimple } from './types';
import axios from 'axios';

const PIECE_ORDER_BACKEND: string[] = [
  'R_CAR1', 'R_HORSE1', 'R_XIANG1', 'R_SHI1', 'R_SHUAI', 'R_SHI2', 'R_XIANG2', 'R_HORSE2',
  'R_CAR2', 'R_PAO1', 'R_PAO2', 'R_BING1', 'R_BING2', 'R_BING3', 'R_BING4', 'R_BING5',
  'B_CAR1', 'B_HORSE1', 'B_XIANG1', 'B_SHI1', 'B_JIANG', 'B_SHI2', 'B_XIANG2', 'B_HORSE2',
  'B_CAR2', 'B_PAO1', 'B_PAO2', 'B_ZU1', 'B_ZU2', 'B_ZU3', 'B_ZU4', 'B_ZU5'
];

const displayMessageClass = computed(() => {
  if (gameOverMessage.value) return 'status-gameover'; // 你可以为游戏结束也定义一个特殊样式
  if (transientUserMessage.value) {
    if (transientUserMessage.value.includes("错误") || transientUserMessage.value.includes("不合规")) {
      return 'status-error';
    }
    if (transientUserMessage.value.includes("思考")) {
      return 'status-thinking';
    }
  }
  return ''; // 默认无特殊class
});

const boardStatePieces = ref<Piece[]>([]);
const currentPlayer = ref<'red' | 'black'>('red');
const moveHistory = ref<string[]>([]);
const gameOverMessage = ref<string>(''); // 用于真正的游戏结束信息
const transientUserMessage = ref<string>(''); // 用于临时提示用户，例如AI走法不合规
const isLoadingAI = ref<boolean>(false);
const chessBoardRef = ref<ChessBoardExposed | null>(null);
const moveHistoryUlRef = ref<HTMLUListElement | null>(null);

var playerMove : Piece = {
  id: "1",
  isActiveOnBoard: false,
  text: "",
  type: "red",
  originalX : 0,
  originalY : 0,
  x : 0,
  y : 0};

// App.vue
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

const currentPlayerText = computed(() => {
  if (gameOverMessage.value) return `游戏结束: ${gameOverMessage.value}`;
  if (transientUserMessage.value) return transientUserMessage.value; // 优先显示临时信息
  return currentPlayer.value === 'red' ? '红方走棋' : '黑方走棋';
});

function convertPiecesToBoardString(pieces: Piece[]): string {
    let boardArray = Array(32).fill("99");
    pieces.forEach(p => {
        const indexInBackendOrder = PIECE_ORDER_BACKEND.indexOf(p.id);
        if (indexInBackendOrder !== -1) {
            let backendPos = "99"; // 默认为被吃
            if (p.isActiveOnBoard && typeof p.x === 'number' && typeof p.y === 'number' && p.x >= 1 && p.x <= 9 && p.y >= 1 && p.y <= 10) {
                const col = p.x - 1;
                const row = p.y - 1;
                backendPos = col.toString() + row.toString();
            }
            boardArray[indexInBackendOrder] = backendPos;
        } else {
             console.warn(`棋子ID ${p.id} 在后端棋子顺序定义中未找到。生成棋盘字符串时将忽略此棋子。`);
        }
    });
    return boardArray.join('');
}

function initializeGame(): void {
  boardStatePieces.value = [
    // 黑方
    { id: 'B_CAR1', x: 1, y: 1, text: "車", type: "black", isActiveOnBoard: true }, { id: 'B_HORSE1', x: 2, y: 1, text: "馬", type: "black", isActiveOnBoard: true },
    { id: 'B_XIANG1', x: 3, y: 1, text: "象", type: "black", isActiveOnBoard: true }, { id: 'B_SHI1', x: 4, y: 1, text: "士", type: "black", isActiveOnBoard: true },
    { id: 'B_JIANG', x: 5, y: 1, text: "将", type: "black", isActiveOnBoard: true }, { id: 'B_SHI2', x: 6, y: 1, text: "士", type: "black", isActiveOnBoard: true },
    { id: 'B_XIANG2', x: 7, y: 1, text: "象", type: "black", isActiveOnBoard: true }, { id: 'B_HORSE2', x: 8, y: 1, text: "馬", type: "black", isActiveOnBoard: true },
    { id: 'B_CAR2', x: 9, y: 1, text: "車", type: "black", isActiveOnBoard: true },
    { id: 'B_PAO1', x: 2, y: 3, text: "炮", type: "black", isActiveOnBoard: true }, { id: 'B_PAO2', x: 8, y: 3, text: "炮", type: "black", isActiveOnBoard: true },
    { id: 'B_ZU1', x: 1, y: 4, text: "卒", type: "black", isActiveOnBoard: true }, { id: 'B_ZU2', x: 3, y: 4, text: "卒", type: "black", isActiveOnBoard: true },
    { id: 'B_ZU3', x: 5, y: 4, text: "卒", type: "black", isActiveOnBoard: true }, { id: 'B_ZU4', x: 7, y: 4, text: "卒", type: "black", isActiveOnBoard: true },
    { id: 'B_ZU5', x: 9, y: 4, text: "卒", type: "black", isActiveOnBoard: true },
    // 红方
    { id: 'R_CAR1', x: 1, y: 10, text: "車", type: "red", isActiveOnBoard: true }, { id: 'R_HORSE1', x: 2, y: 10, text: "馬", type: "red", isActiveOnBoard: true },
    { id: 'R_XIANG1', x: 3, y: 10, text: "相", type: "red", isActiveOnBoard: true }, { id: 'R_SHI1', x: 4, y: 10, text: "仕", type: "red", isActiveOnBoard: true },
    { id: 'R_SHUAI', x: 5, y: 10, text: "帅", type: "red", isActiveOnBoard: true }, { id: 'R_SHI2', x: 6, y: 10, text: "仕", type: "red", isActiveOnBoard: true },
    { id: 'R_XIANG2', x: 7, y: 10, text: "相", type: "red", isActiveOnBoard: true }, { id: 'R_HORSE2', x: 8, y: 10, text: "馬", type: "red", isActiveOnBoard: true },
    { id: 'R_CAR2', x: 9, y: 10, text: "車", type: "red", isActiveOnBoard: true },
    { id: 'R_PAO1', x: 2, y: 8, text: "炮", type: "red", isActiveOnBoard: true }, { id: 'R_PAO2', x: 8, y: 8, text: "炮", type: "red", isActiveOnBoard: true },
    { id: 'R_BING1', x: 1, y: 7, text: "兵", type: "red", isActiveOnBoard: true }, { id: 'R_BING2', x: 3, y: 7, text: "兵", type: "red", isActiveOnBoard: true },
    { id: 'R_BING3', x: 5, y: 7, text: "兵", type: "red", isActiveOnBoard: true }, { id: 'R_BING4', x: 7, y: 7, text: "兵", type: "red", isActiveOnBoard: true },
    { id: 'R_BING5', x: 9, y: 7, text: "兵", type: "red", isActiveOnBoard: true },
  ];
  currentPlayer.value = 'red';
  moveHistory.value = [];
  gameOverMessage.value = '';
  transientUserMessage.value = ''; // 初始化临时信息
  isLoadingAI.value = false;
  console.log("游戏已初始化");
}

async function resetGame(){
  initializeGame();
  chessBoardRef.value?.resetSelectionAndRedraw();
  await axios.get<AISuggestionResponseSimple>(`${API_BASE_URL}/suggest/restart`);
  console.log("游戏已重置");
}

function scrollToBottomMoveHistory(): void {
    nextTick(() => {
        if (moveHistoryUlRef.value) {
            moveHistoryUlRef.value.scrollTop = moveHistoryUlRef.value.scrollHeight;
        }
    });
}

function recordMove(piece: Piece, toX: number, toY: number, captured: Piece | null): void {
  const action = captured ? "吃掉" : "移动到";
  const capturedText = captured ? ` (${captured.text} 在 ${captured.x},${captured.y})` : "";
  const originalPosText = (typeof piece.originalX === 'number' && typeof piece.originalY === 'number')
    ? `(${piece.originalX},${piece.originalY})`
    : `(未知起点)`; // 如果没有原始位置信息

  moveHistory.value.push(
    `${moveHistory.value.length + 1}. ${piece.type === 'red' ? '红' : '黑'}${piece.text} 从 ${originalPosText} ${action} (${toX},${toY})${capturedText}`
  );
  scrollToBottomMoveHistory();
}

// function gameOver(winner: 'red' | 'black'): void {
//   gameOverMessage.value = `${winner === 'red' ? '红方' : '黑方'} 获胜! 游戏结束。`;
//   console.log(`${winner === 'red' ? '红方' : '黑方'} 获胜!`);
// }

function setGameOver(winner: 'red' | 'black' | 'draw', reason?: string): void {
  if (winner === 'draw') {
    gameOverMessage.value = reason || "和棋!";
  } else {
    gameOverMessage.value = `${winner === 'red' ? '红方' : '黑方'} 获胜! ${reason || ''}`;
  }
  console.log(`游戏结束: ${gameOverMessage.value}`);
  // 可以在这里做更多游戏结束后的处理，比如禁用棋盘
}

function updateNowPlayerMove(originalMovex?:number, originalMovey?:number,tox?:number,toy?:number): void{
  playerMove.originalX = originalMovex;
  playerMove.originalY = originalMovey;
  playerMove.x = tox;
  playerMove.y = toy;
}

function getNowPlayerMove(nowPlayerMove: Piece):string{
  let result = '';
  if (nowPlayerMove.originalX){
    result = result + (nowPlayerMove.originalX-1).toString();
  }
  if (nowPlayerMove.originalY){
    result = result + (nowPlayerMove.originalY-1).toString();
  }
  if (nowPlayerMove.x){
    result = result + (nowPlayerMove.x-1).toString();
  }
  if (nowPlayerMove.y){
    result = result + (nowPlayerMove.y-1).toString();
  }
  if (result.length!=4)
    console.log("当前玩家移动数据获取失败！");
  return result;
}

async function applyBlackMove(moveString: string) {
    const response = await axios.get<AISuggestionResponseSimple>(
        `${API_BASE_URL}/suggest/current_apply_ai_step?move=${moveString}`
    );
    return
}

function handlePlayerMove(payload: MovedPayload): void {
  // 只有在没有游戏结束信息，且AI不在思考时才处理玩家移动
  if (gameOverMessage.value || isLoadingAI.value) {
      if (gameOverMessage.value) console.log("游戏已结束，无法移动。");
      if (isLoadingAI.value) console.log("AI正在思考，请稍候。");
      return;
  }
  transientUserMessage.value = ''; // 清除之前的临时提示

  const { movedPiece, toX, toY, capturedPiece } = payload;
  updateNowPlayerMove(movedPiece.x,movedPiece.y,toX,toY);
  console.log(`玩家 (${movedPiece.type}) 移动 ${movedPiece.text} 从 (${movedPiece.x}, ${movedPiece.y}) 到 (${toX}, ${toY})`);

  const pieceToUpdateInState = boardStatePieces.value.find(p => p.id === movedPiece.id);
  if (!pieceToUpdateInState) {
    console.error("严重错误：尝试移动一个在 boardStatePieces 中找不到的棋子:", movedPiece);
    transientUserMessage.value = "内部错误，请重试。"; // 给用户一个通用错误提示
    return;
  }

  const originalX = pieceToUpdateInState.x;
  const originalY = pieceToUpdateInState.y;
  pieceToUpdateInState.x = toX;
  pieceToUpdateInState.y = toY;

  let actualCapturedPieceStateForRecord: Piece | null = null;
  if (capturedPiece) {
    actualCapturedPieceStateForRecord = { ...capturedPiece }; // 拷贝被吃棋子的状态
    const capturedIndexInState = boardStatePieces.value.findIndex(p => p.id === capturedPiece.id);
    if (capturedIndexInState > -1) {
        boardStatePieces.value[capturedIndexInState].isActiveOnBoard = false;
        boardStatePieces.value[capturedIndexInState].x = undefined;
        boardStatePieces.value[capturedIndexInState].y = undefined;
        console.log(`棋子 ${capturedPiece.text} (${capturedPiece.type}) 在 (${actualCapturedPieceStateForRecord.x}, ${actualCapturedPieceStateForRecord.y}) 被吃掉`);
        if (capturedPiece.text === '将' || capturedPiece.text === '帅') {
            recordMove({ ...pieceToUpdateInState, originalX, originalY }, toX, toY, actualCapturedPieceStateForRecord);
            setGameOver(movedPiece.type, "将死对方"); // 玩家获胜
            return; // 游戏结束，不请求AI走棋
        }
    } else {
        console.error("严重错误：尝试标记一个在 boardStatePieces 中找不到的被吃棋子:", capturedPiece);
        // 即使找不到，也尝试记录，但可能信息不全
    }
  }
  recordMove({ ...pieceToUpdateInState, originalX, originalY }, toX, toY, actualCapturedPieceStateForRecord);

  // 切换到AI行棋方
  currentPlayer.value = currentPlayer.value === 'red' ? 'black' : 'red';

  if (!gameOverMessage.value) { // 仅当游戏未结束时请求AI走棋
      console.log(`轮到 ${currentPlayer.value} (AI) 走棋`);
      requestAIMove();
  }
}



async function aiWrongToApi() {
    const currentBoardString = getNowPlayerMove(playerMove);
    const requestStartTime = Date.now();
    const response = await getApiMove(currentBoardString);
    console.log("收到Api响应:", response.data);

    // 计算后端响应时间
    const responseTime = Date.now() - requestStartTime;
    // 设置最小延迟时间，确保 AI 思考时间至少为 2 秒
    const minDelay = 2000;
    let actualDelay = 0;

    // 检查响应是否成功且包含有效的走法数据
    if (response.data.code === 200 && typeof response.data.data === 'string' && response.data.data.length > 0) {
        const aiMoveString = response.data.data;

        // 如果后端响应时间小于最小延迟时间，计算需要额外延迟的时间
        if (responseTime < minDelay) {
            actualDelay = minDelay - responseTime;
        }
        console.log(`后端响应耗时: ${responseTime}ms, 将额外延迟: ${actualDelay}ms`);

        // 如果需要额外延迟，更新提示信息
        if (actualDelay > 0) {
            transientUserMessage.value = "AI 正在思考...";
        }

        // 使用 setTimeout 实现延迟，之后应用 AI 的走法
        setTimeout(() => {
            // transientUserMessage.value = ''; // 在 applyAIMove 开始时清除
            applyAIMove(aiMoveString); // 延迟后应用 AI 走法
        }, actualDelay);
        return
    }else if (response.data.code === 400 && typeof response.data.data === 'string' && response.data.data.length > 0){
        transientUserMessage.value = `AI从未看见过如此逆天的对局，轮到您走棋。`;
        currentPlayer.value = currentPlayer.value === 'red' ? 'black' : 'red'; // 交还行棋权给人类
        isLoadingAI.value = false;
        return
    }
}
async function requestAIMove(): Promise<void> {
  // 检查游戏是否已经结束，如果游戏结束，AI不再走棋
  if (gameOverMessage.value) return;  

  // 设置 AI 正在思考的状态，防止重复请求
  isLoadingAI.value = true;
  // 清除之前的临时提示信息
  transientUserMessage.value = ''; 

  // 获取当前棋盘状态（这里假设有函数 getNowPlayerMove 来获取当前玩家的走法信息）
  const currentBoardString = getNowPlayerMove(playerMove);

  // 打印发送给 AI 的棋盘状态和当前行棋方，方便调试
  console.log("发送给AI的棋盘状态 (status):", currentBoardString, "AI行棋方:", currentPlayer.value);

  // 记录请求开始时间，用于计算响应时间
  const requestStartTime = Date.now();

  try {
    // 向后端 API 发送请求，获取 AI 的走法建议
     // 使用 getApiMove 替换原来的 axios.get
    const response = await axios.get<AISuggestionResponseSimple>(`${API_BASE_URL}/suggest/${currentBoardString}`);
    console.log("收到AI响应:", response.data);

    // 计算后端响应时间
    const responseTime = Date.now() - requestStartTime;
    // 设置最小延迟时间，确保 AI 思考时间至少为 2 秒
    const minDelay = 2000; 
    let actualDelay = 0;

    // 检查响应是否成功且包含有效的走法数据
    if (response.data.code === 200 && typeof response.data.data === 'string' && response.data.data.length > 0) {
      const aiMoveString = response.data.data;

      // 如果后端响应时间小于最小延迟时间，计算需要额外延迟的时间
      if (responseTime < minDelay) {
        actualDelay = minDelay - responseTime;
      }
      console.log(`后端响应耗时: ${responseTime}ms, 将额外延迟: ${actualDelay}ms`);

      // 如果需要额外延迟，更新提示信息
      if (actualDelay > 0) {
        transientUserMessage.value = "AI 正在思考..."; 
      }

      // 使用 setTimeout 实现延迟，之后应用 AI 的走法
      setTimeout(() => {
        // transientUserMessage.value = ''; // 在 applyAIMove 开始时清除
        applyAIMove(aiMoveString); // 延迟后应用 AI 走法
      }, actualDelay);

    } else {
        aiWrongToApi()
            // 如果 AI 未能返回有效走法或后端报错
            // console.error("AI未能返回有效走法或后端报错。响应:", response.data);
            // 提示用户 AI 无棋可走，并将行棋权交还给人类
            // transientUserMessage.value = response.data.message || "AI无棋可走，轮到您走棋。";
            // currentPlayer.value = currentPlayer.value === 'red' ? 'black' : 'red';
            // // 确保解除 AI 加载状态
            // isLoadingAI.value = false;
            // console.log(`AI无法走棋，已将行棋权交还给 ${currentPlayer.value} (人类玩家)`);
    }
  } catch (error) {
        aiWrongToApi()
          // 捕获请求错误
          // console.error("请求AI走法时发生错误:", error);
          // // 提示用户请求失败，并将行棋权交还给人类
          // transientUserMessage.value = "请求AI走法失败，请检查网络或后端服务。轮到您走棋。";
          // currentPlayer.value = currentPlayer.value === 'red' ? 'black' : 'red';
          // // 确保解除 AI 加载状态
          // isLoadingAI.value = false;
      }
  // 注意：isLoadingAI.value 的解除主要在 setTimeout 的回调 (applyAIMove 内部) 或错误处理中
}

/**
 * 向后端请求 AI 的最佳走法建议。
 *
 * @param currentBoardString - 当前棋盘状态的字符串表示，用于传给后端进行 AI 分析。
 * @returns 返回一个 Promise，解析为 AISuggestionResponseSimple 类型的数据，包含 AI 建议的走法。
 * @throws 如果请求失败或网络出错，会抛出错误。
 */
async function getApiMove(currentBoardString: string) {
  try {
    // 发起 GET 请求到 `/suggest/getApiMove` 接口，并将当前棋盘状态作为查询参数传递
    const response = await axios.get<AISuggestionResponseSimple>(
      `${API_BASE_URL}/suggest/getApiMove?board=${currentBoardString}`
    );

    // 打印从后端获取的响应数据，方便调试查看 AI 返回的内容
    console.log("收到 getApiMove 响应:", response.data);
    // 返回响应中的 data 字段，其中通常包含 AI 计算出的最佳走法 moveString
    return response;
  } catch (error) {
    // 捕获请求过程中的异常（如网络问题、接口报错等）
    console.error("调用 getApiMove 失败:", error);

    // 抛出错误以便上层函数可以捕获并做相应处理（例如提示用户或重试）
    throw error;
  }
}



async function applyAIMove(moveString: string): Promise<void> {
  // 首先清除可能存在的"AI正在思考..."等临时消息
  transientUserMessage.value = '';

  // 如果在等待期间游戏已经结束了（不太可能，但作为防御）
  if (gameOverMessage.value) {
      isLoadingAI.value = false;
      return;
  }

  const fromCol = parseInt(moveString[0]);
  const fromRow = parseInt(moveString[1]);
  const toCol = parseInt(moveString[2]);
  const toRow = parseInt(moveString[3]);

  const fromX = fromCol + 1;
  const fromY = fromRow + 1;
  const toX_ai = toCol + 1;
  const toY_ai = toRow + 1;

  const aiPieceToMoveFromState = boardStatePieces.value.find(p =>
    p.x === fromX && p.y === fromY && p.isActiveOnBoard && p.type === currentPlayer.value // currentPlayer 此时应该是 AI
  );

  if (!aiPieceToMoveFromState) {
    // console.error(`AI尝试移动一个不存在或非己方的棋子: 从(${fromX},${fromY}) 移动 ${moveString}, AI方: ${currentPlayer.value}`);
    // transientUserMessage.value = `AI内部错误 (棋子 ${fromX},${fromY} 无效)，轮到您走棋。`;
    // currentPlayer.value = currentPlayer.value === 'red' ? 'black' : 'red'; // 交还行棋权给人类
    // isLoadingAI.value = false;
      aiWrongToApi();
    return;
  }

  // 【前端校验 AI 的走法】
  if (chessBoardRef.value && !chessBoardRef.value.validateMove({ ...aiPieceToMoveFromState }, toX_ai, toY_ai)) {
    // console.error(`AI 走法 (${aiPieceToMoveFromState.text} 从 (${fromX},${fromY}) 到 (${toX_ai},${toY_ai})) 不符合规则!`);
    // transientUserMessage.value = `AI走法不合规 (${aiPieceToMoveFromState.text}: ${fromX},${fromY} -> ${toX_ai},${toY_ai})，轮到您走棋。`;
    // currentPlayer.value = currentPlayer.value === 'red' ? 'black' : 'red'; // 交还行棋权给人类
    // isLoadingAI.value = false;
      aiWrongToApi();
    return;
  }
  // 【校验结束】
    applyBlackMove(moveString);
  // 记录AI移动前的位置
  const originalX_ai = aiPieceToMoveFromState.x;
  const originalY_ai = aiPieceToMoveFromState.y;

  let capturedByAIOriginalState: Piece | null = null;
  const targetPiecePotentiallyCaptured = boardStatePieces.value.find(p =>
    p.x === toX_ai && p.y === toY_ai && p.isActiveOnBoard
  );

  if (targetPiecePotentiallyCaptured) {
    if (targetPiecePotentiallyCaptured.type === aiPieceToMoveFromState.type) {
      console.error("AI尝试吃己方棋子:", toX_ai, toY_ai, moveString);
      transientUserMessage.value = `AI走法错误 (吃己方棋子)，轮到您走棋。`;
      currentPlayer.value = currentPlayer.value === 'red' ? 'black' : 'red';
      isLoadingAI.value = false;
      return;
    }
    capturedByAIOriginalState = { ...targetPiecePotentiallyCaptured }; // 拷贝被吃棋子的状态

    const capturedIndexInState = boardStatePieces.value.findIndex(p => p.id === targetPiecePotentiallyCaptured.id);
    if (capturedIndexInState > -1) {
        boardStatePieces.value[capturedIndexInState].isActiveOnBoard = false;
        boardStatePieces.value[capturedIndexInState].x = undefined;
        boardStatePieces.value[capturedIndexInState].y = undefined;
        console.log(`AI棋子 ${aiPieceToMoveFromState.text} 吃掉 ${capturedByAIOriginalState.text} 在 (${capturedByAIOriginalState.x}, ${capturedByAIOriginalState.y})`);

        if (capturedByAIOriginalState.text === '将' || capturedByAIOriginalState.text === '帅') {
          // 记录最后一步吃将/帅的棋
          recordMove({ ...aiPieceToMoveFromState, originalX: originalX_ai, originalY: originalY_ai }, toX_ai, toY_ai, capturedByAIOriginalState);
          setGameOver(aiPieceToMoveFromState.type, "将死对方"); // AI 获胜
          isLoadingAI.value = false;
          return; // 游戏结束
        }
    } else {
        console.error("严重错误：AI吃子时，在boardStatePieces中找不到被吃棋子:", targetPiecePotentiallyCaptured);
    }
  }

  // 更新AI棋子在 boardStatePieces 中的位置
  aiPieceToMoveFromState.x = toX_ai;
  aiPieceToMoveFromState.y = toY_ai;
  console.log(`AI移动 ${aiPieceToMoveFromState.text} 到 (${toX_ai}, ${toY_ai})`);

  // 记录AI的走法
  recordMove({ ...aiPieceToMoveFromState, originalX: originalX_ai, originalY: originalY_ai }, toX_ai, toY_ai, capturedByAIOriginalState);

  // 切换回人类玩家行棋
  currentPlayer.value = currentPlayer.value === 'red' ? 'black' : 'red';
  if (!gameOverMessage.value) { // 只有游戏未结束才提示轮到玩家
    console.log(`轮到 ${currentPlayer.value} (人类玩家) 走棋`);
  }
  isLoadingAI.value = false; // AI 成功走棋后，解除加载状态
}

onMounted(() => {
  initializeGame();
});

watch(gameOverMessage, (newMessage) => {
    if (newMessage) {
        console.log("游戏结束信息:", newMessage);
        // 可以在 ChessBoard 组件中实现禁用交互的逻辑
        // chessBoardRef.value?.disableInteraction();
    }
});
</script>

<style scoped>
#game-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 800px;
  margin: 20px auto;
  font-family: 'Arial', 'Helvetica Neue', Helvetica, sans-serif; /* 更现代的字体 */
  color: #333; /* 基础文字颜色 */
}

.game-header {
  display: flex;
  justify-content: space-between; /* 让提示文本和按钮分布在两侧 */
  align-items: center;
  width: 100%;
  max-width: 520px; /* 稍微比棋盘宽一点，或者根据棋盘调整 */
  margin-bottom: 15px;
  padding: 0 10px; /* 给左右一些内边距 */
  box-sizing: border-box;
}

#currActiveDisplay {
  font-size: 18px; /* 调整大小 */
  font-weight: bold;
  color: #2c3e50; /* 深蓝灰色，更醒目 */
  padding: 5px 10px;
  background-color: #e9ecef; /* 淡灰色背景 */
  border-radius: 4px;
  text-align: left; /* 左对齐 */
  flex-grow: 1; /* 占据剩余空间，将按钮推到右边 */
  margin-right: 15px; /* 与按钮的间距 */
  /* 为了防止长文本导致按钮换行，可以设置最大宽度和文本溢出处理 */
  max-width: calc(100% - 120px); /* 假设按钮宽度约100px + 间距20px */
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap; /* 强制不换行，配合 ellipsis */
  min-height: 38px; /* 与按钮高度匹配，确保垂直对齐 */
  display: flex; /* 用于垂直居中文本 */
  align-items: center; /* 垂直居中文本 */
}
/* 针对不同类型的提示信息可以有不同颜色 */
#currActiveDisplay.status-error { /* 当 transientUserMessage 包含错误时添加此类 */
    color: #d9534f; /* 错误红色 */
    background-color: #f2dede;
    border: 1px solid #ebccd1;
}
#currActiveDisplay.status-thinking { /* AI 思考时 */
    color: #5bc0de; /* 信息蓝色 */
    background-color: #d9edf7;
    border: 1px solid #bce8f1;
}


.reset-button {
  padding: 10px 18px; /* 增加内边距 */
  font-size: 15px;
  font-weight: bold;
  color: white;
  background-color: #5cb85c; /* 绿色背景 */
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.2s ease-in-out;
  white-space: nowrap; /* 防止按钮文字换行 */
}

.reset-button:hover {
  background-color: #4cae4c; /* 悬停时深一点的绿色 */
}

.reset-button:active {
  background-color: #449d44; /* 点击时更深 */
}


.game-layout {
  display: flex;
  flex-direction: row;
  justify-content: center;
  width: 100%;
}

#moveHistoryPanel {
  width: 220px; /* 稍微加宽 */
  margin-left: 25px; /* 增加与棋盘的间距 */
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 5px; /* 圆角 */
  height: 550px;
  overflow-y: auto;
  font-size: 13px; /* 调整字体大小 */
  background-color: #fdfdfd;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05); /* 轻微阴影 */
}

#moveHistoryPanel h3 {
  margin-top: 0;
  font-size: 16px; /* 调整标题大小 */
  text-align: center;
  margin-bottom: 12px;
  color: #4A5568; /* 较深的灰色 */
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 8px;
}

#moveHistoryPanel ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

#moveHistoryPanel li {
  padding: 5px 3px;
  border-bottom: 1px dotted #e2e8f0; /* 更淡的分隔线 */
  line-height: 1.5;
  color: #4A5568;
}
#moveHistoryPanel li:nth-child(odd) { /* 奇偶行不同背景色 */
    background-color: #f7fafc;
}

#moveHistoryPanel li:last-child {
  border-bottom: none;
}

.game-over-message {
  margin-top: 20px;
  padding: 12px 20px;
  background-color: #fff3cd; /* 温和的黄色背景 */
  border: 1px solid #ffeeba;
  color: #856404; /* 暗黄色文字 */
  font-weight: bold;
  border-radius: 5px;
  text-align: center;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.loading-ai {
  margin-top: 15px;
  color: #4a5568; /* 深灰色 */
  font-style: italic;
  padding: 8px 12px;
  background-color: #f0f4f8; /* 淡蓝色背景 */
  border-radius: 4px;
  border: 1px solid #d3dce6;
}
</style>