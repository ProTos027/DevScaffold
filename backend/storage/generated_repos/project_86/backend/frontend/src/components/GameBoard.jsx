import React, { useState, useEffect, useCallback } from 'react';
import './GameBoard.css'; // Assume this CSS file exists for styling

// Piece SVGs - In a real app, these would be imported from an assets folder
const pieceSVGs = {
  'bP': '&#9823;', 'bR': '&#9820;', 'bN': '&#9822;', 'bB': '&#9821;', 'bQ': '&#9819;', 'bK': '&#9818;',
  'wP': '&#9817;', 'wR': '&#9814;', 'wN': '&#9816;', 'wB': '&#9815;', 'wQ': '&#9813;', 'wK': '&#9812;'
};

const initialBoard = [
  ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
  ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
  [null, null, null, null, null, null, null, null],
  [null, null, null, null, null, null, null, null],
  [null, null, null, null, null, null, null, null],
  [null, null, null, null, null, null, null, null],
  ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
  ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
].flat(); // Flatten to a 1D array of 64 squares

const GameBoardComponent = () => {
  const [board, setBoard] = useState(initialBoard);
  const [selectedSquare, setSelectedSquare] = useState(null); // Index of the selected square
  const [validMoves, setValidMoves] = useState([]); // Array of indices where the selected piece can move
  const [turn, setTurn] = useState('w'); // 'w' for white, 'b' for black
  const [draggedPiece, setDraggedPiece] = useState(null); // The piece being dragged
  const [draggedFrom, setDraggedFrom] = useState(null); // The square index from which piece is dragged

  // Dummy move validation logic for demonstration
  // In a real app, this would use a chess engine (e.g., chess.js)
  const getValidMoves = useCallback((squareIndex, currentBoard) => {
    if (squareIndex === null) return [];
    const piece = currentBoard[squareIndex];
    if (!piece) return [];

    const moves = [];
    // Simulate some moves based on piece type (very basic and not chess-rule compliant)
    const row = Math.floor(squareIndex / 8);
    const col = squareIndex % 8;

    // Example: Allow any empty adjacent square for a selected piece for demo
    for (let r = -1; r <= 1; r++) {
      for (let c = -1; c <= 1; c++) {
        if (r === 0 && c === 0) continue;
        const newRow = row + r;
        const newCol = col + c;
        if (newRow >= 0 && newRow < 8 && newCol >= 0 && newCol < 8) {
          const targetIndex = newRow * 8 + newCol;
          if (!currentBoard[targetIndex]) {
            moves.push(targetIndex);
          }
        }
      }
    }
    // Also allow capture-like moves if target has opposite color piece (simplistic)
    if (piece.startsWith(turn)) {
      for (let i = 0; i < 64; i++) {
        if (i !== squareIndex && currentBoard[i] && !currentBoard[i].startsWith(turn)) {
          moves.push(i);
        }
      }
    }

    return moves;
  }, [turn]);

  useEffect(() => {
    if (selectedSquare !== null) {
      const moves = getValidMoves(selectedSquare, board);
      setValidMoves(moves);
    } else {
      setValidMoves([]);
    }
  }, [selectedSquare, board, getValidMoves]);

  const handlePieceDragStart = (e, squareIndex, pieceType) => {
    if (!pieceType || !pieceType.startsWith(turn)) {
      e.preventDefault(); // Prevent dragging opponent's pieces or empty squares
      return;
    }
    setDraggedPiece(pieceType);
    setDraggedFrom(squareIndex);
    setSelectedSquare(squareIndex); // Select the piece when dragging starts
    e.dataTransfer.setData('squareIndex', squareIndex.toString());
  };

  const handleDragOver = (e) => {
    e.preventDefault(); // Necessary to allow dropping
  };

  const handleDrop = (e, targetSquareIndex) => {
    e.preventDefault();
    const sourceSquareIndex = parseInt(e.dataTransfer.getData('squareIndex'), 10);

    if (sourceSquareIndex === null || !draggedPiece) {
      // No piece was being dragged or invalid source
      resetSelection();
      return;
    }

    if (validMoves.includes(targetSquareIndex)) {
      const newBoard = [...board];
      newBoard[targetSquareIndex] = draggedPiece; // Move the piece
      newBoard[sourceSquareIndex] = null; // Clear the source square
      setBoard(newBoard);
      setTurn(turn === 'w' ? 'b' : 'w'); // Switch turn
    }
    resetSelection();
  };

  const handleSquareClick = (squareIndex) => {
    const clickedPiece = board[squareIndex];

    if (selectedSquare === null) {
      // No piece is selected, select this one if it's current player's
      if (clickedPiece && clickedPiece.startsWith(turn)) {
        setSelectedSquare(squareIndex);
      }
    } else if (selectedSquare === squareIndex) {
      // Clicking the already selected piece deselects it
      resetSelection();
    } else {
      // A piece is selected, now try to move it
      if (validMoves.includes(squareIndex)) {
        const newBoard = [...board];
        const pieceToMove = newBoard[selectedSquare];
        newBoard[squareIndex] = pieceToMove; // Move piece to target
        newBoard[selectedSquare] = null; // Clear source
        setBoard(newBoard);
        setTurn(turn === 'w' ? 'b' : 'w'); // Switch turn
        resetSelection();
      } else if (clickedPiece && clickedPiece.startsWith(turn)) {
        // Clicked another one of current player's pieces, select new one
        setSelectedSquare(squareIndex);
      } else {
        // Clicked an invalid square or opponent's piece, deselect
        resetSelection();
      }
    }
  };

  const resetSelection = () => {
    setSelectedSquare(null);
    setValidMoves([]);
    setDraggedPiece(null);
    setDraggedFrom(null);
  };

  const getSquareClassName = (index) => {
    const row = Math.floor(index / 8);
    const col = index % 8;
    const color = (row + col) % 2 === 0 ? 'light-square' : 'dark-square';
    const classes = [color];

    if (selectedSquare === index) {
      classes.push('selected-square');
    }
    if (validMoves.includes(index)) {
      classes.push('valid-move');
    }
    if (draggedFrom === index) {
      classes.push('dragged-from'); // Highlight where the piece was dragged from
    }

    return classes.join(' ');
  };

  return (
    <div className="game-board-container">
      <h2>Current Turn: {turn === 'w' ? 'White' : 'Black'}</h2>
      <div className="game-board">
        {board.map((piece, index) => (
          <div
            key={index}
            className={`square ${getSquareClassName(index)}`}
            onDragOver={handleDragOver}
            onDrop={(e) => handleDrop(e, index)}
            onClick={() => handleSquareClick(index)}
          >
            {piece && (
              <div
                className={`piece ${piece.startsWith('w') ? 'white-piece' : 'black-piece'}`}
                draggable={piece.startsWith(turn) ? "true" : "false"}
                onDragStart={(e) => handlePieceDragStart(e, index, piece)}
                dangerouslySetInnerHTML={{ __html: pieceSVGs[piece] }}
              ></div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default GameBoardComponent;
