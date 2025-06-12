// src/types.ts
export interface Point {
  x: number;
  y: number;
}

export interface Piece extends Point {
  id: string;
  text: string;
  type: 'red' | 'black';
  isActiveOnBoard: boolean;
  originalX?: number;
  originalY?: number;
  x?: number;
  y?: number;
}

export interface MovedPayload {
  movedPiece: Piece;
  toX: number;
  toY: number;
  capturedPiece: Piece | null;
}

export interface ChessBoardExposed {
  resetSelectionAndRedraw: () => void;
  validateMove: (pieceToMove: Piece, toX: number, toY: number) => boolean; // 新增
}

// // 旧的 AIData 接口 (不再直接使用，但可以保留作为参考或用于更复杂的 data 结构)
// export interface AIDataComplex {
//     move: string;
//     score?: number;
// }

// 新增/修改：匹配后端整体响应的接口 (data 现在是 string | null)
export interface AISuggestionResponseSimple {
    code: number;         // 状态码，例如 200 表示成功，其他表示错误
    data: string | null;  // 成功时是 AI 的走法字符串，失败或无走法时为 null (或空字符串)
    message?: string;     // 可选的错误或状态信息
}