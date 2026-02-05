import React, { useState, useEffect, useMemo } from 'react';

const mockGames = [
  { id: 'g1', name: 'Chess Match 1', players: 1, maxPlayers: 2, status: 'waiting', type: 'Chess' },
  { id: 'g2', name: 'Poker Room 2', players: 3, maxPlayers: 5, status: 'playing', type: 'Poker' },
  { id: 'g3', name: 'Tic-Tac-Toe Fun', players: 1, maxPlayers: 2, status: 'waiting', type: 'Tic-Tac-Toe' },
  { id: 'g4', name: 'Chess Blitz', players: 2, maxPlayers: 2, status: 'playing', type: 'Chess' },
  { id: 'g5', name: 'Bridge Battle', players: 2, maxPlayers: 4, status: 'waiting', type: 'Bridge' },
  { id: 'g6', name: 'Poker High Stakes', players: 4, maxPlayers: 5, status: 'waiting', type: 'Poker' },
];

const gameTypes = ['All', 'Chess', 'Poker', 'Tic-Tac-Toe', 'Bridge'];

function GameLobbyPage() {
  const [games, setGames] = useState(mockGames);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('All');
  const [showCreateGameModal, setShowCreateGameModal] = useState(false);
  const [newGameName, setNewGameName] = useState('');
  const [newGameType, setNewGameType] = useState(gameTypes[1]); // Default to first actual game type
  const [newGameMaxPlayers, setNewGameMaxPlayers] = useState(2);

  // Simulate fetching games on component mount or filter change
  useEffect(() => {
    // In a real app, you would fetch games from an API here
    // For now, we're just using mockGames
    console.log('Fetching games with filter:', filterType, 'and search:', searchTerm);
  }, []); // Empty dependency array means this runs once on mount

  const filteredGames = useMemo(() => {
    let currentGames = games;

    if (filterType !== 'All') {
      currentGames = currentGames.filter(game => game.type === filterType);
    }

    if (searchTerm) {
      currentGames = currentGames.filter(game =>
        game.name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    return currentGames;
  }, [games, searchTerm, filterType]);

  const handleCreateGame = () => {
    if (newGameName.trim() && newGameMaxPlayers > 1) {
      const newGame = {
        id: `g${games.length + 1}`,
        name: newGameName.trim(),
        players: 1,
        maxPlayers: parseInt(newGameMaxPlayers, 10),
        status: 'waiting',
        type: newGameType,
      };
      setGames(prevGames => [...prevGames, newGame]);
      setShowCreateGameModal(false);
      setNewGameName('');
      setNewGameMaxPlayers(2);
      setNewGameType(gameTypes[1]);
      alert(`Game '${newGame.name}' created!`);
    } else {
      alert('Please enter a valid game name and max players (at least 2).');
    }
  };

  const handleJoinGame = (gameId) => {
    // In a real app, this would involve an API call to join a game
    alert(`Attempting to join game ${gameId}`);
    // Simulate updating game state if join is successful
    setGames(prevGames =>
      prevGames.map(game =>
        game.id === gameId && game.players < game.maxPlayers && game.status === 'waiting'
          ? { ...game, players: game.players + 1, status: game.players + 1 === game.maxPlayers ? 'playing' : 'waiting' }
          : game
      )
    );
  };

  const styles = {
    container: {
      fontFamily: 'Arial, sans-serif',
      padding: '20px',
      maxWidth: '1200px',
      margin: '0 auto',
      backgroundColor: '#f4f7f6',
      borderRadius: '8px',
      boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
    },
    header: {
      textAlign: 'center',
      color: '#333',
      marginBottom: '30px',
      borderBottom: '2px solid #eee',
      paddingBottom: '15px',
    },
    controls: {
      display: 'flex',
      justifyContent: 'space-between',
      marginBottom: '20px',
      gap: '10px',
      flexWrap: 'wrap',
    },
    inputGroup: {
      flex: '1 1 200px',
      display: 'flex',
      flexDirection: 'column',
    },
    input: {
      padding: '10px',
      border: '1px solid #ddd',
      borderRadius: '4px',
      fontSize: '1em',
      width: '100%',
      boxSizing: 'border-box',
    },
    select: {
      padding: '10px',
      border: '1px solid #ddd',
      borderRadius: '4px',
      fontSize: '1em',
      width: '100%',
      boxSizing: 'border-box',
      backgroundColor: 'white',
    },
    button: {
      padding: '10px 15px',
      backgroundColor: '#007bff',
      color: 'white',
      border: 'none',
      borderRadius: '4px',
      cursor: 'pointer',
      fontSize: '1em',
      transition: 'background-color 0.2s ease',
    },
    createGameButton: {
      backgroundColor: '#28a745',
      flex: '0 0 auto',
      minWidth: '150px',
    },
    gameList: {
      listStyle: 'none',
      padding: '0',
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
      gap: '20px',
    },
    gameCard: {
      backgroundColor: 'white',
      border: '1px solid #e0e0e0',
      borderRadius: '8px',
      padding: '20px',
      boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between',
      transition: 'transform 0.1s ease-in-out',
    },
    gameCardHover: {
      transform: 'translateY(-3px)',
    },
    gameName: {
      margin: '0 0 10px 0',
      color: '#0056b3',
      fontSize: '1.4em',
    },
    gameDetails: {
      fontSize: '0.9em',
      color: '#555',
      marginBottom: '10px',
    },
    joinButton: {
      backgroundColor: '#007bff',
      width: '100%',
      marginTop: '15px',
    },
    fullButton: {
      backgroundColor: '#6c757d',
      cursor: 'not-allowed',
    },
    playingButton: {
      backgroundColor: '#ffc107',
      cursor: 'not-allowed',
    },
    modalOverlay: {
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0,0,0,0.6)',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      zIndex: 1000,
    },
    modalContent: {
      backgroundColor: 'white',
      padding: '30px',
      borderRadius: '8px',
      boxShadow: '0 5px 15px rgba(0,0,0,0.3)',
      width: '90%',
      maxWidth: '400px',
      position: 'relative',
    },
    modalCloseButton: {
      position: 'absolute',
      top: '10px',
      right: '10px',
      background: 'none',
      border: 'none',
      fontSize: '1.5em',
      cursor: 'pointer',
      color: '#aaa',
    },
    modalTitle: {
      marginBottom: '20px',
      color: '#333',
      textAlign: 'center',
    },
    formGroup: {
      marginBottom: '15px',
    },
    label: {
      display: 'block',
      marginBottom: '5px',
      color: '#333',
      fontWeight: 'bold',
    },
    modalButtonContainer: {
      display: 'flex',
      justifyContent: 'flex-end',
      marginTop: '20px',
      gap: '10px',
    },
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.header}>Game Lobby</h1>

      <div style={styles.controls}>
        <div style={styles.inputGroup}>
          <label htmlFor="search" style={styles.label}>Search Games:</label>
          <input
            type="text"
            id="search"
            style={styles.input}
            placeholder="Search by game name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div style={styles.inputGroup}>
          <label htmlFor="filter" style={styles.label}>Filter by Type:</label>
          <select
            id="filter"
            style={styles.select}
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
          >
            {gameTypes.map(type => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
        </div>

        <button
          style={{ ...styles.button, ...styles.createGameButton }}
          onClick={() => setShowCreateGameModal(true)}
        >
          Create New Game
        </button>
      </div>

      <ul style={styles.gameList}>
        {filteredGames.length > 0 ? (
          filteredGames.map((game) => (
            <li key={game.id} style={styles.gameCard}>
              <div>
                <h2 style={styles.gameName}>{game.name}</h2>
                <p style={styles.gameDetails}>
                  <strong>Type:</strong> {game.type}<br/>
                  <strong>Players:</strong> {game.players}/{game.maxPlayers}<br/>
                  <strong>Status:</strong> {game.status.charAt(0).toUpperCase() + game.status.slice(1)}
                </p>
              </div>
              {
                game.status === 'waiting' && game.players < game.maxPlayers ? (
                  <button
                    style={{ ...styles.button, ...styles.joinButton }}
                    onClick={() => handleJoinGame(game.id)}
                  >
                    Join Game
                  </button>
                ) : game.players === game.maxPlayers ? (
                  <button style={{ ...styles.button, ...styles.joinButton, ...styles.fullButton }} disabled>
                    Full
                  </button>
                ) : (
                  <button style={{ ...styles.button, ...styles.joinButton, ...styles.playingButton }} disabled>
                    Playing
                  </button>
                )
              }
            </li>
          ))
        ) : (
          <p>No games found matching your criteria.</p>
        )}
      </ul>

      {showCreateGameModal && (
        <div style={styles.modalOverlay} onClick={() => setShowCreateGameModal(false)}>
          <div style={styles.modalContent} onClick={e => e.stopPropagation()}>
            <button style={styles.modalCloseButton} onClick={() => setShowCreateGameModal(false)}>&times;</button>
            <h2 style={styles.modalTitle}>Create New Game</h2>
            <div style={styles.formGroup}>
              <label htmlFor="gameName" style={styles.label}>Game Name:</label>
              <input
                type="text"
                id="gameName"
                style={styles.input}
                value={newGameName}
                onChange={(e) => setNewGameName(e.target.value)}
                placeholder="Enter game name"
              />
            </div>
            <div style={styles.formGroup}>
              <label htmlFor="gameType" style={styles.label}>Game Type:</label>
              <select
                id="gameType"
                style={styles.select}
                value={newGameType}
                onChange={(e) => setNewGameType(e.target.value)}
              >
                {gameTypes.filter(type => type !== 'All').map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>
            <div style={styles.formGroup}>
              <label htmlFor="maxPlayers" style={styles.label}>Max Players:</label>
              <input
                type="number"
                id="maxPlayers"
                style={styles.input}
                value={newGameMaxPlayers}
                onChange={(e) => setNewGameMaxPlayers(e.target.value)}
                min="2"
              />
            </div>
            <div style={styles.modalButtonContainer}>
              <button
                style={{ ...styles.button, backgroundColor: '#6c757d' }}
                onClick={() => setShowCreateGameModal(false)}
              >
                Cancel
              </button>
              <button
                style={{ ...styles.button, backgroundColor: '#28a745' }}
                onClick={handleCreateGame}
              >
                Create Game
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default GameLobbyPage;
