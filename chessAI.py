import random
'''
Note for algorithms: A positive score is always good for white and a negative score is always good for black
'''
#point values of each piece type
piecePoints = {"K": 0, "Q": 9, "R": 5, "N": 3, "B": 3, "p": 1}

#2D list of piece scores used to calculate best moves based on position (higher value = better position for piece)
#knight: knights are better off in the center of the board
knightScore = [[1,1,1,1,1,1,1,1],  
               [1,2,2,2,2,2,2,1],
               [1,2,3,3,3,3,2,1],
               [1,2,3,4,4,3,2,1],
               [1,2,3,4,4,3,2,1],
               [1,2,3,3,3,3,2,1],
               [1,2,2,2,2,2,2,1],
               [1,1,1,1,1,1,1,1]]

#bishop: bishops are better off on long diagonals
bishopScore = [[4,3,2,1,1,2,3,4],  
               [3,4,3,2,2,3,4,3],
               [2,3,4,3,3,4,3,2],
               [1,2,3,4,4,3,2,1],
               [1,2,3,4,4,3,2,1],
               [2,3,4,3,3,4,3,2],
               [3,4,3,2,2,3,4,3],
               [4,3,2,1,1,2,3,4]]

#queen: queens are better off on central files or squares close to king
queenScore =  [[1,1,1,3,1,1,1,1],  
               [1,2,3,3,3,1,1,1],
               [1,4,3,3,3,4,2,1],
               [1,2,3,3,3,2,2,1],
               [1,2,3,3,3,2,2,1],
               [1,4,3,3,3,4,2,1],
               [1,1,2,3,3,1,1,1],
               [1,1,1,3,1,1,1,1]]

#rook: rooks are better off on back rows or central files
rookScore =   [[4,3,4,4,4,4,3,4],  
               [4,4,4,4,4,4,4,4],
               [1,1,2,3,3,2,1,1],
               [1,2,3,4,4,3,2,1],
               [1,2,3,4,4,3,2,1],
               [1,1,2,2,2,2,1,1],
               [4,4,4,4,4,4,4,4],
               [4,3,4,4,4,4,3,4]]

#white pawn: white pawns are best off on the opposite side(for promotion) or in the center
whitePawnScore = [[9,9,9,9,9,9,9,9],  
                  [9,9,9,9,9,9,9,9],
                  [5,6,6,7,7,6,6,5],
                  [2,3,3,5,5,3,3,2],
                  [1,2,3,4,4,3,2,1],
                  [1,1,2,3,3,2,1,1],
                  [1,1,1,0,0,1,1,1],
                  [0,0,0,0,0,0,0,0]]

#black pawn: black pawns are best off on the opposite side(for promotion) or in the center
blackPawnScore = [[0,0,0,0,0,0,0,0],  
                  [1,1,1,0,0,1,1,1],
                  [1,1,2,3,3,2,1,1],
                  [1,2,3,4,4,3,2,1],
                  [2,3,3,5,5,3,3,2],
                  [5,6,6,7,7,6,6,5],
                  [9,9,9,9,9,9,9,9],
                  [9,9,9,9,9,9,9,9]]

#dictionary to store pieces and their scores
positionScores = {"N": knightScore, "B": bishopScore, "Q": queenScore,
                  "R": rookScore, "wp": whitePawnScore, "bp": blackPawnScore}
pointMultiplier = 0.1 #multiplier to bring down point weight to reasonable value

CHECKMATE = 1000 #highest possible score
STALEMATE = 0
DEPTH = 3 #how many moves ahead the AI will think (higher = slower response time)

'''
Find a random valid move
'''
#first algorithm tried: make a random move (used to test if the AI works)
def makeRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]

 
'''
Find best move solely based on material (MinMax algorithm)
'''
#second algorithm tried: calculate best move only based on material value (ex: queen worth 8) using MinMax algorithm
def makeBestMove(gs, validMoves):
    scoreSelecter = 1 if gs.whiteMove else -1
    enemyMinMaxScore = CHECKMATE
    bestMove = None
    random.shuffle(validMoves)
    for move in validMoves:
        gs.makeMove(move)
        enemyMoves = gs.validMoves()
        if gs.staleMate:
            enemyMaxScore = STALEMATE
        elif gs.checkMate:
            enemyMaxScore = -CHECKMATE
        else:
            enemyMaxScore = -CHECKMATE
        #go through all enemy moves in search of highest value move
        for enemyMove in enemyMoves:
            gs.makeMove(enemyMove)
            gs.validMoves()
            if gs.checkMate:
                score = CHECKMATE
            elif gs.staleMate:
                score = STALEMATE 
            else:
                score = -scoreSelecter * boardScore(gs.board)
            if (score > enemyMaxScore):
                enemyMaxScore = score
            gs.undoMove()
        #minimization of score 
        if enemyMaxScore < enemyMinMaxScore:
            enemyMinMaxScore = enemyMaxScore
            bestMove = move
        gs.undoMove()
    return bestMove
    

'''
Helper method for first recursive call
'''
def bestMove(gs, validMoves):
    global nextMove
    nextMove = None
    moveNegaMaxAlphaBeta(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteMove else -1) #search for best move
    return nextMove #return best move


'''
Recursive MinMax algorithm to find best move
'''
#third algorithm tried: same as second algorithm except this time it's recursive and can go to more depth
def moveMinMax(gs, validMoves, depth, whiteMove):
    global nextMove
    if depth == 0:
        return boardScore(gs.board)
    
    #maximize score
    if whiteMove:
        maxScore = -CHECKMATE #start at lowest score possible
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.validMoves()
            score = moveMinMax(gs, nextMoves, depth - 1, False) #pass next move (recursive call)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH: #searched all possible moves for depth = 2
                    nextMove = move 
            gs.undoMove()
        return maxScore
            
    #minimize score
    else:
        minScore = CHECKMATE #start at highest score possible
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.validMoves()
            score = moveMinMax(gs, nextMoves, depth - 1, True) #pass next move (recursive call)
            if score < minScore:
                minScore = score
                if depth == DEPTH: #searched all possible moves for depth = 2
                    nextMove = move
            gs.undoMove()
        return minScore
    

'''
Nega Max algorithm to find best move
'''
#fourth algorithm tried: calculate best move based on position rather than material (NegaMax algorithm)
def moveNegaMax(gs, validMoves, depth, scoreSelector):
    global nextMove
    if depth == 0:
        return scoreSelector * scoreBoard(gs)
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.validMoves()
        score = -moveNegaMax(gs, nextMoves, depth - 1, -scoreSelector)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
    return maxScore


'''
Nega Max algorithm to find best move with Alpha Beta Pruning
'''
#fifth algorithm tried (BEST): same as fourth algorithm except I added alpha beta pruning to speed up the process of searching for moves
def moveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, scoreSelector):
    #beta: highest possible score, alpha: lowest possible score
    global nextMove
    if depth == 0:
        return scoreSelector * scoreBoard(gs)
    
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.validMoves()
        score = -moveNegaMaxAlphaBeta(gs, nextMoves, depth - 1, -beta, -alpha, -scoreSelector) #switch to opponent
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
        if maxScore > alpha: #pruning
            alpha = maxScore
        if alpha >= beta: #already found good max score 
            break
    return maxScore


'''
Positive score: good for white, Negative score: good for black
'''
#scoring function used for NegaMax algorithms based on piece position as well as material points
def scoreBoard(gs):
    if gs.checkMate:
        if gs.whiteMove:
            return -CHECKMATE #black wins
        else:
            return CHECKMATE #white wins
    elif gs.staleMate:
        return STALEMATE
    
    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != "--":
                #score based on position
                if square[1] != "K":
                    if square[1] == "p":
                        positionScore = positionScores[square][row][col]
                    else: 
                        positionScore = positionScores[square[1]][row][col]
                    if square[0] == 'w':
                        score += piecePoints[square[1]] + (positionScore * pointMultiplier)
                    elif square[0] == 'b':
                        score -= piecePoints[square[1]] + (positionScore * pointMultiplier)
    return score
                 
    
'''
Find score of board based on material
'''
#initial scoring solely using material (only used for second and third algorithms)
def boardScore(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += piecePoints[square[1]]
            elif square[0] == 'b':
                score -= piecePoints[square[1]]
                
    return score