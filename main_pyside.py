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
                        # Historia ciśnienia z ostatnich klatek,
        # żeby ciśnienie nie skakało ciągle do zera.
        self.historia_cisnienia = []
        self.dlugosc_historii_cisnienia = 120  # ok. 2 sekundy przy 60 FPS

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
        self.historia_cisnienia.clear()

        self.update()

    def ustaw_grawitacje(self, czy_wlaczona):
        self.grawitacja = czy_wlaczona
        print("Grawitacja ustawiona na:", self.grawitacja)
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
        self.losuj_predkosc(cz)

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
        Zmiana temperatury.
        Po zmianie temperatury losujemy prędkości od nowa,
        ale zostawiamy położenia cząstek.
        Dzięki temu histogram dalej ma sensowny kształt.
        """
        self.temperatura = wartosc_suwaka / 10

        for cz in self.czastki:
            self.losuj_predkosc(cz)
    def ustaw_grawitacje(self, czy_wlaczona):
        """
        Włącza albo wyłącza prostą grawitację.
        """
        self.grawitacja = czy_wlaczona
        print("Grawitacja:", czy_wlaczona)

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
                cz.vy += 0.5

            cz.ruch()

            licznik_odbic += self.sprawdz_sciany(cz)
        self.sprawdz_zderzenia_czastek()
        # "Ciśnienie tu to częstość zderzeń cząstek ze ścianami."
        self.historia_cisnienia.append(licznik_odbic)

        if len(self.historia_cisnienia) > self.dlugosc_historii_cisnienia:
            self.historia_cisnienia.pop(0)

        self.cisnienie = sum(self.historia_cisnienia) / len(self.historia_cisnienia)

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

            if self.grawitacja:
                # Przy grawitacji odbicie od podłogi jest tłumione.
                # Dzięki temu cząstki wyraźniej gromadzą się na dole.
                cz.vy *= -0.65
            else:
                cz.vy *= -1

            odbicia += 1

        return odbicia

    def sprawdz_zderzenia_czastek(self):
        """
        Bardzo proste zderzenia sprężyste cząstek.
        Działa dla jednakowych mas i promieni.
        Zabezpieczenie przed dzieleniem przez zero jest w if dystans == 0.
        """
        for i in range(len(self.czastki)):
            for j in range(i + 1, len(self.czastki)):
                c1 = self.czastki[i]
                c2 = self.czastki[j]

                dx = c2.x - c1.x
                dy = c2.y - c1.y

                dystans = math.sqrt(dx ** 2 + dy ** 2)
                min_dystans = c1.promien + c2.promien

                # Jeśli dystans == 0, cząstki są dokładnie w tym samym miejscu.
                # Wtedy unikamy dzielenia przez zero.
                if dystans == 0:
                    dystans = 0.001
                    dx = 0.001
                    dy = 0.001

                if dystans < min_dystans:
                    # Wektor normalny zderzenia
                    nx = dx / dystans
                    ny = dy / dystans

                    # Wektor styczny
                    tx = -ny
                    ty = nx

                    # Składowe prędkości w kierunku normalnym i stycznym
                    v1n = c1.vx * nx + c1.vy * ny
                    v1t = c1.vx * tx + c1.vy * ty

                    v2n = c2.vx * nx + c2.vy * ny
                    v2t = c2.vx * tx + c2.vy * ty

                    # Dla równych mas w zderzeniu sprężystym
                    # cząstki wymieniają składowe normalne prędkości
                    v1n_po = v2n
                    v2n_po = v1n

                    # Składamy nowe prędkości z części normalnej i stycznej
                    c1.vx = v1n_po * nx + v1t * tx
                    c1.vy = v1n_po * ny + v1t * ty

                    c2.vx = v2n_po * nx + v2t * tx
                    c2.vy = v2n_po * ny + v2t * ty

                    # Rozsuwamy cząstki, żeby nie zostały sklejone
                    nachodzenie = min_dystans - dystans

                    c1.x -= nx * nachodzenie / 2
                    c1.y -= ny * nachodzenie / 2

                    c2.x += nx * nachodzenie / 2
                    c2.y += ny * nachodzenie / 2

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
        if self.grawitacja:
          painter.setBrush(QBrush(QColor(80, 180, 255)))
        else:
         painter.setBrush(QBrush(QColor(255, 80, 80)))
         painter.setPen(Qt.NoPen)

        for cz in self.czastki:
            painter.drawEllipse(
                int(cz.x - cz.promien),
                int(cz.y - cz.promien),
                int(2 * cz.promien),
                int(2 * cz.promien),
            )

    def predkosci_czastek(self):
        """
        Zwraca listę wartości prędkości wszystkich cząstek.
        Prędkość = sqrt(vx^2 + vy^2)
        """
        predkosci = []

        for cz in self.czastki:
            v = math.sqrt(cz.vx ** 2 + cz.vy ** 2)
            predkosci.append(v)

        return predkosci
    
    def losuj_predkosc(self, cz):
        """
        Losuje prędkość cząstki z rozkładu normalnego.
        Dzięki temu rozkład prędkości przypomina rozkład Maxwella w 2D.
        """
        sigma = self.temperatura

        cz.vx = random.gauss(0, sigma)
        cz.vy = random.gauss(0, sigma)

    def wspolczynnik_clapeyrona(self):
        """
        Umowny wskaźnik PV/nRT.
        Przy grawitacji go nie pokazujemy, bo gaz nie jest jednorodny.
        """
        if self.grawitacja:
            return None

        n = len(self.czastki)
        R = 1

        if n == 0 or self.temperatura == 0:
            return None

        V = self.szerokosc_naczynia * self.wysokosc_naczynia
        P = self.cisnienie / 900

        return (P * V) / (n * R * self.temperatura)

#główne okno aplikacji

class WykresPredkosci(QWidget):
    """
    Prosty histogram prędkości cząstek.
    To ma pokazywać jakościowo rozkład Maxwella.
    """

    def __init__(self, pole_symulacji):
        super().__init__()

        self.pole = pole_symulacji
        self.setFixedSize(230, 160)

    def paintEvent(self, event):
        painter = QPainter(self)

        # Tło wykresu
        painter.fillRect(self.rect(), QColor(25, 25, 25))

        # Ramka
        painter.setPen(QPen(QColor(180, 180, 180)))
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

        predkosci = self.pole.predkosci_czastek()

        if len(predkosci) == 0:
            return

        liczba_koszykow = 10
        max_v = max(predkosci)

        if max_v == 0:
            return

        koszyki = [0] * liczba_koszykow

        # Liczymy ile cząstek wpada do danego zakresu prędkości
        for v in predkosci:
            indeks = int((v / max_v) * (liczba_koszykow - 1))
            koszyki[indeks] += 1

        max_liczba = max(koszyki)

        if max_liczba == 0:
            return

        szerokosc_slupka = self.width() / liczba_koszykow

        painter.setBrush(QBrush(QColor(80, 180, 255)))
        painter.setPen(Qt.NoPen)

        for i, liczba in enumerate(koszyki):
            wysokosc = (liczba / max_liczba) * (self.height() - 30)

            x = int(i * szerokosc_slupka + 3)
            y = int(self.height() - wysokosc - 20)
            w = int(szerokosc_slupka - 6)
            h = int(wysokosc)

            painter.drawRect(x, y, w, h)

        # Podpis
        painter.setPen(QPen(QColor(230, 230, 230)))
        painter.drawText(10, self.height() - 5, "Rozklad predkosci")

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
        self.label_clapeyron = QLabel()
        self.wykres_predkosci = WykresPredkosci(self.pole)

        # Suwak liczby cząstek
        self.suwak_czastki = QSlider(Qt.Horizontal)
        self.suwak_czastki.setMinimum(1)
        self.suwak_czastki.setMaximum(300)
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
        self.checkbox_grawitacja.clicked.connect(self.zmien_grawitacje)

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
        panel_layout.addWidget(self.label_clapeyron)
        panel_layout.addSpacing(15)
        panel_layout.addWidget(QLabel("Rozkład prędkości cząstek"))
        panel_layout.addWidget(self.wykres_predkosci)

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

    def zmien_grawitacje(self):
        czy_wlaczona = self.checkbox_grawitacja.isChecked()
        self.pole.ustaw_grawitacje(czy_wlaczona)

    def resetuj(self):
        self.pole.resetuj_symulacje()
        self.aktualizuj_napisy()

    
    ...
    def aktualizuj_napisy(self):
        self.label_czastki.setText(f"Aktualnie: {self.pole.liczba_czastek}")
        self.label_temperatura.setText(f"Aktualnie: {self.pole.temperatura:.1f}")
        self.label_cisnienie.setText(f"Ciśnienie umowne: {self.pole.cisnienie:.2f}")
        self.label_energia.setText(f"Średnia energia: {self.pole.srednia_energia():.2f}")
        clapeyron = self.pole.wspolczynnik_clapeyrona()
        if clapeyron is None:
            self.label_clapeyron.setText("PV/nRT: niedostępne przy grawitacji")
        else:
            self.label_clapeyron.setText(f"PV/nRT: {clapeyron:.2f}")
        self.wykres_predkosci.update()
        

#start

if __name__ == "__main__":
    app = QApplication(sys.argv)

    okno = OknoGlowne()
    okno.show()

    sys.exit(app.exec())