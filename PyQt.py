from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import random
import time

mine_img = QImage("./icons/mine.png")
flag_img = QImage("./icons/flag.png")

status_ready = 0
status_playing = 1
status_win = 2
status_fail = 3

status_icons = {
    status_ready: "./icons/ready.png",
    status_playing: "./icons/playing.png",
    status_win: "./icons/win.png",
    status_fail: "./icons/fail.png",
}

colors = {
    1: QColor('#0000FF'),
    2: QColor('#008000'),
    3: QColor('#FF0000'),
    4: QColor('#000080'),
    5: QColor('#800000'),
    6: QColor('#008080'),
    7: QColor('#000000'),
    8: QColor('#808080')
}


class Tile(QWidget):
    expandable = pyqtSignal(int, int)
    start = pyqtSignal()
    failed = pyqtSignal()
    flag_add = pyqtSignal()
    flag_remove = pyqtSignal()

    def __init__(self, x, y, *args, **kwargs):
        super(Tile, self).__init__(*args, **kwargs)
        self.setFixedSize(QSize(30, 30))
        self.x = x
        self.y = y

    def reset(self):
        self.is_mine = False
        self.mines_around = 0
        self.is_opened = False
        self.is_flagged = False
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = event.rect()
        if self.is_opened:
            color = self.palette().color(QPalette.Background)
            outer, inner = color, color
        else:
            outer, inner = Qt.gray, Qt.lightGray

        p.fillRect(r, QBrush(inner))
        pen = QPen(outer)
        pen.setWidth(1)
        p.setPen(pen)
        p.drawRect(r)

        if self.is_opened:
            if self.is_mine:
                p.drawPixmap(r, QPixmap(mine_img))
            elif self.mines_around > 0:
                pen = QPen(colors[self.mines_around])
                p.setPen(pen)
                f = p.font()
                f.setPointSize(15)
                f.setBold(True)
                p.setFont(f)
                p.drawText(r, Qt.AlignHCenter | Qt.AlignVCenter, str(self.mines_around))
        elif self.is_flagged:
            p.drawPixmap(r, QPixmap(flag_img))

    def flag(self):
        if self.is_flagged:
            self.is_flagged = False
            self.flag_remove.emit()
        else:
            self.is_flagged = True
            self.flag_add.emit()
        self.update()

    def open(self):
        self.is_opened = True
        self.update()

    def click(self):
        if not self.is_opened:
            self.open()
            if self.mines_around == 0:
                self.expandable.emit(self.x, self.y)
        self.start.emit()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton and not self.is_opened:
            self.flag()
        elif event.button() == Qt.LeftButton and not self.is_opened:
            self.click()
            if self.is_mine:
                self.failed.emit()


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("MineSweeper")
        self.tiles_res, self.count_mines = 20, 40
        self.count_flags = self.count_mines

        w = QWidget()
        hb = QHBoxLayout()

        self.mines = QLabel()
        self.mines.setStyleSheet('color: red')
        self.mines.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.clock = QLabel()
        self.clock.setStyleSheet('color: red')
        self.clock.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        f = self.mines.font()
        f.setPointSize(30)
        f.setWeight(75)
        self.mines.setFont(f)
        self.clock.setFont(f)

        self._timer = QTimer()
        self._timer.timeout.connect(self.update_timer)
        self._timer.start(1000)
        self.mines.setText("%03d" % self.count_flags)
        self.clock.setText("000")

        self.button = QPushButton()
        self.button.setFixedSize(QSize(50, 50))
        self.button.setIconSize(QSize(50, 50))
        self.button.setIcon(QIcon("./icons/ready.png"))
        self.button.setFlat(True)
        self.button.pressed.connect(self.button_pressed)

        hb.addWidget(self.mines)
        hb.addWidget(self.button)
        hb.addWidget(self.clock)

        vb = QVBoxLayout()
        vb.addLayout(hb)
        self.grid = QGridLayout()
        self.grid.setSpacing(5)
        vb.addLayout(self.grid)
        w.setLayout(vb)
        self.setCentralWidget(w)

        self.init_board()
        self.update_status(status_ready)
        self.reset_board()
        self.update_status(status_ready)
        self.show()

    def init_board(self):
        for x in range(0, self.tiles_res):
            for y in range(0, self.tiles_res):
                tile = Tile(x, y)
                self.grid.addWidget(tile, y, x)
                tile.expandable.connect(self.expand_open)
                tile.start.connect(self.trigger_start)
                tile.failed.connect(self.game_over)
                tile.flag_add.connect(self.add_flag)
                tile.flag_remove.connect(self.remove_flag)

    def reset_board(self):
        for x in range(0, self.tiles_res):
            for y in range(0, self.tiles_res):
                tile = self.grid.itemAtPosition(y, x).widget()
                tile.reset()
        self.clock.setText("000")
        self.count_flags = self.count_mines
        self.mines.setText("%03d" % self.count_flags)
        positions = []
        while len(positions) < self.count_mines:
            x, y = random.randint(0, self.tiles_res - 1), random.randint(0, self.tiles_res - 1)
            if (x, y) not in positions:
                tile = self.grid.itemAtPosition(y, x).widget()
                tile.is_mine = True
                positions.append((x, y))

        def get_count_mines(x, y):
            positions = self.get_surrounding(x, y)
            count_mines = sum(1 if w.is_mine else 0 for w in positions)
            return count_mines

        for x in range(0, self.tiles_res):
            for y in range(0, self.tiles_res):
                tile = self.grid.itemAtPosition(y, x).widget()
                tile.mines_around = get_count_mines(x, y)

    def get_surrounding(self, x, y):
        positions = []
        for xi in range(max(0, x - 1), min(x + 2, self.tiles_res)):
            for yi in range(max(0, y - 1), min(y + 2, self.tiles_res)):
                positions.append(self.grid.itemAtPosition(yi, xi).widget())
        return positions

    def button_pressed(self):
        if self.status == status_playing:
            self.update_status(status_fail)
            self.show_mines()
        elif self.status == status_fail:
            self.update_status(status_ready)
            self.reset_board()

    def show_mines(self):
        for x in range(0, self.tiles_res):
            for y in range(0, self.tiles_res):
                tile = self.grid.itemAtPosition(y, x).widget()
                if tile.is_mine:
                    tile.open()

    def expand_open(self, x, y):
        for xi in range(max(0, x - 1), min(x + 2, self.tiles_res)):
            for yi in range(max(0, y - 1), min(y + 2, self.tiles_res)):
                tile = self.grid.itemAtPosition(yi, xi).widget()
                if not tile.is_mine:
                    tile.click()

    def trigger_start(self, *args):
        if self.status == status_ready:
            self.update_status(status_playing)
            self._timer_start_nsecs = int(time.time())

    def update_status(self, status):
        self.status = status
        self.button.setIcon(QIcon(status_icons[self.status]))

    def update_timer(self):
        if self.status == status_playing:
            n_secs = int(time.time()) - self._timer_start_nsecs
            self.clock.setText("%03d" % n_secs)

    def add_flag(self):
        self.count_flags -= 1
        self.mines.setText("%03d" % self.count_flags)

    def remove_flag(self):
        self.count_flags += 1
        self.mines.setText("%03d" % self.count_flags)

    def game_over(self):
        self.show_mines()
        self.update_status(status_fail)


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    app.exec_()
