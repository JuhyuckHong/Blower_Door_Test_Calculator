import sys
import json
import time
import shutil
import random
import ACH_calculator, graph_plotter, reporting
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QGridLayout, QCheckBox, QMainWindow, QVBoxLayout, QMessageBox
from PyQt5.QtCore import QTimer, QPointF, Qt, QThread, pyqtSignal
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from PyQt5.QtGui import QFont, QFontDatabase, QPixmap


class InputInitalValues(QWidget):
    def __init__(self):
        super().__init__()
        # 창 크기 고정
        # 전체 화면 모드로 설정
        #self.showFullScreen()     
        # 사이즈 조정
        #self.resize(800, 480)
        # 레이아웃 설정
        layout = QGridLayout()
        self.setLayout(layout)

        # 스타일 시트 적용
        self.setStyleSheet('''
            QWidget {
                background-color: #F5F5F5;
            }
            QLabel {
                font-family: Arial;
                font-size: 12px;
                color: #333333;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
            }
            QPushButton {
                padding: 5px;
                background-color: #E0E0E0;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QLineEdit::placeholder {
            color: (0.7, 0.7, 0.7, 0.5);
            }
        ''')

        # 입력 필드와 레이블 생성
        # (표시되는 레이블, 저장되는 key, placeholder)
        labels = [
            ("시험 목적", "purpose", "협회 인증"),
            ("위치", "location", "서울시 송파구 풍납동 497"),
            ("테스트 방식", "method", "method A / method B"),
            ("의뢰자", "requester", "홍길동, 010-0000-0000"),
            ("설계사", "designer", "OO건축사사무소"),
            ("시험자", "tester", "김철수 (주)기밀시험"),
            ("시공사(시공자)", "builder", "OO건축"),
            ("실내 체적 (㎥)", "interior volume", "(필수) 424.21 와 같이 숫자만 작성 가능합니다."),
            ("연면적 (㎡)", "floor area", "92.4"),
            ("구조", "structure", "경량목구조")
        ]
        self.input_fields = {}
        for row, (label_text, label_key, plcae_holder) in enumerate(labels):
            label = QLabel(label_text)
            input_field = QLineEdit()
            # 플레이스홀더
            input_field.setPlaceholderText(plcae_holder)
            # 왼쪽 열에 라벨 추가
            layout.addWidget(label, row, 0)
            # 오른쪽 열에 입력 필드 추가
            layout.addWidget(input_field, row, 1)
            # 데이터 저장
            self.input_fields[label_key] = input_field

        # 체크박스 데이터
        self.checkbox_states = {}

        # 체크 박스 생성
        checkbox1 = QCheckBox("감압 실험")
        checkbox1.setObjectName("depressurization")
        checkbox1.stateChanged.connect(self.save_checkbox_state)
        layout.addWidget(checkbox1, row + 1, 0)

        checkbox2 = QCheckBox("가압 실험")
        checkbox2.setObjectName("pressurization")
        checkbox2.stateChanged.connect(self.save_checkbox_state)
        layout.addWidget(checkbox2, row + 2, 0)

        # 저장 버튼 생성
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_data)
        layout.addWidget(save_button, row + 2, 1)

    def save_checkbox_state(self):
        sender = self.sender()
        checkbox_text = sender.objectName()
        checkbox_state = sender.isChecked()

        self.checkbox_states[checkbox_text] = checkbox_state

    def save_data(self):
        data = {}
        # 입력값을 JSON 파일로 저장
        for key, input_field in self.input_fields.items():
            value = input_field.text()
            data[key] = value
        # 체크박스 데이터 저장
        for key, checkbox in self.checkbox_states.items():
            data[key] = checkbox
        # json으로 저장 (다음 프로세스용)
        with open("conditions.json", "w") as file:
            json.dump(data, file, indent=4)
        # json으로 저장 (백업용)
        now = datetime.now().strftime("%y%m%d-%H%M%S")
        with open(f"./conditions/conditions_{now}.json", "w") as file:
            json.dump(data, file, indent=4)
        # 종료
        self.close()


class LivePressureData(QMainWindow):
    def __init__(self, initial_message="실시간 압력 측정"):
        super(LivePressureData, self).__init__()

        # 초기 시리즈와 차트 설정
        self.series = QLineSeries()
        self.chart = QChart()
        self.chart.legend().setVisible(False)  # Hide the legend
        self.chart.addSeries(self.series)

        # x, y 축 생성
        self.axis_x = QValueAxis()
        self.axis_y = QValueAxis()
        
        # 축 범위 설정
        self.axis_x.setRange(0, 100)
        self.axis_y.setRange(0, 100)

        # 축 레이블 설정
        self.axis_x.setTitleText("Time (s)")
        self.axis_y.setTitleText("Pressure (Pa)")

        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)

        self.series.attachAxis(self.axis_x)
        self.series.attachAxis(self.axis_y)

        # 메세지 레이블
        self.message_label = QLabel(initial_message)

        # 측정 시작 버튼
        self.stop_button = QPushButton("측정 시작")

        # 차트를 메인 위젯으로 설정
        self.chart_view = QChartView(self.chart)

        # 메인 위젯 설정
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.addWidget(self.message_label)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.chart_view)
        self.setCentralWidget(main_widget)

        # 초기 데이터 (x는 시간, y는 랜덤값)
        self.data = [QPointF(i, random.random()) for i in range(10)]
        self.series.replace(self.data)

        # 타이머 설정 (1초마다 update_chart 호출)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_chart)
        self.timer.start(100)

        # 사이즈 조정
        # self.resize(800, 480)

        # 측정 종료 버튼 클릭 이벤트 연결
        self.stop_button.clicked.connect(self.close)

    def update_chart(self):
        # 새로운 랜덤값을 데이터에 추가
        self.data.append(QPointF(self.data[-1].x() + 1, random.randrange(0,100)))
        # 데이터가 100개를 초과하면 가장 오래된 데이터를 제거
        if len(self.data) > 100:
            self.data.pop(0)
            self.axis_x.setRange(self.data[0].x(), self.data[-1].x())

        # 시리즈와 축을 업데이트
        self.series.replace(self.data)


class SimpleMessageAutoDisappear(QMainWindow):
    def __init__(self, initial_message="warning", time_to_close=10):
        super(SimpleMessageAutoDisappear, self).__init__()
        # 창의 제목을 초기 메시지로 설정
        self.setWindowTitle(initial_message)
        # QLabel 위젯을 생성하여 초기 메시지 표시
        self.label = QLabel(initial_message, self)
        # QLabel을 창의 중앙 위젯으로 설정
        self.setCentralWidget(self.label)
        # 글자 중간 정렬
        self.label.setAlignment(Qt.AlignCenter)
        # 남은 닫히기까지의 시간을 10으로 초기화
        self.time_to_close = time_to_close
        # 메시지 업데이트 메서드 호출
        self.update_message()

    def update_message(self):
        if self.time_to_close >= 0:
            message = f"{self.windowTitle()}\n{self.time_to_close}초 후에 창이 닫힙니다."
            self.label.setText(message)
            self.time_to_close -= 1
            # 1초 후에 다시 메시지 업데이트
            QTimer.singleShot(1000, self.update_message)
        else:
            self.close()


class SimpleMessage(QMainWindow):
    def __init__(self, initial_message="warning"):
        super(SimpleMessage, self).__init__()
        # 창의 제목 설정
        self.setWindowTitle(initial_message)
        # QLabel 위젯 생성
        self.label = QLabel(initial_message, self)
        # 글자 중간 정렬
        self.label.setAlignment(Qt.AlignCenter)
        # QLabel을 창의 중앙 위젯으로 설정
        self.setCentralWidget(self.label)


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

class BackgroundTask(QThread):
    finished = pyqtSignal()  # 작업 완료 시그널

    def __init__(self, task_type):
        super().__init__()
        self.task_type = task_type

    def run(self):
        if self.task_type == "blower_door_test":
            self.blower_door_test()
        elif self.task_type == "calculation":
            self.calculation()
        elif self.task_type == "graph_plotting":
            self.graph_plotting()
        elif self.task_type == "reporting":
            self.reporting()

        self.finished.emit()  # 작업 완료 시그널 발생

    def blower_door_test(self):
        initial_time = time.time()
        while True:
            print(f"{self.task_type} is running...")
            time.sleep(1)
            if time.time() - initial_time > 2:
                break

    def calculation(self):
        # 시험 조건 불러오기
        conditions = 'conditions.json'
        with open(conditions, 'r') as file:
            data = json.load(file)
        
        # 아무 시험 결과 없는 경우, Just in case.
        if not data.get("depressurization") and not data.get("pressurization"):
            pass

        # 결과 저장 변수 선언
        calculation_raw = {}
        # 보고서 용 값 저장
        calculation_raw["report"] = {}

        # 저장 할 값 지정
        need_to_save = ["C0", 
                        "n", 
                        "C0 range", 
                        "n range", 
                        "t", 
                        "variance of n", 
                        "variance of x", 
                        "mean x",
                        "N", 
                        "measured values", 
                        "margin of error of y",
                        "Q50",
                        "ACH50",
                        "AL50",
                        "r^2",
                        "Q50+-",
                        "ACH50+-",
                        "n+-",
                        "C0+-"]
        
        need_to_report = ["Q50", "ACH50", "AL50", "C0", "n", "Q50+-", "C0+-", "n+-", "r^2"]
            
        # 감압 시험을 수행 한 경우
        if data.get("depressurization"):
            # 파일 불러오기
            depressureization = ACH_calculator.BlowerDoorTestCalculator.from_file('depressurization_raw.json',
                                                                                'conditions.json')
            # 결과 계산
            results_depr = depressureization.calculate_results()
            # Raw data 저장
            now = datetime.now().strftime("%y%m%d-%H%M%S")
            with open(f"./calculations/depressurization_{now}.json", 'w') as file:
                json.dump(results_depr, file, indent=4)
            # 결과 값 변수 저장
            calculation_raw['depressurization'] = {}
            for i in results_depr.keys():
                if i in need_to_save:
                    calculation_raw['depressurization'][i]=results_depr[i]
            
            for i in need_to_report:
                report_key = i + "-"
                calculation_raw["report"][report_key] = calculation_raw["depressurization"][i]

        # 가압 시험을 수행 한 경우
        if data.get("pressurization"):
            # 파일 불러오기
            pressureization = ACH_calculator.BlowerDoorTestCalculator.from_file('pressurization_raw.json',
                                                                                'conditions.json')
            # 결과 계산
            results_pres = pressureization.calculate_results()
            # Raw data 저장
            now = datetime.now().strftime("%y%m%d-%H%M%S")
            with open(f"./calculations/pressurization_{now}.json", 'w') as file:
                json.dump(results_pres, file, indent=4)
            # 결과 값 변수 저장
            calculation_raw['pressurization'] = {}
            for i in results_pres.keys():
                if i in need_to_save:
                    calculation_raw['pressurization'][i]=results_pres[i]
            
            for i in need_to_report:
                report_key = i + "+"
                calculation_raw["report"][report_key] = calculation_raw["pressurization"][i]

        # 감/가압 시험 모두 수행 한 경우, 평균 값 계산
        if data.get("depressurization") and data.get("pressurization"):
            calculation_raw["average"] = {}
            for i in ["Q50", "ACH50", "AL50"]:
                calculation_raw["report"][i + "_avg"] = (calculation_raw["depressurization"][i] \
                                                        + calculation_raw["pressurization"][i])/2

        with open(f"./calculation_raw.json", 'w') as file:
            json.dump(calculation_raw, file, indent=4)

        print(f"{self.task_type} is done.")

    def graph_plotting(self):
        # 시험 조건 불러오기
        conditions = 'conditions.json'
        with open(conditions, 'r') as file:
            conditions = json.load(file)

        # 계산 결과 불러오기
        with open(f"./calculation_raw.json", 'r') as file:
            calculation_raw = json.load(file)

        if conditions.get("depressurization") and conditions.get("pressurization"):
            graph_plotter.plot_graph(calculation_raw['depressurization'],
                                     calculation_raw['pressurization'],
                                     calculation_raw['report'])
        elif conditions.get("depressurization"):
            graph_plotter.plot_graph(calculation_raw['depressurization'],
                                     False,
                                     calculation_raw['report'])
        elif conditions.get("pressurization"):
            graph_plotter.plot_graph(False,
                                     calculation_raw['pressurization'],
                                     calculation_raw['report'])

    def reporting(self):
        # 템플릿 파일 이름
        template_path = "report_template.xlsx"
        # 결과 파일 명
        now = datetime.now().strftime("%y%m%d-%H%M%S")
        output_path = f"report_{now}.xlsx"
        # 이미지 정보
        image_path = "graph.png"
        cell = "B28"
        width = 590
        height = 355
        # 파일 보호 비밀번호
        key = "asdf"
        report_maker = reporting.ReportMaker(template_path)
        report_maker.process_report(output_path, image_path, cell, width, height, key)
        
        print(f"{self.task_type} is done.")

        # PDF 파일 만들고 열기
        import platform
        if platform.system() == "Linux":
            import subprocess as sub
            sub.call(f"libreoffice --headless --convert-to pdf {output_path}", shell=True)
            shutil.move(output_path.split('.')[0] + '.pdf', "report.pdf")
            sub.call(f"xpdf ./report.pdf", shell=True)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # 창 사이즈 설정
    size_w = 800
    size_h = 480
    # 폰트 설정
    font_db = QFontDatabase()
    # 글꼴 파일 경로
    font_id = font_db.addApplicationFont("./NanumSquare_acL.ttf")  

    if font_id != -1:
        font_families = font_db.applicationFontFamilies(font_id)
        # 로드한 글꼴의 첫 번째 패밀리를 사용
        app.setFont(QFont(font_families[0], 12))
    else:
        print("Failed to load font.")

    # 메세지 종료 시간
    time_to_close = 2

    # 시험 조건 입력
    initialize = InputInitalValues()
    initialize.setWindowTitle("시험 조건 입력")
    initialize.resize(size_w, size_h)
    initialize.show()
    app.exec_()

    # 시험 조건 불러오기
    with open('conditions.json', 'r') as file:
        data = json.load(file)
    
    # 감압, 가압 중 어느 하나라도 선택해야 진행 가능
    if not data.get("depressurization") and not data.get("pressurization"):
        long_message = "감압, 가압 시험 어느 것도 선택하지 않아 시험을 종료합니다."
        end_of_test = SimpleMessageAutoDisappear(long_message, time_to_close)
        end_of_test.resize(size_w, size_h)
        end_of_test.show()
        sys.exit(app.exec_())

    # 측정 시작 시간 저장
    time_start = datetime.now().strftime("%y/%m/%d %H:%M:%S")

    # 감압 시험
    if data.get("depressurization"):
        # 감압 시험 준비
        long_message = "기기의 바람 방향을 건물 바깥쪽으로 향하도록 설치 하고, 측정 시작 버튼을 눌리세요."
        pressure = LivePressureData(long_message)
        pressure.setWindowTitle("감압 시험 준비")
        pressure.resize(size_w, size_h)
        pressure.show()
        app.exec_()
        ###################    
        ## 데이터 측정 시작 with depressurization 파일명
        ###################    
        message = SimpleMessage("측정 중...")
        message.setWindowTitle("...")
        message.resize(size_w, size_h)
        message.show()
        wait_for_end = BackgroundTask("blower_door_test")
        wait_for_end.finished.connect(message.close)
        wait_for_end.start()    
        app.exec_()
        # 측정 종료
        end_of_test = SimpleMessageAutoDisappear("감압 시험 측정 완료.", time_to_close)
        end_of_test.resize(size_w, size_h)
        end_of_test.show()
        app.exec_()

    # 가압 시험
    if data.get("pressurization"):
        # 가압 시험 준비
        long_message = "기기의 바람 방향을 건물 안쪽으로 향하도록 설치 하고, 측정 시작 버튼을 눌리세요."
        pressure = LivePressureData(long_message)
        pressure.setWindowTitle("가압시험 준비")
        pressure.resize(size_w, size_h)
        pressure.show()
        app.exec_()
        ###################    
        ## 데이터 측정 시작 with pressurization 파일명
        ###################
        message = SimpleMessage("측정 중...")
        message.setWindowTitle("...")
        message.resize(size_w, size_h)
        message.show()
        wait_for_end = BackgroundTask("blower_door_test")
        wait_for_end.finished.connect(message.close)
        wait_for_end.start()    
        app.exec_()    
        # 측정 종료
        end_of_test = SimpleMessageAutoDisappear("가압 시험 측정 완료.", time_to_close)
        end_of_test.resize(size_w, size_h)
        end_of_test.show()
        app.exec_()

    # 측정 종료 시간 저장
    time_end = datetime.now().strftime("%H:%M:%S")
    data["test_period"] = f"{time_start}~{time_end}"
    with open("conditions.json", "w") as file:
        json.dump(data, file, indent=4)

    ###################
    ## 결과 계산 코드 실행
    ###################

    # 계산 중 메시지 창
    message = SimpleMessage("시험 결과 계산 중...")
    message.setWindowTitle("...")
    message.resize(size_w, size_h)
    message.show()
    wait_for_end = BackgroundTask("calculation")
    wait_for_end.finished.connect(message.close)
    wait_for_end.start()    
    app.exec_()
    # 계산 종료
    end_of_test = SimpleMessageAutoDisappear("시험 결과 계산 완료.", time_to_close)
    end_of_test.resize(size_w, size_h)
    end_of_test.show()
    app.exec_()

    ###################
    ## 그래프 작성 코드 실행
    ###################
    
    # 그래프 작성 메시지 창
    message = SimpleMessage("그래프 작성 중...")
    message.setWindowTitle("...")
    message.resize(size_w, size_h)
    message.show()
    # 작성 시작
    wait_for_end = BackgroundTask("graph_plotting")
    wait_for_end.finished.connect(message.close)
    wait_for_end.start()    
    app.exec_()
    # 그래프 작성 종료
    end_of_test = SimpleMessageAutoDisappear("그래프 작성 완료.", time_to_close)
    end_of_test.resize(size_w, size_h)
    end_of_test.show()
    app.exec_()

    ###################
    ## 보고서 생성 코드 실행
    ###################
    
    # 보고서 생성 중 메시지 창
    message = SimpleMessage("보고서 생성 중...")
    message.setWindowTitle("...")
    message.resize(size_w, size_h)
    message.show()
    wait_for_end = BackgroundTask("reporting")
    wait_for_end.finished.connect(message.close)
    wait_for_end.start()    
    app.exec_()
    # 보고서 생성 종료
    end_of_test = SimpleMessageAutoDisappear("보고서 생성 완료.", time_to_close)
    end_of_test.resize(size_w, size_h)
    end_of_test.show()
    app.exec_()

    # 시험 종료
    end_of_test = SimpleMessageAutoDisappear("시험이 모두 종료되었습니다.", time_to_close)
    end_of_test.resize(size_w, size_h)
    end_of_test.show()
    app.exec_()

    # 결과 그래프 표시
    result_image = ResultImageWindow("graph.png", size_w, size_h)
    result_image.resize(size_w, size_h)
    result_image.show()
    app.exec_()