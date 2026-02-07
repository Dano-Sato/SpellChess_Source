from REMOLib import *
from myUtils import *

class DebugManager:
    ON_DEBUG = False
    CHECK_CARD_LIST = [5,27,28] # 손패에 추가할 카드 번호
    CHECK_CARD_RANGE = (1,2) # 손패에 추가할 카드 범위
    @staticmethod
    def debug_only(func):
        def wrapper(*args, **kwargs):
            if DebugManager.ON_DEBUG:
                return func(*args, **kwargs)
        return wrapper

    @classmethod
    @debug_only
    def gameInit(cls):
        from scenes import Scenes
        Scenes.chessgameScene.player.setMana(100)
        for i in range(*cls.CHECK_CARD_RANGE):
            card = Scenes.chessgameScene.player.getCard(i)
            card.setParent(Scenes.chessgameScene.player.hands)
        for i in cls.CHECK_CARD_LIST:
            card = Scenes.chessgameScene.player.getCard(i)
            card.setParent(Scenes.chessgameScene.player.hands)
        
        print(Scenes.chessgameScene.board.board.fen)
        

    @classmethod
    @debug_only
    def almostWin(cls):
        from scenes import Scenes
        # 매우 유리한 상황 배치
        Scenes.chessgameScene.board.board.set_fen("kn6/p7/8/8/8/8/8/RNBQKBNR w KQkq - 0 1")
        Scenes.chessgameScene.board._updateBoard()

    @classmethod
    @debug_only
    def gameUpdate(cls):
        from scenes import Scenes

        player = Scenes.chessgameScene.player
        # 'Z' 키가 눌렸을 때 디버그용 카드 추가
        if Rs.userJustPressed(pygame.K_z):
            # 카드 데이터에서 랜덤한 카드 선택
            random_num, random_card = random.choice(list(dataManager.getCardData().items()))
            random_card["num"] = random_num
            # 선택된 카드 데이터로부터 카드 객체 생성
            testCard = cardObj.from_dict(random_card)
            # 카드의 위치 설정 및 손패에 추가
            testCard.pos = RPoint(player.hands.maxWidth, 0)
            testCard.setParent(player.hands)
        if Rs.userJustPressed(pygame.K_x):
            player.setMana(999)
        cls.mouseUpdate()

    @classmethod
    @debug_only
    def mouseUpdate(cls):
        if Rs.userJustLeftClicked():
            print(Rs.mousePos())
###
