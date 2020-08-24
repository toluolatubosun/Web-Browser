import sys
import os
import json
from PyQt5.QtWidgets import (QWidget, QApplication,
                             QVBoxLayout, QHBoxLayout, QLineEdit, QTabBar, QLabel, QFrame, QStackedLayout,
                             QTabWidget, QPushButton, QShortcut, QKeySequenceEdit, QSplitter)
from PyQt5.QtGui import QIcon, QWindow, QImage, QKeySequence
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *


class AddressBar(QLineEdit):
    def __init__(self):
        super().__init__()

    def mousePressEvent(self, e):
        self.selectAll()


class App(QFrame):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Web Browser")
        self.setGeometry(0, 0, 1000, 1000)
        self.CreateApp()
        self.setWindowIcon(QIcon("logo.png"))

    def CreateApp(self):
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Create Tabs
        self.tabbar = QTabBar(movable=True, tabsClosable=True)
        self.tabbar.tabCloseRequested.connect(self.CloseTab)
        self.tabbar.tabBarClicked.connect(self.SwitchTab)
        self.tabbar.setDrawBase(False)
        self.tabbar.setCurrentIndex(0)

        self.shortCutNewTab = QShortcut(QKeySequence("Ctrl+T"), self)
        self.shortCutNewTab.activated.connect(self.AddTab)

        self.shortReload = QShortcut(QKeySequence("Ctrl+R"), self)
        self.shortReload.activated.connect(self.ReloadPage)

        # keep Track of Tabs
        self.tabCount = 0
        self.tabs = []

        # Setup tool Bar
        self.addressBar = AddressBar()
        self.addressBar.returnPressed.connect(self.BrowseTo)

        self.addTabButton = QPushButton("+")
        self.addTabButton.clicked.connect(self.AddTab)

        self.backButton = QPushButton("<")
        self.backButton.clicked.connect(self.GoBack)

        self.forwardButton = QPushButton(">")
        self.forwardButton.clicked.connect(self.GoFoward)

        self.reloadButton = QPushButton("~")
        self.reloadButton.clicked.connect(self.ReloadPage)

        self.toolBar = QWidget()
        self.toolBar.setObjectName("ToolBar")
        self.toolBarLayout = QHBoxLayout()
        self.toolBar.setLayout(self.toolBarLayout)

        self.toolBarLayout.addWidget(self.backButton)
        self.toolBarLayout.addWidget(self.forwardButton)
        self.toolBarLayout.addWidget(self.reloadButton)
        self.toolBarLayout.addWidget(self.addressBar)
        self.toolBarLayout.addWidget(self.addTabButton)

        #set main view
        self.container = QWidget()
        self.container.layout = QStackedLayout()
        self.container.setLayout(self.container.layout)

        #Add Tabs to layout and show
        self.layout.addWidget(self.tabbar)
        self.layout.addWidget(self.toolBar)
        self.layout.addWidget(self.container)

        self.setLayout(self.layout)

        self.AddTab()

        self.show()

    def CloseTab(self, i):
        self.tabbar.removeTab(i)

    def AddTab(self):
        i = self.tabCount
        self.tabs.append(QWidget())
        self.tabs[i].layout = QVBoxLayout()
        self.tabs[i].layout.setContentsMargins(0, 0, 0, 0)
        self.tabs[i].setObjectName("tab "+str(i))

        # open webview
        self.tabs[i].content = QWebEngineView()
        self.tabs[i].content.load(QUrl.fromUserInput("http://google.com"))

        self.tabs[i].content.titleChanged.connect(lambda: self.SetTabContent(i, "title"))
        self.tabs[i].content.iconChanged.connect(lambda: self.SetTabContent(i, "icon"))
        self.tabs[i].content.urlChanged.connect(lambda: self.SetTabContent(i, "url"))

        # add webview to tabs layout
        self.tabs[i].splitview = QSplitter()
        self.tabs[i].layout.addWidget(self.tabs[i].splitview)
        self.tabs[i].splitview.addWidget(self.tabs[i].content)

        # set top level tap from [] to layout
        self.tabs[i].setLayout(self.tabs[i].layout)

        # add tab tp top level stacked widget
        self.container.layout.addWidget(self.tabs[i])
        self.container.layout.setCurrentWidget(self.tabs[i])

        # set the tab at top of screen
        self.tabbar.addTab("New Tab")
        self.tabbar.setTabData(i, {"object": "tab " + str(i), "initial": i})
        self.tabbar.setCurrentIndex(i)

        self.tabCount += 1

    def SetTabContent(self, i, type):
        tab_name = self.tabs[i].objectName()

        count = 0
        running = True

        current_tab = self.tabbar.tabData(self.tabbar.currentIndex())["object"]

        if current_tab == tab_name and type == "url":
            new_url = self.findChild(QWidget, tab_name).content.url().toString()
            self.addressBar.setText(new_url)
            return False

        while running:
            tab_data_name = self.tabbar.tabData(count)

            if count >= 99:
                running = False

            if tab_name == tab_data_name["object"]:
                if type == "title":
                    new_title = self.findChild(QWidget, tab_name).content.title()
                    self.tabbar.setTabText(count, new_title)
                elif type == "icon":
                    newIcon = self.findChild(QWidget, tab_name).content.icon()
                    self.tabbar.setTabIcon(count, newIcon)

                running = False
            else:
                count += 1

    def SwitchTab(self, i):
        if self.tabbar.tabData(i):
            tab_data = self.tabbar.tabData(i)["object"]

            tab_content = self.findChild(QWidget, tab_data)
            self.container.layout.setCurrentWidget(tab_content)

            new_url = tab_content.content.url().toString()
            self.addressBar.setText(new_url)

    def BrowseTo(self):
        text = self.addressBar.text()

        i = self.tabbar.currentIndex()
        tab = self.tabbar.tabData(i)["object"]
        webview = self.findChild(QWidget, tab).content

        if "http" not in text:
            if "." not in text:
                url = "https://google.com/#q=" + text
            else:
                url = "http://" + text
        else:
            url = text

        webview.load(QUrl.fromUserInput(url))

    def GoBack(self):
        activeIndex = self.tabbar.currentIndex()
        tab_name = self.tabbar.tabData(activeIndex)["object"]
        tab_content = self.findChild(QWidget, tab_name).content

        tab_content.back()

    def GoFoward(self):
        activeIndex = self.tabbar.currentIndex()
        tab_name = self.tabbar.tabData(activeIndex)["object"]
        tab_content = self.findChild(QWidget, tab_name).content

        tab_content.forward()

    def ReloadPage(self):
        activeIndex = self.tabbar.currentIndex()
        tab_name = self.tabbar.tabData(activeIndex)["object"]
        tab_content = self.findChild(QWidget, tab_name).content

        tab_content.reload()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    os.environ['QTWEBENGINE_REMOTE_DEBUGGING'] = "667"

    window = App()

    with open("style.css", "r") as style:
        app.setStyleSheet(style.read())



    sys.exit(app.exec_())


