from REMOLib import *
from myUtils import *

class mainMenuScene(Scene):
    def initOnce(self):


        return

    def init(self):
        from scenes import Scenes
        self.title = textObj(REMOLocalizeManager.getText("game_title"), size=60, color=GUIManager.textColor)
        self.gameButton = monoTextButton(REMOLocalizeManager.getText("chess_game"),size=40, color=GUIManager.textColor)
        self.gameButton.connect(lambda: Rs.setCurrentScene(Scenes.charaChoiceScene))
        self.helpButton = monoTextButton(REMOLocalizeManager.getText("help"),size=40, color=GUIManager.textColor)
        self.configButton = monoTextButton(REMOLocalizeManager.getText("config"),size=40, color=GUIManager.textColor)
        def attachConfigIcon(obj):
            obj.clearChilds(1)
            configIcon = imageObj(Icons.GEAR,scale=0.4)
            configIcon.colorize(GUIManager.textColor)
            configIcon.setParent(obj,depth=1)
            configIcon.midleft = obj.offsetRect.midright + RPoint(5,-3)
        attachConfigIcon(self.configButton)

        self.configButton.connect(lambda: Rs.setCurrentScene(Scenes.settingScene))
        self.cardGalleryButton = monoTextButton(REMOLocalizeManager.getText("card_gallery"),size=40, color=GUIManager.textColor)
        self.cardGalleryButton.connect(lambda: Rs.setCurrentScene(Scenes.cardGalleryScene))
        self.exitButton = monoTextButton(REMOLocalizeManager.getText("exit"),size=40, color=GUIManager.textColor)
        self.exitButton.connect(REMOGame.exit)
        self.buttons = layoutObj(childs=[self.gameButton,self.helpButton,self.cardGalleryButton,self.configButton,self.exitButton],spacing=20)

        Rs.changeMusic("bgm1.mp3")
        self.buttons.midright = Rs.screenRect().midright + RPoint(-300,0)
        self.buttons.slidein()
        self.title.midtop = Rs.screenRect().midtop + RPoint(0, 150)
        self.title.slidein()
        self.title.apply_effect(FloatingEffect)

        return

    def update(self):
        from debug import DebugManager
        self.buttons.update()
        DebugManager.mouseUpdate()
        return

    def draw(self):
        GUIManager.drawBg()
        self.buttons.draw()
        self.title.draw()
        return

class cardGalleryScene(Scene):
    columns = 4
    horizontal_spacing = 30
    vertical_spacing = 40

    def initOnce(self):
        from scenes import Scenes
        self.bg = rectObj(Rs.screenRect().inflate(-200, -160), color=Cs.black, alpha=180, radius=40)
        self.bg.center = Rs.screenRect().center

        self.title = textObj(REMOLocalizeManager.getText("card_gallery"), size=60, color=GUIManager.textColor)

        def _adjustTitle(obj):
            obj.midtop = self.bg.midtop + RPoint(0, 40)

        self.title.localize("card_gallery", callback=_adjustTitle)
        self.title.midtop = self.bg.midtop + RPoint(0, 40)

        self.backButton = imageButton(Icons.RETURN, scale=1.2)
        self.backButton.connect(lambda: Rs.setCurrentScene(Scenes.mainMenuScene))
        self.backButton.colorize(GUIManager.textColor)
        self.backButton.topright = self.bg.topright


        self.galleryLayout = None
        self.cardEntries = []
        self.previewCard = None

        return

    def _sort_key(self, item):
        key = item[0]
        if isinstance(key, (int, float)):
            return key
        try:
            return int(key)
        except (TypeError, ValueError):
            return str(key)

    def _createRow(self, cards):
        row_layout = layoutObj(childs=list(cards), spacing=self.horizontal_spacing, isVertical=False)
        row_layout.adjustLayout()
        return row_layout

    def _showPreview(self, card_data):
        preview = cardObj.from_dict(dict(card_data))
        preview.resize(cardObj.big_size)
        preview.midright = self.bg.midright + RPoint(-140, 0)
        self.previewCard = preview

    def _buildGallery(self):
        cards = dataManager.getCardData()
        items = sorted(cards.items(), key=self._sort_key)

        self.cardEntries = []
        rows = []
        current_row = []

        for key, value in items:
            card_payload = dict(value)
            card_payload["num"] = key
            gallery_card = cardObj.from_dict(dict(card_payload))
            self.cardEntries.append({"card": gallery_card, "data": card_payload})
            current_row.append(gallery_card)

            if len(current_row) == self.columns:
                rows.append(self._createRow(current_row))
                current_row = []

        if current_row:
            rows.append(self._createRow(current_row))

        scroll_width = max(640, self.bg.rect.w - cardObj.big_size.width - 360)
        scroll_height = max(400, self.bg.rect.h - 220)
        viewport_rect = pygame.Rect(0, 0, scroll_width, scroll_height)

        self.galleryLayout = scrollLayout(viewport_rect, childs=rows, spacing=self.vertical_spacing, isVertical=True, scrollColor=GUIManager.textColor, enableMouseWheel=True,thickness=20)
        self.galleryLayout.pad = RPoint(40, 0)
        self.galleryLayout.pos = self.bg.pos + RPoint(100, 140)
        self.galleryLayout.adjustLayout()
        self.galleryLayout.scrollBar.color = GUIManager.textColor
        self.galleryLayout.scrollBar.value = 0
        self.galleryLayout.scrollBar.adjustObj()

        if self.cardEntries:
            self._showPreview(self.cardEntries[0]["data"])
        else:
            self.previewCard = None

    def init(self):
        self.bg.center = Rs.screenRect().center
        self.backButton.topright = self.bg.topright
        self.title.midtop = self.bg.midtop + RPoint(0, 40)

        self._buildGallery()

        self.bg.alpha = 0
        self.bg.easeout("alpha", 180, steps=20)
        self.title.alpha = 0
        self.title.easeout("alpha", 255, steps=20)
        self.backButton.alpha = 0
        self.backButton.easeout("alpha", 255, steps=20)
        if self.galleryLayout:
            self.galleryLayout.alpha = 0
            self.galleryLayout.easeout("alpha", 255, steps=20)
        if self.previewCard:
            self.previewCard.alpha = 0
            self.previewCard.easeout("alpha", 255, steps=20)

        return

    def update(self):
        from scenes import Scenes

        self.backButton.update()
        if self.galleryLayout:
            self.galleryLayout.enableMouseWheel = self.galleryLayout.collideMouse()
            self.galleryLayout.update()

        if Rs.userJustLeftClicked():
            for entry in self.cardEntries:
                if entry["card"].collideMouse():
                    self._showPreview(entry["data"])
                    break

        if Rs.userJustPressed(pygame.K_ESCAPE):
            Rs.setCurrentScene(Scenes.mainMenuScene)

        return

    def draw(self):
        GUIManager.drawBg()
        self.bg.draw()
        if self.galleryLayout:
            self.galleryLayout.draw()
        if self.previewCard:
            self.previewCard.draw()
        self.title.draw()
        self.backButton.draw()

        return

class settingSheets:
    resolution = {
        "2560x1440":(2560,1440),
        "1920x1080":(1920,1080),
        "1280x720":(1280,720)
    }
    fullscreen = {
        "FullScreen":True,
        "Window":False
    }
    language = {
        "English":"en",
        "한국어":"kr",
        "日本語":"jp",
        "中文":"cn",
    }
class settingScene(Scene):
    def initOnce(self):
        from scenes import Scenes
        self.bg = rectObj(Rs.screenRect().inflate(-100,-50),color=Cs.black,alpha=150)
        self.title = textObj("설정",size=60,color=Cs.white)
        def adjustTitle(obj):
            obj.midtop = Rs.screenRect().midtop + RPoint(0,50)
        self.title.localize("config",callback=adjustTitle)
        self.title.midtop = Rs.screenRect().midtop + RPoint(0,50)
        self.backButton = imageButton(Icons.RETURN,scale=1.2)
        self.backButton.connect(lambda: Rs.setCurrentScene(Scenes.mainMenuScene))
        self.backButton.colorize(GUIManager.textColor)
        self.backButton.bottomright = Rs.screenRect().bottomright + RPoint(-110,-110)

        self.resolutionLabel = textObj("해상도",size=40,color=Cs.white)
        self.resolutionLabel.localize("resolution")
        self.resolutionOptions = Rs.makeOptionLayout(settingSheets.resolution,settingFunc=Rs.setWindowRes)


        self.fullscreenLabel = textObj("전체 화면 모드",size=40,color=Cs.white)
        self.fullscreenLabel.localize("fullscreen_mode")
        self.fullscreenOptions = Rs.makeOptionLayout(settingSheets.fullscreen,settingFunc=Rs.setFullScreen)

        self.musicVolumeLabel = textObj("음악 볼륨",size=40,color=Cs.white)
        self.musicVolumeLabel.localize("music_volume")
        self.musicVolumeSlider = Rs.musicVolumeSlider(length=600,color=Cs.cyan)
        if Rs.isMuted():
            self.musicVolumeSlider.color = Cs.grey
        def _musicCallback():
            if Rs.isMuted():
                GUIManager.toggleMute()
        self.musicVolumeSlider.callback = _musicCallback

        self.seVolumeLabel = textObj("효과음 볼륨",size=40,color=Cs.white)
        self.seVolumeLabel.localize("se_volume")
        self.seVolumeSlider = Rs.SEVolumeSlider(length=600,color=Cs.orange,testFunc=lambda:Rs.playSound('move-chess.wav', volume=0.9))

        self.languageLabel = textObj("언어",size=40,color=Cs.white)
        self.languageLabel.localize("language")
        saved_language = load_language_config(REMOLocalizeManager.getLanguage())

        def set_language(l):
            save_language_config(l)
            REMOLocalizeManager.setLanguage(l)
            dataManager.init()

        self.languageOptions = Rs.makeOptionLayout(
            settingSheets.language,
            curState=saved_language,
            settingFunc=set_language,
        )


        self.leftLayout = layoutObj(childs=[self.resolutionLabel,self.resolutionOptions,
                                            self.fullscreenLabel,self.fullscreenOptions,
                                            self.musicVolumeLabel,self.musicVolumeSlider,
                                            self.seVolumeLabel,self.seVolumeSlider,
                                            self.languageLabel,self.languageOptions
                                             ],spacing=30)
        self.leftLayout.midleft = Rs.screenRect().midleft + RPoint(100,0)


        return
    
    def init(self):
        self.bg.alpha = 0
        self.bg.easeout("alpha",150,steps=20)
        self.backButton.alpha = 0
        self.backButton.easeout("alpha",255,steps=20)
        self.title.alpha = 0
        self.title.easeout("alpha",255,steps=20)
        self.leftLayout.alpha = 0
        self.leftLayout.easeout("alpha",255,steps=20)

        return
    
    def update(self):
        self.backButton.update()
        self.leftLayout.update()
        return
    
    def draw(self):
        GUIManager.drawBg()
        self.bg.draw()
        self.title.draw()
        self.leftLayout.draw()
        self.backButton.draw()
        return
    




class myButton(rectObj,clickable):
    buttonSize = pygame.Rect(0,0,300,300)
    def __init__(self,text="girl1",enabled=True,func=lambda:None):
        from scenes import Scenes
        super().__init__(self.buttonSize,color=Cs.darkgray,radius=20)
        self.text = text
        chara = imageObj(f"{text}_thm.png",self.buttonSize)
        chara.setParent(self,depth=1)
        border = imageObj("border.png",self.buttonSize)
        border.setParent(self,depth=1)
        hoverObj = rectObj(self.buttonSize,color=Cs.white,alpha=100)
        hoverObj.setParent(self,depth=0)

        ##그림자 오브젝트 생성
        self.shadow = imageObj('REMO_rectShadow.png')
        self.shadow.alpha = 255
        self.shadow.rect = self.offsetRect.inflate(28,28)
        self.shadow.rect.midtop = self.offsetRect.midtop
        self.shadow.setParent(self,depth=-1)

        self.shadow1 = rectObj(self.offsetRect,color=Cs.black,radius=20)
        self.shadow1.pos = RPoint(1,1)
        self.shadow1.alpha = 100
        self.shadow1.setParent(self,depth=-1)
        self.enabled = enabled
        if not self.enabled:
            self.hideChilds(0)

        self.func = []
        self.connect(lambda:Scenes.charaChoiceScene.showGirl(text))

class charaChoiceScene(Scene):
    slidein_speed = 3
    def initOnce(self):
        from scenes import Scenes
        self.db = REMODatabase.loadExcel("chara_choice.xlsx")[REMOLocalizeManager.getLanguage()]
        self.backButton = imageButton(Icons.RETURN,scale=1.5)
        self.backButton.connect(lambda: Rs.setCurrentScene(Scenes.mainMenuScene))
        self.backButton.colorize(GUIManager.textColor)
        self.backButton.bottomright = Rs.screenRect().bottomright + RPoint(-40,-40)
        self.available_girls = ["girl1","girl2"] if DEMO else ["girl1","girl2","girl3","girl4"]
        self.buttons = layoutObj(childs=[myButton(girl_id) for girl_id in self.available_girls],spacing=20,isVertical=False)
        

        self.text = ""
        self.girl = None

        return
    
    def showGirl(self,text):

        from scenes import Scenes, chessgameScene
        self.text = text
        self.girl = imageObj(f"{text}_default.png",scale=1)
        self.girl.midright = Rs.screenRect().midright + RPoint(-250,300)
        girl_shadow = Rs.copyImage(self.girl)
        girl_shadow.colorize(Cs.grey75)
        girl_shadow.pos = RPoint(-100,0)
        girl_shadow.alpha = 200
        girl_shadow.setParent(self.girl,depth=-1)
        girl_shadow.slidein(delta=RPoint(-50,0),speed=self.slidein_speed)
        self.girl.slidein(speed=self.slidein_speed)
        self.title = textObj(self.db[text]['title'],size=80)
        self.title.midtop = Rs.screenRect().midtop + RPoint(-200,50)
        self.title.slidein(speed=self.slidein_speed)
        self.info = longTextObj(self.db[text]['info'],size=40,textWidth=800)
        self.info.midtop = self.title.midbottom + RPoint(0,70)
        self.info.slidein(speed=self.slidein_speed)
        self.skill = textObj(f"{REMOLocalizeManager.getText('chess_skill')} : {self.db[text]['skill']}",size=40)
        self.skill.midtop = self.info.midbottom + RPoint(0,70)
        self.skill.slidein(speed=self.slidein_speed)
        self.personality = longTextObj(f"{REMOLocalizeManager.getText('personality')} : {self.db[text]['personality']}",size=40,textWidth=800)
        self.personality.midtop = self.skill.midbottom + RPoint(0,70)
        self.personality.slidein(speed=self.slidein_speed)

        self.playButton = textButton(REMOLocalizeManager.getText("start_game"),pygame.Rect(0,0,300,100),size=40)
        self.playButton.midright = Rs.screenRect().midright + RPoint(-40,0)
        self.playButton.connect(lambda: Rs.setCurrentScene(difficultySettingScene(text,greeting=self.db[text]['greeting'])))
        self.playButton.slidein(speed=self.slidein_speed)


    def init(self):
        self.buttonsLabel = textObj(REMOLocalizeManager.getText("chara_choice"),size=40)

        Rs.changeMusic("bgm1.mp3")
        self.db = REMODatabase.loadExcel("chara_choice.xlsx")[REMOLocalizeManager.getLanguage()]

        self.backButton.alpha = 0
        self.backButton.easeout("alpha",255,steps=20)
        if not self.text or self.text not in self.available_girls:
            self.text = self.available_girls[0]
        self.showGirl(self.text)
        self.buttons.bottomleft = Rs.screenRect().bottomleft + RPoint(40,-40)
        self.buttonsLabel.bottomleft = self.buttons.pos + RPoint(0,-40)
        self.buttons.slidein(speed=self.slidein_speed)
        self.buttonsLabel.slidein(speed=self.slidein_speed)
        return

    def update(self):
        self.backButton.update()
        self.buttons.update()
        if self.girl:
            self.playButton.update()
        return

    def draw(self):
        GUIManager.drawBg()    
        self.backButton.draw()
        self.buttons.draw()
        self.buttonsLabel.draw()
        if self.girl:
            self.girl.draw()
            self.title.draw()
            self.info.draw()
            self.skill.draw()
            self.personality.draw()
            self.playButton.draw()
        return    
    
class difficultySettingScene(Scene):
    init_mana = [50,30,20,10,0]
    init_card = [5,4,3,1,0]
    temp_list = ["매우 쉬움","쉬움","보통","어려움","매우 어려움"]
    temp_caption = ["체스판을 압도적인 힘으로 지배할 수 있습니다.",
                    "초보자가 체스를 즐기기에 적합합니다.",
                    "편안하게 트롤 체스를 즐길 수 있습니다.",
                    "체스 실력에 자신 있는 사람에게 적합합니다.",
                    "가장 순정 체스에 가깝습니다."]
    temp_talk = "여기 자리가 비었네요."
    difficulty_color = [Cs.green,Cs.yellow,Cs.orange,Cs.red,Cs.violet]
    def __init__(self,girl_id,difficulty=2,greeting=None):
        super().__init__()
        from scenes import Scenes
        self.playButton = textButton(REMOLocalizeManager.getText("start_game"),pygame.Rect(0,0,300,100),size=40)
        self.playButton.midright = Rs.screenRect().midright + RPoint(-40,0)
        self.girl_id = girl_id
        self.playButton.connect(self.gameStart)
        self.playButton.slidein()
        self.slider = sliderObj(RPoint(200,200),1200,isVertical=False,thickness=20,color=Cs.orange,value=difficulty/4)

        self.slider.slidein()
        self.slider.callback = self.selectDifficulty
        self.difficulty = -1
        self.selectDifficulty()
        self.userIsWhite = True
        self.colorTitle = textObj("Choose Your Side", size=50)
        self.colorTitle.midtop = self.playButton.midbottom + RPoint(-40, 160)
        self.colorTitle.slidein()
        button_rect = pygame.Rect(0, 0, 260, 90)
        self.whiteButton = textButton("White", button_rect.copy(), size=40)
        self.blackButton = textButton("Black", button_rect.copy(), size=40)
        self.whiteButton.midtop = self.colorTitle.midbottom + RPoint(-170, 40)
        self.blackButton.midtop = self.colorTitle.midbottom + RPoint(170, 40)
        self.whiteButton.connect(lambda: self.setPlayerColor(True))
        self.blackButton.connect(lambda: self.setPlayerColor(False))
        self.whiteButton.slidein()
        self.blackButton.slidein()
        self.setPlayerColor(self.userIsWhite)
        self.title = textObj(REMOLocalizeManager.getText("difficulty"),size=60)
        self.title.midtop = self.slider.midtop + RPoint(70,-150)
        self.title.slidein()
        self.returnButton = imageButton(Icons.RETURN,scale=1.5)
        self.returnButton.connect(lambda: Rs.setCurrentScene(Scenes.charaChoiceScene))
        self.returnButton.colorize(GUIManager.textColor)
        self.returnButton.bottomright = Rs.screenRect().bottomright + RPoint(-40,-40)
        self.textBubble = textBubbleObj(greeting,pos=RPoint(2110,382),size=30,textWidth=400)
        Scenes.charaChoiceScene.girl.alpha = 255
        Scenes.charaChoiceScene.girl.jump("pos",Scenes.charaChoiceScene.girl.pos+RPoint(0,-30),steps=9)
        Scenes.charaChoiceScene.girl.setImage(f"{self.girl_id}_normal.png")
        Rs.future(self.girlTalked,delay=self.textBubble.liveTimer.duration)
    

        return

    def init(self):
        return
    
    def gameStart(self):
        from scenes import Scenes, chessgameScene
        new_chessgameScene = chessgameScene(self.girl_id,self.initCardCount,self.initMana,self.difficulty, userIsWhite=self.userIsWhite)
        Scenes.chessgameScene = new_chessgameScene
        Rs.transition(Scenes.chessgameScene)

    def setPlayerColor(self, is_white):
        self.userIsWhite = is_white
        selected_color = Cs.tiffanyBlue
        unselected_color = Cs.grey
        if is_white:
            self.whiteButton.color = selected_color
            self.blackButton.color = unselected_color
        else:
            self.whiteButton.color = unselected_color
            self.blackButton.color = selected_color

    def selectDifficulty(self):
        difficulty = self.difficulty
        self.difficulty = round(self.slider.value * 4)
        if self.difficulty == difficulty:
            return
        self.temp_list = [REMOLocalizeManager.getText("very_easy"),REMOLocalizeManager.getText("easy"),REMOLocalizeManager.getText("normal"),REMOLocalizeManager.getText("hard"),REMOLocalizeManager.getText("very_hard")]
        self.difficultyTitle = textObj(f"{self.temp_list[self.difficulty]}",size=60,color=self.difficulty_color[self.difficulty])
        self.difficultyTitle.midtop = self.slider.midbottom + RPoint(0,50)
        self.temp_caption = [REMOLocalizeManager.getText("very_easy_desc"),REMOLocalizeManager.getText("easy_desc"),REMOLocalizeManager.getText("normal_desc"),REMOLocalizeManager.getText("hard_desc"),REMOLocalizeManager.getText("very_hard_desc")]
        self.caption = textObj(self.temp_caption[self.difficulty],size=40,color=Cs.grey75)
        self.caption.midtop = self.difficultyTitle.midbottom + RPoint(0,50)

        self.initCardCount = self.init_card[self.difficulty]
        self.initMana = self.init_mana[self.difficulty]
        self.initCardLabel = textObj(f"- {REMOLocalizeManager.getText('starting_cards')} : {self.initCardCount}",size=40)
        self.initManaLabel = textObj(f"- {REMOLocalizeManager.getText('starting_mana')} : {self.initMana}",size=40)
        self.labelLayout = layoutObj(pos=RPoint(647,640),childs=[self.initCardLabel,self.initManaLabel],spacing=60)
        cards = []
        for i in range(self.init_card[self.difficulty]):
            card = rectObj(cardObj.small_size,color=Cs.grey25,edge=5, radius=50)
            icon = imageObj(Icons.CHESS_KNIGHT,scale=1)
            icon.colorize(Cs.grey75)
            icon.center = card.offsetRect.center + RPoint(0,-30)
            icon.setParent(card)
            card.merge()
            cards.append(card)
        self.cardPreview = layoutObj(childs=cards,spacing=10,isVertical=False)
        self.cardPreview.center = RPoint(767,1077)

        self.difficultyTitle.slidein()
        self.caption.slidein()
        self.labelLayout.slidein()
        self.cardPreview.slidein()

    def girlTalked(self):
        from scenes import Scenes
        if Scenes.charaChoiceScene.text == self.girl_id:
            Scenes.charaChoiceScene.girl.setImage(f"{self.girl_id}_default.png")



    def update(self):
        self.playButton.update()
        self.slider.update()
        self.slider.updateByMouseWheel(scrollSpeed=5)
        self.returnButton.update()
        self.whiteButton.update()
        self.blackButton.update()
        self.textBubble.updateText()
        from debug import DebugManager
        DebugManager.mouseUpdate()
        return
    
    def draw(self):
        GUIManager.drawBg()
        self.playButton.draw()
        self.returnButton.draw()
        self.title.draw()
        self.caption.draw()
        self.slider.draw()
        self.difficultyTitle.draw()
        self.labelLayout.draw()
        self.cardPreview.draw()
        self.textBubble.draw()
        from scenes import Scenes
        Scenes.charaChoiceScene.girl.draw()
        self.colorTitle.draw()
        self.whiteButton.draw()
        self.blackButton.draw()

        return



class scriptScene(Scene):

    def __init__(self,scriptName,callback=lambda:None):
        super().__init__()
        REMODatabase.loadScript(scriptName)
        self.renderer = scriptRenderer(scriptName,endFunc=callback)

    def initOnce(self):
        return

    def init(self):
        return

    def update(self):
        self.renderer.update()
        if Rs.userJustRightClicked():
            print(Rs.mousePos())
        return

    def draw(self):
        self.renderer.draw()
        return
