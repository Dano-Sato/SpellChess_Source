from REMOLib import *
from myUtils import *
from myChess import *



# 플레이어 클래스 정의
class Player():
    """
    플레이어의 마나와 손패(카드)를 관리하는 클래스입니다.
    """

    handArea = pygame.Rect(1090,770, 1500, 700) # 손패 영역
    manacounter_text_size = 45


    def __init__(self, mana=0):
        from scenes import Scenes
        """
        플레이어 객체를 초기화합니다.

        Args:
            mana (int, optional): 초기 마나 값. 기본값은 0입니다.
        """
        # 플레이어의 마나 초기화 (은닉화된 속성)
        self.__mana = mana

        # 마나 보드 이미지 객체 생성 및 위치 설정
        self.manaBoard = imageObj("manaBoard.png", scale=0.3)
        self.manaBoard.midleft = Scenes.chessgameScene.divider.bottomleft + RPoint(0, -5)

        # 마나 카운터 텍스트 객체 생성 및 위치 설정
        self.manaCounter = textObj(str(mana), size=self.manacounter_text_size)
        self.manaCounter.setParent(self.manaBoard)
        self.manaCounter.center = self.manaBoard.offsetRect.center

        # 플레이어의 손에 들고 있는 카드 레이아웃 생성
        self.hands = cardLayout(RPoint(1140,880), maxWidth=1100)
        self.drawCost = 1
        self.shuffleCost = 1

        buttonSize= pygame.Rect(0,0,250,70)
        # 카드 뽑기 버튼 생성
        self.drawButton = textButton(REMOLocalizeManager.getText("draw_card"),buttonSize,color=Cs.black,size=35)
        self.drawButton.connect(self.drawCard)  
        self.drawCostLabel = textObj(f"{REMOLocalizeManager.getText('mana')}:{self.drawCost}",size=35)
        self.drawCostLabel.midtop = self.drawButton.offsetRect.midbottom + RPoint(0,20)
        self.drawCostLabel.setParent(self.drawButton,depth=2)

        # 카드 셔플 버튼 생성
        self.shuffleButton = textButton(REMOLocalizeManager.getText("shuffle"),buttonSize,color=Cs.black,size=35)
        self.shuffleButton.connect(self.shuffleCard)
        self.shuffleCostLabel = textObj(f"{REMOLocalizeManager.getText('mana')}:{self.shuffleCost}",size=35)
        self.shuffleCostLabel.midtop = self.shuffleButton.offsetRect.midbottom + RPoint(0,20)
        self.shuffleCostLabel.setParent(self.shuffleButton,depth=2)

        spacer = graphicObj(pygame.Rect(0,0,100,50))

        self.resignButton = textButton(REMOLocalizeManager.getText("resign"),buttonSize,color=Cs.black,size=35)
        self.resignButton.color = Cs.dark(Cs.red)
        self.resignButton.textColor = Cs.grey75
        self.resignButton.connect(Scenes.chessgameScene.resign)


        self.buttons = layoutObj(pos=RPoint(0,0),spacing=80,childs=[self.drawButton,self.shuffleButton,spacer,self.resignButton])
        self.buttons.topright = Rs.screenRect().midright + RPoint(-20,150)


        ## 이벤트 처리 블록


        # 다음 턴 이벤트에 마나 증가 함수 등록
        Scenes.chessgameScene.board.addEvent(chessEvent.NEXTTURN, self.increaseMana)


    def increaseMana(self):
        self.setMana(self.getMana() + 1)



    def update(self):
        """
        플레이어 상태를 업데이트하고 입력을 처리합니다.
        """
        # 손패의 레이아웃 조정
        self.hands.adjustLayout()
        # 카드의 드래그 앤 드롭 기능 처리
        self.handleCardDragAndDrop()

        self.buttons.update()

    def drawCard(self):
        '''
        덱에서 카드를 뽑습니다.
        '''
        if self.getMana() < self.drawCost:
            self.lackManaPopup()
            return
        
        self.setMana(self.getMana() - self.drawCost)
        self.addRandomCardToHand()

        self.setDrawCost(self.drawCost+1)

    def addRandomCardToHand(self):
        card = self.getRandomCard()
        self.addCardToHand(card)    
    
    def addCardToHand(self,card:cardObj):
        card.pos = RPoint(self.hands.maxWidth, 0)
        card.alpha=0
        card.easeout("alpha",255,steps=15)
        card.setParent(self.hands)           
        Rs.playSound("cardDraw.wav",volume=0.7)

    def getRandomCard(self):
        # 카드 데이터에서 랜덤한 카드 선택
        random_num = random.choice(list(dataManager.getCardData().keys()))
        # 선택된 카드 데이터로부터 카드 객체 생성
        return self.getCard(random_num)

    def setDrawCost(self,cost):
        self.drawCost = cost
        self.drawCostLabel.text = f"{REMOLocalizeManager.getText('mana')}:{self.drawCost}"

    def getCard(self,index):
        '''
        인덱스에 해당하는 카드 오브젝트를 반환합니다.
        '''
        card_data = dataManager.getCardData()[index]
        card_data["num"] = index
        # 선택된 카드 데이터로부터 카드 객체 생성
        card = cardObj.from_dict(card_data)
        return card


    def shuffleCard(self):
        '''
        덱에 손패를 넣고 섞은 뒤 다시 드로우합니다.
        '''
        if self.getMana() < self.shuffleCost:
            self.lackManaPopup()
            return
        
        self.setMana(self.getMana() - self.shuffleCost)
        cardCount = len(self.hands)
        print(cardCount)
        self.hands.clearChilds()
        
        for i in range(cardCount):
            Rs.future(self.addRandomCardToHand,100*i)


        self.setShuffleCost(self.shuffleCost+1)

    def setShuffleCost(self,cost):
        self.shuffleCost = cost
        self.shuffleCostLabel.text = f"{REMOLocalizeManager.getText('mana')}:{self.shuffleCost}"

    def draw(self):
        """
        플레이어 관련 UI 요소를 화면에 그립니다.
        """
        # 손패와 마나 보드 그리기
        self.hands.draw()
        self.manaBoard.draw()
        self.buttons.draw()


    def lackManaPopup(self):
        GUIManager.showText(REMOLocalizeManager.getText("not_mana"),steps=40)

    def dropCard(self,card:cardObj, index):
        '''
        카드를 드래그 & 드롭했을 때 실행되는 함수입니다.
        '''
        from scenes import Scenes

        GUIManager.releaseText()

        if self.handArea.collidepoint(Rs.mousePos().x, Rs.mousePos().y): #카드가 드롭된 위치가 손패 안에 있을 때
            self.returnCard(card,index)
            return
        if self.getMana() < card.cost: # 마나가 부족할 때   
            self.returnCard(card,index)
            self.lackManaPopup()
            return
        
        if Scenes.chessgameScene.board.isUserTurn() == False:
            self.returnCard(card,index)
            GUIManager.showPopup("상대의 턴에는 카드를 사용할 수 없습니다.")
            return
        
        #카드 사용
        self.setMana(self.getMana() - card.cost)
        Scenes.chessgameScene.recordCardPlayed()
        Rs.playSound("cardUsed.wav",volume=0.7)
        Scenes.chessgameScene.initSpellMode(card,index)



        print("card dropped")
        print(len(self.hands))

    def returnCard(self,card:cardObj,index):
        '''
        카드를 손패로 되돌립니다.
        '''
        p = card.pos
        card.pos = p - self.hands.pos
        card.y = 0
        card.setParent(self.hands, index=index)

    def handleCardDragAndDrop(self):
        """
        카드의 드래그 앤 드롭 기능을 처리합니다.
        """
        # 손패의 자식 객체들(카드들)을 가져옴
        hands_children = self.hands.getChilds()
        for i, card in enumerate(hands_children):
            # 카드가 클릭되었을 때
            if card.isJustClicked():
                # 드래그된 객체로 설정하고 부모 설정 해제
                Rs.draggedObj = card
                card.setParent(None)
                GUIManager.showText(REMOLocalizeManager.getText("card_desc"),steps=40)

                # 드롭 함수 설정
                Rs.dropFunc = lambda: self.dropCard(card, i)
                break

    def getMana(self):
        """
        현재 마나 값을 반환합니다.

        Returns:
            int: 현재 마나.
        """
        # 현재 마나 반환
        return self.__mana

    def setMana(self, mana):
        """
        마나를 설정하고 마나 카운터를 업데이트합니다.

        Args:
            mana (int): 설정할 마나 값.
        """
        previous_mana = getattr(self, "_Player__mana", 0)
        # 마나 설정 및 마나 카운터 업데이트
        self.__mana = mana
        from scenes import Scenes
        delta = previous_mana - mana
        if delta > 0:
            if hasattr(Scenes, "chessgameScene") and hasattr(Scenes.chessgameScene, "recordManaSpend"):
                Scenes.chessgameScene.recordManaSpend(delta)
        self.manaCounter.text = str(mana)
        self.manaCounter.size=70
        self.adjustCounter()
        self.manaCounter.easeout(["size"],[self.manacounter_text_size],steps=10,on_update=self.adjustCounter)
    
    def adjustCounter(self):
        self.manaCounter.center = self.manaBoard.offsetRect.center


class girlEmotion(Enum):
    SHOCKED = "SHOCKED"
    START = "START"
    THINKING = "THINKING"
    BLUNDER = "BLUNDER"
    BOAST = "BOAST"
    MISTAKE = "MISTAKE"
    PRAISE = "PRAISE"

# 소녀 객체 클래스 정의
class girlObj():
    """
    게임 내 미소녀 캐릭터의 그래픽 표현과 상호작용을 관리하는 클래스입니다.
    """
    bubble_pos = RPoint(1720,320)  # 말풍선 위치
    girl_image_offset = {
        "girl1": RPoint(0,0),
        "girl2": RPoint(0,70),
        "girl3": RPoint(0,70),
        "girl4": RPoint(0,0),
    } # 소녀 이미지 위치 보정값
    girl_engine = {
        "girl1":engineType.MIRAI,
        "girl2":engineType.KAREN,
        "girl3":engineType.RIN,
        "girl4":engineType.VAMPIRE,
    }

    def __init__(self,id="girl1"):
        from scenes import Scenes
        import queue
        """
        소녀 객체를 초기화합니다.
        """

        # 소녀 이미지 객체 생성 및 위치 설정
        self.id = id
        self.girl = imageObj(f"{self.id}_default.png", scale=0.9)
        self.girl.center = Scenes.chessgameScene.divider.bottomleft + RPoint(250,100) + self.girl_image_offset[self.id]

        Scenes.chessgameScene.board.engine = self.girl_engine[self.id]

        # 소녀의 대화 말풍선 객체 초기화
        self.girlTalkObj = None
        self.emotionQueue = queue.Queue()
        self.prevEval = {'START': {'type': 'cp', 'value': 0}, 'END': {'type': 'cp', 'value': 0},'TOP':{}}

        self.loadScript(f"{self.id}_talk.xlsx")

    def girlTalk(self, text):
        """
        소녀가 대사를 말하도록 합니다.
        DEPRECATED

        Args:
            text (str): 소녀가 말할 대사.
        """
        # 대화 내용에 따른 말풍선 객체 생성
        self.girlTalkObj = textBubbleObj(text, self.bubble_pos, size=30, liveTimerDuration=2400,textWidth=400)
        # 소녀에게 점프 애니메이션 적용
        RMotion.jump(self.girl, RPoint(0, -30), gravity=2)
        # 소녀 이미지를 대화하는 표정으로 변경
        self.girl.setImage(f"{self.id}_normal.png")

    def showEmotion(self, emotion:girlEmotion,jump=30,duration=2400):
        """
        소녀의 감정을 변경합니다.

        Args:
            emotion (girlEmotion): 변경할 감정.
        """
        if emotion == girlEmotion.THINKING:
            jump = 10

        text = self.script.get(emotion.value,None)
        text = random.choice(text)
        # 감정에 따른 이미지 설정
        image = f"{self.id}_{emotion.value.lower()}.png"
        if not REMODatabase.assetExist(image):
            image = f"{self.id}_normal.png"
        self.girl.setImage(image)
        # 대화 내용에 따른 말풍선 객체 생성
        self.girlTalkObj = textBubbleObj(text, self.bubble_pos, size=30, liveTimerDuration=duration,textWidth=400)
        # 소녀에게 점프 애니메이션 적용
        RMotion.jump(self.girl, RPoint(0, -jump), gravity=4)
        from scenes import Scenes
        Scenes.chessgameScene.board.thinkTimer = RTimer(duration//2)

    def getEmotion(self,emotion:girlEmotion):


        self.emotionQueue.put(emotion)       

    def actByEvaluation(self,eval):
        ##TODO: 형세판단을 통해 소녀의 행동을 결정합니다.
        print("ACT BY",eval,"PREV",self.prevEval)
        gap_by_user = eval["START"]["value"]-self.prevEval["END"]["value"] # 유저 착수로 인한 형세 점수 변화
        gap_by_ai = eval["END"]["value"]-eval["START"]["value"] # AI 착수로 인한 형세 점수 변화
        print("GAP_USER",gap_by_user)
        print("GAP_AI",gap_by_ai)
        print("TOP",self.prevEval["TOP"])

        self.gap = {"USER":gap_by_user,"AI":gap_by_ai}

        self.evaluateGap(gap_by_user,gap_by_ai) # 형세를 평가하고 반응합니다.

        self.prevEval = eval # 이전 평가 저장

    def evaluateGap(self,gap_user,gap_ai):
        '''
        형세를 평가합니다.
        '''
        from scenes import Scenes
        if Scenes.chessgameScene.board.userIsWhite:
            gap_user = -gap_user
            gap_ai = -gap_ai
        
        delta = gap_user + gap_ai
        
        if delta>100:
            r = random.randint(0,100)
            if gap_user + r > 150:
                print("BLUNDER")
                self.getEmotion(girlEmotion.BLUNDER)
            else:
                print("BOAST")
                self.getEmotion(girlEmotion.BOAST)
        elif delta<0:
            print("PRAISE")
    def think(self):
        '''
        소녀가 고민합니다.
        '''
        try:
            if abs(self.gap["USER"])+abs(self.gap["AI"]) > 100:
                t = random.randint(600,3000)
            else:
                t = random.randint(300,2000)

            if t > 1000:
                self.showEmotion(girlEmotion.THINKING)
            from scenes import Scenes 
            Scenes.chessgameScene.board.thinkTimer = RTimer(t)
        except Exception as e:
            print(e)
            pass

    def shocked(self):
        '''
        소녀가 놀라는 행동을 합니다.
        '''
        self.showEmotion(girlEmotion.SHOCKED,jump=50,duration=1800) # 쇼크를 먹은 뒤
        t = random.randint(2000,4000)
        self.getEmotion(girlEmotion.THINKING) #생각에 빠진다.
        from scenes import Scenes 
        Scenes.chessgameScene.board.thinkTimer = RTimer(t)



    def loadScript(self, fileName):
        """
        소녀 캐릭터의 대사 스크립트 엑셀 파일을 불러와 딕셔너리 형태로 저장합니다.
        """

        file_path = REMODatabase.getPath(fileName)
        try:
            data = pandas.read_excel(file_path,sheet_name=REMOLocalizeManager.getLanguage()) # 엑셀 파일에서 데이터 불러오기
        except:
            data = pandas.read_excel(file_path,sheet_name="en")
        
        # Drop any rows that are entirely NaN to clean up data
        cleaned_data = data.dropna(how='all')

        # Convert each column to a key-value format where the key is the column name and the value is a list of non-null entries
        self.script = {col.upper(): cleaned_data[col].dropna().tolist() for col in cleaned_data.columns}        

        print(self.script)

    def __loadScript_DEPRECATED1(self, fileName):
        '''
        인게임 대화 데이터가 .txt 파일일때 사용되던 함수. 지금은 버려졌다.
        '''
        file_path = REMODatabase.getPath(fileName)
        self.script = {}        
        current_key = None
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()  # 줄 끝의 공백 제거
                
                if line.startswith('#'):  # 키값이 '#key'로 시작될 때
                    current_key = line[1:].upper()  # '#' 이후의 텍스트를 key로 설정
                    self.script[current_key] = []  # 해당 key에 빈 리스트를 생성
                elif current_key:  # 현재 key에 해당하는 값이 존재할 때
                    self.script[current_key].append(line)  # 값을 리스트에 추가

    def update(self):
        """
        소녀의 상태를 업데이트합니다.
        """
        # 말풍선 객체가 존재하면 업데이트
        if self.girlTalkObj != None:
            self.girlTalkObj.updateText()
            # 말풍선의 라이브 타이머가 종료되면
            if self.girlTalkObj.liveTimer.isOver():

                if not self.emotionQueue.empty():
                    emotion = self.emotionQueue.get()
                    self.showEmotion(emotion)
                else:
                    # 소녀 이미지를 웃는 표정으로 변경
                    self.girl.setImage(f"{self.id}_default.png")
                    # 말풍선 객체 제거
                    self.girlTalkObj = None
        else:
            if not self.emotionQueue.empty():
                emotion = self.emotionQueue.get()
                self.showEmotion(emotion)

    def draw(self):
        """
        소녀와 관련된 그래픽 요소를 그립니다.
        """
        # 소녀 화면 그리기
        self.girl.draw()
        # 말풍선 객체가 존재하면 그리기
        if self.girlTalkObj != None:
            self.girlTalkObj.draw()

