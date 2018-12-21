from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QWidget, QMessageBox, QMainWindow
from Learn3K import Ui_Learn
from Main3K import Ui_Main_window
import sys
import random
import time
import pandas as pd


class MainWindow(QMainWindow, Ui_Main_window):
    def __init__(self, config):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.config = config

    def load_word_book(self):
        try:
            self.config["words"] = pd.read_csv(self.lineEdit.text(), sep="*", index_col=0, header=0)
            self.config["file"] = self.lineEdit.text()
            self.config["hasWords"] = True
            self.list_box.setMaximum(round(self.config["words"].shape[0] / 100))
            self.statusbar.showMessage("load %s finish" % self.config["file"])
        except FileNotFoundError:
            print("file not found")

    def load_default(self):
        self.lineEdit.setText("default_3000.csv")

    def random(self):
        self.config["random"] = not self.config["random"]

    def shuffle(self):
        self.config["shuffle"] = not self.config["shuffle"]

    def fast_review(self):
        self.config["fast_review"] = not self.config["fast_review"]

    def star_only(self):
        self.config["star_only"] = not self.config["star_only"]

    def set_review(self):
        self.config["review"] = self.review_box.value()


class LearnWindow(QWidget, Ui_Learn):
    def __init__(self, config):
        super(LearnWindow, self).__init__()
        self.setupUi(self)
        self.config = config
        self.curr_dict = {}
        self.counter = 0
        self.meaning_flag = False

    def init_display(self):
        if not self.config["star_only"]:
            self.curr_dict["words"] = self.config["words"]
        else:
            self.curr_dict["words"] = self.config["words"].loc[self.config["words"].star == True]
            self.curr_dict["words"].index = list(range(self.curr_dict["words"].shape[0]))
        self.info_browser.setPlainText("按next开始")
        self.curr_dict["list"] = self.config["start_list"]
        self.curr_dict["unit"] = self.config["start_unit"]

        self.curr_dict["tmp"] = list(range(10))
        if self.config["shuffle"]:
            random.shuffle(self.curr_dict["tmp"])

    def refresh(self):
        self.info_browser.setText("List: %d, Unit: %d, Number: %d, Star: %s\n%d left" %
                                  (self.curr_dict["list"] + 1,
                                   self.curr_dict["unit"] + 1,
                                   10 - len(self.curr_dict["tmp"]),
                                   "True" if self.curr_dict["star"] else "False",
                                   self.config["left"]))
        self.word_browser.setText(self.curr_dict["word"])
        self.word_browser.setAlignment(QtCore.Qt.AlignCenter)
        self.meaning_browser.setText(self.curr_dict["meaning"] if self.meaning_flag else "")

    def finish(self):
        self.info_browser.setText("congratulations! this window will close")
        # time.sleep(5)
        self.close()

    def show_meaning(self):
        self.meaning_flag = not self.meaning_flag
        self.refresh()

    def next_word(self):
        try:
            self.curr_dict["number"] = self.curr_dict["tmp"].pop(0)
            self.counter = 100 * self.curr_dict["list"] + 10 * self.curr_dict["unit"] + self.curr_dict["number"]

            self.curr_dict["word"] = self.curr_dict["words"].loc[self.counter, "word"]
            self.curr_dict["meaning"] = "\n".join(["%d. %s" % (i + 1, j) for i, j in
                                                   enumerate(
                                                       self.curr_dict["words"].loc[self.counter, "meaning"].split(";"))])
            self.curr_dict["star"] = self.curr_dict["words"].loc[self.counter, "star"]
            if self.meaning_flag:
                self.meaning_flag = False
            self.refresh()

            self.config["left"] = self.curr_dict["words"].shape[0] \
                                  - self.curr_dict["unit"] * 10 \
                                  - self.curr_dict["list"] * 100 \
                                  + len(self.curr_dict["tmp"]) - 10
            if not self.curr_dict["tmp"]:
                self.curr_dict["unit"] += 1
                self.curr_dict["tmp"] = list(range(min(self.config["left"], 10)))
                if self.config["shuffle"]:
                    random.shuffle(self.curr_dict["tmp"])
            if self.curr_dict["unit"] == 10:
                self.curr_dict["unit"] = 0
                self.curr_dict["list"] += 1

        except KeyError:
            self.finish()

    def star_word(self):
        self.curr_dict["star"] = not self.curr_dict["star"]
        self.curr_dict["words"].loc[self.counter, "star"] = self.curr_dict["star"]
        self.config["words"].loc[self.config["words"].word == self.curr_dict["word"], "star"] = self.curr_dict["star"]
        self.refresh()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message', 'You sure to quit?\nChanges will be saved.',
                                               QMessageBox.Yes | QMessageBox.No,
                                               QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.config["words"].to_csv(self.config["file"], sep="*")
            self.counter = 0
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_D:
            self.next_word()
        elif e.key() == QtCore.Qt.Key_S:
            self.show_meaning()
        elif e.key() == QtCore.Qt.Key_W:
            self.star_word()


def my_show():
    config["start_list"] = main_window.list_box.value() - 1
    config["start_unit"] = main_window.unit_box.value() - 1

    if not config.get("hasWords"):
        main_window.statusbar.showMessage("Please load a word book first!")
    elif config["start_list"] * 100 + config["start_unit"] * 10 >= config["words"].shape[0]:
        main_window.statusbar.showMessage("Invalid start location!")
    else:
        learn_window.init_display()
        learn_window.show()


if __name__ == "__main__":
    config = {
        "random": False,
        "shuffle": False,
        "star_only": False,
        "fast_review": False,
        "review": 0,
        "left": 0,
        "start_list": 0,
        "start_unit": 0,
        "hasWords": False
    }
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow(config)
    learn_window = LearnWindow(config)
    main_window.pushButton_2.clicked.connect(my_show)
    main_window.show()
    sys.exit(app.exec_())
