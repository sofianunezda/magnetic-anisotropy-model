"""
Magnetic Anisotropy Model

Modelo sencillo de una película magnética con anisotropía uniaxial
sometida a un campo magnético externo.

Se consideran:

    E_an = K_u * sin^2(theta)

    E_Z = -mu_0 * M_s * H * cos(theta - phi_H)

    E_total = E_an + E_Z

El programa calcula la orientación de equilibrio de la magnetización
mediante la minimización numérica de la energía total y estudia:

- el caso base;
- campo paralelo y perpendicular al eje fácil;
- dependencia con la intensidad del campo;
- campo característico de anisotropía H_k;
- dependencia con la dirección del campo.

Las figuras se guardan automáticamente en la carpeta "figures".
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# 1. CONSTANTES Y PARÁMETROS FÍSICOS
mu_0 = 4 * np.pi * 1e-7       # Permeabilidad del vacío [H/m]

K_u = 5e4                     # Constante de anisotropía uniaxial [J/m^3]
M_s = 8e5                     # Magnetización de saturación [A/m]

H = 5e4                       # Campo magnético aplicado [A/m]
phi_H = 0                     # Dirección del campo aplicado [grados]

# 2. CARPETAS DEL PROYECTO
carpeta_actual = Path(__file__).resolve().parent

carpeta_figuras = carpeta_actual / "figures"
carpeta_figuras.mkdir(exist_ok=True)

# 3. DOMINIO ANGULAR
theta_deg = np.linspace(0, 360, 1000)
theta = np.deg2rad(theta_deg)

# 4. FUNCIONES DEL MODELO FÍSICO
def energia_anisotropia(theta, K_u):
    """Calcula la densidad de energía de anisotropía uniaxial."""
    return K_u * np.sin(theta)**2

def energia_zeeman(theta, H, phi_H_deg, M_s):
    """Calcula la densidad de energía de Zeeman."""
    phi_H_rad = np.deg2rad(phi_H_deg)

    return -mu_0 * M_s * H * np.cos(theta - phi_H_rad)

def energia_total(theta, H, phi_H_deg, K_u, M_s):
    """Calcula la densidad de energía magnética total."""
    E_an = energia_anisotropia(theta, K_u)
    E_Z = energia_zeeman(theta, H, phi_H_deg, M_s)

    return E_an + E_Z

def calcular_equilibrio(theta_deg, E_total):
    """Obtiene el mínimo global de la energía total."""
    index_min = np.argmin(E_total)

    theta_eq = theta_deg[index_min]
    E_min = E_total[index_min]

    return theta_eq, E_min

def calcular_equilibrio_rama(theta_deg, E_total):
    """
    Obtiene el mínimo de energía dentro de la rama angular 0°-90°.

    Esta selección se utiliza para representar de forma continua
    una de las ramas equivalentes de la anisotropía uniaxial.
    """

    mascara = (theta_deg >= 0) & (theta_deg <= 90)

    theta_deg_rama = theta_deg[mascara]
    E_total_rama = E_total[mascara]

    index_min = np.argmin(E_total_rama)

    theta_eq = theta_deg_rama[index_min]
    E_min = E_total_rama[index_min]

    return theta_eq, E_min

# 5. CÁLCULOS
# ----- Caso base -----
E_an = energia_anisotropia(theta, K_u)
E_Z = energia_zeeman(theta, H, phi_H, M_s)

E_total = energia_total(theta, H, phi_H, K_u, M_s)

theta_eq, E_min = calcular_equilibrio(theta_deg, E_total)

# ----- Campo paralelo al eje fácil -----
phi_H_paralelo = 0

E_total_paralelo = energia_total(theta, H, phi_H_paralelo, K_u, M_s)
theta_eq_paralelo, E_min_paralelo = calcular_equilibrio(theta_deg, E_total_paralelo)

# ----- Campo perpendicular al eje fácil -----
phi_H_perpendicular = 90

E_total_perpendicular = energia_total(theta, H, phi_H_perpendicular, K_u, M_s)
theta_eq_perpendicular, E_min_perpendicular = calcular_equilibrio_rama(theta_deg, E_total_perpendicular)

# ----- Barrido de intensidad de campo -----
H_values = np.linspace(0, 1.5e5, 200)

theta_eq_vs_H = np.zeros_like(H_values)
E_min_vs_H = np.zeros_like(H_values)

# Para este barrido seguimos una rama equivalente entre 0° y 90°
mascara_rama = (theta_deg >= 0) & (theta_deg <= 90)

theta_deg_rama = theta_deg[mascara_rama]
theta_rama = theta[mascara_rama]

for i, H_i in enumerate(H_values):
    E_total_i = energia_total(theta_rama, H_i, phi_H_perpendicular, K_u, M_s)
    theta_eq_i, E_min_i = calcular_equilibrio(theta_deg_rama, E_total_i)

    theta_eq_vs_H[i] = theta_eq_i
    E_min_vs_H[i] = E_min_i

# ----- Comparación para varios valores concretos de campo -----
H_bajo  = 2e4
H_medio = 5e4
H_alto  = 1e5

E_total_bajo  = energia_total(theta, H_bajo,  phi_H_perpendicular, K_u, M_s)
E_total_medio = energia_total(theta, H_medio, phi_H_perpendicular, K_u, M_s)
E_total_alto  = energia_total(theta, H_alto,  phi_H_perpendicular, K_u, M_s)

theta_eq_bajo,  E_min_bajo   = calcular_equilibrio_rama(theta_deg, E_total_bajo)
theta_eq_medio, E_min_medio  = calcular_equilibrio_rama(theta_deg, E_total_medio)
theta_eq_alto,  E_min_alto   = calcular_equilibrio_rama(theta_deg, E_total_alto)

# ----- Campo característico de anisotropía -----
H_k = (2*K_u)/(mu_0*M_s)

# ----- Barrido de la dirección del campo aplicado -----
phi_H_values = np.linspace(0, 180, 181)

theta_eq_vs_phi = np.zeros_like(phi_H_values)
E_min_vs_phi = np.zeros_like(phi_H_values)

for i, phi_H_i in enumerate(phi_H_values):

    E_total_i = energia_total(theta, H, phi_H_i, K_u, M_s)

    theta_eq_i, E_min_i = calcular_equilibrio(theta_deg, E_total_i)

    if theta_eq_i > 90:
        theta_eq_i = 180 - theta_eq_i

    theta_eq_vs_phi[i] = theta_eq_i
    E_min_vs_phi[i] = E_min_i

# ----- Curvas de energía para varios ángulos del campo -----
phi_H_0  = 0
phi_H_45 = 45
phi_H_90 = 90

E_total_phi_0  = energia_total(theta, H, phi_H_0,  K_u, M_s)
E_total_phi_45 = energia_total(theta, H, phi_H_45, K_u, M_s)
E_total_phi_90 = energia_total(theta, H, phi_H_90, K_u, M_s)

theta_eq_phi_0,  E_min_phi_0  = calcular_equilibrio(theta_deg, E_total_phi_0)
theta_eq_phi_45, E_min_phi_45 = calcular_equilibrio(theta_deg, E_total_phi_45)
theta_eq_phi_90, E_min_phi_90 = calcular_equilibrio_rama(theta_deg, E_total_phi_90)

# 6. RESULTADOS EN PANTALLA
print("\nMODELO DE ANISOTROPÍA MAGNÉTICA")
print("=" * 45)

print("\nPARÁMETROS FÍSICOS")
print(f"K_u = {K_u:.2e} J/m\u00B3")
print(f"M_s = {M_s:.2e} A/m")
print(f"H   = {H:.2e} A/m")
print(f"H_k = {H_k:.2e} A/m")

print("\nCASO BASE")
print(f"\u03C6_H   = {phi_H:.1f}\u00B0")
print(f"\u03B8_eq  = {theta_eq:.2f}\u00B0")
print(f"E_min = {E_min:.2f} J/m\u00B3")

print("\nCAMPO PARALELO AL EJE FÁCIL")
print(f"\u03C6_H   = {phi_H_paralelo:.1f}\u00B0")
print(f"\u03B8_eq  = {theta_eq_paralelo:.2f}\u00B0")
print(f"E_min = {E_min_paralelo:.2f} J/m\u00B3")

print("\nCAMPO PERPENDICULAR AL EJE FÁCIL")
print(f"\u03C6_H   = {phi_H_perpendicular:.1f}\u00B0")
print(f"\u03B8_eq  = {theta_eq_perpendicular:.2f}\u00B0")
print(f"E_min = {E_min_perpendicular:.2f} J/m\u00B3")

print("\nCOMPARACIÓN SEGÚN LA INTENSIDAD DEL CAMPO")
print(f"H = {H_bajo:.2e} A/m -> "  f"\u03B8_eq = {theta_eq_bajo:.2f}\u00B0")
print(f"H = {H_medio:.2e} A/m -> " f"\u03B8_eq = {theta_eq_medio:.2f}\u00B0")
print(f"H = {H_alto:.2e} A/m -> "  f"\u03B8_eq = {theta_eq_alto:.2f}\u00B0")

print("\nCOMPARACIÓN SEGÚN LA DIRECCIÓN DEL CAMPO")
print(f"\u03C6_H = {phi_H_0:.0f}\u00B0  -> " f"\u03B8_eq = {theta_eq_phi_0:.2f}\u00B0")
print(f"\u03C6_H = {phi_H_45:.0f}\u00B0 -> " f"\u03B8_eq = {theta_eq_phi_45:.2f}\u00B0")
print(f"\u03C6_H = {phi_H_90:.0f}\u00B0 -> " f"\u03B8_eq = {theta_eq_phi_90:.2f}\u00B0")

# 7. REPRESENTACIONES GRÁFICAS

# Figura 1. Energías del caso base
plt.figure(figsize=(9, 5))

plt.plot(theta_deg, E_an, label="Energía de anisotropía")
plt.plot(theta_deg, E_Z, label="Energía de Zeeman")
plt.plot(theta_deg, E_total, label="Energía total")

plt.axvline(theta_eq, linestyle="--", label=f"Equilibrio: \u03B8 = {theta_eq:.1f} \u00B0")

plt.xlabel("\u03B8 (\u00B0)")
plt.ylabel("Densidad de energía (J/m\u00B3)")
plt.title("Energías magnéticas del caso base")

plt.legend()
plt.grid()
plt.tight_layout()

ruta_figura_1 = carpeta_figuras / "01_energias_caso_base.png"
plt.savefig(ruta_figura_1, dpi=300, bbox_inches="tight")

# Figura 2. Campo paralelo y perpendicular
plt.figure(figsize=(9, 5))

plt.plot(theta_deg, E_total_paralelo, label="Campo paralelo al eje fácil")
plt.plot(theta_deg, E_total_perpendicular, label="Campo perpendicular al eje fácil")

plt.xlabel("\u03B8 (\u00B0)")
plt.ylabel("Densidad de energía total (J/m\u00B3)")
plt.title("Efecto de la dirección del campo sobre la energía")

plt.legend()
plt.grid()
plt.tight_layout()

ruta_figura_2 = carpeta_figuras / "02_campo_paralelo_perpendicular.png"
plt.savefig(ruta_figura_2, dpi=300, bbox_inches="tight")

# Figura 3. Evolución del ángulo de equilibrio con el campo
plt.figure(figsize=(9, 5))

plt.plot(H_values, theta_eq_vs_H)

plt.axvline(H_k, linestyle="--", label=f"H_k = {H_k:.2e} A/m")

plt.xlabel("Campo aplicado H (A/m)")
plt.ylabel("\u03B8_eq (\u00B0)")
plt.title("Orientación de equilibrio frente a un campo perpendicular")

plt.legend()
plt.grid()
plt.tight_layout()

ruta_figura_3 = carpeta_figuras / "03_angulo_equilibrio_vs_campo.png"
plt.savefig(ruta_figura_3, dpi=300, bbox_inches="tight")

# Figura 4. Dependencia con la dirección del campo
plt.figure(figsize=(9, 5))

plt.plot(phi_H_values, theta_eq_vs_phi)

plt.xlabel("\u03C6_H (\u00B0)")
plt.ylabel("\u03B8_eq (\u00B0)")
plt.title("Orientación de equilibrio según la dirección del campo")

plt.grid()
plt.tight_layout()

ruta_figura_4 = carpeta_figuras / "04_angulo_equilibrio_vs_direccion_campo.png"
plt.savefig(ruta_figura_4, dpi=300, bbox_inches="tight")

print("\nFIGURAS GUARDADAS")
print("=" * 45)

print("\n")
print(ruta_figura_1)
print(ruta_figura_2)
print(ruta_figura_3)
print(ruta_figura_4)

plt.show()
