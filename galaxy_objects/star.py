from enum import Enum
from random import choice, randint, uniform, triangular
from random_utils import random_choice_from_dict
import numpy as np
from math import sqrt, pi, log10
from typing import Tuple

# Sun's luminosity: 3.827E+26 watts
# Stefan-Boltzmann Law: L = 4 * pi * (R^2) * (5.670E-8) * (T^4)


class StellarClass(Enum):
    CLASS_O = "O"
    CLASS_B = "B"
    CLASS_A = "A"
    CLASS_F = "F"
    CLASS_G = "G"
    CLASS_K = "K"
    CLASS_M = "M"
    CLASS_D = "D"  # White Dwarf


class LuminosityClass(Enum):
    IA_PLUS = "Ia+"     # hypergiants or extremely luminous supergiants
    IA = "Ia"           # luminous supergiants
    IB = "Ib"           # less luminous supergiants
    II = "II"           # bright giants
    III = "III"         # normal giants
    IV = "IV"           # subgiants
    V = "V"             # main-sequence stars (dwarfs)
    VI = "VI"           # subdwarfs
    VII = "VII"         # white dwarfs


weighted_chance = {
    StellarClass.CLASS_O: 3,
    StellarClass.CLASS_B: 4,
    StellarClass.CLASS_A: 6,
    StellarClass.CLASS_F: 30,
    StellarClass.CLASS_G: 200,
    StellarClass.CLASS_K: 225,
    StellarClass.CLASS_M: 250,
    StellarClass.CLASS_D: 12
                  }


class Star:
    # noinspection PyTypeChecker
    def __init__(self):
        self.name: str = ""
        self.color: Tuple[int, int, int] = (0, 0, 0)
        self.mass: float = 0.0
        self.luminosity: float = 3.827E+26
        self.temperature: int = 0
        self.temperature_class: int = 0
        self.stellar_class: StellarClass = None
        self.luminosity_class: LuminosityClass = None
        self.h_inner: float = 0.0
        self.h_outer: float = 0.0

    def generate(self):
        self.stellar_class = random_choice_from_dict(weighted_chance)
        if self.stellar_class == StellarClass.CLASS_O:
            min_temp = 30000
            max_temp = 55000
            temp_difference = max_temp - min_temp
            self.color = (128, 128, 255)
            self.mass = round(uniform(16, 100), 2)
            self.luminosity = round(randint(30000, 1000000) * 3.827E+26, 2)
            self.temperature = round(randint(min_temp, max_temp), -3)
            self.h_inner = round(sqrt((self.luminosity / 3.827E+26) / 1.1) * 500.0, 2)
            self.h_outer = round(sqrt((self.luminosity / 3.827E+26) / 0.53) * 500.0, 2)
        elif self.stellar_class == StellarClass.CLASS_B:
            min_temp = 10000
            max_temp = 30000
            temp_difference = max_temp - min_temp
            self.color = (64, 64, 255)
            self.mass = round(uniform(2.1, 16), 2)
            self.luminosity = round(randint(25, 30000)) * 3.827E+26
            self.temperature = round(randint(min_temp, max_temp), -2)
            self.h_inner = round(sqrt(self.luminosity / 1.1) * 500.0, 2)
            self.h_outer = round(sqrt(self.luminosity / 0.53) * 500.0, 2)
        elif self.stellar_class == StellarClass.CLASS_A:
            min_temp = 7500
            max_temp = 10000
            temp_difference = max_temp - min_temp
            self.color = (0, 0, 255)
            self.mass = round(uniform(1.4, 2.1), 2)
            self.luminosity = round(randint(5, 25)) * 3.827E+26
            self.temperature = round(randint(min_temp, max_temp), -2)
            self.h_inner = round(sqrt(self.luminosity / 1.1) * 500.0, 2)
            self.h_outer = round(sqrt(self.luminosity / 0.53) * 500.0, 2)
        elif self.stellar_class == StellarClass.CLASS_F:
            min_temp = 6000
            max_temp = 7500
            temp_difference = max_temp - min_temp
            self.color = (255, 255, 128)
            self.mass = round(uniform(1.04, 1.4), 2)
            self.luminosity = round(uniform(1.5, 5)) * 3.827E+26
            self.temperature = round(randint(min_temp, max_temp), -2)
            self.h_inner = round(sqrt(self.luminosity / 1.1) * 500.0, 2)
            self.h_outer = round(sqrt(self.luminosity / 0.53) * 500.0, 2)
        elif self.stellar_class == StellarClass.CLASS_G:
            min_temp = 5200
            max_temp = 6000
            temp_difference = max_temp - min_temp
            self.color = (255, 255, 0)
            self.mass = round(uniform(0.8, 1.04), 2)
            self.luminosity = round(uniform(0.6, 1.5), 2) * 3.827E+26
            self.temperature = round(randint(min_temp, max_temp), -2)
            self.h_inner = round(sqrt((self.luminosity / 3.827E+26) / 1.1) * 500.0, 2)
            self.h_outer = round(sqrt((self.luminosity / 3.827E+26) / 0.53) * 500.0, 2)
        elif self.stellar_class == StellarClass.CLASS_K:
            min_temp = 3700
            max_temp = 5200
            temp_difference = max_temp - min_temp
            self.color = (255, 185, 115)
            self.mass = round(uniform(0.45, 0.8), 2)
            self.luminosity = round(uniform(0.08, 0.6), 2) * 3.827E+26
            self.temperature = round(randint(min_temp, max_temp), 2)
            self.h_inner = round(sqrt(self.luminosity / 1.1) * 500.0, 2)
            self.h_outer = round(sqrt(self.luminosity / 0.53) * 500.0, 2)
        elif self.stellar_class == StellarClass.CLASS_M:
            min_temp = 2400
            max_temp = 3700
            temp_difference = max_temp - min_temp
            self.color = (255, 127, 0)
            self.mass = round(uniform(0.08, 0.45), 2)
            self.luminosity = round(uniform(0.02, 0.04), 2) * 3.827E+26
            self.temperature = round(randint(min_temp, max_temp), -2)
            self.h_inner = round(sqrt(self.luminosity / 1.1) * 500.0, 2)
            self.h_outer = round(sqrt(self.luminosity / 0.53) * 500.0, 2)
        else:  # White Dwarf
            min_temp = 3900
            max_temp = 5000
            temp_difference = max_temp - min_temp

            self.color = (255, 255, 255)
            self.mass = round(triangular(0.17, 1.0, mode=0.6), 2)
            self.temperature = round(randint(min_temp, max_temp), -2)
            self.luminosity = 4 * pi * ((self.mass ** (1/3)) ** 2) * 5.670E-8 * (self.temperature ** 4)

            self.h_inner = round(uniform(0.009, 0.012) * 500, 2)
            self.h_outer = round(uniform(0.029, 0.032) * 500, 2)

        temp_intervals = [t for t in range(min_temp, max_temp, (temp_difference // 10))]
        for index, interval in enumerate(temp_intervals):
            if self.temperature > interval:
                self.temperature_class = index

        bolometric_magnitude = -2.5 * log10(self.luminosity) + 71.197
        if bolometric_magnitude <= -8:
            self.luminosity_class = LuminosityClass.IA_PLUS
        elif -8 < bolometric_magnitude <= -7:
            self.luminosity_class = LuminosityClass.IA
        elif -7 < bolometric_magnitude <= -5:
            self.luminosity_class = LuminosityClass.IB
        elif -5 < bolometric_magnitude <= -2:
            self.luminosity_class = LuminosityClass.II
        elif -2 < bolometric_magnitude <= 0:
            self.luminosity_class = LuminosityClass.III
        elif 0 < bolometric_magnitude <= 2.5:
            self.luminosity_class = LuminosityClass.IV
        elif 2.5 < bolometric_magnitude <= 5:
            self.luminosity_class = LuminosityClass.V
        else:
            self.luminosity_class = LuminosityClass.VI

        if self.stellar_class == StellarClass.CLASS_D:
            self.temperature_class = ""
            self.luminosity_class = ""


if __name__ == '__main__':

    while True:
        star = Star()
        star.generate()
        if star.stellar_class in [StellarClass.CLASS_G]:
            print(f"Class: {star.stellar_class.value}{star.temperature_class}{star.luminosity_class.value}\nMass: {star.mass} Msol\nLuminosity: {star.luminosity:.3e} W\nTemperature: {star.temperature} K\nHabitable Zone: {star.h_inner} - {star.h_outer} Ls")
            print(f"Mbol: {-2.5 * log10(star.luminosity) + 71.197:.2f}\n")
