from scenes import *
from myUtils import load_language_config


# 메인 실행 부분
if __name__ == "__main__":
    """
    프로그램의 진입점으로, 게임 창을 설정하고 메인 루프를 실행합니다.
    """
    import multiprocessing
    multiprocessing.freeze_support()
    # 화면 설정
    window = REMOGame(window_resolution=(2560,1440), screen_size=(2560, 1440), fullscreen=False, caption="Troll Chess Sekai")
    # 현재 씬을 체스 게임 씬으로 설정
    #Rs.initCursor()
    GUIManager.init()

    # 번역 파일
    localization_db = REMODatabase.loadExcel("db.xlsx")["localization"]
    REMOLocalizeManager.importTranslations(localization_db)

    saved_language = load_language_config(REMOLocalizeManager.getLanguage())
    REMOLocalizeManager.setLanguage(saved_language)
    dataManager.init()
    Rs.set_cache_size(1000)
    Rs.defaultUpdate = GUIManager.updateUtilities
    Rs.defaultDraw = GUIManager.drawUtilities

    #신 선택
    #window.setCurrentScene(Scenes.chessgameScene)
    #window.setCurrentScene(scriptScene("girl1_1.scr",lambda:Rs.transition(Scenes.charaChoiceScene)))
    window.setCurrentScene(Scenes.mainMenuScene)
    # 게임 실행
    window.run()

    # 완료! 프로그램을 종료합니다.
