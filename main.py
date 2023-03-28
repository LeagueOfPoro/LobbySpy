import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QListWidgetItem, QLabel
from qdarkstyle import load_stylesheet

from ConnectionManager import ConnectionManager


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.cmRiot = ConnectionManager("RIOT")
        self.cmClient = ConnectionManager("CLIENT")
        self.clientRegion = self.getRegion()
        self.initUI()

    def initUI(self):
        # apply the material theme
        self.setStyleSheet(load_stylesheet())

        # create the buttons
        self.buttonReveal = QPushButton("Reveal teammates", self)
        self.buttonReveal.setStyleSheet("padding: 5px;")
        self.buttonReveal.clicked.connect(self.getNames)
        self.buttonUgg = QPushButton("Search on U.GG", self)
        self.buttonUgg.clicked.connect(self.searchUgg)
        self.buttonUgg.setStyleSheet("padding: 5px;")
        self.buttonOpgg = QPushButton("Search on OP.GG", self)
        self.buttonOpgg.clicked.connect(self.searchOpgg)
        self.buttonOpgg.setStyleSheet("padding: 5px;")

        # set the padding for the buttons
        buttonLayout = QHBoxLayout()
        buttonLayout.setSpacing(10)
        buttonLayout.addWidget(self.buttonReveal)
        buttonLayout.addWidget(self.buttonUgg)
        buttonLayout.addWidget(self.buttonOpgg)

        # create the list of names
        self.listNames = QListWidget()
        self.listNames.setObjectName("list_widget")

        # create the layout and add the widgets
        vbox = QVBoxLayout()
        vbox.addLayout(buttonLayout)
        vbox.addWidget(self.listNames)

        self.setLayout(vbox)
        self.setWindowTitle("Lobby Spy")

    def getNames(self):
        # send a get request to the server to get the names
        response = self.cmRiot.get("/chat/v5/participants/champ-select")
        if response.status_code == 200:
            # clear the list of names
            self.listNames.clear()
            # add the names to the list
            responseJson = response.json()
            for player in responseJson.get("participants", []):
                playerName = player.get("name")
                item = QListWidgetItem(playerName)
                
                # create the two buttons for the name
                buttonMobalytics = QPushButton("Mobalytics", self)
                buttonMobalytics.setObjectName("yellow_button")
                buttonMobalytics.clicked.connect(lambda _, n=playerName: self.lookupPlayerMobalytics(n))

                buttonMastery = QPushButton("Mastery", self)
                buttonMastery.setObjectName("purple_button")
                buttonMastery.clicked.connect(lambda _, n=playerName: self.lookupPlayerMastery(n))
                
                container = QWidget(self)
                containerLayout = QHBoxLayout(container)
                containerLayout.setContentsMargins(0, 0, 0, 0)
                containerLayout.setSpacing(1)

                nameLabel = QLabel(playerName, self)
                containerLayout.addWidget(nameLabel, 1)

                # add the two buttons to the container
                buttonLayout = QVBoxLayout()
                buttonLayout.addWidget(buttonMobalytics)
                buttonLayout.addWidget(buttonMastery)
                containerLayout.addLayout(buttonLayout, 1)

                # set the container widget as the widget for the list item
                item.setSizeHint(container.sizeHint())

                self.listNames.addItem(item)
                self.listNames.setItemWidget(item, container)

    def searchUgg(self):
        # get the names from the list
        names = [self.listNames.item(i).text() for i in range(self.listNames.count())]
        # create the url for U.GG
        url = f"https://u.gg/multisearch?summoners={','.join(names)}&region={self.clientRegion}1"
        # open the url in a web browser
        import webbrowser
        webbrowser.open(url)

    def searchOpgg(self):
        # get the names from the list
        names = [self.listNames.item(i).text() for i in range(self.listNames.count())]
        # create the url for OP.GG
        url = f"https://www.op.gg/multisearch/{self.clientRegion}?summoners={','.join(names)}" 
        # open the url in a web browser
        import webbrowser
        webbrowser.open(url)

    def lookupPlayerMastery(self, playerName):
        url = f"https://championmastery.gg/summoner?summoner={playerName}&region={self.clientRegion}" 
        # open the url in a web browser
        import webbrowser
        webbrowser.open(url)

    def lookupPlayerMobalytics(self, playerName):
        url = f"https://app.mobalytics.gg/lol/profile/{self.clientRegion}/{playerName}/overview" 
        # open the url in a web browser
        import webbrowser
        webbrowser.open(url)

    def getRegion(self):
        res = self.cmClient.get("/riotclient/region-locale").json()
        return res.get("region").lower() 

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MyWindow()
    win.show()
    sys.exit(app.exec_())