import sys
import json
import time
import random
import ACH_calculator, graph_plotter, reporting
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QGridLayout, QCheckBox, QMainWindow, QVBoxLayout, QMessageBox
from PyQt5.QtCore import QTimer, QPointF, Qt, QThread, pyqtSignal
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from PyQt5.QtGui import QFont, QFontDatabase, QPixmap


class ResultImageWindow(QWidget):
    def __init__(self, image_path, size_w, size_h):
        super().__init__()
        self.setWindowTitle('시험 결과 그래프')
        
        # 이미지를 QLabel에 표시하기 위한 QLabel 위젯 생성
        self.label = QLabel(self)
        # 이미지가 창에 맞게 리사이즈되도록 설정
        self.label.setScaledContents(True)
        
        # 이미지 파일을 QPixmap으로 로드
        pixmap = QPixmap(image_path)
        pixmap = pixmap.scaled(size_w, size_h)
        
        # QLabel에 QPixmap 설정
        self.label.setPixmap(pixmap)


app = QApplication(sys.argv)
# 결과 그래프 표시
result_image = ResultImageWindow("graph.png", 800, 480)
result_image.resize(800, 480)
result_image.show()
app.exec_()