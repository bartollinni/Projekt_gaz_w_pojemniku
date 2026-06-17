#wersja w PySide6 zamiast pyGame i wiele cząstek juz jest
# Uruchamianie:
#   pip install PySide6
#   python main_pyside.py

import sys
import random
import math

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QPen, QBrush
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QPushButton,
    QSlider,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QCheckBox,
)

from czastka import Czastka


#widget do rysowania gazu
class PoleSymulacji(QWidget):
    def __init__(self):
        super().__init__()

        # Rozmiar naczynia w pikselach
        self.szerokosc_naczynia = 500
        self.wysokosc_naczynia = 500

        self.setFixedSize(self.szerokosc_naczynia, self.wysokosc_naczynia)

        # Dane symulacji
        self.czastki = []
        self.liczba_czastek = 40
        self.promien = 5
        self.temperatura = 1.0
        self.grawitacja = False
        self.pauza = False

        # Uproszczone ciśnienie: liczba odbić od ścian w ostatniej klatce
        self.cisnienie = 0

        self.resetuj_symulacje()

        # Timer działa jak pętla animacji
        self.timer = QTimer()
        self.timer.timeout.connect(self.krok_symulacji)
        self.timer.start(16)  # około 60 FPS

    def resetuj_symulacje(self):
        """
        Tworzy cząstki od nowa.
        """
        self.czastki = []

        for _ in range(self.liczba_czastek):
            self.czastki.append(self.stworz_czastke())

        self.cisnienie = 0
        self.update()

    def stworz_czastke(self):
        """
        Tworzy jedną cząstkę w losowym miejscu.
        """
        x = random.randint(self.promien, self.szerokosc_naczynia - self.promien)
        y = random.randint(self.promien, self.wysokosc_naczynia - self.promien)

        cz = Czastka(x=x, y=y, promien=self.promien)

        # Prędkość zależy od temperatury.
        # Im większa temperatura, tym szybciej latają cząstki.
        skala = self.temperatura

        cz.vx = random.uniform(-2, 2) * skala
        cz.vy = random.uniform(-2, 2) * skala

        # Gdyby cząstka wylosowała prawie zerową prędkość
        if abs(cz.vx) < 0.3:
            cz.vx = 0.8
        if abs(cz.vy) < 0.3:
            cz.vy = 0.8

        return cz

    def ustaw_liczbe_czastek(self, liczba):
        """
        Zmienia liczbę cząstek i resetuje symulację.
        """
        self.liczba_czastek = liczba
        self.resetuj_symulacje()

    def ustaw_temperature(self, wartosc_suwaka):
        """
        Suwak daje wartości całkowite, np. 10-50.
        Zamieniamy to na temperaturę 1.0-5.0.
        """
        self.temperatura = wartosc_suwaka / 10

        # Po zmianie temperatury przeskalowanie prędkości.
        for cz in self.czastki:
            aktualna_predkosc = math.sqrt(cz.vx ** 2 + cz.vy ** 2)

            if aktualna_predkosc == 0:
                continue

            nowa_predkosc = self.temperatura * 2

            cz.vx = cz.vx / aktualna_predkosc * nowa_predkosc
            cz.vy = cz.vy / aktualna_predkosc * nowa_predkosc

    def ustaw_grawitacje(self, czy_wlaczona):
        """
        Włącza albo wyłącza prostą grawitację.
        """
        self.grawitacja = czy_wlaczona

    def start_stop(self):
        """
        Pauza albo wznowienie symulacji.
        """
        self.pauza = not self.pauza

    def krok_symulacji(self):
        """
        Jeden krok symulacji.
        """
        if self.pauza:
            return

        licznik_odbic = 0

        for cz in self.czastki:
            if self.grawitacja:
                #prosta grawitacja: cząstki przyspieszają w dół
                cz.vy += 0.05

            cz.ruch()

            licznik_odbic += self.sprawdz_sciany(cz)

        # "Ciśnienie tu to częstość zderzeń cząstek ze ścianami."
        self.cisnienie = licznik_odbic

        self.update()

    def sprawdz_sciany(self, cz):
        """
        Odbicia cząstek od ścian naczynia.
        Zwraca liczbę odbić, żeby można było policzyć umowne ciśnienie.
        """
        odbicia = 0

        # Lewa ściana
        if cz.x - cz.promien < 0:
            cz.x = cz.promien
            cz.vx *= -1
            odbicia += 1

        # Prawa ściana
        if cz.x + cz.promien > self.szerokosc_naczynia:
            cz.x = self.szerokosc_naczynia - cz.promien
            cz.vx *= -1
            odbicia += 1

        # Górna ściana
        if cz.y - cz.promien < 0:
            cz.y = cz.promien
            cz.vy *= -1
            odbicia += 1

        # Dolna ściana
        if cz.y + cz.promien > self.wysokosc_naczynia:
            cz.y = self.wysokosc_naczynia - cz.promien
            cz.vy *= -1
            odbicia += 1

        return odbicia

    def srednia_energia(self):
        """
        Średnia energia kinetyczna cząstek.
        Masa cząstek w klasie Czastka domyślnie wynosi 1.
        """
        if len(self.czastki) == 0:
            return 0

        suma = 0

        for cz in self.czastki:
            v2 = cz.vx ** 2 + cz.vy ** 2
            suma += 0.5 * cz.masa * v2

        return suma / len(self.czastki)

    def paintEvent(self, event):
        """
        Funkcja automatycznie wywoływana przez Qt.
        Tutaj rysujemy naczynie i cząstki.
        """
        painter = QPainter(self)

        # Tło
        painter.fillRect(self.rect(), QColor(30, 30, 30))

        # Ramka naczynia
        pen = QPen(QColor(0, 220, 0))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRect(1, 1, self.szerokosc_naczynia - 2, self.wysokosc_naczynia - 2)

        # Cząstki
        painter.setBrush(QBrush(QColor(255, 80, 80)))
        painter.setPen(Qt.NoPen)

        for cz in self.czastki:
            painter.drawEllipse(
                int(cz.x - cz.promien),
                int(cz.y - cz.promien),
                int(2 * cz.promien),
                int(2 * cz.promien),
            )

#główne okno aplikacji

class OknoGlowne(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Symulator gazu doskonałego - PySide6")

        self.pole = PoleSymulacji()

        # Panel sterowania po prawej stronie
        panel = QWidget()
        panel_layout = QVBoxLayout()

        self.label_czastki = QLabel()
        self.label_temperatura = QLabel()
        self.label_cisnienie = QLabel()
        self.label_energia = QLabel()

        # Suwak liczby cząstek
        self.suwak_czastki = QSlider(Qt.Horizontal)
        self.suwak_czastki.setMinimum(1)
        self.suwak_czastki.setMaximum(150)
        self.suwak_czastki.setValue(self.pole.liczba_czastek)
        self.suwak_czastki.valueChanged.connect(self.zmien_liczbe_czastek)

        # Suwak temperatury
        self.suwak_temperatura = QSlider(Qt.Horizontal)
        self.suwak_temperatura.setMinimum(5)
        self.suwak_temperatura.setMaximum(50)
        self.suwak_temperatura.setValue(10)
        self.suwak_temperatura.valueChanged.connect(self.zmien_temperature)

        # Przyciski
        self.przycisk_start = QPushButton("Start / Pauza")
        self.przycisk_start.clicked.connect(self.pole.start_stop)

        self.przycisk_reset = QPushButton("Reset")
        self.przycisk_reset.clicked.connect(self.resetuj)

        # Checkbox grawitacji
        self.checkbox_grawitacja = QCheckBox("Grawitacja")
        self.checkbox_grawitacja.stateChanged.connect(self.zmien_grawitacje)

        # Dodajemy elementy do panelu
        panel_layout.addWidget(QLabel("Liczba cząstek"))
        panel_layout.addWidget(self.suwak_czastki)
        panel_layout.addWidget(self.label_czastki)

        panel_layout.addSpacing(15)

        panel_layout.addWidget(QLabel("Temperatura"))
        panel_layout.addWidget(self.suwak_temperatura)
        panel_layout.addWidget(self.label_temperatura)

        panel_layout.addSpacing(15)

        panel_layout.addWidget(self.przycisk_start)
        panel_layout.addWidget(self.przycisk_reset)
        panel_layout.addWidget(self.checkbox_grawitacja)

        panel_layout.addSpacing(20)

        panel_layout.addWidget(QLabel("Wyniki uproszczone"))
        panel_layout.addWidget(self.label_cisnienie)
        panel_layout.addWidget(self.label_energia)

        panel_layout.addStretch()

        panel.setLayout(panel_layout)
        panel.setFixedWidth(250)

        # Główny układ: symulacja po lewej, panel po prawej
        glowny_widget = QWidget()
        glowny_layout = QHBoxLayout()
        glowny_layout.addWidget(self.pole)
        glowny_layout.addWidget(panel)
        glowny_widget.setLayout(glowny_layout)

        self.setCentralWidget(glowny_widget)

        # Timer do aktualizacji napisów w panelu
        self.timer_panel = QTimer()
        self.timer_panel.timeout.connect(self.aktualizuj_napisy)
        self.timer_panel.start(100)

        self.aktualizuj_napisy()

    def zmien_liczbe_czastek(self, wartosc):
        self.pole.ustaw_liczbe_czastek(wartosc)
        self.aktualizuj_napisy()

    def zmien_temperature(self, wartosc):
        self.pole.ustaw_temperature(wartosc)
        self.aktualizuj_napisy()

    def zmien_grawitacje(self, stan):
        self.pole.ustaw_grawitacje(stan == Qt.Checked)

    def resetuj(self):
        self.pole.resetuj_symulacje()
        self.aktualizuj_napisy()

    def aktualizuj_napisy(self):
        self.label_czastki.setText(f"Aktualnie: {self.pole.liczba_czastek}")
        self.label_temperatura.setText(f"Aktualnie: {self.pole.temperatura:.1f}")
        self.label_cisnienie.setText(f"Ciśnienie umowne: {self.pole.cisnienie}")
        self.label_energia.setText(f"Średnia energia: {self.pole.srednia_energia():.2f}")


#start

if __name__ == "__main__":
    app = QApplication(sys.argv)

    okno = OknoGlowne()
    okno.show()

    sys.exit(app.exec())