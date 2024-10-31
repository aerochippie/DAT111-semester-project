import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.patches as mpatches
from matplotlib.widgets import TextBox

# Generer tilfeldig data for et år
import random
from random import randint

def GenereateRandomYearDataList(intencity: float, seed: int = 0) -> list[int]:
    if seed != 0:
        random.seed(seed)
    centervals = [200, 150, 100, 75, 75, 75, 50, 75, 100, 150, 200, 250, 300]
    centervals = [x * intencity for x in centervals]
    nox = centervals[0]
    inc = True
    noxList = []

    for index in range(1, 365):
        if randint(1, 100) > 50:
            inc = not inc
        center = centervals[int(index / 30)]
        dx = min(2.0, max(0.5, nox / center))
        nox = nox + randint(1, 5) / dx if inc else nox - randint(1, 5) * dx
        nox = max(10, nox)
        noxList.append(nox)
    return noxList

kron_nox_year = GenereateRandomYearDataList(intencity=1.0, seed=2)
nord_nox_year = GenereateRandomYearDataList(intencity=.3, seed=1)

# Globale variabler
coordinates_Nordnes = (450, 250)
coordinates_Kronstad = (1280, 1260)
marked_point = (0, 0)
days_interval = (1, 365)

# Vindu bredde og høyde
figureWidth = 12
figureHeight = 4

# Opprett figur og akser
fig = plt.figure(figsize=(figureWidth, figureHeight))

axNokWidth = 0.40
axBergenWidth = 0.40

axNok = fig.add_axes((0.05, 0.07, axNokWidth, 0.87))
axBergen = fig.add_axes((0.45, 0.07, axBergenWidth, 0.87))

# Tekstbokser for start og slutt dato
axboxStart = plt.axes([0.89, 0.5, 0.1, 0.085])
start_box = TextBox(axboxStart, 'Start: ', initial="1")
start_box.on_submit(lambda text: update_interval(text, slutt_box.text))

axboxSlutt = plt.axes([0.89, 0.40, 0.1, 0.085])
slutt_box = TextBox(axboxSlutt, 'Slutt: ', initial="365")
slutt_box.on_submit(lambda text: update_interval(start_box.text, text))

def update_interval(start_val, slutt_val):
    global days_interval
    try:
        start = int(start_val)
        slutt = int(slutt_val)
        if start >= 0 and slutt <= 365 and start < slutt:
            days_interval = (start, slutt)
            plot_graph()
        else:
            print("Ugyldig intervall. Sørg for at start < slutt og innenfor 0-365.")
    except ValueError:
        print("Ugyldig input. Skriv inn heltall.")

# Beregn NOx-verdi basert på avstand til målingsstasjoner
def CalcPointValue(valN, valK):
    distNordnes = math.dist(coordinates_Nordnes, marked_point)
    distKronstad = math.dist(coordinates_Kronstad, marked_point)
    distNordnesKronstad = math.dist(coordinates_Nordnes, coordinates_Kronstad)
    val = (1 - distKronstad / (distKronstad + distNordnes)) * valK + (1 - distNordnes / (distKronstad + distNordnes)) * valN
    val = val * (distNordnesKronstad / (distNordnes + distKronstad)) ** 4
    return val

# Klikk event for å markere punkt
def on_click(event):
    global marked_point
    if ax := event.inaxes:
        if ax == axBergen:
            marked_point = (event.xdata, event.ydata)
            plot_graph()

# Tegne NOx-verdier og kartet
def plot_graph():
    axNok.cla()
    axBergen.cla()

    nord_nox = nord_nox_year[days_interval[0]:days_interval[1]]
    kron_nox = kron_nox_year[days_interval[0]:days_interval[1]]
    days = len(nord_nox)
    list_days = np.linspace(days_interval[0], days_interval[1] - 1, days)

    avg_nord = np.mean(nord_nox)
    avg_kron = np.mean(kron_nox)
    avg_mark = 0
    l3 = None

    if marked_point != (0, 0):
        nox_point = [CalcPointValue(nord_nox[i], kron_nox[i]) for i in range(days)]
        l3, = axNok.plot(list_days, nox_point, 'limegreen', linewidth=1.5)
        avg_mark = np.mean(nox_point)
        circle = mpatches.Circle((marked_point[0], marked_point[1]), 50, color='green')
        axBergen.add_patch(circle)

    # Beregn relativt forurensningsnivå i prosent
    percent_nord = avg_nord / avg_kron * 100
    percent_kron = 100
    percent_mark = avg_mark / avg_kron * 100 if avg_mark != 0 else 0

    # Tegn linjer
    l1, = axNok.plot(list_days, nord_nox, 'blue', linewidth=1.5)
    l2, = axNok.plot(list_days, kron_nox, 'deeppink', linewidth=1.5)
    axNok.set_title("NOX verdier")

    # Sett x-aksen til å reflektere start og slutt verdier som første og siste etiketter
    axNok.set_xlim(days_interval)  # Sett x-aksen til valgt intervall
    axNok.set_xticks(np.linspace(days_interval[0], days_interval[1], 5).astype(int))  # Fyll inn mellomverdier

    # Lag oppdatert etikett for gjennomsnittsverdiene i prosentformat
    labels = [
        f"Nordnes ({percent_nord:.1f}% - Gj.snitt: {avg_nord:.2f})",
        f"Kronstad ({percent_kron:.1f}% - Gj.snitt: {avg_kron:.2f})"
    ]
    lines = [l1, l2]

    if l3:
        labels.append(f"Markert plass ({percent_mark:.1f}% - Gj.snitt: {avg_mark:.2f})")
        lines.append(l3)

    # Legg til legend
    axNok.legend(lines, labels)

    # Tegn kart over Bergen
    axBergen.axis('off')
    img = mpimg.imread('Bergen.jpg')
    img = axBergen.imshow(img)
    axBergen.set_title("Kart Bergen")
    draw_circles_stations()

    plt.draw()

# Tegn sirkler for målestasjoner
def draw_circles_stations():
    circle = mpatches.Circle(coordinates_Nordnes, 50, color='blue')
    axBergen.add_patch(circle)
    circle = mpatches.Circle(coordinates_Kronstad, 50, color='deeppink')
    axBergen.add_patch(circle)

# Koble klikk-event
plt.connect('button_press_event', on_click)

plot_graph()

plt.show()
