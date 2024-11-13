import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QAction, QLineEdit, QTabWidget, QWidget, 
    QVBoxLayout, QPushButton, QInputDialog, QMessageBox
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt


class BrowserTab(QWidget):
    def __init__(self, url="https://www.google.com"):
        super().__init__()
        layout = QVBoxLayout()
        self.browser = QWebEngineView()

        # Ensure URL is properly formatted with http:// or https:// prefix
        if isinstance(url, str):
            if not url.startswith("http"):
                url = "http://" + url
            url = QUrl(url)
        
        self.browser.setUrl(url)
        layout.addWidget(self.browser)
        self.setLayout(layout)


class Browser(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize the tab widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabs.customContextMenuRequested.connect(self.show_tab_context_menu)
        self.tabs.tabBarDoubleClicked.connect(self.add_new_tab)
        self.tabs.currentChanged.connect(self.update_url_bar)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)

        self.setCentralWidget(self.tabs)

        # Create the navigation toolbar
        nav_toolbar = QToolBar("Navigation")
        self.addToolBar(nav_toolbar)

        back_button = QAction("Back", self)
        back_button.triggered.connect(lambda: self.tabs.currentWidget().browser.back())
        nav_toolbar.addAction(back_button)

        forward_button = QAction("Forward", self)
        forward_button.triggered.connect(lambda: self.tabs.currentWidget().browser.forward())
        nav_toolbar.addAction(forward_button)

        reload_button = QAction("Reload", self)
        reload_button.triggered.connect(lambda: self.tabs.currentWidget().browser.reload())
        nav_toolbar.addAction(reload_button)

        home_button = QAction("Home", self)
        home_button.triggered.connect(self.navigate_home)
        nav_toolbar.addAction(home_button)

        self.url_bar = QLineEdit(self)
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        nav_toolbar.addWidget(self.url_bar)

        new_tab_button = QPushButton("+", self)
        new_tab_button.clicked.connect(lambda: self.add_new_tab(QUrl("https://www.google.com"), "New Tab"))
        nav_toolbar.addWidget(new_tab_button)

        # Add the initial tab
        self.add_new_tab(QUrl("https://www.google.com"), "New Tab")
        self.setWindowTitle("PyZodiac")
        self.showMaximized()

    def add_new_tab(self, qurl=None, label="New Tab"):
        # Check if a valid URL is provided, or set default
        if qurl is None:
            qurl = QUrl("https://www.google.com")
        elif isinstance(qurl, str):
            if not qurl.startswith("http"):
                qurl = "http://" + qurl
            qurl = QUrl(qurl)
        
        # Initialize new tab with URL
        new_tab = BrowserTab(qurl)
        index = self.tabs.addTab(new_tab, label)
        self.tabs.setCurrentIndex(index)

        # Connect the tab's browser URL change to update the URL bar
        new_tab.browser.urlChanged.connect(lambda qurl, browser=new_tab.browser: self.update_url_bar_for_browser(qurl, browser))

    def close_tab(self, index):
        # Safeguard to prevent closing the last tab
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def navigate_home(self):
        self.tabs.currentWidget().browser.setUrl(QUrl("https://www.google.com"))

    def navigate_to_url(self):
        url = self.url_bar.text().strip()
        if not url.startswith("http"):
            url = "http://" + url
        # Check for HTTP protocol and prompt if necessary
        if url.startswith("http://"):
            choice = QMessageBox.warning(
                self,
                "Unsecure Connection Warning",
                "PyZodiac is about to go to an http:// website, NOT a https:// website, meaning the following website is (potentionally) not safe, or you forgot to type the https:// in the domain, which for some reason activates this popup, but i wont fix this because there is no way to check if its http or not otherwise. Do you want to continue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if choice == QMessageBox.No:
                return  # Stop navigation if the user chooses "Return to safety"

        # Navigate to the URL if the user continues or if it's a secure URL
        self.tabs.currentWidget().browser.setUrl(QUrl(url))

    def update_url_bar(self, index):
        current_browser = self.tabs.widget(index).browser if self.tabs.widget(index) else None
        if current_browser:
            self.url_bar.setText(current_browser.url().toString())

    def update_url_bar_for_browser(self, qurl, browser):
        # Only update the URL bar if the signal came from the active tab
        if self.tabs.currentWidget().browser == browser:
            self.url_bar.setText(qurl.toString())

    def show_tab_context_menu(self, pos):
        index = self.tabs.tabBar().tabAt(pos)
        if index != -1:
            new_name, ok = QInputDialog.getText(self, "Rename Tab", "Enter new tab name:")
            if ok and new_name:
                self.tabs.setTabText(index, new_name)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Browser()
    window.show()
    sys.exit(app.exec_())
