import pywhatkit
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox, QMessageBox, QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QScrollArea
from datetime import datetime, timedelta
from template_group import templates
import re
import sys
try:
    from PyQt5.QtWinExtras import QtWin
    myappid = 'mycompany.myproduct.subproduct.version'
    QtWin.setCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

class ScrollMessageBox(QMessageBox):
   def __init__(self, l, *args, **kwargs):
      QMessageBox.__init__(self, *args, **kwargs)
      scroll = QScrollArea(self)
      scroll.setWidgetResizable(True)
      self.content = QWidget()
      scroll.setWidget(self.content)
      lay = QVBoxLayout(self.content)
      for item in l:
         lay.addWidget(QLabel(item, self))
      self.layout().addWidget(scroll, 0, 0, 1, self.layout().columnCount())
      self.setStyleSheet("QScrollArea{min-width:600 px; min-height: 500px}")

class W(QWidget):
   def __init__(self):
      super().__init__()
      self.btn = QPushButton('Show Message', self)
      self.btn.setGeometry(10, 10, 100, 100)
      self.btn.clicked.connect(self.buttonClicked)
      self.lst = [str(i) for i in range(2000)]
      self.show()


   def buttonClicked(self):
      result = ScrollMessageBox(self.lst, None)
      result.exec_()

app = QtWidgets.QApplication(sys.argv)
app.setWindowIcon(QtGui.QIcon('Unknown.png'))

main_win = QtWidgets.QWidget()
main_win.resize(600, 300)

main_win.setWindowTitle("Рассылка WhatsApp")

lable_number = QLabel("Номер телефона")
lable_name = QLabel("Имя")
lable_date = QLabel("Дата")
lable_time = QLabel("Время")
lable_template = QLabel("Выбери шаблон")


line_number = QLineEdit()
line_time= QLineEdit()
line_date = QLineEdit()
line_name = QLineEdit()
line_template = QLineEdit()
templates_list = QComboBox()

bnt_send = QPushButton()
bnt_next = QPushButton()
bnt_info = QPushButton()
bnt_text = QPushButton()
bnt_send.setText("Отправить")
bnt_next.setText("Далее")
bnt_info.setText("Список")
bnt_text.setText("Свой текст")

for i in templates:
    templates_list.addItem(i)

hline_labels_1 = QHBoxLayout()
hline_labels_2 = QHBoxLayout()
hline_labels_3 = QHBoxLayout()
hline_labels_1.addWidget(lable_number)
hline_labels_1.addWidget(lable_name)
hline_labels_2.addWidget(lable_date)
hline_labels_2.addWidget(lable_time)
hline_labels_3.addWidget(lable_template)


hline_1 = QHBoxLayout()
hline_2 = QHBoxLayout()
hline_3 = QHBoxLayout()
hline_4 = QHBoxLayout()
hline_1.addWidget(line_number)
hline_1.addWidget(line_name)
hline_2.addWidget(line_date)
hline_2.addWidget(line_time)
hline_3.addWidget(templates_list)
hline_3.addWidget(line_template)
hline_4.addStretch(1)
hline_4.addWidget(bnt_next, stretch=1)
hline_4.addWidget(bnt_info, stretch=1)
hline_4.addWidget(bnt_text, stretch=1)
hline_4.addWidget(bnt_send, stretch=1)
hline_4.addStretch(1)

vline_main = QVBoxLayout()
vline_main.addLayout(hline_labels_1)
vline_main.addLayout(hline_1)
vline_main.addLayout(hline_labels_2)
vline_main.addLayout(hline_2)
vline_main.addLayout(hline_labels_3)
vline_main.addLayout(hline_3)
vline_main.addLayout(hline_4)

vline_main.setSpacing(20)

data_dict = {}

def send():
    global data_dict
    for i in data_dict:
        pywhatkit.sendwhatmsg_instantly(i, data_dict[i])
    data_dict = {}

def next():
    number = line_number.text()
    if len(number) != 12 or number[0:2] != "+7" or re.findall(r"\D", number[2:]) != [] or number in data_dict.keys():
        mesbox = QMessageBox()
        if number in data_dict.keys():
            mesbox.setText("Номер уже есть в списке")
        elif number == "":
            mesbox.setText("Поле номера пустое")
        else:
            mesbox.setText("Номер введен некорректно")
        mesbox.exec_()
        return

    title_text = None
    if bnt_text.text() == "Свой текст":
        title_text = templates_list.currentText()
        mes_text = templates[title_text]
    else:
        mes_text = line_template.text()
        line_template.clear()

    if title_text == "Приглашение":
        name = line_name.text()
        time = line_time.text()
        date = line_date.text()
        if len(time) != 5 or time[2] != ":" or len(re.findall(r"[\D]", time)) > 1 or "" in [date, name, time] or int(time[0]) not in range(3) or int(time[3]) not in range(6):
            mesbox = QMessageBox()
            if "" in [date, name, time]:
                mesbox.setText("Шаблон приглашения требует заполнения всех полей")
            else:
                mesbox.setText("Время введено некорректно")
            mesbox.exec_()
            return
        cur_time = datetime.strptime(time, "%H:%M")
        time_before = cur_time - timedelta(minutes=5)
        time_before = f"{time_before.hour}:{time_before.minute}"

        line_name.clear()
        line_time.clear()
        line_date.clear()

        mes_text = mes_text.format(name, date, time, time_before)
    else:
        name = line_name.text()
        time = line_time.text()
        date = line_date.text()
        if date != name or date != time:
            mesbox = QMessageBox()
            mesbox.setText("Данный шаблон требует только номер")
            mesbox.exec_()
            return


    data_dict[number] = mes_text

    line_number.clear()

def info():
    result = ScrollMessageBox([f"{i}: {data_dict[i]}\n\n\n" for i in data_dict])
    result.exec_()

def format_text():
    if bnt_text.text() == "Свой текст":
        templates_list.hide()
        line_template.show()
        bnt_text.setText("Список шаблонов")
        lable_template.setText("Напиши свой текст")



    else:
        line_template.hide()
        templates_list.show()
        bnt_text.setText("Свой текст")
        lable_template.setText("Выбери шаблон")




line_template.hide()

bnt_send.clicked.connect(send)
bnt_next.clicked.connect(next)
bnt_info.clicked.connect(info)
bnt_text.clicked.connect(format_text)
main_win.setLayout(vline_main)
main_win.setWindowIcon(QtGui.QIcon('Unknown.png'))
main_win.show()
sys.exit(app.exec_())
