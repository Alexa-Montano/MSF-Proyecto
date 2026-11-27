"""
Proyecto: Sistema gastroesofágico

Departamento de Ingeniería Eléctrica y Electrónica
Ingeniería Biomédica
Tecnológico Nacional de México [TecNM - Tijuana]

Nombre del alumno: 

Mildred Angel Torales 23212731
Alexa Montaño Gómez 23212215
Africa Montserrat Rodriguez Garcia C21211891


Asignatura: Modelado de Sistemas Fisiológicos
Docente: Dr. Paul Antonio Valle Trujillo
"""

# Librerías
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import control as ctrl
from pathlib import Path


# Datos de la simulación
x0, t0, tend, dt, w, h = 0, 0, 10, 1E-3, 11, 4.5

N = round((tend-t0)/dt)+1
t = np.linspace(t0, tend, N)


# Señal de entrada: pulso unitario
u = np.zeros(N)
u[(t >= 1) & (t < 2)] = 1


# Modelo del circuito gastroesofágico
def gastro(R1, L1, R2, C1, R3, Re):

    b1 = Re*R2*C1
    b0 = Re

    a2 = L1*C1*(R2+R3+Re)

    a1 = (L1 + R1*C1*(R2+R3+Re)
          + R2*C1*(R3+Re))

    a0 = R1+R3+Re

    num = np.array([b1, b0])
    den = np.array([a2, a1, a0])

    return num, den


# SISTEMA DE CONTROL (SANO)
R1 = 10E3
L1 = 1E-6
R2 = 10E3
C1 = 50E-6
R3 = 100E3
Re = 10E3

nc, dc = gastro(R1, L1, R2, C1, R3, Re)

sysControl = ctrl.tf(nc, dc)
polosControl = np.roots(dc)

print(f"\nFunción de transferencia del control: {sysControl}")

print(f"Polos del sistema: "
      f"L1 = {polosControl[0]:.3e}, "
      f"L2 = {polosControl[1]:.3e}")


# SISTEMA DEL CASO (REFLUJO)
R1 = 10E3
L1 = 1E-6
R2 = 10E3
C1 = 10E-6
R3 = 10E3
Re = 150E3

ne, de = gastro(R1, L1, R2, C1, R3, Re)

sysCaso = ctrl.tf(ne, de)
polosCaso = np.roots(de)

print(f"\nFunción de transferencia del caso: {sysCaso}")

print(f"Polos del sistema: "
      f"L1 = {polosCaso[0]:.3e}, "
      f"L2 = {polosCaso[1]:.3e}")


# CONTROLADOR PI
kP = 2
kI = 500
kD = 0

nPI = np.array([kP, kI])
dPI = np.array([1., 0.])

sysPI = ctrl.tf(nPI, dPI)


# Función de transferencia en lazo cerrado
nh = np.polymul(nPI, ne)

dh = np.polyadd(
    np.polymul(dPI, de),
    nh
)

sysLazoCerrado = ctrl.tf(nh, dh)
polosPI = np.roots(dh)

print(f"\nFunción de transferencia del sistema "
      f"gastroesofágico en lazo cerrado: {sysLazoCerrado}")

print(f"Polos del sistema: "
      f"L1 = {polosPI[0]:.3e}, "
      f"L2 = {polosPI[1]:.3e}, "
      f"L3 = {polosPI[2]:.3e}")


# Función de transferencia total
nt = np.polymul(nc, nh)
dtot = np.polymul(dc, dh)


# Respuesta al escalón mediante fracciones parciales
def escalon(num, den, tiempo):

    r, p, k = signal.residue(
        num,
        np.polymul(den, [1., 0.]),
        tol=1E-8
    )

    y = np.zeros_like(tiempo, dtype=float)

    mask = tiempo >= 0

    y[mask] = np.real(
        np.sum(
            r[:, None] *
            np.exp(p[:, None]*tiempo[mask]),
            axis=0
        )
    )

    return y


# Respuesta al pulso unitario
def pulso(num, den):

    y1 = escalon(num, den, t-1)
    y2 = escalon(num, den, t-2)

    return y1-y2


# Respuestas del sistema
Fsx = pulso(nc, dc)
Fsy = pulso(ne, de)
PI = pulso(nt, dtot)


# Configuración global de la gráfica
plt.rcParams['font.size'] = 11
plt.rcParams['font.family'] = 'serif'

plt.rcParams['font.serif'] = [
    'Times New Roman',
    'Liberation Serif',
    'DejaVu Serif'
]

plt.rcParams['mathtext.fontset'] = 'stix'


# Colores del cuadernillo MATLAB
clr1 = np.array([255, 38, 0])/255
clr2 = np.array([0, 230, 118])/255
clr3 = np.array([255, 214, 10])/255
clr4 = np.array([0, 145, 255])/255


# Gráfica
fg, ax = plt.subplots(
    figsize=(w, h),
    facecolor='white'
)

ax.plot(
    t, u, '-',
    linewidth=1.5,
    color=clr1,
    label=r'$F(t)$'
)

ax.plot(
    t, Fsx, '-',
    linewidth=1.5,
    color=clr2,
    label=r'$Fs(t)$: Control'
)

ax.plot(
    t, Fsy, '-',
    linewidth=1.5,
    color=clr3,
    label=r'$Fs(t)$: Caso'
)

ax.plot(
    t, PI, '--',
    linewidth=1.5,
    color=clr4,
    label=r'$PID(t)$'
)


# Límites y divisiones de los ejes
ax.set_xticks(np.arange(0, 11, 1))
ax.set_xlim(0, 10)

ax.set_yticks(np.arange(-0.1, 1.11, 0.1))
ax.set_ylim(-0.1, 1.1)

ax.set_xlabel(r'$t$ [s]')
ax.set_ylabel(r'$F(t)$ [V]')

ax.grid(False)

ax.legend(
    loc='lower center',
    bbox_to_anchor=(0.5, 1.01),
    ncol=4,
    frameon=True,
    fancybox=False,
    edgecolor='black'
)

fg.tight_layout()
fg.savefig(
    Path(__file__).with_name(
        'Control_y_caso.python.pdf'
    )
)
fg.savefig(
    Path(__file__).with_name(
        'Control_y_caso.python.png'
    ),
    dpi=180
)
plt.show()