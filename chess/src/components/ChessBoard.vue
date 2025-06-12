<template>
  <canvas ref="chessCanvasRef" :width="canvasWidth" :height="canvasHeight" @mousedown="handleMouseDown"></canvas>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import type { Piece, Point } from '../types';

const props = defineProps<{
  pieces: Piece[];
  currentPlayer: 'red' | 'black';
}>();

const emit = defineEmits<{
  (e: 'piece-moved', payload: { movedPiece: Piece; toX: number; toY: number; capturedPiece: Piece | null }): void;
}>();

const chessCanvasRef = ref<HTMLCanvasElement | null>(null);
const ctx = ref<CanvasRenderingContext2D | null>(null);

const chunk = 50;
const radius = 23;
const candidateCircleR = 5;

const canvasWidth = chunk * 10; // 棋盘宽度 (9列 + 边距)
const canvasHeight = chunk * 11; // 棋盘高度 (10行 + 边距)

const selectedPiece = ref<Piece | null>(null);
const candidateMoves = ref<Point[]>([]);

const text_arr_cols_chinese: string[] = ["九", "八", "七", "六", "五", "四", "三", "二", "一"]; // 红方视角（底部）列名

onMounted(() => {
  if (chessCanvasRef.value) {
    ctx.value = chessCanvasRef.value.getContext('2d');
    redraw();
    console.log("棋盘画布已初始化");
  }
});

watch(() => props.pieces, () => { redraw(); }, { deep: true });
watch(() => props.currentPlayer, () => {
    // 如果行棋方改变（例如AI走完后），可能需要清除之前的选择
    if (selectedPiece.value && selectedPiece.value.type !== props.currentPlayer) {
        // resetSelectionInternal(); // 这通常由父组件驱动，或在此处处理
    }
    redraw();
});


function redraw(): void {
  if (!ctx.value || !chessCanvasRef.value) return;
  const context = ctx.value;
  context.clearRect(0, 0, chessCanvasRef.value.width, chessCanvasRef.value.height);
  drawBoardBackground(context);
  drawAllPieces(context);
  if (selectedPiece.value) {
    drawSelectedPieceHighlight(context, selectedPiece.value);
    drawCandidateMoveMarkers(context);
  }
}

function drawBoardBackground(context: CanvasRenderingContext2D): void {
    const lineWidth = 1; // 假设棋盘线的宽度为1

    for (let i = 1; i <= 10; i++) drawLine(context, 1, i, 9, i, lineWidth); // 横线
    for (let i = 1; i <= 9; i++) drawLine(context, i, 1, i, 10, lineWidth); // 竖线

    // 清除河道区域，从第5条线的正下方到第6条线的正上方
    // yStart 是第5条线的 y 坐标 + 线宽的一半
    // yEnd 是第6条线的 y 坐标 - 线宽的一半
    // height 是 yEnd - yStart
    const yRiverStart = 5 * chunk + lineWidth / 2;
    const riverHeight = chunk - lineWidth; // 河道的高度大约是一个格子减去两条线的宽度

    // xStart 从第1列右边到第9列左边
    const xRiverStart = 1 * chunk + lineWidth / 2;
    const riverWidth = 8 * chunk - lineWidth; // (9-1)*chunk - lineWidth

    context.clearRect(xRiverStart, yRiverStart, riverWidth, riverHeight);

    drawSpecialMarkers(context);
    drawDiagonalLinesForPalace(context);
    drawBoardText(context); // 文字应该在这个清除之后绘制
}

function drawLine(context: CanvasRenderingContext2D, x0: number, y0: number, x1: number, y1: number, lw: number = 1): void {
    const cX0 = x0 * chunk; const cY0 = y0 * chunk;
    const cX1 = x1 * chunk; const cY1 = y1 * chunk;
    context.beginPath(); context.strokeStyle = "#000"; context.lineWidth = lw;
    context.moveTo(cX0, cY0); context.lineTo(cX1, cY1);
    context.stroke(); context.closePath();
}

function drawSpecialMarkers(context: CanvasRenderingContext2D): void {
    const positions: Point[] = [
        {x:2,y:3}, {x:8,y:3}, {x:1,y:4}, {x:3,y:4}, {x:5,y:4}, {x:7,y:4}, {x:9,y:4},
        {x:2,y:8}, {x:8,y:8}, {x:1,y:7}, {x:3,y:7}, {x:5,y:7}, {x:7,y:7}, {x:9,y:7}
    ];
    positions.forEach(pos => drawSingleMarker(context, pos.x, pos.y));
}
function drawSingleMarker(context: CanvasRenderingContext2D, x0: number, y0: number): void {
    const cX = x0 * chunk; const cY = y0 * chunk;
    context.beginPath(); context.strokeStyle = "#000"; context.lineWidth = 1;
    const d = 5; const l = 10;
    if (x0 !== 1) {
        context.moveTo(cX - d, cY - l); context.lineTo(cX - d, cY - d); context.lineTo(cX - l, cY - d);
        context.moveTo(cX - d, cY + l); context.lineTo(cX - d, cY + d); context.lineTo(cX - l, cY + d);
    }
    if (x0 !== 9) {
        context.moveTo(cX + d, cY - l); context.lineTo(cX + d, cY - d); context.lineTo(cX + l, cY - d);
        context.moveTo(cX + d, cY + l); context.lineTo(cX + d, cY + d); context.lineTo(cX + l, cY + d);
    }
    context.stroke(); context.closePath();
}

function drawDiagonalLinesForPalace(context: CanvasRenderingContext2D): void {
    drawLine(context, 4, 1, 6, 3, 0.5); drawLine(context, 4, 3, 6, 1, 0.5);
    drawLine(context, 4, 8, 6, 10, 0.5); drawLine(context, 4, 10, 6, 8, 0.5);
}

function drawBoardText(context: CanvasRenderingContext2D): void {
    context.font = `bold ${chunk * 0.55}px Courier New`;
    context.fillStyle = "#000"; context.textAlign = "center";
    // y 坐标应该是 5.5 * chunk (河道中间)
    const riverTextY = 5.5 * chunk + (chunk * 0.55 * 0.3); // 稍微调整基线

    context.fillText("楚 河", chunk * 3, riverTextY); // X 坐标大致在 2-4 列之间
    context.fillText("漢 界", chunk * 7, riverTextY); // X 坐标大致在 6-8 列之间

    context.font = `${chunk * 0.28}px Courier New`;
    for (let i = 0; i < 9; i++) {
        // 顶部数字 (1-9 from left to right)
        context.fillText((i + 1).toString(), chunk * (i + 1), chunk * 0.7);
        // 底部中文数字 (九-一 from left to right)
        context.fillText(text_arr_cols_chinese[i], chunk * (i + 1), chunk * 10 + chunk * 0.7); // 原来是 8-i，应该是 i
    }
}

function drawAllPieces(context: CanvasRenderingContext2D): void {
  props.pieces.forEach(piece => {
    if (piece.isActiveOnBoard && typeof piece.x === 'number' && typeof piece.y === 'number') {
        drawSinglePiece(context, piece);
    }
  });
}

function drawSinglePiece(context: CanvasRenderingContext2D, piece: Piece): void {
    if (typeof piece.x !== 'number' || typeof piece.y !== 'number') return;
    const pColor = piece.type === 'red' ? '#f00' : '#000'; const pBgColor = '#fff';
    context.beginPath(); context.fillStyle = pBgColor; context.strokeStyle = pColor;
    context.lineWidth = 2;
    context.arc(piece.x * chunk, piece.y * chunk, radius, 0, Math.PI * 2, true);
    context.closePath(); context.fill(); context.stroke();
    context.font = `bold ${chunk * 0.65}px Courier New`; // 调整大小
    context.fillStyle = pColor; context.textAlign = "center"; context.textBaseline = "middle";
    context.fillText(piece.text, piece.x * chunk, piece.y * chunk + chunk * 0.05); // 微调Y使文字居中
}

function drawSelectedPieceHighlight(context: CanvasRenderingContext2D, piece: Piece): void {
    if (typeof piece.x !== 'number' || typeof piece.y !== 'number') return;
    const cX = piece.x * chunk; const cY = piece.y * chunk;
    context.beginPath(); context.strokeStyle = "#007bff"; context.lineWidth = 3; // 蓝色高亮
    const off = radius + 4;
    context.strokeRect(cX - off, cY - off, off * 2, off * 2);
    context.closePath();
}

function drawCandidateMoveMarkers(context: CanvasRenderingContext2D): void {
    candidateMoves.value.forEach(move => {
        context.beginPath(); context.fillStyle = "rgba(0, 100, 255, 0.3)"; context.strokeStyle = "rgba(0, 50, 150, 0.5)";
        context.lineWidth = 1;
        context.arc(move.x * chunk, move.y * chunk, candidateCircleR + 2, 0, Math.PI * 2, true); // 稍大一点的标记
        context.closePath(); context.fill(); context.stroke();
    });
}

function handleMouseDown(event: MouseEvent): void {
  if (!chessCanvasRef.value || props.currentPlayer !== selectedPiece.value?.type && selectedPiece.value !== null) { // 防止在AI回合操作或游戏结束时操作
      if (selectedPiece.value && props.currentPlayer !== selectedPiece.value.type) {
          console.log("非当前玩家回合，无法操作。");
          //可以考虑取消选择
          // resetSelectionInternal();
          // redraw();
          return;
      }
  }


  const rect = chessCanvasRef.value!.getBoundingClientRect();
  const clickX = event.clientX - rect.left; const clickY = event.clientY - rect.top;
  const boardX = Math.round(clickX / chunk); const boardY = Math.round(clickY / chunk);

  if (boardX < 1 || boardX > 9 || boardY < 1 || boardY > 10) return;

  const clickedTargetPiece = getPieceAt(boardX, boardY);

  if (selectedPiece.value) {
    if (clickedTargetPiece && clickedTargetPiece.type === selectedPiece.value.type) {
      selectPiece(clickedTargetPiece);
    } else if (isValidMoveForSelectedPiece(selectedPiece.value, boardX, boardY)) { // 传递 selectedPiece
      emit('piece-moved', {
        movedPiece: { ...selectedPiece.value },
        toX: boardX, toY: boardY,
        capturedPiece: (clickedTargetPiece && clickedTargetPiece.type !== selectedPiece.value.type) ? clickedTargetPiece : null,
      });
      resetSelectionInternal();
    } else {
      console.log(`无效移动: 从 (${selectedPiece.value.x},${selectedPiece.value.y}) 到 (${boardX},${boardY})`);
      resetSelectionInternal(); // 点击无效位置则取消选择
    }
  } else {
    if (clickedTargetPiece && clickedTargetPiece.type === props.currentPlayer) {
      selectPiece(clickedTargetPiece);
    }
  }
  redraw();
}

function getPieceAt(x: number, y: number): Piece | undefined {
  return props.pieces.find(p => p.x === x && p.y === y && p.isActiveOnBoard);
}
function isPieceAt(x: number, y: number): boolean {
  return props.pieces.some(p => p.x === x && p.y === y && p.isActiveOnBoard);
}

function selectPiece(piece: Piece): void {
  selectedPiece.value = piece;
  calculateCandidateMoves(piece);
}
function resetSelectionInternal(): void {
  selectedPiece.value = null;
  candidateMoves.value = [];
}
function resetSelectionAndRedraw(): void {
    resetSelectionInternal();
    redraw();
}

// --- 规则函数 ---
function calculateCandidateMoves(p: Piece): void {
    candidateMoves.value = [];
    if (!p || typeof p.x !== 'number' || typeof p.y !== 'number') return;

    // 确保对所有棋子都调用了isValidMoveForSelectedPiece
    for (let r = 1; r <= 10; r++) {
        for (let c = 1; c <= 9; c++) {
            if (isValidMoveForSelectedPiece(p, c, r)) { // p 是当前选中的棋子
                candidateMoves.value.push({ x: c, y: r });
            }
        }
    }
}

function isValidMoveForSelectedPiece(piece: Piece, toX: number, toY: number): boolean {
    if (!piece || typeof piece.x !== 'number' || typeof piece.y !== 'number') return false;
    if (piece.x === toX && piece.y === toY) return false; // 不能移动到原位

    const targetPiece = getPieceAt(toX, toY);
    if (targetPiece && targetPiece.type === piece.type) return false; // 不能吃己方棋子

    switch (piece.text) {
        case "車": return rule_Car(piece, toX, toY);
        case "馬": return rule_Horse(piece, toX, toY);
        case "相": return rule_Elephant_R(piece, toX, toY); // 红相
        case "象": return rule_Elephant_B(piece, toX, toY); // 黑象
        case "仕": return rule_Scholar_R(piece, toX, toY); // 红仕
        case "士": return rule_Scholar_B(piece, toX, toY); // 黑士
        case "帅": return rule_General_R(piece, toX, toY); // 红帅
        case "将": return rule_General_B(piece, toX, toY); // 黑将
        case "炮": return rule_Cannon(piece, toX, toY, targetPiece !== undefined);
        case "兵": return rule_Pawn_R(piece, toX, toY);   // 红兵
        case "卒": return rule_Pawn_B(piece, toX, toY);   // 黑卒
        default: return false;
    }
}

// 单独的规则函数 (移植并适配)
function rule_Car(p: Piece, toX: number, toY: number): boolean {
    if (p.x !== toX && p.y !== toY) return false; // 必须直线
    if (p.x === toX) { // 垂直移动
        const startY = Math.min(p.y!, toY); const endY = Math.max(p.y!, toY);
        for (let y = startY + 1; y < endY; y++) if (isPieceAt(p.x!, y)) return false;
    } else { // 水平移动
        const startX = Math.min(p.x!, toX); const endX = Math.max(p.x!, toX);
        for (let x = startX + 1; x < endX; x++) if (isPieceAt(x, p.y!)) return false;
    }
    return true;
}

function rule_Horse(p: Piece, toX: number, toY: number): boolean {
    const dx = Math.abs(p.x! - toX); const dy = Math.abs(p.y! - toY);
    if (!((dx === 1 && dy === 2) || (dx === 2 && dy === 1))) return false; // 日字
    // 别马腿
    if (dx === 2) { // 横跳
        if (isPieceAt(p.x! + (toX > p.x! ? 1 : -1), p.y!)) return false;
    } else { // 直跳 (dy === 2)
        if (isPieceAt(p.x!, p.y! + (toY > p.y! ? 1 : -1))) return false;
    }
    return true;
}

function rule_Elephant_R(p: Piece, toX: number, toY: number): boolean { // 红相
    if (toY < 6) return false; // 不过河
    if (!(Math.abs(p.x! - toX) === 2 && Math.abs(p.y! - toY) === 2)) return false; // 田字
    // 塞象眼
    if (isPieceAt(p.x! + (toX > p.x! ? 1 : -1), p.y! + (toY > p.y! ? 1 : -1))) return false;
    return true;
}
function rule_Elephant_B(p: Piece, toX: number, toY: number): boolean { // 黑象
    if (toY > 5) return false; // 不过河
    if (!(Math.abs(p.x! - toX) === 2 && Math.abs(p.y! - toY) === 2)) return false; // 田字
    // 塞象眼
    if (isPieceAt(p.x! + (toX > p.x! ? 1 : -1), p.y! + (toY > p.y! ? 1 : -1))) return false;
    return true;
}

function rule_Scholar_R(p: Piece, toX: number, toY: number): boolean { // 红仕
    if (!(toX >= 4 && toX <= 6 && toY >= 8 && toY <= 10)) return false; // 九宫格内
    if (!(Math.abs(p.x! - toX) === 1 && Math.abs(p.y! - toY) === 1)) return false; // 斜走
    return true;
}
function rule_Scholar_B(p: Piece, toX: number, toY: number): boolean { // 黑士
    if (!(toX >= 4 && toX <= 6 && toY >= 1 && toY <= 3)) return false; // 九宫格内
    if (!(Math.abs(p.x! - toX) === 1 && Math.abs(p.y! - toY) === 1)) return false; // 斜走
    return true;
}

function rule_General_R(p: Piece, toX: number, toY: number): boolean { // 红帅
    // 检查是否在九宫格内
    if (!(toX >= 4 && toX <= 6 && toY >= 8 && toY <= 10)) return false;
    // 检查是否只移动一格（直走）
    const dx = Math.abs(p.x! - toX);
    const dy = Math.abs(p.y! - toY);
    if (!((dx === 1 && dy === 0) || (dx === 0 && dy === 1))) {
        // 检查飞将 (如果目标是对方将的位置)
        const opponentGeneral = props.pieces.find(op => op.text === "将" && op.isActiveOnBoard);
        if (opponentGeneral && opponentGeneral.x === toX && toX === p.x! && opponentGeneral.y === toY) { // 确保目标是对方将
            let hasObstacleBetween = false;
            for (let y = Math.min(p.y!, opponentGeneral.y!) + 1; y < Math.max(p.y!, opponentGeneral.y!); y++) {
                if (isPieceAt(p.x!, y)) {
                    hasObstacleBetween = true;
                    break;
                }
            }
            return !hasObstacleBetween; // 如果没有阻挡，可以飞将
        }
        return false; // 如果不是飞将，也不是直走一格
    }
    return true; // 直走一格是允许的
}
// rule_General_B 类似地检查
function rule_General_B(p: Piece, toX: number, toY: number): boolean { // 黑将
    if (!(toX >= 4 && toX <= 6 && toY >= 1 && toY <= 3)) return false;
    const dx = Math.abs(p.x! - toX);
    const dy = Math.abs(p.y! - toY);
    if (!((dx === 1 && dy === 0) || (dx === 0 && dy === 1))) {
        const opponentGeneral = props.pieces.find(op => op.text === "帅" && op.isActiveOnBoard);
        if (opponentGeneral && opponentGeneral.x === toX && toX === p.x! && opponentGeneral.y === toY) {
            let hasObstacleBetween = false;
            for (let y = Math.min(p.y!, opponentGeneral.y!) + 1; y < Math.max(p.y!, opponentGeneral.y!); y++) {
                if (isPieceAt(p.x!, y)) { hasObstacleBetween = true; break; }
            }
            return !hasObstacleBetween;
        }
        return false;
    }
    return true;
}

function rule_Cannon(p: Piece, toX: number, toY: number, isTargetOccupied: boolean): boolean {
    if (p.x !== toX && p.y !== toY) return false;
    let obstacles = 0;
    if (p.x === toX) {
        const startY = Math.min(p.y!, toY); const endY = Math.max(p.y!, toY);
        for (let y = startY + 1; y < endY; y++) if (isPieceAt(p.x!, y)) obstacles++;
    } else {
        const startX = Math.min(p.x!, toX); const endX = Math.max(p.x!, toX);
        for (let x = startX + 1; x < endX; x++) if (isPieceAt(x, p.y!)) obstacles++;
    }
    if (isTargetOccupied) return obstacles === 1; // 吃子跳一个
    else return obstacles === 0; // 移动不能跳
}

function rule_Pawn_R(p: Piece, toX: number, toY: number): boolean { // 红兵
    if (p.y! > 5) { // 未过河
        return p.x === toX && p.y! - 1 === toY; // 只能前进
    } else { // 已过河
        return (p.x === toX && p.y! - 1 === toY) || // 前进
               (p.y === toY && Math.abs(p.x! - toX) === 1); // 横走
    }
}
function rule_Pawn_B(p: Piece, toX: number, toY: number): boolean { // 黑卒
    if (p.y! < 6) { // 未过河 (注意黑卒的河界是y=5和y=6之间)
        return p.x === toX && p.y! + 1 === toY; // 只能前进
    } else { // 已过河
        return (p.x === toX && p.y! + 1 === toY) || // 前进
               (p.y === toY && Math.abs(p.x! - toX) === 1); // 横走
    }
}
function validateMove(pieceToMove: Piece, toX: number, toY: number): boolean {
    if (!pieceToMove || typeof pieceToMove.x !== 'number' || typeof pieceToMove.y !== 'number') {
        console.error("校验走法：提供的棋子无效或无坐标", pieceToMove);
        return false;
    }
    // 这里的逻辑与 isValidMoveForSelectedPiece 非常相似
    // 区别在于 pieceToMove 是直接传入的，而不是 this.selectedPiece.value

    const targetPiece = getPieceAt(toX, toY); // 检查目标位置是否有棋子
    if (targetPiece && targetPiece.type === pieceToMove.type) {
        console.log(`校验走法：不能吃己方棋子 at (${toX}, ${toY})`);
        return false; // 不能吃己方棋子
    }

    switch (pieceToMove.text) {
        case "車": return rule_Car(pieceToMove, toX, toY);
        case "馬": return rule_Horse(pieceToMove, toX, toY);
        case "相": return rule_Elephant_R(pieceToMove, toX, toY);
        case "象": return rule_Elephant_B(pieceToMove, toX, toY);
        case "仕": return rule_Scholar_R(pieceToMove, toX, toY);
        case "士": return rule_Scholar_B(pieceToMove, toX, toY);
        case "帅": return rule_General_R(pieceToMove, toX, toY);
        case "将": return rule_General_B(pieceToMove, toX, toY);
        case "炮": return rule_Cannon(pieceToMove, toX, toY, targetPiece !== undefined);
        case "兵": return rule_Pawn_R(pieceToMove, toX, toY);
        case "卒": return rule_Pawn_B(pieceToMove, toX, toY);
        default:
            console.error(`校验走法：未知棋子类型 "${pieceToMove.text}"`);
            return false;
    }
}

defineExpose({
  resetSelectionAndRedraw,
  validateMove // 暴露校验方法
});
</script>

<style scoped>
canvas {
  background: #EAC591;
  border: 1px solid #000;
  display: block; /* 避免底部额外空白 */
}
</style>