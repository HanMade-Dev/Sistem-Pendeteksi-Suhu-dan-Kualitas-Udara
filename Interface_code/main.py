import sys
import serial
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
import time

from UI import Ui_MainWindow

class BacaSuhuThread(QtCore.QThread):
    suhu_ds18b20_update = QtCore.pyqtSignal(float)  # Mengubah tipe sinyal menjadi float
    suhu_dht22_update = QtCore.pyqtSignal(float)  # Mengubah tipe sinyal menjadi float
    suhu_mq135_update = QtCore.pyqtSignal(float)  # Mengubah tipe sinyal menjadi float

    def run(self):
        ser = serial.Serial("COM9", 9600)  # Definisikan objek ser di dalam fungsi run()
        while True:
            if ser.in_waiting > 0:
                data = ser.readline().decode('latin-1').rstrip()
                if 'Temperature DS18B20:' in data:
                    suhu_str = data.split(':')[1].strip().split(' ')[0]
                    try:
                        suhu = float(suhu_str)
                        self.suhu_ds18b20_update.emit(suhu)  # Mengirimkan suhu dalam float
                    except ValueError:
                        print("Gagal mengonversi nilai suhu DS18B20 menjadi float:", suhu_str)
                elif 'Temperature DHT22:' in data:
                    suhu_str = data.split(':')[1].strip().split(' ')[0]
                    try:
                        suhu = float(suhu_str)
                        self.suhu_dht22_update.emit(suhu)  # Mengirimkan suhu dalam float
                    except ValueError:
                        print("Gagal mengonversi nilai suhu DHT22 menjadi float:", suhu_str)
                elif 'MQ135 Value: ' in data:
                    suhu_str = data.split(':')[1].strip().split(' ')[0]
                    try:
                        suhu = float(suhu_str)
                        self.suhu_mq135_update.emit(suhu)  
                    except ValueError:
                        print("Gagal mengonversi nilai suhu MQ135 menjadi float:", suhu_str)
                else:
                    print("Data tidak valid:", data)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.home_btn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.home))
        self.ui.monitor_btn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.monitor))

        self.thread = BacaSuhuThread()  # Buat objek BacaSuhuThread
        self.thread.suhu_ds18b20_update.connect(self.update_plot_ds18b20)  # Hubungkan sinyal suhu_ds18b20_update ke slot update_plot_ds18b20
        self.thread.suhu_dht22_update.connect(self.update_plot_dht22)  # Hubungkan sinyal suhu_dht22_update ke slot update_plot_dht22
        self.thread.suhu_mq135_update.connect(self.update_label_mq135)  # Hubungkan sinyal suhu_mq135_update ke slot update_label_mq135
        self.thread.suhu_ds18b20_update.connect(self.update_label_ds18b20)  # Hubungkan sinyal suhu_ds18b20_update ke slot update_label_ds18b20
        self.thread.suhu_dht22_update.connect(self.update_label_dht22)  # Hubungkan sinyal suhu_dht22_update ke slot update_label_dht22
        self.thread.start()  # Mulai thread

        self.history_ds18b20 = []
        self.x_ds18b20 = []
        self.history_dht22 = []
        self.x_dht22 = []
        self.history_mq135 = []
        self.x_mq135 = []

        self.ui.plot_widget.setBackground('k')
        self.ui.plot_widget2.setBackground('k')

        self.ui.plot_curve_ds18b20 = self.ui.plot_widget.plot(pen='r')
        self.ui.plot_curve_dht22 = self.ui.plot_widget.plot(pen='b')
        self.ui.plot_curve_mq135 = self.ui.plot_widget2.plot(pen='g')

        self.show()

    def update_plot_ds18b20(self, suhu):  # Menerima suhu sebagai float
        self.history_ds18b20.append(suhu)
        self.x_ds18b20.append(len(self.history_ds18b20))
        self.ui.plot_curve_ds18b20.setData(self.x_ds18b20, self.history_ds18b20)

    def update_plot_dht22(self, suhu):  # Menerima suhu sebagai float
        self.history_dht22.append(suhu)
        self.x_dht22.append(len(self.history_dht22))
        self.ui.plot_curve_dht22.setData(self.x_dht22, self.history_dht22)

    def update_label_ds18b20(self, suhu):  # Menerima suhu sebagai float
        self.ui.hasil_ds18b20.setStyleSheet("QLabel { color: rgb(223, 223, 223); font-weight: bold; font-size: 28px; }")
        self.ui.hasil_ds18b20.setText(f"{suhu}°C")  # Menampilkan suhu di label hasilsuhu_ds18b20

    def update_label_dht22(self, suhu):  # Menerima suhu sebagai float
        self.ui.hasil_dht22.setStyleSheet("QLabel { color: rgb(223, 223, 223); font-weight: bold; font-size: 28px; }")
        self.ui.hasil_dht22.setText(f"{suhu}°C")  # Menampilkan suhu di label hasilsuhu_dht22

    def update_label_mq135(self, ppm):  # Menerima data MQ135 dalam PPM
        self.ui.hasil_mq135.setStyleSheet("QLabel { color: rgb(223, 223, 223); font-weight: bold; font-size: 28px; }")
        self.ui.hasil_mq135.setText(f"{ppm} PPM")  # Menampilkan data MQ135 di label hasil_mq135
        self.history_mq135.append(ppm)  # Menambahkan data MQ135 ke dalam history
        self.x_mq135.append(len(self.history_mq135))
        self.ui.plot_curve_mq135.setData(self.x_mq135, self.history_mq135)  # Menggambar data MQ135 di plot_widget2


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    sys.exit(app.exec_())