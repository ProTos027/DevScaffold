import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams } from 'react-router-dom';

// Mock Board component for demonstration purposes.
// In a real application, this would be a more complex, dedicated component
// handling piece rendering, drag-and-drop, valid move highlighting, etc.
const GameBoard = ({ board, onSquareClick, playerColor, currentTurn }) => {
    const boardSize = 8;
    const renderSquare = (row, col) => {
        const isLight = (row + col) % 2 === 0;
        const squareColor = isLight ? 'bg-indigo-100' : 'bg-indigo-300';
        const piece = board[row * boardSize + col]; // Simple 1D array for board pieces
        const squareId = `${String.fromCharCode(97 + col)}${8 - row}`;

        return (
            <div
                key={squareId}
                className={`w-16 h-16 sm:w-20 sm:h-20 flex items-center justify-center text-xl font-bold cursor-pointer transition-colors ${squareColor} ${piece ? 'text-gray-900' : 'text-gray-600'} hover:ring-2 hover:ring-blue-500`}
                onClick={() => onSquareClick(squareId)}
            >
                {piece || squareId}
            </div>
        );
    };

    return (
        <div className="grid grid-cols-8 gap-0 border-4 border-gray-700 shadow-xl">
            {Array.from({ length: boardSize }).map((_, r) =>
                Array.from({ length: boardSize }).map((_, c) => renderSquare(r, c))
            )}
        </div>
    );
};

// Mock MoveHistory component for demonstration purposes.
const MoveHistory = ({ history }) => (
    <div className="p-4 bg-gray-800 rounded-lg shadow-inner max-h-96 overflow-y-auto border border-gray-700">
        <h3 className="text-lg font-semibold mb-3 text-gray-200">Move History</h3>
        {history.length === 0 ? (
            <p className="text-gray-400">No moves yet.</p>
        ) : (
            <ol className="list-decimal list-inside text-gray-300">
                {history.map((move, index) => (
                    <li key={index} className="mb-1 text-sm">{move}</li>
                ))}
            </ol>
        )}
    </div>
);

// Mock GameControls component for demonstration purposes.
const GameControls = ({ onResign, onDrawOffer }) => (
    <div className="flex space-x-4 mt-6">
        <button
            onClick={onResign}
            className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors shadow-md"
        >
            Resign
        </button>
        <button
            onClick={onDrawOffer}
            className="px-6 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors shadow-md"
        >
            Offer Draw
        </button>
    </div>
);

function GamePage() {
    const { gameId } = useParams(); // Retrieves gameId from the URL (e.g., /game/:gameId)

    const [gameState, setGameState] = useState({
        board: Array(64).fill(null), // Represents an empty 8x8 board
        turn: 'white',
        status: 'waiting', // 'playing', 'checkmate', 'stalemate', 'draw', 'white_wins', 'black_wins'
        winner: null,
    });
    const [moveHistory, setMoveHistory] = useState([]);
    const [playerColor, setPlayerColor] = useState(null); // The color assigned to the current player ('white' or 'black')
    const [isConnected, setIsConnected] = useState(false);
    const [error, setError] = useState(null);

    const ws = useRef(null); // useRef to persist WebSocket instance across renders

    // Establishes and manages the WebSocket connection
    const connectWebSocket = useCallback(() => {
        if (!gameId) {
            setError("Game ID is missing. Cannot connect to game server.");
            return;
        }

        // Close any existing connection before creating a new one
        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            ws.current.close();
        }

        const websocketUrl = `ws://localhost:8080/game/${gameId}`; // Adjust hostname/port as per backend configuration
        const newWs = new WebSocket(websocketUrl);
        ws.current = newWs; // Store the new WebSocket instance in the ref

        newWs.onopen = () => {
            console.log('WebSocket connected successfully.');
            setIsConnected(true);
            setError(null);
            // Optionally, send a 'join_game' message with user auth token/ID
            // newWs.send(JSON.stringify({ type: 'JOIN_GAME', gameId, userId: '...' }));
        };

        newWs.onmessage = (event) => {
            const message = JSON.parse(event.data);
            console.log('Received WebSocket message:', message);

            switch (message.type) {
                case 'GAME_STATE_UPDATE':
                    setGameState({ // Update the main game state
                        board: message.board,
                        turn: message.turn,
                        status: message.status,
                        winner: message.winner,
                    });
                    setMoveHistory(message.moveHistory || []); // Update move history
                    break;
                case 'PLAYER_INFO':
                    setPlayerColor(message.color); // Assign player color from the server
                    break;
                case 'ERROR':
                    setError(message.message); // Display error messages from the server
                    break;
                case 'GAME_OVER':
                    setGameState(prev => ({ ...prev, status: message.status, winner: message.winner }));
                    break;
                case 'DRAW_OFFERED':
                    // Handle draw offer UI (e.g., show a modal to accept/decline)
                    console.log(`Draw offered by ${message.offeringPlayer}.`)
                    break;
                // Add more cases for other message types (e.g., 'DRAW_ACCEPTED', 'DRAW_REJECTED', 'CHAT_MESSAGE')
                default:
                    console.warn('Unknown message type received:', message.type);
            }
        };

        newWs.onerror = (errorEvent) => {
            console.error('WebSocket error:', errorEvent);
            setError('WebSocket connection error. Please try again.');
            setIsConnected(false);
        };

        newWs.onclose = (closeEvent) => {
            console.log('WebSocket disconnected:', closeEvent);
            setIsConnected(false);
            if (!closeEvent.wasClean) {
                // If the connection was not closed cleanly, attempt to reconnect after a delay
                console.log('WebSocket closed unexpectedly. Attempting to reconnect...');
                // setTimeout(connectWebSocket, 3000); // Reconnect after 3 seconds, implement robust reconnection logic in a real app
            }
        };
    }, [gameId]); // Reconnect if gameId changes

    useEffect(() => {
        connectWebSocket(); // Establish connection on component mount

        // Cleanup function: Close WebSocket when the component unmounts
        return () => {
            if (ws.current) {
                console.log('Closing WebSocket on component unmount.');
                ws.current.close();
            }
        };
    }, [connectWebSocket]); // Dependency on connectWebSocket ensures it runs if gameId changes

    // Sends a message over the WebSocket connection
    const sendWebSocketMessage = useCallback((message) => {
        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify(message));
        } else {
            console.warn('WebSocket is not open. Cannot send message:', message);
            setError('Not connected to the game server. Please refresh the page.');
        }
    }, []);

    // Handles a player making a move (called by the GameBoard component)
    const handlePlayerMove = useCallback((from, to) => {
        // Basic validation before sending the move
        if (gameState.status !== 'playing') {
            setError("Game is not in 'playing' status.");
            return;
        }
        if (gameState.turn !== playerColor) {
            setError("It's not your turn.");
            return;
        }

        console.log(`Sending move: from ${from} to ${to}`);
        sendWebSocketMessage({ // Send the move to the backend
            type: 'PLAYER_MOVE',
            gameId,
            move: { from, to }, // Structure of a chess move
            playerColor, // To identify which player is making the move
        });
    }, [gameId, playerColor, sendWebSocketMessage, gameState.status, gameState.turn]);

    // This function acts as a simplified handler for board clicks.
    // In a full chess game, GameBoard would manage selecting pieces and identifying valid target squares.
    // For this demonstration, we simulate a move from a fixed source to the clicked square.
    const handleBoardSquareClick = useCallback((squareId) => {
        if (gameState.status !== 'playing' || gameState.turn !== playerColor) {
            setError("Cannot make a move: It's not your turn, or the game is not active.");
            return;
        }

        // --- SIMPLIFIED MOVE LOGIC FOR DEMONSTRATION ONLY ---
        // In a real chess application, the GameBoard component would manage piece selection
        // and pass both 'from' and 'to' squares to `handlePlayerMove`.
        // Here, we're just simulating a move from a dummy source to the clicked square.
        const simulatedFromSquare = 'e2'; // Example dummy source square
        const simulatedToSquare = squareId; // The clicked square is the target

        console.log(`Simulating click-based move from ${simulatedFromSquare} to ${simulatedToSquare}`);
        handlePlayerMove(simulatedFromSquare, simulatedToSquare);

    }, [gameState.status, gameState.turn, playerColor, handlePlayerMove]);

    // Handles a player resigning from the game
    const handleResign = useCallback(() => {
        if (window.confirm('Are you sure you want to resign? This will result in a loss.')) {
            sendWebSocketMessage({
                type: 'RESIGN',
                gameId,
                playerColor,
            });
        }
    }, [gameId, playerColor, sendWebSocketMessage]);

    // Handles a player offering a draw
    const handleOfferDraw = useCallback(() => {
        if (window.confirm('Do you want to offer a draw to your opponent?')) {
            sendWebSocketMessage({
                type: 'OFFER_DRAW',
                gameId,
                playerColor,
            });
        }
    }, [gameId, playerColor, sendWebSocketMessage]);

    if (!gameId) {
        return (
            <div className="flex items-center justify-center min-h-screen bg-gray-900 text-white p-4">
                <p className="text-xl text-red-400">No game ID provided. Please navigate from a valid game link.</p>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center p-4 sm:p-8">
            <h1 className="text-3xl sm:text-4xl font-extrabold mb-6 text-blue-400">Game: {gameId}</h1>

            {error && (
                <div className="bg-red-700 p-3 sm:p-4 rounded-lg mb-4 w-full max-w-xl text-center shadow-lg animate-pulse-fade">
                    <p className="text-lg font-medium">Error: {error}</p>
                </div>
            )}

            {!isConnected && !error && (
                <div className="bg-blue-600 p-3 sm:p-4 rounded-lg mb-4 w-full max-w-xl text-center shadow-lg">
                    <p className="text-lg font-medium">Connecting to game server...</p>
                </div>
            )}

            <div className="flex flex-col lg:flex-row gap-8 w-full max-w-7xl items-start">
                <div className="flex-1 flex flex-col items-center lg:items-start order-2 lg:order-1">
                    <div className="mb-6 text-center lg:text-left">
                        <p className="text-xl mb-2">Your Color: <span className="font-bold capitalize text-green-400">{playerColor || 'N/A'}</span></p>
                        <p className="text-xl mb-2">Current Turn: <span className="font-bold capitalize text-purple-400">{gameState.turn}</span></p>
                        <p className="text-xl">Game Status: <span className="font-bold capitalize text-orange-400">{gameState.status.replace(/_/g, ' ')}</span></p>
                        {gameState.winner && <p className="text-2xl mt-3 font-extrabold text-teal-400">Winner: <span className="capitalize">{gameState.winner}</span>!</p>}
                    </div>

                    <GameBoard
                        board={gameState.board}
                        onSquareClick={handleBoardSquareClick}
                        playerColor={playerColor}
                        currentTurn={gameState.turn}
                    />
                    <GameControls onResign={handleResign} onDrawOffer={handleOfferDraw} />
                </div>

                <div className="lg:w-1/3 w-full order-1 lg:order-2">
                    <MoveHistory history={moveHistory} />
                </div>
            </div>
        </div>
    );
}

export default GamePage;
