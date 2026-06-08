# main.py
import pygame
import sys
# Importujemy Twoją klasę oraz wymiary naczynia
from czastka import Czastka
from naczynie import sciana_prawa_x, sciana_dolna_y

# 1. Inicjalizacja Pygame i ustawienie okna
pygame.init()

# Tworzymy okno o wymiarach Waszego naczynia (dodajemy lekki margines, żeby ściany były widoczne)
SZEROKOSC_OKNA = sciana_prawa_x + 50
WYSOKOSC_OKNA = sciana_dolna_y + 50
ekran = pygame.display.set_mode((SZEROKOSC_OKNA, WYSOKOSC_OKNA))
pygame.display.set_caption("Symulator - Jedna cząstka")

# Zegar do kontrolowania liczby klatek na sekundę (FPS)
zegar = pygame.time.Clock()

# 2. Tworzenie JEDNEJ cząstki
# Ustalamy pozycję startową w bezpiecznym miejscu (np. środek naczynia)
# Dajemy jej większy promień (np. 15), żeby była dobrze widoczna podczas testu
srodek_x = sciana_prawa_x // 2
srodek_y = sciana_dolna_y // 2
moja_czastka = Czastka(x=srodek_x, y=srodek_y, promien=15)

# 3. Główna pętla programu
while True:
    # A. Obsługa zdarzeń (zamykanie okna krzyżykiem)
    for zdarzenie in pygame.event.get():
        if zdarzenie.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # B. FIZYKA: Aktualizacja pozycji i sprawdzanie ścian
    moja_czastka.ruch()
    moja_czastka.czy_sciana()

    # C. GRAFIKA: Rysowanie wszystkiego na ekranie
    ekran.fill((30, 30, 30))  # Ciemnoszare tło naczynia

    # Rysujemy kontury naczynia (prostokąt od punktu (0,0) do ścian)
    granica_naczynia = pygame.Rect(0, 0, sciana_prawa_x, sciana_dolna_y)
    pygame.draw.rect(ekran, (0, 255, 0), granica_naczynia, 2)  # Zielona ramka o grubości 2 pikseli

    # Rysujemy naszą cząstkę (ekran, kolor czerwony, pozycja X i Y, promień)
    pygame.draw.circle(
        ekran, 
        (255, 80, 80), 
        (int(moja_czastka.x), int(moja_czastka.y)), 
        moja_czastka.promien
    )

    # Odświeżenie obrazu i ustawienie prędkości animacji na 60 FPS
    pygame.display.flip()
    zegar.tick(60)