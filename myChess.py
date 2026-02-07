### 체스판 관련 GUI 구현 프로젝트 ###
### pychess, Stockfish 관련 라이센스 확인 -> REMOChess-license.txt
### The Project is under GNU License, public domain

from model import Stockfish
from collections import defaultdict
import chess
from REMOLib import *
from concurrent.futures import ProcessPoolExecutor
from myUtils import myUtils,GUIManager


## 스톡피쉬 임포트
stockFishPath = "REMOStockFish.exe"  # Stockfish 엔진의 실행 파일 경로


class engineType(Enum):
    MIRAI = auto()
    KAREN = auto()
    RIN = auto()
    VAMPIRE = auto()

class chessEngine:
    myStockfish = Stockfish(path=stockFishPath)
    stockfish_mirai = {"Threads": 4,"Hash":1024,"Contempt":10,"Ponder":False,"Slow Mover":100,"UCI_Elo":800}
    stockfish_karen = {"Threads": 4,"Hash":1024,"Contempt":18,"Ponder":True,"Slow Mover":100,"UCI_Elo":1600}
    stockfish_rin = {"Threads": 4,"Hash":1024,"Contempt":18,"Ponder":True,"Slow Mover":100,"UCI_Elo":2000}
    stockfish_vampire = {"Threads": 4,"Hash":1024,"Contempt":24,"Ponder":True,"Slow Mover":100,"UCI_Elo":3800}
    engine_map = {engineType.MIRAI:stockfish_mirai,
                  engineType.KAREN:stockfish_karen,
                  engineType.RIN:stockfish_rin,
                  engineType.VAMPIRE:stockfish_vampire}

    @classmethod
    def get_engine(cls,engine) -> Stockfish:
        return cls.engine_map.get(engine)
    
    @classmethod
    def check_parameter(cls,stockfish,parameters):
        '''
        stockfish의 파라미터가 주어진 파라미터와 일치하는지 확인
        '''
        target_dict = stockfish.get_parameters()
        for key,value in parameters.items():
            if key not in target_dict or target_dict[key] != value:
                return False
        return True
    @classmethod
    def get_best_move(cls,engine_type,board_fen):
        '''
        주어진 보드 상태에서 최선의 수를 계산
        engine_type : 파라미터 입력
        '''
        stockfish = cls.myStockfish
        if cls.check_parameter(stockfish,cls.engine_map[engine_type]) == False:
            stockfish.update_engine_parameters(cls.engine_map[engine_type]) # 엔진 파라미터 업데이트
            print(stockfish.get_parameters())
        # Stockfish로부터 최선의 수를 계산
        stockfish.set_fen_position(board_fen)
        start_eval = stockfish.get_evaluation()
        ai_move = stockfish.get_best_move()            

        stockfish.make_moves_from_current_position([ai_move])
        end_eval = stockfish.get_evaluation()
        #top_moves = stockfish.get_top_moves(10) # 유저가 하면 좋을 추천수 10개를 뽑는다.
        top_moves = []
        return {"MOVE":ai_move,"START":start_eval,"END":end_eval,"TOP":top_moves}

        


class chessObj(imageObj):
    """
    체스 기물을 나타내는 클래스입니다.

    Attributes:
        code (str): 체스 기물의 FEN 코드입니다.
    """

    def __init__(self, algCode, tileSize):
        """
        체스 기물 객체를 초기화합니다.

        Args:
            algCode (str): 체스 기물의 FEN 코드 ('K', 'Q', 'B', 'N', 'R', 'P', 'k', 'q', 'b', 'n', 'r', 'p').
            tileSize (int): 체스판 타일의 크기.
        """
        index = chessBoard.fenToSprite.index(algCode)
        scale = tileSize / 400.0
        super().__init__(["chess_sprite.png", (2, 6), index], pos=RPoint(0, 0), scale=scale)
        self.code = algCode
        self.tileSize = tileSize
        self.adjust()

    def adjust(self):
        self.center = RPoint(self.tileSize // 2, self.tileSize // 2)

class chessMode(Enum):
    """
    체스 게임 모드를 나타내는 열거형입니다.

    Attributes:
        NORMAL (int): 일반 모드.
        AI (int): AI와 대전하는 모드.
    """
    NORMAL = 0
    AI = 1

class moveFlag(Enum):
    ANY = "any" # 임의의 공간으로 이동
    ONE = "one" # 인접한 한 칸 이동
    DIGONALONE = "digonal-one" # 대각선으로 한 칸 이동


class chessEvent(Enum):
    """
    체스 게임에서 발생하는 이벤트를 나타내는 열거형입니다.

    Attributes:
        NEXTTURN: 다음 턴이 시작될 때 발생하는 이벤트.
        CHECKMATE: 체크메이트가 발생했을 때.
        STALEMATE: 스테일메이트가 발생했을 때.
        DRAW: 무승부가 되었을 때.
        PROMOTION: 프로모션이 발생했을 때.
        PIECETAKEN: 기물이 잡혔을 때.
    """
    NEXTTURN = auto()
    CHECKMATE = auto()
    STALEMATE = auto()
    DRAW = auto()
    PROMOTION = auto()
    PIECETAKEN = auto()
    SELECTED = auto()
    DROPPED = auto()
    EVALUATED = auto()

class chessBoard(gridObj):
    """
    체스판을 구현하는 클래스입니다.

    Attributes:
        fenToSprite (str): FEN 코드와 스프라이트 인덱스를 매핑하는 문자열.
        stockFishPath (str): Stockfish 엔진의 실행 파일 경로.
        tileSize (tuple): 체스판 타일의 크기.
        legalMoveObjects (list): 가능한 이동 위치를 표시하는 객체들의 리스트.
        clickedPos (list): 클릭된 체스판의 좌표.
        promotionGUI (layoutObj): 프로모션 기물을 선택할 수 있는 GUI.
        movingObj (list): 현재 움직이고 있는 체스말 객체들의 리스트.
        freezed (bool): 체스판이 조작 가능한 상태인지 여부.
        board (chess.Board): 체스 게임의 상태를 관리하는 객체.
        userIsWhite (bool): 유저가 백색 기물인지 여부.
        chessObjPool (defaultdict): 체스 기물 객체들을 재사용하기 위한 풀.
        stockfish (Stockfish): Stockfish 엔진 객체.
        mode (chessMode): 현재 게임 모드.
        events (defaultdict): 이벤트 리스너를 관리하는 딕셔너리.
        thinkTimer (RTimer): AI의 생각 시간을 조절하기 위한 타이머.
        result_queue (list): AI의 결과를 받을 큐.
        AIprocess (threading.Thread): AI 계산을 위한 스레드.
    """

    fenToSprite = 'KQBNRPkqbnrp'  # FEN과 스프라이트 인덱스를 매핑하는 문자열
    piece_scores = {
        'p': 1,    # Pawn
        'n': 3,    # Knight
        'b': 3,    # Bishop
        'r': 5,    # Rook
        'q': 9,    # Queen
    }



    def __init__(self, tileSize, pos, color=Cs.brown, userIsWhite=True, mode=chessMode.NORMAL):
        """
        체스판 객체를 초기화합니다.

        Args:
            tileSize (int): 체스판 타일의 크기.
            pos (RPoint): 체스판의 위치.
            color (tuple): 체스판의 색상.
            userIsWhite (bool): 유저가 백색 기물인지 여부.
            mode (chessMode): 게임 모드.
        """
        self.tileSize = (tileSize, tileSize)

        # 마지막에 움직인 기물을 표시하기 위한 초록 불빛
        # 가능한 이동 위치를 표시하는 객체들의 리스트
        self.legalMoveObjects = []
        # 클릭된 체스판의 좌표
        self.clickedPos = []
        # 프로모션 기물을 선택할 수 있는 GUI
        self.promotionGUI = None
        # 현재 움직이고 있는 체스말 객체들의 리스트
        self.movingObj = []
        # 체스판이 조작 가능한 상태인지 여부
        self.freezed = False
        self.executor = ProcessPoolExecutor()
        self.engine = engineType.MIRAI

        self.selectObjs = []
        self.selectPoints = []

        self.board = chess.Board()
        self.color = color
        super().__init__(pos, tileSize=(tileSize, tileSize), grid=(8, 8), color=self.color)

        self.userIsWhite = userIsWhite

        # 체스판의 타일 색상 설정 및 초기화
        for i in range(8):
            for j in range(8):
                if (i + j) % 2 == 1:
                    self[i][j].color = Cs.dark(self.color)
                self[i][j].chessObj = None  # 각 타일의 체스말 정보를 초기화

        self.chessObjPool = defaultdict(list)

        self._initChessObj()
        self._updateBoard()
        self._makeCoordinate()


        self.showStartAndEndObj = []


        self.mode = mode
        self.events = defaultdict(list)
        self.thinkTimer = RTimer(500)
        self.waiting = False # AI가 판단을 끝내고, 기다리는 중인지 여부

        self.result_queue = []  # 결과를 받을 큐
        self.AIprocess = None  # AI 프로세스


    @property
    def tileWidth(self):
        """
        체스 타일의 가로 길이를 반환합니다.

        Returns:
            int: 타일의 가로 길이.
        """
        return self.tileSize[0]

    def _makeChessObj(self, algCode: str) -> chessObj:
        """
        체스 기물 객체를 생성하여 풀에 저장합니다.

        Args:
            algCode (str): 체스 기물의 FEN 코드.

        Returns:
            chessObj: 생성된 체스 기물 객체.
        """
        obj = chessObj(algCode, self.tileWidth)
        self.chessObjPool[algCode].append(obj)
        return obj

    def _initChessObj(self, poolSize: int = 32):
        """
        체스 기물 객체들을 초기화하여 풀에 저장합니다.

        Args:
            poolSize (int, optional): 각 기물당 생성할 객체의 수. 기본값은 32.
        """
        self.chessObjPool.clear()
        for code in chessBoard.fenToSprite:
            for _ in range(poolSize):
                self._makeChessObj(code)

    def removeExistingPiece(self, x, y):
        """
        해당 위치의 기존 체스 기물을 제거하고 풀에 반환합니다.

        Args:
            x (int): x 좌표 (0~7).
            y (int): y 좌표 (0~7).
        """
        obj = self[y][x].chessObj
        if obj:
            self.chessObjPool[obj.code].append(obj)
            obj.setParent(None)
            self[y][x].chessObj = None

    def popChessPiece(self, target):
        """
        풀에서 해당 체스 기물을 제거하고 반환합니다.

        Args:
            target (str): 체스 기물의 FEN 코드.

        Returns:
            chessObj: 풀에서 제거된 체스 기물 객체.
        """
        obj = self.chessObjPool[target].pop(0)
        obj.adjust()
        return obj

    def addNewPiece(self, x, y, target):
        """
        새 체스 기물을 해당 위치에 추가합니다.

        Args:
            x (int): x 좌표 (0~7).
            y (int): y 좌표 (0~7).
            target (str): 체스 기물의 FEN 코드.
        """
        newObj = self.popChessPiece(target)
        self[y][x].chessObj = newObj
        newObj.setParent(self[y][x], depth=1)

    def _setCell(self, x, y, target):
        """
        GUI 보드의 셀을 초기화합니다.

        Args:
            x (int): x 좌표 (0~7).
            y (int): y 좌표 (0~7).
            target (str or None): 체스 기물의 FEN 코드 또는 None.

        예시:
            self._setCell(5, 3, "K")
        """
        # 타겟이 None이면 해당 셀의 체스말을 제거
        if target is None:
            self.removeExistingPiece(x, y)
        else:
            current_obj = self[y][x].chessObj

            # 셀에 말이 있고, 다른 오브젝트가 있으면 교체
            if current_obj:
                if current_obj.code != target:
                    self.removeExistingPiece(x, y)  # 기존 오브젝트 제거
                    self.addNewPiece(x, y, target)  # 새로운 오브젝트 추가
            else:
                self.addNewPiece(x, y, target)  # 새로운 오브젝트 추가 (비어 있을 때)

    def _clearCell(self, x, y):
        """
        해당 위치의 체스 기물을 제거합니다.

        Args:
            x (int): x 좌표 (0~7).
            y (int): y 좌표 (0~7).
        """
        self._setCell(x, y, None)

    def setChessPiece(self, x, y, target):
        """
        체스 기물을 변경합니다.

        Args:
            x (int): x 좌표 (0~7).
            y (int): y 좌표 (0~7).
            target (str or None): 체스 기물의 FEN 코드 또는 None.

        target을 None으로 설정하면 해당 위치의 체스말을 제거합니다.
        """
        sqr = chess.parse_square(self.posToChessPos(x, y))  # 예: (3,5) -> chess.E3 (Square)
        if target is not None:
            piece = chess.Piece.from_symbol(target)  # 예: 'K' -> chess.Piece 객체
        else:
            piece = None
        self.board.set_piece_at(sqr, piece)
        self._setCell(x, y, target)  # GUI 업데이트

    def _makeCoordinate(self):
        """
        체스판의 좌표를 표시하는 GUI를 만듭니다.
        """
        coordinateX = 'abcdefgh'
        if not self.userIsWhite:
            coordinateX = coordinateX[::-1]
        temp = []
        for c in coordinateX:
            obj = textButton(c, pygame.Rect(0, 0, self.tileWidth, self.tileWidth // 2), enabled=False, color=Cs.black)
            temp.append(obj)
        pos = self.pos + RPoint(0, self.tileWidth * 8)
        self.coordinateXObj = layoutObj(pos=pos, spacing=0, isVertical=False, childs=temp)

        coordinateY = '12345678'
        if self.userIsWhite:
            coordinateY = coordinateY[::-1]
        temp = []
        for c in coordinateY:
            obj = textButton(c, pygame.Rect(0, 0, self.tileWidth // 2, self.tileWidth), enabled=False, color=Cs.black)
            temp.append(obj)
        pos = self.pos + RPoint(-self.tileWidth // 2, 0)
        self.coordinateYObj = layoutObj(pos=pos, spacing=0, childs=temp)

    def _updateBoard(self,showAnimation=False):
        """
        체스 보드를 FEN 문자열에 맞게 업데이트합니다.
        
        최적화 내용:
        1. 문자열 파싱 최적화
        2. 좌표 변환 로직 단순화
        3. 조건 검사 최소화
        """
        fen = self.board.board_fen()  # 더 짧은 FEN 문자열 사용
        rank = 0
        file = 0
        
        # 숫자를 미리 매핑하여 int() 변환 제거
        digit_map = {'1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8}
        
        for char in fen:
            if char == '/':
                rank += 1
                file = 0
                continue
                
            if char in digit_map:
                # 빈 칸 처리
                empty_count = digit_map[char]
                for _ in range(empty_count):
                    x, y = (file, rank) if self.userIsWhite else (7 - file, 7 - rank)
                    self._setCell(x, y, None)
                    file += 1
            else:
                # 기물 처리
                x, y = (file, rank) if self.userIsWhite else (7 - file, 7 - rank)
                
                # 애니메이션 조건 검사 최적화
                curr_cell = self[y][x]
                needs_animation = (showAnimation and 
                                 (curr_cell.chessObj is None or 
                                  curr_cell.chessObj.code != char))
                
                if needs_animation:
                    Rs.playAnimation("promote_effect.png", 
                                   center=curr_cell.geometryCenter-RPoint(0,20), 
                                   sheetMatrix=(1,8), 
                                   scale=2, 
                                   frameDuration=100)
                    
                self._setCell(x, y, char)
                file += 1

    def posToChessPos(self, i, j):
        """
        그리드상의 좌표 (i, j)를 체스 보드 좌표로 변환합니다.

        Args:
            i (int): x 좌표 (0~7).
            j (int): y 좌표 (0~7).

        Returns:
            str: 체스 보드 좌표 (예: 'e4').
        """
        x_axis = 'abcdefgh'
        y_axis = '12345678'

        x = x_axis[i] if self.userIsWhite else x_axis[7 - i]
        y = y_axis[7 - j] if self.userIsWhite else y_axis[j]

        return f"{x}{y}"

    def chessPosToPos(self, pos):
        """
        체스 좌표 ('a1', 'd4' 등)를 그리드상의 좌표로 변환합니다.

        Args:
            pos (str): 체스 보드 좌표 (예: 'e4').

        Returns:
            list: [x, y] 좌표 (0~7).
        """
        x = 'abcdefgh'.index(pos[0])
        y = '12345678'.index(pos[1])

        return [x, 7 - y] if self.userIsWhite else [7 - x, y]

    def getLegalMoves(self):
        """
        현재 가능한 움직임을 딕셔너리로 반환합니다.

        Returns:
            dict: 가능한 움직임들. 예: {'e2': ['e3', 'e4'], ...}
        """
        legal_moves = {str(move)[:2]: [] for move in self.board.legal_moves}
        for move in self.board.legal_moves:
            move_str = str(move)
            start = move_str[:2]
            end = move_str[2:]
            legal_moves[start].append(end)
        return legal_moves

    def isMovable(self, i, j):
        """
        특정 위치의 기물이 움직일 수 있는지 여부를 판단합니다.

        Args:
            i (int): x 좌표 (0~7).
            j (int): y 좌표 (0~7).

        Returns:
            bool: 움직일 수 있으면 True, 아니면 False.
        """
        fen = self.posToChessPos(i, j)
        legalMoves = self.getLegalMoves()
        return fen in list(legalMoves)

    def updatePossiblePoint(self, i, j, *, alpha=20):
        """
        특정 기물이 이동할 수 있는 위치를 표시합니다.

        Args:
            i (int): x 좌표 (0~7).
            j (int): y 좌표 (0~7).
            alpha (int, optional): 투명도 설정. 기본값은 20.
        """
        fen = self.posToChessPos(i, j)
        legalMoves = self.getLegalMoves()
        for obj in self.legalMoveObjects:
            obj.setParent(None)
        self.legalMoveObjects = []
        self.legalMovePoints = []

        if fen in list(legalMoves):
            for point in legalMoves[fen]:
                x, y = self.chessPosToPos(point)
                self.legalMoveObjects.append(self.makeHoverObj(x, y, alpha=alpha))
                self.legalMovePoints.append([x, y])

    def updatePossiblePointWithFlag(self, i, j, *, alpha=20,flag):

        for obj in self.legalMoveObjects:
            obj.setParent(None)
        self.legalMoveObjects = []
        self.legalMovePoints = []

        if flag == moveFlag.ANY:
            for x in range(8):
                for y in range(8):
                    if [x,y]==[i,j]:
                        continue
                    if self[y][x].chessObj is None:
                        self.legalMoveObjects.append(self.makeHoverObj(x, y, alpha=alpha))
                        self.legalMovePoints.append([x, y])
        elif flag == moveFlag.ONE:
            for x,y in [[i+1,j],[i-1,j],[i,j+1],[i,j-1]]:
                if 0<=x<8 and 0<=y<8 and self[y][x].chessObj is None:
                    self.legalMoveObjects.append(self.makeHoverObj(x, y, alpha=alpha))
                    self.legalMovePoints.append([x, y])
        elif flag == moveFlag.DIGONALONE:
            for x,y in [[i+1,j+1],[i-1,j+1],[i+1,j-1],[i-1,j-1]]:
                if 0<=x<8 and 0<=y<8 and self[y][x].chessObj is None:
                    self.legalMoveObjects.append(self.makeHoverObj(x, y, alpha=alpha))
                    self.legalMovePoints.append([x, y])



    def makeHoverObj(self, i, j,alpha=20,color=Cs.yellow,steps=5):

        
        """
        특정 위치에 마우스 호버 시 나타나는 객체를 생성합니다.

        Args:
            i (int): x 좌표 (0~7).
            j (int): y 좌표 (0~7).
            alpha (int, optional): 투명도 설정. 기본값은 20.
        Returns:
            rectObj: 마우스 호버 시 나타나는 객체.
        """
        hoverObj = rectObj(self[0][0].rect, color=color, alpha=0)
        hoverObj.easeout("alpha",alpha,steps=steps)
        hoverObj.setParent(self[j][i])
        return hoverObj
    
    def showCastlingText(self,s):
        if self.board.is_queenside_castling(chess.Move.from_uci(s)):
            t = REMOLocalizeManager.getText("queen_castle")
        else:
            t = REMOLocalizeManager.getText("king_castle")
        GUIManager.showText(t)
    
    def showEnPassantText(self,s):
        if len(s[2:]) == 2 and self.board.is_en_passant(chess.Move.from_uci(s)):
            GUIManager.showText(REMOLocalizeManager.getText("en_passant"))


    def moveByString(self, s):
        """
        'd2d4'와 같은 문자열 입력으로 체스말을 이동합니다.

        Args:
            s (str): 움직임을 나타내는 문자열 (예: 'e2e4').
        """
        # 이동할 시작점과 끝점을 설정
        startPoint = s[:2]
        endPoint = s[2:]

        # 시작점과 끝점의 좌표 변환
        start_x, start_y = self.chessPosToPos(startPoint)
        end_x, end_y = self.chessPosToPos(endPoint)

        start_cell = self[start_y][start_x]
        end_cell = self[end_y][end_x]

        # 이동할 체스말
        movingPiece = start_cell.chessObj
        movingPiece.pos = movingPiece.geometryPos
        self.removeExistingPiece(start_x, start_y)

        delta = start_cell.geometryPos - end_cell.geometryPos

        # 상대방 말을 잡을 경우
        if end_cell.chessObj:
            Rs.playSound('chess-kill.wav', volume=0.6)
            self._clearCell(end_x, end_y)


        # 캐슬링 처리
        if self.is_castling_move(s):
            self.handle_castling_animation(startPoint, endPoint)
            self.showCastlingText(s)
        self.showEnPassantText(s)

        # 체스 엔진에 무브 전달
        self.board.push_san(s)
        self.freezed = True




        self.showStartAndEnd(start_x,start_y,end_x,end_y) # 기물의 이동 시작과 끝을 표시

        # 체스말 이동 애니메이션 처리
        self.movingObj.append(movingPiece)

        RMotion.move(movingPiece, delta=-delta, callback=lambda: self._moveEnd(movingPiece), smoothness=4)

    def showStartAndEnd(self, start_x,start_y,end_x,end_y):
        for obj in self.showStartAndEndObj:
            obj.setParent(None)
        self.showStartAndEndObj = []
        self.showStartAndEndObj.append(self.makeHoverObj(start_x, start_y, alpha=120,color=Cs.limegreen,steps=10))
        self.showStartAndEndObj.append(self.makeHoverObj(end_x, end_y, alpha=120,color=Cs.limegreen,steps=10))

    def is_castling_move(self, s):
        """
        주어진 움직임이 캐슬링인지 확인합니다.

        Args:
            s (str): 움직임을 나타내는 문자열 (예: 'e1g1').

        Returns:
            bool: 캐슬링이면 True, 아니면 False.
        """
        return len(s[2:]) == 2 and self.board.is_castling(chess.Move.from_uci(s))

    def handle_castling_animation(self, startPoint, endPoint):
        """
        캐슬링 움직임에 대한 애니메이션을 처리합니다.

        Args:
            startPoint (str): 시작 위치 (예: 'e1').
            endPoint (str): 종료 위치 (예: 'g1').
        """
        if endPoint[0] == 'g':  # 킹사이드 캐슬링
            startRookPoint = self.chessPosToPos(startPoint.replace('e', 'h'))
            endRookPoint = self.chessPosToPos(endPoint.replace('g', 'f'))
        elif endPoint[0] == 'c':  # 퀸사이드 캐슬링
            startRookPoint = self.chessPosToPos(startPoint.replace('e', 'a'))
            endRookPoint = self.chessPosToPos(endPoint.replace('c', 'd'))

        rook_from = self[startRookPoint[1]][startRookPoint[0]]
        rook_to = self[endRookPoint[1]][endRookPoint[0]]
        rookObj = rook_from.chessObj
        rookObj.pos = rookObj.geometryPos
        self.removeExistingPiece(startRookPoint[0], startRookPoint[1])

        self.movingObj.append(rookObj)

        def _rookMoveEnd(obj):
            obj.center = RPoint(self.tileWidth // 2, self.tileWidth // 2)

        RMotion.move(rookObj, delta=rook_to.geometryPos - rook_from.geometryPos,
                     callback=lambda: _rookMoveEnd(rookObj), smoothness=4.3)

    def _moveEnd(self, obj):
        """
        체스말 이동 애니메이션이 끝났을 때 호출되는 콜백 함수입니다.

        Args:
            obj (chessObj): 이동이 완료된 체스 기물 객체.
        """
        obj.center = RPoint(self.tileWidth // 2, self.tileWidth // 2)
        self.movingObj = []
        self._updateBoard()
        self.occurEvent(chessEvent.NEXTTURN)
        self.freezed = False

    def isUserTurn(self):
        """
        현재 유저의 턴인지 확인합니다.

        Returns:
            bool: 유저의 턴이면 True, 아니면 False.
        """
        return self.board.turn == (chess.WHITE if self.userIsWhite else chess.BLACK)

    def getTurnCount(self):
        """
        현재 턴 수를 반환합니다.

        Returns:
            int: 현재 턴 수.
        """
        number = self.board.fullmove_number
        return 2 * number - 1 if self.board.turn == chess.WHITE else 2 * number

    def endTurn(self):
        """
        턴을 넘깁니다.
        """
        self.board.push(chess.Move.null())

    def _chessMoveSound(self):
        """
        체스말 이동 사운드를 재생합니다.
        """
        Rs.playSound('move-chess.wav', volume=0.9)

    def _dealPromotionGUI(self):
        """
        프로모션 GUI를 처리합니다.
        """
        if Rs.userJustLeftClicked() and self.promotionGUI:
            for c in self.promotionGUI.getChilds():
                if c.collideMouse():
                    s = self.promotionKey + c.code
                    self.moveByString(s)
                    self._chessMoveSound()

            self._clearPromotionGUI()

    def _clearPromotionGUI(self):
        """
        프로모션 GUI 객체를 제거합니다.
        """
        for obj in self.promotionGUI.getChilds():
            obj.setParent(None)
        self.promotionGUI = None
        self.clickedPos = []

    def _clickAndMoveChessPiece(self):
        """
        체스말을 클릭하여 이동하는 로직을 처리합니다. (Deprecated)
        현재는 드래그 앤 드롭 방식으로 대체되었습니다.
        """
        for j in range(8):
            for i in range(8):
                curObj = self[j][i]
                if curObj.collideMouse() and Rs.userJustLeftClicked():
                    if not self.clickedPos:
                        # 말을 처음 선택했을 때
                        if self.isMovable(i, j):
                            self._handlePieceSelection(i, j)
                    else:
                        # 말을 선택한 뒤 다시 클릭했을 때
                        x, y = self.clickedPos
                        legal = self.getLegalMoves()[self.posToChessPos(x, y)]

                        # 프로모션 처리
                        self._handlePromotion(i, j, legal)

                        # 일반 이동 처리
                        if self.posToChessPos(i, j) in legal:
                            s = self.posToChessPos(x, y) + self.posToChessPos(i, j)
                            self.moveByString(s)
                            self._chessMoveSound()

                        # 기물을 다시 선택하거나 선택 해제
                        if self.isMovable(i, j) and not self.clickedPos == [i, j]:
                            self._handlePieceSelection(i, j)
                        else:
                            self._clearSelection()


    def _returnChessPiece(self):
        i, j = self.clickedPos
        self.addNewPiece(i, j, Rs.draggedObj.code)
        self._clearSelection()     


    def _forceDropChessPiece(self):
        """
        드래그한 체스말을 강제로 놓는 로직을 처리합니다.
        """
        for point in self.legalMovePoints:
            x, y = point
            if self[y][x].collideMouse():
                i, j = self.clickedPos
                self.setChessPiece(x, y, Rs.draggedObj.code)
                self.setChessPiece(i, j, None)
                self._clearSelection()
                self.occurEvent(chessEvent.DROPPED)
                return
        self._returnChessPiece()
        self.initSelection(self.targetCode,show_marker=False)

    def _dropChessPiece(self):
        """
        드래그한 체스말을 놓을 때의 로직을 처리합니다.
        """
        for point in self.legalMovePoints:
            x, y = point
            if self[y][x].collideMouse():
                i, j = self.clickedPos
                s = self.posToChessPos(i, j) + self.posToChessPos(x, y)


                is_promo = self._handlePromotion(x, y, self.getLegalMoves()[self.posToChessPos(i,j)])
                if is_promo:
                    # 드래그한 체스말을 되돌려놓는다.
                    self._returnChessPiece()
                    return

                # 상대방 말을 잡을 경우
                if self[y][x].chessObj:
                    Rs.playSound('chess-kill.wav', volume=0.6)
                    from scenes import Scenes
                    # 잡힌 말의 점수를 플레이어의 마나로 추가
                    Scenes.chessgameScene.player.setMana(Scenes.chessgameScene.player.getMana()+ self.piece_scores[self[y][x].chessObj.code.lower()])
                    self._clearCell(x, y)
                    

                self.showStartAndEnd(i,j,x,y) # 기물의 이동 시작과 끝을 표시                

                if self.is_castling_move(s):
                    self.showCastlingText(s)
                self.showEnPassantText(s)

                self.board.push_san(s)
                self._updateBoard()
                self._chessMoveSound()
                self._clearSelection()
                self.thinkTimer = RTimer(100)
                self.occurEvent(chessEvent.NEXTTURN)
                return

        # 드래그한 체스말을 되돌려놓는다.
        self._returnChessPiece()

    def _dragAndMoveChessPiece(self):
        """
        체스말을 드래그하여 이동하는 로직을 처리합니다.
        """

        movables = list(self.getLegalMoves()) # 이동 가능한 피스들의 좌표를 리스트로 반환

        for movable in movables:
            i,j = self.chessPosToPos(movable)
            curObj = self[j][i]
            if self[j][i].isJustClicked():
                Rs.draggedObj = curObj.chessObj 
                myUtils.pulse(curObj.chessObj) # 시각 효과가 필요한가?
                self._clearCell(i, j)
                self.updatePossiblePoint(i, j, alpha=80)
                self.clickedPos = [i, j]
                Rs.dropFunc = self._dropChessPiece


    def _dragAndDropChessPiece(self,flag):
        """
        체스말 드래그&드롭 모드에서 체스말을 선택했을 때의 로직을 처리합니다.
        아직 개발중
        """
        for point in self.selectPoints:
            x, y = point
            curObj = self[y][x]
            if curObj.isJustClicked():
                Rs.draggedObj = curObj.chessObj
                self._clearCell(x,y)
                self.updatePossiblePointWithFlag(x,y,alpha=80,flag=flag)
                self.clickedPos = [x, y]
                Rs.dropFunc = self._forceDropChessPiece

                self.clearSelectionMode()
                return        

    def _handlePieceSelection(self, i, j, alpha=60):
        """
        기물을 선택했을 때의 처리를 수행합니다.

        Args:
            i (int): x 좌표 (0~7).
            j (int): y 좌표 (0~7).
            alpha (int, optional): 이동 가능 위치 표시의 투명도. 기본값은 60.
        """
        self.clickedPos = [i, j]
        self.updatePossiblePoint(i, j, alpha=alpha)

    def _clearSelection(self):
        """
        기물 선택을 해제합니다.
        """
        self.clickedPos = []
        for obj in self.legalMoveObjects:
            obj.setParent(None)
        self.legalMoveObjects = []
        self.legalMovePoints = []

    def _handlePromotion(self, i, j, legal):
        """
        프로모션을 처리합니다.

        Args:
            i (int): x 좌표 (0~7).
            j (int): y 좌표 (0~7).
            legal (list): 해당 기물의 합법적인 움직임 목록.
        """
        def is_promo(move):
            return len(move) == 3  # 프로모션은 3글자로 표현됨

        promotion_list = list(filter(is_promo, legal))
        promotion = {}
        for p in promotion_list:
            key = p[:2]
            if key in promotion:
                promotion[key].append(p[2:])
            else:
                promotion[key] = [p[2:]]

        if self.posToChessPos(i, j) in promotion:
            self._createPromotionGUI(i, j, promotion)  # 프로모션 GUI를 생성
            return True
        return False

    def _createPromotionGUI(self, i, j, promotion):
        """
        프로모션 GUI를 생성합니다.

        Args:
            i (int): x 좌표 (0~7).
            j (int): y 좌표 (0~7).
            promotion (dict): 프로모션 가능한 기물의 딕셔너리.
        """
        curObj = self[j][i]
        self.promotionGUI = layoutObj(pos=curObj.geometryPos, spacing=0)
        t = self.tileWidth
        self.promotionBoard = rectObj(pygame.Rect(0, 0, t, 4 * t + t // 4).inflate(t // 2, t // 2),
                                      color=Cs.black, alpha=200, edge=10)
        self.promotionBoard.pos = curObj.geometryPos - RPoint(t // 5, t // 8)
        self.promotionKey = self.posToChessPos(self.clickedPos[0], self.clickedPos[1]) + self.posToChessPos(i, j)

        for code in promotion[self.posToChessPos(i, j)]:
            if self.userIsWhite:
                code = code.upper()
            obj = chessObj(code, self.tileWidth)
            obj.setParent(self.promotionGUI)

        label = textObj("  Promotion",size=25)
        label.setParent(self.promotionGUI)

    def _playCheckSound(self):
        '''
        체크 시 사운드와 함께 애니메이션을 재생합니다. (체크당한 킹을 강조)
        '''
        if self.board.is_check():
            king_square = self.board.king(self.board.turn)
            king_pos = chess.square_name(king_square)
            x,y = self.chessPosToPos(king_pos)
            Rs.playSound("check-sound.wav",volume=0.13)
            try:
                self.showStartAndEndObj.append(self.makeHoverObj(x,y,alpha=150,color=Cs.red))
            
            except:
                pass

    def initSelection(self,code,show_marker=True):
        """
        체스말 선택 모드로 진입합니다.
        선택할 수 있는 체스말을 표시합니다.

        Args:
            code (str): 체스 기물의 FEN 코드.
        """
        self.targetCode = code
        for j in range(8):
            for i in range(8):
                curObj = self[j][i]
                if curObj.chessObj and curObj.chessObj.code == code:
                    self.selectObjs.append(self.makeHoverObj(i, j, alpha=60))
                    self.selectPoints.append([i, j])
                    if show_marker:
                                marker = imageButton(Icons.DOWN,scale=0.5)
                                marker.colorize(Cs.red)
                                marker.midbottom = curObj.boundary.midtop + RPoint(0,25)
                                marker.jump(["pos","alpha"],[marker.pos+RPoint(0,-20),100],revert=True,show=True,steps=30)


    def updateSelection(self):
        """
        체스말 선택 모드에서 체스말을 선택했을 때의 로직을 처리합니다.
        """
        for point in self.selectPoints:
            x, y = point
            if self[y][x].collideMouse() and Rs.userJustLeftClicked():
                print("user selected",self.posToChessPos(x, y)) # DEBUG
                self.occurEvent(chessEvent.SELECTED,[x,y])
                self.clearSelectionMode()
                return
            
    def clearSelectionMode(self):
        for obj in self.selectObjs:
            obj.setParent(None)
        self.selectObjs = []
        self.selectPoints = []



    def _aiMove(self):
        """
        AI의 움직임을 처리합니다.
        """

        if self.waiting:
            if self.thinkTimer.isOver():
                self.waiting = False
                self.moveByString(self._move["MOVE"])
                self._chessMoveSound()
                self._move = None                
            return


        if self.AIprocess is None:
            # 프로세스 풀에서 Stockfish 작업을 처리
            # 체스판의 현재 상태를 FEN 문자열로 변환
            board_fen = self.board.fen()
            if self.executor:
                self.AIprocess = self.executor.submit(chessEngine.get_best_move,self.engine, board_fen)
            else:
                return

        # 아직 프로세스가 실행 중일 경우 대기
        if not self.AIprocess.done():
            return
    
        # 결과 가져오기
        self._move = self.AIprocess.result()

        if self._move:
            self.eval = {"START": self._move["START"],"END":self._move["END"],"TOP":self._move["TOP"]}
            self.occurEvent(chessEvent.EVALUATED,self.eval) # AI의 형세판단 결과를 전달
            self.waiting = True # AI가 판단을 끝내고, 기다리는 중
            self.AIprocess = None


    def update(self):
        """
        매 프레임마다 호출되어 체스판의 상태를 업데이트합니다.
        """
        if self.freezed:
            return

        self._dealPromotionGUI()

        if self.mode == chessMode.NORMAL:
            self._dragAndMoveChessPiece()
        elif self.mode == chessMode.AI:
            if self.isUserTurn():
                self._dragAndMoveChessPiece()
            else:
                if self.thinkTimer.isOver():
                    self._aiMove()

        if self.promotionGUI:
            self.promotionGUI.update()
            

    def addEvent(self, event_name, listener):
        """
        이벤트 리스너를 등록합니다.

        Args:
            event_name (chessEvent): 이벤트 이름.
            listener (callable): 이벤트 발생 시 호출될 함수.
        """
        self.events[event_name].append(listener)

    def occurEvent(self, event_name, *args, **kwargs):
        """
        이벤트를 발생시킵니다.

        Args:
            event_name (chessEvent): 이벤트 이름.
            *args: 이벤트 리스너에 전달될 위치 인자.
            **kwargs: 이벤트 리스너에 전달될 키워드 인자.
        """
        if event_name in self.events:
            for listener in self.events[event_name]:
                listener(*args, **kwargs)

    def draw(self):
        """
        체스판과 관련된 모든 그래픽 요소를 그립니다.
        """
        self.coordinateXObj.draw()
        self.coordinateYObj.draw()
        super().draw()
        for obj in self.movingObj:
            obj.draw()
        if self.promotionGUI:
            self.promotionBoard.draw()
            self.promotionGUI.draw()

    def destroy(self):
        """
        체스보드 객체를 정리합니다.
        프로세스 풀을 종료하고 리소스를 해제합니다.
        """
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)  # 실행 중인 작업이 완료될 때까지 대기
            self.executor = None
        
        # 진행 중인 AI 프로세스가 있다면 취소
        if self.AIprocess is not None:
            self.AIprocess.cancel()
            self.AIprocess = None