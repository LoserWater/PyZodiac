import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QAction, QLineEdit, QTabWidget, QWidget, QVBoxLayout, QPushButton, QInputDialog, QMessageBox, QMenu
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt


class BrowserTab(QWidget):
    def __init__(self, url="https://www.google.com"):
        super().__init__()
        layout = QVBoxLayout()
        self.browser = QWebEngineView()

        # Ensure `url` is a valid string or QUrl
        if isinstance(url, str):
            url = QUrl(url)  # Convert string to QUrl if necessary
        elif not isinstance(url, QUrl):
            url = QUrl("https://www.google.com")  # Default to a valid URL if something went wrong

        self.browser.setUrl(url)  # Pass the URL directly as a QUrl object
        layout.addWidget(self.browser)
        self.setLayout(layout)


class Browser(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the tab widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.add_new_tab)  # Double-click to add new tab
        self.tabs.currentChanged.connect(self.update_url_bar)  # Update URL bar on tab change
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)  # Close tab on request
        self.tabs.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabs.customContextMenuRequested.connect(self.show_context_menu)  # Right-click for custom menu

        self.setCentralWidget(self.tabs)

        # Create the navigation toolbar
        nav_toolbar = QToolBar("Navigation")
        self.addToolBar(nav_toolbar)

        # Back button
        back_button = QAction("Back", self)
        back_button.triggered.connect(lambda: self.navigate_and_reset(self.tabs.currentWidget().browser.back))
        nav_toolbar.addAction(back_button)

        # Forward button
        forward_button = QAction("Forward", self)
        forward_button.triggered.connect(lambda: self.navigate_and_reset(self.tabs.currentWidget().browser.forward))
        nav_toolbar.addAction(forward_button)

        # Reload button
        reload_button = QAction("Reload", self)
        reload_button.triggered.connect(lambda: self.navigate_and_reset(self.tabs.currentWidget().browser.reload))
        nav_toolbar.addAction(reload_button)

        # Home button
        home_button = QAction("Home", self)
        home_button.triggered.connect(lambda: self.navigate_and_reset(self.navigate_home))
        nav_toolbar.addAction(home_button)

        # URL bar
        self.url_bar = QLineEdit(self)
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        nav_toolbar.addWidget(self.url_bar)

        # Add a new tab button to the toolbar
        new_tab_button = QPushButton("+", self)
        new_tab_button.clicked.connect(self.add_new_tab)
        nav_toolbar.addWidget(new_tab_button)

        # Add initial tab
        self.add_new_tab(QUrl("https://www.google.com"), "New Tab")

        # Window settings
        self.setWindowTitle("PyZodiac")
        self.showMaximized()

    def add_new_tab(self, qurl=None, label="New Tab"):
        if qurl is None:
            qurl = QUrl("https://www.google.com")  # Default to QUrl if None is passed

        # Ensure `qurl` is a valid QUrl object before creating a tab
        if isinstance(qurl, str):
            qurl = QUrl(qurl)
        
        # Create a new BrowserTab with the QUrl object directly
        new_tab = BrowserTab(qurl)  # No need for `.toString()`
        i = self.tabs.addTab(new_tab, label)
        self.tabs.setCurrentIndex(i)

        # Update URL bar to the new tab's URL
        new_tab.browser.urlChanged.connect(lambda qurl, browser=new_tab.browser: self.update_url_bar(qurl, browser))

    def close_tab(self, i):
        if self.tabs.count() < 2:
            return  # Prevent closing the last tab
        self.tabs.removeTab(i)

    def navigate_home(self):
        self.tabs.currentWidget().browser.setUrl(QUrl("https://www.google.com"))

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith("http"):
            url = "http://" + url
        # Check for HTTP vs HTTPS
        if url.startswith("http://"):
            self.show_http_warning(url)
        else:
            self.tabs.currentWidget().browser.setUrl(QUrl(url))

    def update_url_bar(self, qurl=None, browser=None):
        if browser != self.tabs.currentWidget().browser:
            return
        self.url_bar.setText(self.tabs.currentWidget().browser.url().toString())

    def show_http_warning(self, url):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setText("PyZodiac is about to go to a http:// website, NOT a https:// website, meaning the following website is not safe. Do you want to continue?")
        msg_box.setWindowTitle("Unsafe Website Warning")
        continue_button = msg_box.addButton("Continue to unsafe website", QMessageBox.AcceptRole)
        return_button = msg_box.addButton("Return to safety", QMessageBox.RejectRole)
        
        msg_box.exec_()

        if msg_box.clickedButton() == continue_button:
            self.tabs.currentWidget().browser.setUrl(QUrl(url))
        else:
            self.url_bar.setText("")

    def show_context_menu(self, pos):
        index = self.tabs.tabBar().tabAt(pos)
        if index != -1:
            menu = QMenu()
            rename_action = QAction("Rename Tab", self)
            rename_action.triggered.connect(lambda: self.rename_tab(index))
            menu.addAction(rename_action)
            menu.exec_(self.tabs.tabBar().mapToGlobal(pos))

    def rename_tab(self, index):
        current_name = self.tabs.tabText(index)
        new_name, ok = QInputDialog.getText(self, "Rename Tab", "Enter new tab name:", text=current_name)
        if ok and new_name:
            self.tabs.setTabText(index, new_name)
        
        # Ensure buttons are visually reset after renaming
        QApplication.processEvents()

    def navigate_and_reset(self, navigation_action):
        navigation_action()  # Perform the navigation action
        QApplication.processEvents()  # Process all pending UI events


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Browser()
    window.show()
    sys.exit(app.exec_())
