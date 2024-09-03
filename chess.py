'''
Driver file: interacts with user input and game state changes
'''

import pygame as p
import ChessEngine, chessAI


p.init() #initialize pygame
#set board and log constraints
WIDTH = HEIGHT = 512
MOVE_LOG_WIDTH = 250
MOVE_LOG_HEIGHT = HEIGHT
DIMENSION = 8 #chess board is 8x8
SQ_SIZE = HEIGHT // DIMENSION #size of square
MAX_FPS = 15 #for animations
IMAGES = {}

'''
Initializes global dictionary of images (only called once)
'''
def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

'''
Main driver: handles user input and updating graphics
'''
def main():
    screen = p.display.set_mode((WIDTH + MOVE_LOG_WIDTH, HEIGHT))
    clock = p.time.Clock()
    moveLogFont = p.font.SysFont("Arial", 14, False, False)
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState() #initialize game state
    validMoves = gs.validMoves() #initialize valid moves
    moveMade = False #flag variable for when a move is made
    canAnimate = False #flag variable for when we should animate
    loadImages() #load in images 
    running = True
    sqSelected = () #(row,col) of users last click
    sqsClicked = [] #keeps track of player clicks [(row,col),(row,col)]
    gameEnd = False
    #if human is playing true, else false
    global playerOne, playerTwo, playerColor  
    
    #check to see how the game wants to be played
    playerInput =  input("How would you like to play? (Please enter a number) 1. Player vs. Player  2. Player vs. AI  ")
    if playerInput == "1":
        playerOne = True
        playerTwo = True
    elif playerInput == "2":
        playerOne = True
        playerTwo = False
    playerColor = input("Enter board color (purple, pink, light blue, gray): ")
    
    #start game
    while running:        
        playerTurn = (gs.whiteMove and playerOne) or (not gs.whiteMove and playerTwo) #set whos turn it is to move
        #event handler
        for e in p.event.get():
            if e.type == p.QUIT: #check if user wants to quit
                running = False
            #mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameEnd and playerTurn:
                    location = p.mouse.get_pos() #(x,y) location of mouse
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row,col) or col >= 8: #user already selected this square or mouse log was clicked
                        sqSelected = ()
                        sqsClicked = []
                    else:
                        sqSelected = (row,col)
                        sqsClicked.append(sqSelected)
                    if len(sqsClicked) == 2: #check if the selected square is the users 2nd click
                        move = ChessEngine.Move(sqsClicked[0], sqsClicked[1], gs.board) #make move
                        for i in range(len(validMoves)):
                            if move == validMoves[i]: #check if move made is valid
                                gs.makeMove(validMoves[i]) #finalize the move
                                #set flags
                                moveMade = True
                                canAnimate = True
                                #reset user clicks
                                sqSelected = ()
                                sqsClicked = [] 
                        if not moveMade:
                            sqsClicked = [sqSelected] 
            #key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_u: #undo when key 'u' is pressed
                    gs.undoMove() #undo move
                    #set flags
                    moveMade = True
                    canAnimate = False
                    gameEnd = False
                if e.key == p.K_r: #reset board when 'r' is pressed
                    gs = ChessEngine.GameState() #reinitialize game state
                    validMoves = gs.validMoves() #reinitialize valid moves
                    #reset flags and lists
                    sqSelected = ()
                    sqsClicked = []
                    moveMade = False
                    canAnimate = False
                    gameEnd = False
        
        #artifical intelligence move logic
        if not gameEnd and not playerTurn:
            move = chessAI.bestMove(gs, validMoves) #use NegaMax algorithm to make move
            if move is None: #check if there is a move
                move = chessAI.makeRandomMove(validMoves) #make random move
            gs.makeMove(move) #make move
            #set flags
            moveMade = True
            canAnimate = True
                  
        if moveMade:
            if canAnimate:
                animate(gs.moveLog[-1], screen, gs.board, clock) #animate last move in log
            validMoves = gs.validMoves()
            #set flags
            moveMade = False
            canAnimate = False
            
        drawGameState(screen, gs, validMoves, sqSelected, moveLogFont, playerColor) #draw the current game state
        
        if gs.checkMate: #check if player is in checkmate
            gameEnd = True
            if gs.whiteMove: #check who won
                drawEndText(screen, 'Black wins by checkmate') #display end text
            else:
                drawEndText(screen, 'White wins by checkmate') #display end text 
        elif gs.staleMate: #check if game ended in stalemate
            gameEnd = True
            drawEndText(screen, 'Stalemate') #display end text
            
        clock.tick(MAX_FPS)
        p.display.flip()


'''
Resposible for all graphics within a current game state
'''
def drawGameState(screen, gs, validMoves, sqSelected, moveLogFont, playerColor):
    drawBoard(screen, playerColor) #draw squares on the board
    highlight(screen, gs, validMoves, sqSelected) #highlight selected square and possible moves
    drawPieces(screen, gs.board) #draw pieces on top of current gs squares
    drawMoveLog(screen, gs, moveLogFont) #draw move log
    
    
'''
Draw squares on the board
'''
def drawBoard(screen, playerColor):
    global colors
    colors = [p.Color("white"), p.Color(playerColor)]
    #loop through the entire board 
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[((row+col) % 2)]
            p.draw.rect(screen, color, p.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))  
            
            
'''
Highlight possible moves and selected square
'''
def highlight(screen, gs, validMoves, sqSelected):
    if sqSelected != (): #check if a square is selected
        row, col = sqSelected #split tuple into row and col
        if gs.board[row][col][0] == ('w' if gs.whiteMove else 'b'):
            #highlight selected square
            surface = p.Surface((SQ_SIZE, SQ_SIZE))
            surface.set_alpha(100) #transparency value (0 = transparent, 255 = opaque)
            surface.fill(p.Color('blue'))
            screen.blit(surface, (col * SQ_SIZE, row * SQ_SIZE))
            #highlight possible moves
            surface.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == row and move.startCol == col:
                    screen.blit(surface, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))
    
    
'''
Draw pieces on the board using current game state data
'''
def drawPieces(screen, board):
    #loop through entire board
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
Draws the move log
'''
def drawMoveLog(screen, gs, font):
    rectangle = p.Rect(WIDTH, 0, MOVE_LOG_WIDTH, MOVE_LOG_HEIGHT)
    p.draw.rect(screen, p.Color("black"), rectangle)
    moveLog = gs.moveLog #add move log data 
    moveText = []
    for i in range(0, len(moveLog), 2):
        moveString = str(i//2 + 1) + ". " + str(moveLog[i]) + "  "
        if i + 1 < len(moveLog): #make sure black made move
            moveString += str(moveLog[i+1])
        moveText.append(moveString)
    movesPerRow = 3 #number of moves listed per row
    padding = 6
    textY = padding
    for i in range(0, len(moveText), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i + j < len(moveText):
                text += moveText[i+j] + "  " 
        textData = font.render(text, True, p.Color("white"))
        textLocation = rectangle.move(padding, textY) #set location of text
        screen.blit(textData, textLocation) #display text on screen
        textY += textData.get_height() + 2 #add line spacing 


'''
Animate a move
'''
def animate(move, screen, board, clock):
    global colors
    deltaRow = move.endRow - move.startRow
    deltaCol = move.endCol - move.startCol
    framesPerSq = 10 # fps for one animation
    frameCount = (abs(deltaRow) + abs(deltaCol)) * framesPerSq
    for frame in range(frameCount + 1):
        row, col = (move.startRow + deltaRow * frame/frameCount, move.startCol + deltaCol * frame/frameCount)
        drawBoard(screen, playerColor)
        drawPieces(screen, board)
        #erase piece moved from end square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        #redraw captured piece when animation is complete
        if move.pieceCaptured != '--':
            if move.enPassant:
                row = move.endRow + 1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
                endSquare = p.Rect(move.endCol * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        #draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(100) #frames per second
      
        
'''
Draw ending text
'''
def drawEndText(screen, text):
    font = p.font.SysFont("Montserrat", 50, True, False)
    textData = font.render(text, 0, p.Color("Gray"))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textData.get_width()/2, 
                                                    HEIGHT/2 - textData.get_height()/2)
    screen.blit(textData, textLocation)
    textData = font.render(text, 0, p.Color("Black"))
    screen.blit(textData, textLocation.move(2,2))
       
        
if __name__ == "__main__":
    main()