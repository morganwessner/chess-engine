# stores all information regarding current chess game state
# helps determine valid chess moves from current state, and keeps a move log

class GameState():
    def __init__(self):
        #creates an 8x8 2D list where each element is a either a piece or blank space
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR" ] ,
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp" ] ,
            ["--", "--", "--", "--", "--", "--", "--", "--" ] ,
            ["--", "--", "--", "--", "--", "--", "--", "--" ] ,
            ["--", "--", "--", "--", "--", "--", "--", "--" ] ,
            ["--", "--", "--", "--", "--", "--", "--", "--" ] ,
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp" ] ,
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR" ]]
        
        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'K': self.getKingMoves, 'Q': self.getQueenMoves}
        self.whiteMove = True #can white move
        self.moveLog = [] #log of moves
        self.whiteKing = (7,4) #white king location
        self.blackKing = (0,4) #black king location
        self.inCheck = False 
        self.pins = [] #keep track of pins
        self.checks = [] #keep track of checks
        self.checkMate = False
        self.staleMate = False
        self.enPassantPossible = () #square where en passant can occur
        self.enPassantPossibleLog = [self.enPassantPossible]
        #castling
        self.currentCastle = CastleRights(True, True, True, True)
        self.castleLog = [CastleRights(self.currentCastle.wks, self.currentCastle.bks, 
                                       self.currentCastle.wqs, self.currentCastle.bqs)]
         
    '''
    Takes move as a parameter and executes it
    '''
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--" #make start square empty
        self.board[move.endRow][move.endCol] = move.pieceMoved #move piece to end square
        self.moveLog.append(move) #log the move
        self.whiteMove = not self.whiteMove #swap players turn
        if move.pieceMoved == "wK":
            self.whiteKing = (move.endRow, move.endCol) 
        elif move.pieceMoved == "bK":
            self.blackKing = (move.endRow, move.endCol)
        #if pawn moves two squares, next move can en passant
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enPassantPossible = ((move.endRow + move.startRow) // 2, move.endCol)
        else:
            self.enPassantPossible = ()
        #if en passant move, update board to capture
        if move.enPassant:
            self.board[move.startRow][move.endCol] = "--"
        #if pawn promotion, change piece
        if move.pawnPromotion: 
          self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'
    
        #castle moves
        if move.castle:
            if move.endCol - move.startCol == 2: #kingside
                # Ensure indices are valid (move.endCol should be 6 for kingside)
                if move.endCol == 6:
                    self.board[move.endRow][5] = self.board[move.endRow][7] # move rook from column 7 to 5
                    self.board[move.endRow][7] = '--' # empty space where rook was
            else: # queenside
                # Ensure indices are valid (move.endCol should be 2 for queenside)
                if move.endCol == 2:
                    self.board[move.endRow][3] = self.board[move.endRow][0] # move rook from column 0 to 3
                    self.board[move.endRow][0] = '--' # empty space where rook was

#        if move.castle:
#            if move.endCol - move.startCol == 2: #kingside
#                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1] #move rook
#                self.board[move.endRow][move.endCol + 1] = '--' #empty space where rook was
#            else: #queenside
#                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2] #move rook
#                    self.board[move.endRow][move.endCol - 2] = '--' #empty space where rook was
                
        self.enPassantPossibleLog.append(self.enPassantPossible) #update log
        
        #update castle log
        self.updateCastleRights(move)
        self.castleLog.append(CastleRights(self.currentCastle.wks, self.currentCastle.bks, 
                                           self.currentCastle.wqs, self.currentCastle.bqs))
                
    '''
    Undos the last move made
    '''
    def undoMove(self):
        if len(self.moveLog) != 0: #make sure there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteMove = not self.whiteMove #switch turns back
            if move.pieceMoved == "wK":
                self.whiteKing = (move.startRow, move.startCol) 
            elif move.pieceMoved == "bK":
                self.blackKing = (move.startRow, move.startCol)
            #undo en passant
            if move.enPassant:
                self.board[move.endRow][move.endCol] = "--" #removes pawn added
                self.board[move.startRow][move.endCol] = move.pieceCaptured #places pawn back to start
                
            self.enPassantPossibleLog.pop()
            self.enPassantPossible = self.enPassantPossibleLog[-1]
                
            #restore ability to castle
            self.castleLog.pop()
            self.currentCastle = self.castleLog[-1] #set current castle rights to last in list
            
            #undo castle move
            if move.castle:
                if move.endCol - move.startCol == 2: #kingside
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1] #move rook
                    self.board[move.endRow][move.endCol - 1] = '--' #empty space where rook was
                else: # queenside
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1] #move rook
                    self.board[move.endRow][move.endCol + 1] = '--' #empty space where rook was
            
            #any time move is undone, we can not be in these states
            self.checkMate = False
            self.staleMate = False
                    
    '''
    All moves considering checks
    '''
    def validMoves(self):
        tempCastle = CastleRights(self.currentCastle.wks, self.currentCastle.bks, 
                                  self.currentCastle.wqs, self.currentCastle.bqs) #copy of current castle rights
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteMove: #whites turn
           kingRow = self.whiteKing[0]
           kingCol = self.whiteKing[1]
        else: #blacks turn
           kingRow = self.blackKing[0]
           kingCol = self.blackKing[1]
        if self.inCheck:
            if len(self.checks) == 1: #only one check (block or move)
                moves = self.getAllPossibleMoves()
                #to block, move piece 
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol] #enemy piece that's checking
                validSquares = [] #list of valid squares to move a piece
                #if knight, capture piece or move king
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1,8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break #capture piece (ends check)
                #remove moves that don't block check or move king
                for i in range(len(moves) - 1, -1, -1): #go backwards through list
                    if moves[i].pieceMoved[1] != 'K': #doesn't move king
                        if not (moves[i].endRow, moves[i].endCol) in validSquares: #doesn't check or capture piece
                            moves.remove(moves[i]) #remove move
            else: #double check, king must move
                self.getKingMoves(kingRow,kingCol,moves)
        else: #not in check
            moves = self.getAllPossibleMoves()  
            if self.whiteMove:
                self.getCastleMoves(self.whiteKing[0], self.whiteKing[1], moves)
            else:
                self.getCastleMoves(self.blackKing[0], self.blackKing[1], moves)
            
        if len(moves) == 0:
            if self.inCheck:
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False
            
        self.currentCastle = tempCastle
        return moves
        
    '''
    All moves without considering checks
    '''
    def getAllPossibleMoves(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                if (turn == 'w' and self.whiteMove) or (turn == 'b' and not self.whiteMove):
                    piece = self.board[row][col][1]
                    self.moveFunctions[piece](row,col,moves) #calls move function based on piece type
        return moves
    
    '''
    Get all pawn moves and add them to all possible moves
    '''
    def getPawnMoves(self, row, col, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
            
        if self.whiteMove:
            moveAmount = -1
            startRow = 6
            backRow = 0
            opponentColor = 'b'
            kingRow, kingCol = self.whiteKing
        else:
            moveAmount = 1
            startRow = 1
            backRow = 7
            opponentColor = 'w'
            kingRow, kingCol = self.blackKing
        pawnPromotion = False
            
        if self.board[row+moveAmount][col] == "--": #one square pawn advance
            if not piecePinned or pinDirection == (moveAmount,0):
                if row + moveAmount == backRow: #if piece gets to back rank (pawn promotion)
                    pawnPromotion = True
                moves.append(Move((row,col), (row + moveAmount, col), self.board, pawnPromotion = pawnPromotion))
                if row == startRow and self.board[row + 2 * moveAmount][col] == "--": #two square pawn advance
                    moves.append(Move((row,col), (row + 2 * moveAmount, col), self.board))
        if col-1 >= 0: #captures to left
            if not piecePinned or pinDirection == (moveAmount,-1):
                if self.board[row + moveAmount][col - 1][0] == opponentColor:
                    if row + moveAmount == backRow: #if piece gets to back rank (pawn promotion)
                        pawnPromotion = True
                    moves.append(Move((row,col), (row + moveAmount,col-1), self.board, pawnPromotion = pawnPromotion))
                if (row + moveAmount, col - 1) == self.enPassantPossible:
                    isAttacking = isBlocking = False #check if there is an attacking or blocking piece
                    if kingRow == row:
                        if kingCol < col: #king is left of the pawn
                            inside = range(kingCol + 1, col - 1)
                            outside = range(col + 1, 8)
                        else: #king is right of the pawn
                            inside = range(kingCol - 1, col, -1)
                            outside = range(col - 2, -1, -1)
                        for i in inside:
                            if self.board[row][i] != "--": #piece blocking
                                isBlocking = True
                        for i in outside:
                            square = self.board[row][i]
                            if square[0] == opponentColor and (square[1] == "R" or square[1] == "Q"): #attacking piece
                                isAttacking = True
                            elif square != "--":
                                isBlocking = True
                    if not isAttacking or isBlocking:
                        moves.append(Move((row,col), (row + moveAmount, col - 1), self.board, enPassant = True))
        if col+1 < 7: #captures to right
            if not piecePinned or pinDirection == (moveAmount,1):
                if self.board[row + moveAmount][col + 1][0] == opponentColor:
                    if row + moveAmount == backRow: #if piece gets to back rank (pawn promotion)
                        pawnPromotion = True
                    moves.append(Move((row,col), (row + moveAmount,col+1), self.board, pawnPromotion = pawnPromotion))
                if (row + moveAmount, col + 1) == self.enPassantPossible:
                    isAttacking = isBlocking = False #check if there is an attacking or blocking piece
                    if kingRow == row:
                        if kingCol < col: #king is left of the pawn
                            inside = range(kingCol + 1, col)
                            outside = range(col + 2, 8)
                        else: #king is right of the pawn
                            inside = range(kingCol - 1, col + 1, -1)
                            outside = range(col - 1, -1, -1)
                        for i in inside:
                            if self.board[row][i] != "--": #piece blocking
                                isBlocking = True
                        for i in outside:
                            square = self.board[row][i]
                            if square[0] == opponentColor and (square[1] == "R" or square[1] == "Q"): #attacking piece
                                isAttacking = True
                            elif square != "--":
                                isBlocking = True
                    if not isAttacking or isBlocking:
                        moves.append(Move((row,col), (row + moveAmount, col + 1), self.board, enPassant = True))
                    
    '''
    Get all rook moves and add them to all possible moves
    '''
    def getRookMoves(self, row, col, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[row][col][1] != 'Q': #can't remove queen from pin
                    self.pins.remove(self.pins[i])
                break
            
        directions = ((-1,0), (0,-1), (1,0), (0,1)) #(row,col)
        opponentColor = "b" if self.whiteMove else "w"
        for d in directions:
            for i in range(1,8): #can move a max of 7 squares
                endRow = row + d[0] * i
                endCol = col + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: #valid board move
                    #check if pin is in the direction or opposite direction
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endMove = self.board[endRow][endCol]
                        if endMove == "--": #empty space
                            moves.append(Move((row,col), (endRow,endCol), self.board))
                        elif endMove[0] == opponentColor: #enemy piece
                            moves.append(Move((row,col), (endRow,endCol), self.board))
                            break
                        else:
                            break #friendly piece
                else:
                    break #off the board
                
    '''
    Get all knight moves and add them to all possible moves
    '''
    def getKnightMoves(self, row, col, moves):
            piecePinned = False
            for i in range(len(self.pins) - 1, -1, -1):
                if self.pins[i][0] == row and self.pins[i][1] == col:
                    piecePinned = True
                    self.pins.remove(self.pins[i])
                    break
            directions = ((-2,-1), (-2,1), (-1,-2), (-1,2), (1,-2), (1,2), (2,-1), (2,1)) #(row,col) , stay on diagonal
            friendlyColor = "w" if self.whiteMove else "b"
            for d in directions:
                endRow = row + d[0]
                endCol = col + d[1]
                if 0 <= endRow < 8 and 0 <= endCol < 8: #valid board move
                    if not piecePinned:
                        endMove = self.board[endRow][endCol]
                        if endMove[0] != friendlyColor: #not a friendly piece (empty or enemy piece)
                            moves.append(Move((row,col), (endRow,endCol), self.board))
    
    '''
    Get all bishop moves and add them to all possible moves
    '''
    def getBishopMoves(self, row, col, moves):
            piecePinned = False
            pinDirection = ()
            for i in range(len(self.pins) - 1, -1, -1):
                if self.pins[i][0] == row and self.pins[i][1] == col:
                    piecePinned = True
                    pinDirection = (self.pins[i][2], self.pins[i][3])
                    self.pins.remove(self.pins[i])
                    break
                
            directions = ((-1,-1), (-1,1), (1,-1), (1,1)) #(row,col) , stay on diagonal
            opponentColor = "b" if self.whiteMove else "w"
            for d in directions:
                for i in range(1,8): #can move a max of 7 squares
                    endRow = row + d[0] * i
                    endCol = col + d[1] * i
                    if 0 <= endRow < 8 and 0 <= endCol < 8: #valid board move
                        #check if pin is in the direction or opposite direction
                        if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                            endMove = self.board[endRow][endCol]
                            if endMove == "--": #empty space
                                moves.append(Move((row,col), (endRow,endCol), self.board))
                            elif endMove[0] == opponentColor: #enemy piece
                                moves.append(Move((row,col), (endRow,endCol), self.board))
                                break
                            else:
                                break #friendly piece
                    else:
                        break #off the board
    
    '''
    Get all king moves and add them to all possible moves
    '''
    def getKingMoves(self, row, col, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        friendlyColor = "w" if self.whiteMove else "b"
        for i in range(8):
            endRow = row + rowMoves[i]
            endCol = col + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8: #valid board move
                endMove = self.board[endRow][endCol]
                if endMove[0] != friendlyColor: #not a friendly piece (empty or enemy piece)
                    #place king on end square, check for checks
                    if friendlyColor == 'w':
                        self.whiteKing = (endRow, endCol)
                    else:
                        self.blackKing = (endRow, endCol)
                    inCheck, pins, checks, = self.checkForPinsAndChecks()
                    if not inCheck: #valid move
                        moves.append(Move((row,col), (endRow,endCol), self.board))
                    #king goes back to original location
                    if friendlyColor == 'w':
                        self.whiteKing = (row, col)
                    else:
                        self.blackKing = (row, col)
        
    '''
    Generate all valid castle moves for the king at (row,col)
    '''
    def getCastleMoves(self, row, col, moves):
        if self.squareUnderAttack(row, col):
            return #can't castle
        if (self.whiteMove and self.currentCastle.wks) or (not self.whiteMove and self.currentCastle.bks):
            self.kingsideCastle(row, col, moves)
        if (self.whiteMove and self.currentCastle.wqs) or (not self.whiteMove and self.currentCastle.bqs):
            self.queensideCastle(row, col, moves)
        
        
    def kingsideCastle(self, row, col, moves):
        if col + 2 < len(self.board[row]) and self.board[row][col+1] == '--' and self.board[row][col+2] == '--':
            if not self.squareUnderAttack(row, col+1) and not self.squareUnderAttack(row, col+2):
                moves.append(Move((row, col), (row, col+2), self.board, castle = True))
                
        
    def queensideCastle(self, row, col, moves):
        if self.board[row][col-1] == '--' and self.board[row][col-2] == '--' and self.board[row][col-3] == '--':
            if not self.squareUnderAttack(row, col-1) and not self.squareUnderAttack(row, col-2):
                moves.append(Move((row, col), (row, col-2), self.board, castle = True))
        
    '''
    Get all queen moves and add them to all possible moves
    '''
    def getQueenMoves(self, row, col, moves):
        self.getRookMoves(row,col,moves)
        self.getBishopMoves(row,col,moves)
        
    '''
    Returns if piece is in check, a list of pinned pieces, and a list of checks
    '''
    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False

        if self.whiteMove:
            opponentColor = "b"
            friendlyColor = "w"
            startRow, startCol = self.whiteKing
        else:
            opponentColor = "w"
            friendlyColor = "b"
            startRow, startCol = self.blackKing

        #directions: 8 possible for Rooks/Bishops/Queens
        directions = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endMove = self.board[endRow][endCol]
                    if endMove[0] == friendlyColor and endMove[1] != 'K':
                        if possiblePin == ():
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:
                            break  #second friendly piece, no pin or check possible in this direction
                    elif endMove[0] == opponentColor:
                        type = endMove[1]
                        #checks for rook, bishop, queen
                        if (type == 'R' and (d[0] == 0 or d[1] == 0)) or \
                        (type == 'B' and (d[0] != 0 and d[1] != 0)) or \
                        (type == 'Q') or \
                        (i == 1 and type == 'K') or \
                        (i == 1 and type == 'p' and ((opponentColor == 'w' and 6 <= j <= 7) or (opponentColor == 'b' and 4 <= j <= 5))):
                            if possiblePin == ():  #no blocking piece, check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:  #piece blocking, pin
                                pins.append(possiblePin)
                                break
                        else:
                            break  #enemy piece but not checking, stop in this direction
                else:
                    break  #off the board

        #knights possible moves
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for move in knightMoves:
            endRow = startRow + move[0]
            endCol = startCol + move[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endMove = self.board[endRow][endCol]
                if endMove[0] == opponentColor and endMove[1] == 'N':
                    inCheck = True
                    checks.append((endRow, endCol, move[0], move[1]))

        return inCheck, pins, checks
    
    '''
    Update castle rights 
    '''
    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastle.wks = False
            self.currentCastle.wqs = False
        elif move.pieceMoved == 'bk':
            self.currentCastle.bks = False
            self.currentCastle.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastle.wqs == False
                elif move.startCol == 7:
                    self.currentCastle.wks == False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastle.bqs == False
                elif move.startCol == 7:
                    self.currentCastle.bks == False
            
    '''
    Determine if square can be attacked
    '''
    def squareUnderAttack(self, row, col):
        self.whiteMove = not self.whiteMove
        enemyMoves = self.getAllPossibleMoves()
        self.whiteMove = not self.whiteMove
        for move in enemyMoves:
            if move.endRow == row and move.endCol == col:
                return True
        return False
                    
                    
class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs
                       
    
class Move():
    #maps keys to values (key : value)
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                  "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                  "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}
        
    def __init__(self, startSq, endSq, board, enPassant = False, pawnPromotion = False, castle = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1] #keeps tracks of starting square
        self.endRow = endSq[0] 
        self.endCol = endSq[1] #keeps tracks of ending square
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol] #keeps track of pieces moved & captured
        self.enPassant = enPassant
        self.pawnPromotion = pawnPromotion
        self.castle = castle
        if enPassant:
            self.pieceCaptured = 'bp' if self.pieceMoved == 'wp' else 'wp'
        self.isCapture = self.pieceCaptured != '--'
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol #gives each move a unique ID
        
    '''
    Overriding the equals method
    '''
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False
        
    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
        
    def getRankFile(self, row, col):
        return self.colsToFiles[col] + self.rowsToRanks[row]
    
    #override string function
    def __str__(self):
        
        #castle move
        if self.castle:
            return "O-O" if self.endCol == 6 else "O-O-O"
        endSquare = self.getRankFile(self.endRow, self.endCol)
        
        #pawn moves
        if self.pieceMoved[1] == 'p':
            if self.isCapture:
                return self.colsToFiles[self.startCol] + "x" + endSquare
            else:
                return endSquare
            
        #other piece moves
        moveString = self.pieceMoved[1]
        if self.isCapture:
            moveString += "x"
        return moveString + endSquare