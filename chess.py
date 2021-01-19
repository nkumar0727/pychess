import math

EMPTY_SQUARE = '_'
BOARD_SIZE = 8

def main():
    while True:
        print('New chess match')
        __new_game()
        print('Do you want to play again? (y/n): ', end='')
        if input().strip().lower() == 'n':
            break

def __new_game():
    state = GameState()
    print('Note: all moves should be in 0-index 2d array notation.')
    print('Example: \'(1,0)-(1,1)\'')
    while not __is_game_over(state):
        state.print_board()
        move = __get_valid_move(state)
        state.update(move)

def __get_valid_move(state):
    while True:
        print('[%s] Enter move: ' % state.current_player, end='')
        move_str = input().replace(' ', '')
        try:
            raw_move = __convert_move_str_to_move(move_str)
            contextual_move = __decorate_move_with_context(raw_move, state)
            __validate_move(contextual_move, state)
            return contextual_move
        except Exception as e:
            print('Move [%s] is not valid: %s' % (move_str, e))

def __decorate_move_with_context(raw_move, state):
    piece_type = state.board[int(raw_move[0][0])][int(raw_move[0][1])]
    piece_owner = None
    if piece_type != EMPTY_SQUARE:
        piece_owner = 'black' if piece_type.islower() else 'white'
    return (raw_move, piece_type, piece_owner)

def __convert_move_str_to_move(move_str):
    move_arr = move_str.split('-')
    if len(move_arr) != 2:
        raise Exception('Move is not in correct format: [start_rank, start_file]-[end_rank, end_file]')
    start = (int(move_arr[0][1]), int(move_arr[0][3]))
    end = (int(move_arr[1][1]), int(move_arr[1][3]))
    return (start, end)

def __validate_move(move, state):
    raw_move, piece_type, piece_owner = move
    raw_piece_type = piece_type.lower()
    # move start and end location are on the board
    if raw_move[0][0] < 0 or raw_move[0][0] >= BOARD_SIZE or \
        raw_move[0][1] < 0 or raw_move[0][1] >= BOARD_SIZE or \
        raw_move[1][0] < 0 or raw_move[1][0] >= BOARD_SIZE or \
        raw_move[1][1] < 0 or raw_move[1][1] >= BOARD_SIZE:
        raise Exception('Move [%s] out of board range' % raw_move)
    # move an actual piece - not just an empty square   
    if piece_owner is None:
        raise Exception('Player [%s] cannot move an empty square' % state.current_player)
    # touch your own pieces
    if piece_owner != state.current_player:
        raise Exception('Player [%s] cannot move a piece owned by [%s]' % (state.current_player, piece_owner))
    # Movement rules
    # pawn rules 
    if raw_piece_type == 'p':
        # TODO: pawn promotion?
        # if pawn's first move, square can be 2:
        is_pawn_first_move = (piece_owner == 'black' and raw_move[0][0] == 1) \
            or (piece_owner == 'white' and raw_move[0][0] == 6)
        forward_move_multiplier = 2 if is_pawn_first_move else 1
        # new square has to be one ahead if not first move
        rank_movement_vector = forward_move_multiplier * (-1 if piece_owner == 'white' else 1)
        if raw_move[0][0] + rank_movement_vector != raw_move[1][0]:
            raise Exception('Pawns can only move one square forward (2 on the first turn for each player)')
        # new square has to be same file, unless capture - in which case only adjacent file
        file_displacement = abs(raw_move[0][1] - raw_move[1][1])
        if file_displacement > 1:
            raise Exception('Pawns cannot change files unless capturing an opponent\'s piece')
        elif file_displacement == 1:
            # check for capture
            # TODO: en passant?
            opposing_piece_owner = 'black' if state.board[raw_move[1][0]][raw_move[1][1]].islower() else 'white'
            if opposing_piece_owner is None or opposing_piece_owner == piece_owner:
                raise Exception('Pawns cannot change files unless capturing an opponent\'s piece')
    # knight rules
    elif raw_piece_type == 'n':
        abs_file_diff = abs(raw_move[1][1] - raw_move[0][1])
        abs_rank_diff = abs(raw_move[1][0] - raw_move[0][0])
        if abs_file_diff == 2 and abs_rank_diff != 1:
            raise Exception('Knights may only move in an L shape') 
        if abs_file_diff == -1 and abs_rank_diff != 2:
            raise Exception('Knights may only move in an L shape') 
    # bishop rules
    elif raw_piece_type == 'b':
        file_diff = raw_move[1][1] - raw_move[0][1]
        rank_diff = raw_move[1][0] - raw_move[0][0]
        if file_diff != rank_diff and file_diff + rank_diff != 0: 
            raise Exception('Bishops can only move diagonally')
        # [3,3] - [4,4], [2,2], [4,2], [2,4]
        # [4,4] - [5,5], [6,6]
        # [2,2] - [1,1], [0,0]
        # [4,2] - [5,1], [6,0]
        # [2,4] - [1,5], [0,6]
        # TODO: what about accidentally not going through a piece?
    # rook rules
    elif raw_piece_type == 'r':
        file_diff = raw_move[1][1] - raw_move[0][1]
        rank_diff = raw_move[1][0] - raw_move[0][0]
        if file_diff != 0 and rank_diff != 0:
            raise Exception('Rooks can move either horizontally or vertically - not both')
        # TODO: what about accidentally not going through a piece?
        # TODO: castling?
    # queen rules
    elif raw_piece_type == 'q':
        file_diff = raw_move[1][1] - raw_move[0][1]
        rank_diff = raw_move[1][0] - raw_move[0][0]
        # invalid if neither a bishop movement, nor a rook movement
        if file_diff != rank_diff and file_diff + rank_diff != 0: 
            if file_diff != 0 and rank_diff != 0:
                raise Exception('Queens can move either diagonally or horizontally or vertically')
        # TODO: what about accidentally not going through a piece?
    # king rules
    elif raw_piece_type == 'k':
        abs_file_diff = abs(raw_move[1][1] - raw_move[0][1])
        abs_rank_diff = abs(raw_move[1][0] - raw_move[0][0])
        if abs_file_diff > 1 or abs_rank_diff > 1:
            raise Exception('King can move at most 1 square horizontally and/or vertically')
        # TODO; king in check rules?
        # TODO: castling?
def __is_piece_black(piece):
    return piece.islower()
    
def __is_game_over(state):
    return False

class ChessMove:
    def __init__(self):
        pass

class GameState:
    def update(self, move):
        self.previous_move = move
        self.current_turn += 0.5
        self.current_player = 'white' if self.current_player == 'black' else 'black'
        # copy piece to new location
        new_loc = move[0][1]
        self.board[new_loc[0]][new_loc[1]] = move[1]
        # erase old one
        old_loc = move[0][0]
        self.board[old_loc[0]][old_loc[1]] = EMPTY_SQUARE

    def __create_new_board(self):
        board = [[EMPTY_SQUARE for x in range(0, BOARD_SIZE)] for x in range(0, BOARD_SIZE)]

        # pawns
        '''
        for file in range(0, BOARD_SIZE):
            board[1][file] = 'p'
        for file in range(0, BOARD_SIZE):
            board[BOARD_SIZE - 2][file] = 'P'
        '''
        
        # knights
        board[0][1] = board[0][BOARD_SIZE - 2] = 'n'
        board[BOARD_SIZE - 1][1] = board[BOARD_SIZE - 1][BOARD_SIZE - 2] = 'N'

        # bishops
        board[0][2] = board[0][BOARD_SIZE - 3] = 'b'
        board[BOARD_SIZE - 1][2] = board[BOARD_SIZE - 1][BOARD_SIZE - 3] = 'B'
    
        # rooks
        board[0][0] = board[0][BOARD_SIZE - 1] = 'r'
        board[BOARD_SIZE - 1][0] = board[BOARD_SIZE - 1][BOARD_SIZE - 1] = 'R'

        # queens
        board[0][3] = 'q'
        board[BOARD_SIZE - 1][3] = 'Q'

        # kings
        board[0][4] = 'k'
        board[BOARD_SIZE - 1][4] = 'K'

        return board
    
    def print_board(self):
        print('=' * 10)
        print('Turn %d: Current player - %s' % (math.trunc(self.current_turn), self.current_player))
        print('-' * 8)
        for rank in range(0, BOARD_SIZE):
            for file in range(0, BOARD_SIZE):
                print(self.board[rank][file], end=' ')
            print()
        print('-' * 8)
        print('=' * 10)

    def __init__(self):
        self.board = self.__create_new_board()
        self.current_player = 'white'
        self.current_turn = 1
        self.winner = None
        self.previous_move = None

if __name__ == '__main__':
    main()