import pytest
from unittest.mock import Mock, MagicMock, patch
from Parabox import enterIn, blocks, boxes, clone, epsilon, infinity, voidbox, push

class TestEnterIn:
    
    @pytest.fixture
    def mock_game(self):
        game = Mock()
        game.boxdict = {}
        game.lastmove = None
        return game
    
    @pytest.fixture
    def mock_block(self):
        block = Mock(spec=blocks)
        block.container = Mock()
        return block
    
    @pytest.fixture
    def mock_box(self):
        box = Mock(spec=boxes)
        box.name = "TestBox"
        box.row = 5
        box.col = 5
        box.board = [[Mock(spec=blocks) for _ in range(5)] for _ in range(5)]
        box.place = Mock()
        return box
    
    def test_enter_infinity_box_returns_zero(self, mock_block, mock_game):
        """Entering an infinity box should return 0"""
        inf_box = Mock(spec=infinity)
        result = enterIn(mock_block, inf_box, 0, [], [], mock_game)
        assert result == 0
    
    def test_enter_from_void_box_returns_zero(self, mock_block, mock_box, mock_game):
        """A block inside a void box cannot enter other boxes"""
        mock_block.container = Mock(spec=voidbox)
        result = enterIn(mock_block, mock_box, 0, [], [], mock_game)
        assert result == 0
    
    def test_clone_redirects_to_extension(self, mock_block, mock_game):
        """Clones should redirect entry to their extension"""
        true_box = Mock(spec=boxes)
        true_box.name = "TrueBox"
        true_box.row = 5
        true_box.col = 5
        true_box.board = [[Mock(spec=blocks, tangible=False) for _ in range(5)] for _ in range(5)]
        true_box.place = Mock()
        
        clone_box = Mock(spec=clone)
        clone_box.extension = true_box
        
        result = enterIn(mock_block, clone_box, 0, [], [], mock_game)
        assert result == 1
        true_box.place.assert_called_once()
    
    def test_enter_empty_space_returns_one(self, mock_block, mock_box, mock_game):
        """Entering an empty space should succeed"""
        mock_box.board[4][2] = Mock(spec=blocks, tangible=False)
        result = enterIn(mock_block, mock_box, 0, [], [], mock_game)
        assert result == 1
        mock_box.place.assert_called_once()
    
    def test_enter_wall_returns_zero(self, mock_block, mock_box, mock_game):
        """Entering a wall should fail"""
        mock_box.board[4][2] = Mock(spec=blocks, tangible=True, pushable=False)
        result = enterIn(mock_block, mock_box, 0, [], [], mock_game)
        assert result == 0
    
    @patch('Parabox.push')
    def test_enter_pushable_block_success(self, mock_push, mock_block, mock_box, mock_game):
        """Entering with a pushable block in the way should place block after successful push"""
        mock_box.board[4][2] = Mock(spec=blocks, tangible=True, pushable=True)
        mock_push.return_value = 1
        
        result = enterIn(mock_block, mock_box, 0, [], [], mock_game)
        assert result == 1
        mock_box.place.assert_called_once()
    
    @patch('Parabox.push')
    def test_enter_cycle_detection_returns_two(self, mock_push, mock_block, mock_box, mock_game):
        """Cycle detection should return 2"""
        mock_box.board[4][2] = Mock(spec=blocks, tangible=True, pushable=True)
        mock_push.return_value = 2
        
        result = enterIn(mock_block, mock_box, 0, [], [], mock_game)
        assert result == 2
    
    @patch('Parabox.enterIn', wraps=enterIn)
    @patch('Parabox.epsilon')
    def test_infinite_enter_creates_epsilon(self, mock_epsilon_class, mock_enter, mock_block, mock_box, mock_game):
        """Infinite enter loop should create epsilon box"""
        eps_box = Mock(spec=epsilon)
        eps_box.container = Mock()
        eps_box.container.name = "EpsContainer"
        eps_box.name = "EpsBox"
        eps_box.board = [[Mock(spec=blocks, tangible=False) for _ in range(5)] for _ in range(5)]
        eps_box.place = Mock()
        
        mock_epsilon_class.return_value = eps_box
        
        result = enterIn(mock_block, mock_box, 0, [mock_box.name], [], mock_game)
        mock_epsilon_class.assert_called_once()