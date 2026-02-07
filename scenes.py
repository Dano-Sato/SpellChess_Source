### Bishoujo 스펠 체스 1
## 미소녀와 체스로 전투하자! 스펠 카드로 전투하자!

from REMOLib import *
from myChess import *
from myUtils import *
from gameObjects import *
from debug import DebugManager
from scenes_others import *


class gameMode(Enum):
    NORMAL = auto()
    SPELL = auto()

class spellMode(Enum):
    NULL = auto()
    SELECTION = auto()
    DRAGDROP = auto()



class gameEndMode(Enum):
    WIN = auto()
    LOSE = auto()
    DRAW = auto()

class gameEndFlag(Enum):
    RESIGN = auto()
    SUICIDE = auto()


class gameEndScene(Scene):
    def __init__(self,win=gameEndMode.WIN,flag=None):
        super().__init__()
        stats_scene = getattr(Scenes, 'chessgameScene', None)
        if stats_scene:
            difficulty_text = self._getDifficultyText(getattr(stats_scene, "difficulty_index", None))
            mana_used = getattr(stats_scene, "mana_used", 0)
            cards_used = getattr(stats_scene, "cards_used", 0)
        else:
            difficulty_text = REMOLocalizeManager.getText("normal")
            mana_used = 0
            cards_used = 0
        if win == gameEndMode.WIN:
            text = f"{REMOLocalizeManager.getText('victory')}!"
            Rs.changeMusic("winBGM.mp3")
        elif win == gameEndMode.LOSE:
            text = f"{REMOLocalizeManager.getText('defeat')}!"
            Rs.changeMusic("loseBGM.mp3")
        elif win == gameEndMode.DRAW:
            text = f"{REMOLocalizeManager.getText('draw')}!"
        if Scenes.chessgameScene.board.board.is_checkmate():
            caption = f"{REMOLocalizeManager.getText('checkmate')}."
        elif Scenes.chessgameScene.board.board.is_stalemate():
            caption = f"{REMOLocalizeManager.getText('stalemate')}."
        else:
            if flag == gameEndFlag.SUICIDE:
                caption = f"{REMOLocalizeManager.getText('self_destruct')}."
            elif flag == gameEndFlag.RESIGN:
                caption = f"{REMOLocalizeManager.getText('resigned')}."
            else:
                caption = ""

        self.title = textObj(text, size=120, color=Cs.white)
        self.caption = textObj(caption, size=50, color=Cs.grey75)
        self.difficultyText = textObj(f"{REMOLocalizeManager.getText('difficulty_2')} : {difficulty_text}", size=50, color=Cs.white)
        self.manaUsedText = textObj(f"{REMOLocalizeManager.getText('used_mana')} : {mana_used}", size=45, color=Cs.white)
        self.cardsUsedText = textObj(f"{REMOLocalizeManager.getText('used_card')} : {cards_used}", size=45, color=Cs.white)
        self.makeArea(820)
        self.endButton = textButton(REMOLocalizeManager.getText("confirm"),pygame.Rect(0,0,200,50),size=50)
        self.endButton.connect(lambda: Rs.transition(Scenes.mainMenuScene))

        Scenes.chessgameScene.board.destroy()

    def makeArea(self,board_width):
        w,h = Rs.screenRect().size
        self.area = pygame.Rect(board_width,0,w-board_width,h)
        print(self.area)

    def _getDifficultyText(self, difficulty_index):
        difficulty_keys = [
            "very_easy",
            "easy",
            "normal",
            "hard",
            "very_hard"
        ]
        if difficulty_index is None or difficulty_index < 0 or difficulty_index >= len(difficulty_keys):
            return REMOLocalizeManager.getText("normal")
        key = difficulty_keys[difficulty_index]
        return REMOLocalizeManager.getText(key)


    def init(self):
        self.title.midtop = self.area.midtop + RPoint(0,50)
        self.caption.midtop = self.title.midbottom + RPoint(0,50)
        self.title.slidein(speed=1)
        self.caption.slidein(speed=1)
        self.difficultyText.midtop = self.caption.midbottom + RPoint(0,40)
        self.manaUsedText.midtop = self.difficultyText.midbottom + RPoint(0,30)
        self.cardsUsedText.midtop = self.manaUsedText.midbottom + RPoint(0,30)
        self.difficultyText.slidein(speed=1)
        self.manaUsedText.slidein(speed=1)
        self.cardsUsedText.slidein(speed=1)
        self.endButton.midbottom = self.area.midbottom + RPoint(0,-50)
        self.endButton.slidein(speed=1)
        return

    def update(self):
        DebugManager.mouseUpdate()
        self.endButton.update()
        return

    def draw(self):
        GUIManager.drawBg()
        Scenes.chessgameScene.board.draw()
        self.title.draw()
        self.caption.draw()
        self.difficultyText.draw()
        self.manaUsedText.draw()
        self.cardsUsedText.draw()
        self.endButton.draw()
        return




# 체스 게임 씬 클래스 정의
class chessgameScene(Scene):
    """
    게임의 주요 씬(Scene)을 구성하는 클래스입니다.
    """

    def initSpellMode(self,card:cardObj,index):
        '''
        스펠 카드 사용 모드에 진입
        '''
        self.gameMode = gameMode.SPELL
        self.loseTurn = True
        self.currentCard = card
        self.cardIndex = index
        commands = [item.strip() for item in card.query.split(",")]  

        self.spellTitle = textObj(f"{REMOLocalizeManager.getText('use_card')} <{card.name}>", size=50)
        self.spellTitle.midtop = Rs.screenRect().midtop + RPoint(400, 50)
        self.currentCard.resize(cardObj.big_size)
        self.currentCard.midtop = self.spellTitle.midbottom + RPoint(0, 50)
        self.spellCancelButton.midtop = self.currentCard.midbottom + RPoint(0, 50)

        self.commands = []
        self.loseTurn = True # 커맨드 종료시 턴을 잃는지 여부
        # 각 명령어를 처리
        for command in commands:
            
            # 명령어와 인자를 분리
            match = command.split(" ")
            if match:
                operation = match[0]  # 명령어 (select, destroy 등)
                argument = match[1:]   # 인자 (e-p 등)
                if len(argument) == 1:
                    argument = argument[0]
                self.commands.append({
                    'operation': operation,
                    'argument': argument if argument else None
                })

        print(self.commands)
        self.handleCommand()


        self.filter.alpha=0

        self.filter.easeout("alpha",200,steps=10)


    def cancleSpellMode(self):
        if not self.currentCard:
            return
        self.recordManaRefund(self.currentCard.cost)
        self.recordCardRefund()
        self.player.setMana(self.player.getMana() + self.currentCard.cost)
        self.gameMode = gameMode.NORMAL
        self.currentCard.resize(cardObj.small_size)
        self.currentCard.pos = RPoint(1000,0)
        self.player.returnCard(self.currentCard,self.cardIndex)
        self.spellTitle = None
        self.currentCard = None
        self.cardIndex = None
        self.board.clearSelectionMode()

    
    def parse_piece_code(self,argument):
        '''
        m-p, e-p 등의 코드를 분석하여 체스말 코드로 변환
        '''
        # 인자를 분리하여 소유자와 코드 추출
        is_mine_str, code = argument.split('-')
        # 소유자 여부 결정
        is_mine = is_mine_str == 'm'
        # 현재 플레이어의 색상과 비교하여 백색인지 결정
        is_white = is_mine == self.board.userIsWhite
        if is_white:
            code = code.upper()
        else:
            code = code.lower()       
        return code
    
    def resign(self):
        Rs.transition(gameEndScene(gameEndMode.LOSE,gameEndFlag.RESIGN))

     

    def handleCommand(self):
        '''
        카드의 명령어 쿼리를 처리하는 함수
        '''
        
        # 명령 리스트가 비어있는 경우 턴 종료 처리
        if not self.commands:
            self.gameMode = gameMode.NORMAL
            self.spellTitle = None
            self.currentCard = None
            self.cardIndex = None
            if self.loseTurn:
                # 카드를 사용하고 턴을 잃는 경우
                if self.board.board.is_check():
                    # 킹이 자결했다. 패배
                    self.board._playCheckSound()
                    Rs.transition(gameEndScene(gameEndMode.LOSE,gameEndFlag.SUICIDE))
                    return
                self.board.endTurn()
                self.girl.shocked() # 소녀는 쇼크에 빠진다.
            self.spellMode = spellMode.NULL
            self.endPhase()
            return

        # 명령 리스트에서 첫 번째 명령을 가져옴
        command = self.commands.pop(0)
        operation = command.get('operation')
        argument = command.get('argument')

        # operation이 유효한지 확인
        if not operation:
            print("Error: Operation is missing.")
            return

        # 'select' 작업 처리 (체스말 선택)
        if operation == 'select':
            try:
                code = self.parse_piece_code(argument)
                print("SELECT", code)
                # 선택 초기화                
                self.board.initSelection(code)
                self.spellMode = spellMode.SELECTION
                GUIManager.showText(REMOLocalizeManager.getText("click_piece"),steps=60)

            except ValueError:
                print("Error: Invalid argument format.")
                return
        elif operation == 'move': # 'move' 작업 처리 (체스말 이동)
            code = self.parse_piece_code(argument[0])
            self.moveFlag = moveFlag(argument[1])
            self.board.initSelection(code)
            self.spellMode = spellMode.DRAGDROP
            GUIManager.showText(REMOLocalizeManager.getText("drag_drop_piece"),steps=60)

            print("MOVE", code, self.moveFlag)
        # 'destroy' 작업 처리 (체스말 파괴)
        elif operation == 'destroy':
            x, y = self.selectedPos
            # 파괴 효과 재생
            self.playDestroyEffect(x, y)
            # 체스말 제거
            self.obj_destroyed = Rs.copyImage(self.board[y][x].chessObj)
            self.obj_destroyed.easeout(["angle","pos","alpha"],[-120,self.obj_destroyed.pos+RPoint(150,150),0],callback=lambda: setattr(self, 'obj_destroyed', None),steps=20) # 체스말이 파괴되어 나뒹구는 애니메이션
            self.board.setChessPiece(x, y, None)
            # 다음 명령 처리
            self.handleCommand()
        elif operation == 'change': # 변신, 프로모션 처리


            if argument in ["rand", "rande"]: # 변신 처리 (랜덤으로 변신)
                #rand: 나의 말, rande: 상대 말 변신
                is_mine = True if argument == "rand" else False
                argument = random.choice(["p", "n", "b", "r", "q"])  # 랜덤으로 선택
                
                # userIsWhite 여부에 따라 대소문자 처리
                if is_mine == self.board.userIsWhite:
                    argument = argument.upper()
            else:
                if self.board.userIsWhite:
                    argument = argument.upper() # 프로모션 처리


                

            x, y = self.selectedPos
            # 체스말 변경
            Rs.playAnimation("promote_effect.png", center=self.board[y][x].geometryCenter-RPoint(0,20), sheetMatrix=(1,8), scale=2, frameDuration=1000 / 10)
            Rs.playSound("promote_sound.mp3")
            self.board.setChessPiece(x, y, argument)
            # 다음 명령 처리
            self.handleCommand()
        elif operation == 'change-all': # 전체 변화 카드
            if type(argument) == list:
                code:str = argument[0]
                prob = float(argument[1])
            else:
                code:str = argument
                prob = 1.0

            # FEN 코드에서 체스판 부분만 추출
            board = self.board.board.board_fen()

            # 킹을 제외한 모든 기물을 code가 지정하는 기물로 변환
            transformed_board = ""
            for char in board:
                r = random.random()
                if char in "QRBNP": 
                    if r < prob:
                        transformed_board += code.upper()
                        continue
                elif char in "qrbnp":
                    if r < prob:
                        transformed_board += code.lower()
                        continue
                transformed_board += char  # 킹과 숫자는 그대로 유지

            self.board.board.set_board_fen(transformed_board)
            self.board._updateBoard(showAnimation=True)
            self.handleCommand()
        elif operation == 'change_any': # 임의의 argument [0] 피스를 argument[1]로 변경 (기사 개종 카드에 쓰임)
            # FEN 코드에서 체스판 부분만 추출
            board = self.board.board.board_fen()
            piece_from,piece_to = argument[0], argument[1]
            if self.board.userIsWhite:
                piece_from,piece_to = piece_from.upper(),piece_to.upper()
            transformed_board = board.replace(piece_from,piece_to)
            self.board.board.set_board_fen(transformed_board)
            self.board._updateBoard(showAnimation=True)
            self.handleCommand()
            
        elif operation == "draw":
            if type(argument) == list:
                _card_from = int(argument[0])
                _card_get = int(argument[1])
                Rs.setCurrentScene(drawCardScene(_card_from,_card_get))
            else:
                _card_from = int(argument)
                _card_get = int(argument)
                Rs.setCurrentScene(drawCardScene(_card_from,_card_get))




        elif operation == 'check': # 확률 체크 처리
            threshold = float(argument)
            if random.random() < threshold:
                myUtils.showPopupText(f"{REMOLocalizeManager.getText('success')}!", color=Cs.green) 
                self.currentCard.easeout(["pos","alpha"],[self.currentCard.pos+RPoint(0,-100),0],steps=50,show=True)

                self.handleCommand()
            else: # 실패 시 다음 턴으로 넘어감
                myUtils.showPopupText(f"{REMOLocalizeManager.getText('fail')}!", color=Cs.red)
                self.currentCard.easeout(["pos","alpha"],[self.currentCard.pos+RPoint(0,-100),0],steps=50,show=True)
                Rs.playSound("check_fail.wav")
                Rs.stopSound("cardUsed.wav")

                self.commands.clear()
                self.handleCommand()
        elif operation == 'mana': # 마나 증감 처리
            amount = int(argument)
            self.player.setMana(self.player.getMana() + amount)
            self.handleCommand()
        elif operation == 'not_lose_turn':
            self.loseTurn = False
            self.handleCommand()
        elif operation == 'discount':
            code = argument[0]
            discount = float(argument[1])

            if code == "draw":
                self.player.setDrawCost(math.floor(self.player.drawCost * discount))
            elif code == "reroll":
                self.player.setShuffleCost(math.floor(self.player.shuffleCost * discount))
            elif code == "all":
                for card in self.player.hands.getChilds():
                    card.setCost(int(max(card.cost - discount,0)))
                    card.costObj.color = Cs.green
            self.handleCommand()
        elif operation == 'special':
            if argument == 'exchange_bn':
                # FEN 코드에서 체스판 부분만 추출
                _mycode = "bxn"
                fen_code = self.board.board.board_fen()
                if self.board.userIsWhite:
                    _mycode = _mycode.upper()
                b,x,n = _mycode
                fen_code = fen_code.replace(b,x).replace(n,b).replace(x,n)               
                self.board.board.set_board_fen(fen_code)
                self.board._updateBoard(showAnimation=True)
                self.handleCommand()
            elif argument == 'exchange_bn_enemy':
                # FEN 코드에서 체스판 부분만 추출
                _mycode = "bxn"
                fen_code = self.board.board.board_fen()
                if not self.board.userIsWhite:
                    _mycode = _mycode.upper()
                b,x,n = _mycode
                fen_code = fen_code.replace(b,x).replace(n,b).replace(x,n)               
                self.board.board.set_board_fen(fen_code)
                self.board._updateBoard(showAnimation=True)
                self.handleCommand()
            else:
                print(f"Error: Unknown special argument '{argument}'.")


        else:
            print(f"Error: Unknown operation '{operation}'.")

    def playDestroyEffect(self, x, y):
        # 파괴 효과의 위치 계산
        position = self.board[y][x].geometryPos - RPoint(30, 30)
        # 파괴 애니메이션 및 사운드 재생
        Rs.playAnimation(
            "destroy_effect.png",
            pos=position,
            sheetMatrix=(1, 8),
            scale=2,
            frameDuration=1000 / 10
        )
        Rs.playSound("destroy_sound.wav",volume=0.3)

    def updateTurnMarker(self):
        steps = 10
        iswhite = self.board.userIsWhite == self.board.isUserTurn()
        if self.board.isUserTurn():
            self.turnMarker.text = REMOLocalizeManager.getText("your_turn")
            to = self.turnMarker.right_pos
            alpha_to = 245
        else:
            self.turnMarker.text = REMOLocalizeManager.getText("her_turn")
            to = self.turnMarker.left_pos
            alpha_to = 200
        self.turnMarker.textObj.alpha = 0
        if iswhite:
            self.turnMarker.easeout(["alpha","color","pos"],[alpha_to,Cs.hexColor("EEEEEE"),to],steps=steps)
            self.turnMarker.textObj.easeout(["alpha","color"],[225,Cs.hexColor("111111")],steps=steps)
        else:
            self.turnMarker.easeout(["alpha","color","pos"],[alpha_to,Cs.hexColor("111111"),to],steps=steps)
            self.turnMarker.textObj.easeout(["alpha","color"],[225,Cs.hexColor("EEEEEE")],steps=steps)
    
    def __init__(self,girl_id="girl1",cardCount=0,mana=0,difficulty_index=2,userIsWhite=True):
        super().__init__()
        self.girl_id = girl_id
        self.init_cardCount = cardCount
        self.init_mana = mana
        self.difficulty_index = difficulty_index
        self.mana_used = 0
        self.cards_used = 0
        self.user_is_white = userIsWhite

    def recordManaSpend(self, amount):
        if amount <= 0:
            return
        self.mana_used += amount

    def recordManaRefund(self, amount):
        if amount <= 0:
            return
        self.mana_used = max(0, self.mana_used - amount)

    def recordCardPlayed(self):
        self.cards_used += 1

    def recordCardRefund(self):
        if self.cards_used > 0:
            self.cards_used -= 1

    def initOnce(self):
        """
        씬이 처음 생성될 때 한 번만 실행되는 초기 설정을 진행합니다.
        """
        ## GUI 요소 선언 블록
        # 체스 보드 객체 생성 및 초기화
        self.board = chessBoard(
            GUIManager.tileSize,
            RPoint(120, 110),
            color=Cs.brown_old,
            userIsWhite=self.user_is_white,
            mode=chessMode.AI,
        )

        # 화면 분할을 위한 구분선 객체 생성 및 위치 설정
        self.divider = rectObj(pygame.Rect(0, 0, Rs.screenRect().width*0.4, 10), color=Cs.apply(GUIManager.themeColor, 2.0), radius=8, edge=2)
        self.divider.midleft = Rs.screenRect().center + RPoint(-100, 50)
        self.filter = rectObj(Rs.screenRect(), color=Cs.black, alpha=150, radius=0)

        #desk : 미소녀 일러스트를 가리기 위한 데스크 이미지
        self.desk = imageObj("chess-desk.png",pos=RPoint(1080,770)) 
        deskfilter = rectObj(self.desk.offsetRect, color=Cs.black, alpha=150, radius=0)
        deskfilter.setParent(self.desk)

        self.turnMarker = textButton("당신의 차례",pygame.Rect(0,0,250,70),size=35,color=Cs.black,enabled=False,alpha=200)
        self.turnMarker.midright = self.divider.midright - RPoint(70,0)
        self.turnMarker.right_pos = self.turnMarker.pos
        self.turnMarker.left_pos = self.turnMarker.pos - RPoint(50,0)
        self.updateTurnMarker()



        _h = self.divider.pos.y
        # 소녀 객체 생성
        self.girl = girlObj(id=self.girl_id)
        print(self.girl.script)

        # 플레이어 객체 생성
        self.player = Player()

        # 데이터 매니저 초기화 및 카드 데이터 출력
        print(dataManager.getCardData())

        ## 스펠 모드 관련 변수
        self.gameMode = gameMode.NORMAL
        self.spellMode = spellMode.NULL
        self.currentCard = None
        self.cardIndex = None
        self.query = []


        #스펠 모드시 사용할 GUI
        self.spellTitle = None
        self.filter = rectObj(Rs.screenRect(), color=Cs.black, alpha=150, radius=0)
        self.spellCancelButton = textButton(REMOLocalizeManager.getText("cancle"),pygame.Rect(0,0,200,80), size=30, color=Cs.grey)
        self.spellCancelButton.connect(self.cancleSpellMode)

        self.makeBoardEvent()
        Rs.changeMusic(f"{self.girl_id}_theme.mp3")

        self.obj_destroyed = None
        self.player.setMana(self.init_mana)
        for i in range(self.init_cardCount):
            Rs.future(self.player.addRandomCardToHand,800+160*i)
        DebugManager.gameInit()
        # 게임 시작시 GUI 애니메이션
        print(self.board.getLegalMoves())
        self.girl.showEmotion(girlEmotion.START)
        self.girl.girl.slidein()
        self.player.manaBoard.slidein()
        self.divider.slidein()
        self.player.buttons.slidein(delta=RPoint(-50,0))
        self.board.slidein()
        self.board.coordinateXObj.slidein()
        self.board.coordinateYObj.slidein()
        return
    
    def makeBoardEvent(self):
        '''
        체스보드와 게임 이벤트를 연결하는 함수
        '''
        self.board.addEvent(chessEvent.NEXTTURN, self.endPhase)
        self.board.addEvent(chessEvent.NEXTTURN, self.girlThink)
        self.board.addEvent(chessEvent.EVALUATED,self.girl.actByEvaluation)
        self.board.addEvent(chessEvent.SELECTED, self.selectEvent)
        self.board.addEvent(chessEvent.DROPPED,lambda:self.handleCommand())

    def endPhase(self):
        '''
        턴 종료시 실행되는 함수
        '''
        self.board._playCheckSound()
        if self.board.board.is_checkmate():
            if self.board.isUserTurn():
                Rs.transition(gameEndScene(gameEndMode.LOSE))
            else:
                Rs.transition(gameEndScene(gameEndMode.WIN))
            return
        elif self.board.board.is_stalemate():
            Rs.transition(gameEndScene(gameEndMode.DRAW))
            return
        self.updateTurnMarker()
    
    def girlThink(self):
        if not self.board.isUserTurn():
            self.girl.think() # 소녀의 턴이 되면 생각한다.


    def selectEvent(self, pos):
        self.selectedPos = pos
        self.handleCommand() # 다음 커맨드 실행

    def init(self):
        """
        씬이 활성화될 때마다 실행되는 초기 설정을 진행합니다.
        """

        return

    def update(self):
        """
        매 프레임마다 씬의 상태를 업데이트합니다.
        """

        DebugManager.gameUpdate()


        if self.gameMode == gameMode.NORMAL:
            # 플레이어와 소녀 객체 업데이트
            self.player.update()
            self.girl.update()
            # 체스 보드 업데이트
            self.board.update()
        elif self.gameMode == gameMode.SPELL:
            if self.spellMode == spellMode.SELECTION:
                self.board.updateSelection()
            elif self.spellMode == spellMode.DRAGDROP:
                self.board._dragAndDropChessPiece(self.moveFlag)
            if Rs.userJustPressed(pygame.K_ESCAPE):
                self.cancleSpellMode()
            self.spellCancelButton.update()

        # 드래그된 객체가 있으면 위치 업데이트
        if Rs.draggedObj:
            Rs.draggedObj.center = Rs.mousePos()

        return

    def draw(self):
        """
        매 프레임마다 화면에 그래픽 요소를 그립니다.
        """
        # 배경 화면 색상 채우기
        GUIManager.drawBg()    
        # 소녀, 구분선, 체스 보드, 플레이어 그리기
        self.girl.draw()
        self.desk.draw()
        self.divider.draw()
        self.turnMarker.draw()
        self.player.draw()
        if self.gameMode == gameMode.SPELL:
            self.filter.draw()
            self.spellTitle.draw()
            self.currentCard.draw()
            self.spellCancelButton.draw()
        self.board.draw()

        # 드래그된 객체가 있으면 그리기
        if Rs.draggedObj:
            Rs.draggedObj.draw()
        if self.obj_destroyed!=None:
            self.obj_destroyed.draw()
        return

# 기본 씬 클래스 정의 (사용되지 않음)
class defaultScene(Scene):
    """
    기본 씬 클래스로, 현재 사용되지 않습니다.
    """

    def initOnce(self):
        """
        씬이 처음 생성될 때 한 번만 실행되는 초기 설정을 진행합니다.
        """
        return

    def init(self):
        """
        씬이 활성화될 때마다 실행되는 초기 설정을 진행합니다.
        """
        return

    def update(self):
        """
        매 프레임마다 씬의 상태를 업데이트합니다.
        """
        return

    def draw(self):
        """
        매 프레임마다 화면에 그래픽 요소를 그립니다.
        """
        return
    

class myCheckBoxObj(rectObj):
    def __init__(self,rect:pygame.Rect,checked=False,callback = lambda checked: None):
        super().__init__(rect,color=Cs.grey75)
        self.checkmark = imageObj(Icons.CHECKMARK,scale=0.4)
        self.checkmark.center = self.offsetRect.center
        self.checkmark.setParent(self)
        self.callback = callback
        self.checked = checked
        self.checked = False
        self.setChecked(checked)
    def setChecked(self,checked):
        self.checked = checked
        self.callback(self.checked)
        if self.checked:
            self.showChilds(0)
            self.color = Cs.salmon
        else:
            self.hideChilds(0)
            self.color = Cs.grey
        
    def toggleCheck(self):
        self.setChecked(not self.checked)

    def update(self):
        if self.isJustClicked():
            self.toggleCheck()

    
class drawCardScene(Scene):
    def __init__(self,card_from,card_get):
        self.bg = Rs.captureScreenShot()
        super().__init__()
        self.card_from = card_from
        self.card_get = card_get
        cards = []
        for _ in range(card_from):
            cards.append(Scenes.chessgameScene.player.getRandomCard())
        self.cardLayout = layoutObj(pos=RPoint(1129,158),childs=cards,isVertical=False)
        self.button = textButton(REMOLocalizeManager.getText("confirm"),pygame.Rect(0,0,200,50),size=50) 
        self.button.pos = RPoint(1708,672)
        self.button.connect(self.endScene)

        self.flags = [True] * card_from
        self.checkboxs = []
        if card_from != card_get:
            for i in range(card_from):
                def toggleFlag(checked, index=i):
                    self.flags[index] = checked
                    print (self.flags)
                    if sum(self.flags) == card_get:
                        self.button.easeout("color",Cs.tiffanyBlue,steps=10)
                        self.button.enabled = True
                    else:
                        self.button.easeout("color",Cs.grey,steps=10)
                        self.button.enabled = False

                checkbox = myCheckBoxObj(pygame.Rect(0,0,50,50),callback=toggleFlag)
                checkbox.midtop = self.cardLayout.geometryPos + self.cardLayout[i].midbottom + RPoint(0,10)
                self.checkboxs.append(checkbox)
        if card_from==4:
            self.title = textObj(REMOLocalizeManager.getText("get_card_4_2"),size=50)
        elif card_from==2:
            self.title = textObj(REMOLocalizeManager.getText("get_card_2_1"),size=50)

        self.title.center = RPoint(1812,82)
    def endScene(self):
        self.cards =list(enumerate(self.cardLayout))
        for i,card in reversed(self.cards):
            if self.flags[i]:
                Rs.future(lambda card=card:Scenes.chessgameScene.player.addCardToHand(card),100*i)
        Scenes.chessgameScene.handleCommand()
        Rs.setCurrentScene(Scenes.chessgameScene)
    def initOnce(self):
        return

    def init(self):
        return
    
    def update(self):
        DebugManager.mouseUpdate()
        Scenes.chessgameScene.player.hands.adjustLayout()
        self.button.update()
        if self.checkboxs:
            for checkbox in self.checkboxs:
                checkbox.update()
            for i,card in enumerate(self.cardLayout):
                if card.isJustClicked():
                    self.checkboxs[i].toggleCheck()
        return
    
    def draw(self):
        GUIManager.drawBg()
        Scenes.chessgameScene.filter.draw()
        Scenes.chessgameScene.player.hands.draw()
        Scenes.chessgameScene.player.manaBoard.draw()
        Scenes.chessgameScene.board.draw()
        self.cardLayout.draw()
        for checkbox in self.checkboxs:
            checkbox.draw()
        self.button.draw()
        self.title.draw()
        return
    

# 씬들을 관리하는 클래스 정의
class Scenes:
    """
    게임에서 사용되는 씬들을 관리하는 클래스입니다.
    """
    # 체스 게임 씬을 속성으로 설정
    chessgameScene = chessgameScene()
    mainMenuScene = mainMenuScene()
    charaChoiceScene = charaChoiceScene()
    cardGalleryScene = cardGalleryScene()
    settingScene = settingScene()