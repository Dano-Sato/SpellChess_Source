from REMOLib import *
import json
import os


LANGUAGE_CONFIG_PATH = "language_settings.json"
DEMO = True


def load_language_config(default_language: str = "en") -> str:
    """Load the saved language from the JSON configuration file.

    Args:
        default_language (str): The language code to fall back to when no
            configuration is available.

    Returns:
        str: The saved language code or the provided default value.
    """
    try:
        with open(LANGUAGE_CONFIG_PATH, "r", encoding="utf-8") as config_file:
            data = json.load(config_file)
            if isinstance(data, dict):
                language = data.get("language")
                if isinstance(language, str) and language:
                    return language
    except FileNotFoundError:
        pass
    except json.JSONDecodeError:
        pass

    return default_language


def save_language_config(language: str) -> None:
    """Persist the selected language to the JSON configuration file."""
    os.makedirs(os.path.dirname(LANGUAGE_CONFIG_PATH) or ".", exist_ok=True)
    with open(LANGUAGE_CONFIG_PATH, "w", encoding="utf-8") as config_file:
        json.dump({"language": language}, config_file, ensure_ascii=False, indent=2)


class myUtils:
    @classmethod
    def showPopupText(cls,text,*,color=Cs.white):
        temp_obj = textObj(text, size=100, color=color)
        temp_obj.center = Rs.screenRect().center
        temp_obj.easeout(["center","alpha","size"], [temp_obj.center+RPoint(0,-100),0,150], steps=50,show=True)

    @classmethod
    def pulse(cls,obj:imageObj):
        '''
        obj가 심장 박동처럼 잠깐 커졌다 작아지는 애니메이션을 실행합니다.
        '''
        s = obj.scale
        obj.scale = s*1.2
        obj.easeout("scale",s,steps=10)


# 게임 GUI 오브젝트들을 선언하고 관리하는 곳입니다.
class GUIManager:
    """
    GUI 관련 설정을 관리하는 클래스입니다.
    """
    # 보드 타일의 크기 설정
    tileSize = 120
    # 테마 색상 설정 (16진수 색상 코드 사용)
    themeColor = Cs.hexColor("111111")
    textColor = Cs.grey75

    @classmethod
    def showPopup(cls,text,*,size=50,color=Cs.black):
        popup = textButton(text, size=size, color=color,enabled=False)
        popup.center = Rs.screenRect().center
        Rs.fadeAnimation(popup, time=70)

    @classmethod
    def init(cls):
        cls.bg = imageObj("chess-room.png",Rs.screenRect())
        cls.filter = rectObj(Rs.screenRect(), color=Cs.black, alpha=150, radius=0)
        cls.text_popup = None

        cls.muteButton = imageButton(Icons.AUDIOON,scale=0.5)
        cls.muteButton.colorize(Cs.grey75)
        cls.muteButton.topright = Rs.screenRect().topright + RPoint(-10,10)
        cls.muteButton.connect(cls.toggleMute)
    
    @classmethod
    def toggleMute(cls):
        Rs.setMute(not Rs.isMuted())
        if Rs.isMuted():
            cls.muteButton.setImage(Icons.AUDIOOFF)
            cls.muteButton.hoverObj.setImage(Icons.AUDIOOFF)
            try:
                from scenes import Scenes
                Scenes.settingScene.musicVolumeSlider.easeout("color",Cs.grey,steps=20)
            except:
                pass
        else:
            cls.muteButton.setImage(Icons.AUDIOON)
            cls.muteButton.hoverObj.setImage(Icons.AUDIOON)
            try:
                from scenes import Scenes
                Scenes.settingScene.musicVolumeSlider.easeout("color",Cs.cyan,steps=20)
            except:
                pass


        cls.muteButton.colorize(Cs.grey75)


    @classmethod
    def drawBg(cls):
        cls.bg.draw()
        cls.filter.draw()        

    @classmethod
    def updateUtilities(cls):
        cls.muteButton.update()

    @classmethod
    def drawUtilities(cls):
        cls.muteButton.draw()

    @classmethod
    def showText(cls,text,*,size=30,color=Cs.grey75,steps=80):
        cls.releaseText()
        cls.text_popup = textObj(text, RPoint(141,1226), size=size, color=color)
        cls.text_popup.alpha = 0
        cls.text_popup.easeout(["alpha","pos"],[255,cls.text_popup.pos+RPoint(50,0)],steps=steps,show=True,revert=True)

    @classmethod
    def releaseText(cls):
        if cls.text_popup and cls.text_popup.onInterpolation():
            interpolateManager.release(cls.text_popup)
        




class dataType(Enum):
    DIFFICULTY = "difficulty"

# 데이터 매니저 클래스 정의
class dataManager:
    """
    게임에서 사용하는 데이터를 관리하는 클래스입니다.
    """

    # 카드 데이터를 저장할 클래스 변수 (은닉화)
    __cardData = {}
    __configData = {}
    __defaultConfig = {
        dataType.DIFFICULTY.value:2
    }
    __configPath = "config.pickle"

    @classmethod
    def getCardData(cls):
        """
        카드 데이터를 반환합니다.

        Returns:
            dict: 카드 데이터 딕셔너리.
        """
        # 카드 데이터 반환
        return cls.__cardData

    @classmethod
    def init(cls):
        """
        엑셀 파일로부터 데이터를 로드하여 초기화합니다.
        """
        # 엑셀 파일로부터 데이터 로드하여 카드 데이터 초기화
        db = REMODatabase.loadExcel("db.xlsx")
        cls.__cardData = db["cards_{0}".format(REMOLocalizeManager.getLanguage())]
        cls.loadConfig()

    @classmethod
    def setConfig(cls,key:dataType,value):
        cls.__configData[key.value] = value
        cls.saveConfig()
    
    @classmethod
    def saveConfig(cls):
        REMODatabase.saveData(cls.__configPath,cls.__configData)

    @classmethod
    def loadConfig(cls):
        try:
            cls.__configData = REMODatabase.loadData(cls.__configPath)
        except:
            cls.__configData = cls.__defaultConfig


# 카드 객체 클래스 정의
class cardObj(rectObj):
    """
    스펠 카드를 표현하는 그래픽 객체 클래스입니다.

    Attributes:
        small_size (pygame.Rect): 작은 사이즈의 카드 사각형.
    """

    # 작은 사이즈의 카드 사각형 정의
    small_size = pygame.Rect(0, 0, 270, 390)
    big_size = pygame.Rect(0, 0, 620,910)
    rarityColor = [Cs.burlywood, Cs.orange, Cs.salmon, Cs.light(Cs.blueviolet)]
    rarityText = ["N","R","SR","SSR"]

    @classmethod
    def getImage(cls, num):
        """
        카드 번호에 해당하는 이미지 파일명을 반환합니다.

        Args:
            num (int): 카드 번호.

        Returns:
            str: 이미지 파일명 또는 기본 아이콘.
        """
        # 카드 번호에 해당하는 이미지 파일명 생성
        my_image = f"card_{num}.png"
        # 이미지 파일이 존재하면 해당 파일명 반환, 없으면 기본 아이콘 반환
        if REMODatabase.assetExist(my_image):
            return my_image
        else:
            return Icons.CROSS

    def __init__(self, num, name, info, cost, query, rarity=0):
        """
        카드 객체를 초기화합니다.

        Args:
            num (int): 카드 번호.
            name (str): 카드 이름.
            info (str): 카드 설명.
            cost (int): 카드 비용.
            query (str): 카드 효과에 대한 쿼리.
            rarity (int, optional): 카드 희귀도. 기본값은 0입니다.
        """
        # 카드의 속성 초기화
        self.num = num
        self.rarity = rarity
        # 부모 클래스(rectObj)의 초기화 호출 (카드의 크기와 스타일 설정)
        super().__init__(pygame.Rect(0, 0, 700, 980), color=self.rarityColor[self.rarity], edge=5, radius=50)

        # 카드 이름 텍스트 객체 생성 및 위치 설정

        # 카드의 비용 토큰 객체 생성 및 부모 설정
        costToken = rectObj(pygame.Rect(10, 10, 150, 150), color=Cs.yellow, edge=5)
        costToken.setParent(self)

        self.name = name
        nameObj = textObj(name, size=70, color=Cs.black)
        if nameObj.width > self.rect.width - 180:
            nameObj.size = 70 * (self.rect.width - 180) // nameObj.width
        nameObj.midleft = costToken.midright + RPoint(20,0)
        nameObj.setParent(self)

        # 카드 이미지 객체 생성 및 위치 설정
        image = imageObj(self.getImage(num), pygame.Rect(0, 0, 500,500))
        image.midtop = self.offsetRect.midtop + RPoint(0, 120)
        image.setParent(self)

        # 카드 정보 텍스트 객체 생성 및 위치 설정
        info = longTextObj(info, textWidth=self.rect.width - 30, color=Cs.black, size=50)
        info.merge()
        if info.width > self.rect.width - 40:
            c = (self.rect.width - 40) / info.width
            info.rect = pygame.Rect(0, 0, c * info.rect.width, c * info.rect.height)
        info.pos = RPoint(15, image.rect.bottom + 10)
        info.setParent(self)

        rarityText = textObj(self.rarityText[self.rarity],size=70, color=Cs.black)
        rarityText.midtop = costToken.midbottom + RPoint(0, 40)
        rarityText.setParent(self)

        # 카드의 모든 요소를 하나의 이미지로 병합
        self.merge()

        # 카드의 크기를 작은 사이즈로 재설정
        self.rect = self.small_size
        # 카드의 쿼리 속성 설정
        self.query = query
        # 카드 비용 텍스트 객체 생성 및 위치 설정
        self.costObj = textObj(str(cost), size=20, color=Cs.black)
        self.costObj.setParent(self)
        self.setCost(cost)

    def setCost(self,cost):
        self.cost = cost
        self.costObj.text = str(cost)
        self.adjustCostObj()


    def adjustCostObj(self):
        c = int(self.rect.w * 0.12)
        self.costObj.size = int(c * 0.8)
        self.costObj.center = RPoint(c, c)


    def resize(self,rect):
        self.rect = rect
        self.adjustCostObj()


    @classmethod
    def from_dict(cls, data):
        """
        딕셔너리 데이터를 사용하여 카드 객체를 생성합니다.

        Args:
            data (dict): 카드 속성이 포함된 딕셔너리.

        Returns:
            cardObj: 생성된 카드 객체.
        """
        # 딕셔너리의 키-값 쌍을 **kwargs로 전달하여 카드 객체 생성
        return cls(**data)
