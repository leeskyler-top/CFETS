import sys
import re
import cv2
import numpy as np
from PIL import Image
import requests
from io import BytesIO
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont, QPixmap, QImage, QIcon
from datetime import datetime

class MyWindow(QWidget):
    def __init__(self, data, api_server, headers, cookies):
        self._app = QtWidgets.QApplication([])
        super(MyWindow, self).__init__()
        self.data = data
        self.api_server = api_server
        self.headers = headers
        self.cookies = cookies

    def set_font(self, controls, size, color = (0, 0, 255)):
        font = QFont()
        font.setPointSize(size)
        controls.setFont(font)
        controls.setStyleSheet("color:rgb({}, {}, {})".format(color[0], color[1], color[2]))

    def NdarrayToQimage(self, img):
        try:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            height, width, channel = img.shape
            qImg = QImage(img.data, width, height, channel * width, QImage.Format_RGB888)
            return qImg
        except:
            print("国/区旗获取失败， img可能为None或不是cv2支持读取的图片格式")
            return None

    def read_online_image(self, url):
        try:
            response = requests.get(url, headers=self.headers, cookies=self.cookies)
            image_data = np.frombuffer(response.content, np.uint8)
            image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
            qImg = self.NdarrayToQimage(image)
            pixmap = QPixmap(qImg)
            return pixmap
        except:
            print("国/区旗获取失败")
            return None

    def read_online_GIF_image(self, url):
        try:
            response = requests.get(url, headers=self.headers, cookies=self.cookies)
            image_data = BytesIO(response.content)
            image = Image.open(image_data)
            image = image.convert("RGB")
            image_qt = QImage(image.tobytes("raw", "RGB"), image.width, image.height, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(image_qt)
            return pixmap
        except:
            print("国/区旗获取失败， img可能为None或不是PIL支持读取的GIF图片")
            return None

    def init_ui(self):
        self.win = QWidget()
        self.win.setWindowTitle("中国外汇交易中心-今日汇率查询")
        self.win.setWindowIcon(QIcon("./icon/CFETS.png"))
        foreignCName = [item['foreignCName'] for item in self.data]
        foreignCName.append("CNY")
        self.rate = {item['foreignCName']: item['price'] for item in self.data}
        self.rate['CNY']= 1.000
        self.national_flags = {item['foreignCName']: self.api_server + item['bannerPic'] for item in self.data}
        self.national_flags['CNY'] = "https://www.gov.cn/govweb/xhtml/2019zhuanti/guoqiguohui20201217V1/images/guoqi.jpg"
        # 判断是人民币贵还是外币贵
        self.flag = {item['foreignCName']: 0 if re.match(r'^CNY', item['vrtEName']) else 1 for item in self.data}
        self.flag['CNY'] = 0
        self.flag['JPY'] = 0
        # 设置初始窗口大小为800x600
        self.win.resize(800, 600)

        self.row_layout01 = QHBoxLayout()
        self.row_layout02 = QHBoxLayout()
        self.row_layout03 = QHBoxLayout()
        self.col_layout01 = QVBoxLayout()
        self.main_layout = QVBoxLayout()

        self.convert_button = QPushButton(self.win)
        self.nation_left_list = QComboBox(self.win)
        self.nation_right_list = QComboBox(self.win)
        self.national_left_flag = QLabel(self.win)
        self.national_right_flag = QLabel(self.win)
        self.input_left = QLineEdit(self.win)
        self.input_right = QLineEdit(self.win)
        self.text_label = QLabel(self.win)
        self.text_label_2 = QLabel(self.win)
        self.datetime_label = QLabel(self.win)

        self.nation_left_list.setFixedSize(220, 30)
        self.nation_right_list.setFixedSize(220, 30)

        self.national_left_flag.setFixedSize(28, 20)
        self.national_right_flag.setFixedSize(28, 20)

        self.convert_button.setFixedSize(80, 30)
        self.convert_button.clicked.connect(self.convert)
        self.convert_button.setText('转换')

        self.input_left.setFixedSize(340, 35)
        self.input_right.setFixedSize(340, 35)

        self.text_label.setFixedSize(329, 30)
        self.text_label.setText("请选择转换汇率")
        self.set_font(self.text_label, 12, (0, 0, 0))
        self.text_label_2.setFixedSize(470, 100)
        self.text_label_2.setText(" ")
        self.set_font(self.text_label_2, 12, (255, 0, 0))
        self.datetime_label.setFixedSize(470, 100)
        self.datetime_label.setText(" ")
        self.set_font(self.datetime_label, 8, (0, 0, 0))

        self.row_layout01.addWidget(self.nation_left_list)
        self.row_layout01.addWidget(self.national_left_flag)
        self.row_layout01.addWidget(self.convert_button)
        self.row_layout01.addWidget(self.nation_right_list)
        self.row_layout01.addWidget(self.national_right_flag)

        self.row_layout02.addWidget(self.input_left)
        self.row_layout02.addWidget(self.input_right)

        self.col_layout01.addWidget(self.text_label)
        self.col_layout01.addWidget(self.text_label_2)
        self.col_layout01.addWidget(self.datetime_label)

        self.nation_left_list.addItems(foreignCName)
        self.nation_left_list.activated.connect(self.set_national_left_flag)
        self.nation_right_list.addItems(foreignCName)
        self.nation_right_list.activated.connect(self.set_national_right_flag)

        self.main_layout.addLayout(self.row_layout01)
        self.main_layout.addLayout(self.row_layout02)
        self.main_layout.addLayout(self.col_layout01)
        self.win.setLayout(self.main_layout)

        # 设置主布局
        self.win.show()
        sys.exit(self._app.exec_())

    def set_datetime(self):
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        self.datetime_label.setText(formatted_time)

    def convert(self):
        try:
            left_val = round(float(self.input_left.text()), 3)
        except:
            print("数值错误")
            sys.exit(0)
        if left_val <= float(0.009):
            print("数值错误")
            sys.exit(0)
        current_left_nation = self.nation_left_list.currentText()
        current_right_nation = self.nation_right_list.currentText()

        try:
            if self.flag[current_right_nation] == 1 and current_left_nation == "CNY":
                result = left_val / float(self.rate[current_right_nation])
                self.input_right.setText(str(round(result, 3)))
                self.text_label.setText(
                    "{}与{}转换汇率为：{}".format("CNY", current_right_nation, self.rate[current_right_nation]))
                self.text_label_2.setText(" ")
            elif self.flag[current_right_nation] == 0 and current_left_nation == "CNY":
                result = left_val * float(self.rate[current_right_nation])
                self.input_right.setText(str(round(result, 3)))
                self.text_label.setText(
                    "{}与{}转换汇率为：{}".format("CNY", current_right_nation, self.rate[current_right_nation]))
                self.text_label_2.setText(" ")
            elif self.flag[current_left_nation] == 1 and current_right_nation == "CNY":
                result = left_val * float(self.rate[current_left_nation])
                self.input_right.setText(str(round(result, 3)))
                self.text_label.setText(
                    "{}与{}转换汇率为：{}".format(current_left_nation, "CNY", self.rate[current_left_nation]))
                self.text_label_2.setText(" ")
            elif self.flag[current_left_nation] == 0 and current_right_nation == "CNY":
                result = left_val / float(self.rate[current_left_nation])
                self.input_right.setText(str(round(result, 3)))
                self.text_label.setText(
                    "{}与{}转换汇率为：{}".format(current_left_nation, "CNY", self.rate[current_left_nation]))
                self.text_label_2.setText(" ")
            elif self.flag[current_left_nation] == 0 and current_right_nation != "CNY":
                CNY = left_val / float(self.rate[current_left_nation])
                if self.flag[current_right_nation] == 1:
                    result = CNY / float(self.rate[current_right_nation])
                    self.input_right.setText(str(round(result, 3)))
                    if result > left_val:
                        self.text_label.setText("{}与{}转换汇率为：{}".format(current_right_nation, current_left_nation,
                                                                             round(float(left_val) / float(
                                                                                 self.input_right.text()), 3)))
                    else:
                        self.text_label.setText("{}与{}转换汇率为：{}".format(current_left_nation, current_right_nation,
                                                                             round(float(left_val) / float(
                                                                                 self.input_right.text()), 3)))

                    self.text_label_2.setText("⚠警告: 正在使用间接兑换为人民币的方式查询汇率！")
                elif self.flag[current_right_nation] == 0:
                    result = CNY * float(self.rate[current_right_nation])
                    self.input_right.setText(str(round(result, 3)))
                    if result > left_val:
                        self.text_label.setText("{}与{}转换汇率为：{}".format(current_right_nation, current_left_nation,
                                                                             round(float(left_val) / float(
                                                                                 self.input_right.text()), 3)))
                    else:
                        self.text_label.setText("{}与{}转换汇率为：{}".format(current_left_nation, current_right_nation,
                                                                             round(float(left_val) / float(
                                                                                 self.input_right.text()), 3)))
                    self.text_label_2.setText("⚠警告: 正在使用间接兑换为人民币的方式查询汇率！")
                else:
                    self.text_label.setText(" ")
                    self.text_label_2.setText("未知错误")
                    self.input_right.setText("Unknown")
            elif self.flag[current_left_nation] == 1 and current_right_nation != "CNY":
                CNY = left_val * float(self.rate[current_left_nation])
                if self.flag[current_right_nation] == 1:
                    result = CNY / float(self.rate[current_right_nation])
                    self.input_right.setText(str(round(result, 3)))
                    self.text_label.setText("{}与{}转换汇率为：{}".format(current_left_nation, current_right_nation,
                                                                         round(float(left_val) / float(
                                                                             self.input_right.text()), 3)))
                    self.text_label_2.setText("⚠警告: 正在使用间接兑换为人民币的方式查询汇率！")
                elif self.flag[current_right_nation] == 0:
                    result = CNY * float(self.rate[current_right_nation])
                    self.input_right.setText(str(round(result, 3)))
                    self.text_label.setText("{}与{}转换汇率为：{}".format(current_left_nation, current_right_nation,
                                                                         round(float(left_val) / float(
                                                                             self.input_right.text()), 3)))
                    self.text_label_2.setText("⚠警告: 正在使用间接兑换为人民币的方式查询汇率！")
                else:
                    self.text_label.setText(" ")
                    self.text_label_2.setText("未知错误")
                    self.input_right.setText("Unknown")
            else:
                self.input_right.setText("Unknown")
            if current_left_nation == "JPY" or current_left_nation == "JPY":
                if current_left_nation != "CNY" and current_right_nation != "CNY":
                    self.text_label_2.setText(
                        "⚠警告: 正在使用间接兑换为人民币的方式查询汇率！\n⚠警告: 此处JPY的汇率实际是100日元！")
                else:
                    self.text_label_2.setText("⚠警告: 此处JPY的汇率实际是100日元！")
        except ZeroDivisionError:
            self.input_right.setText("0")
            self.text_label_2.setText("⚠警告: 不足以兑换此货币，请提升金额！")
        self.set_datetime()
    def set_national_left_flag(self):
        current_left_nation = self.nation_left_list.currentText()
        try:
            if current_left_nation == "CNY":
                pixmap = self.read_online_image(self.national_flags[current_left_nation])
            else:
                pixmap = self.read_online_GIF_image(self.national_flags[current_left_nation])
            self.national_left_flag.setPixmap(pixmap)
            self.national_left_flag.setScaledContents(True)
        except:
            print("左侧国/区旗显示失败")

    def set_national_right_flag(self):
        current_right_nation = self.nation_right_list.currentText()
        try:
            if current_right_nation == "CNY":
                pixmap = self.read_online_image(self.national_flags[current_right_nation])
            else:
                pixmap = self.read_online_GIF_image(self.national_flags[current_right_nation])
            self.national_right_flag.setPixmap(pixmap)
            self.national_right_flag.setScaledContents(True)
        except:
            print("右侧国/区旗显示失败")