# Implementation of fuzzy logic with fuzzylite
# Sergi Magret Goy - 12/05/2020
# This program tries to land a towercopter (a copter with only a degree of movement - up/down) gently based on
# the distance to the floor and the variation of distance in a specific time.
#
# It also plots the different activation rules and its values.
# At the end plots a graph showing the values that would take the function with matplotlib

import fuzzylite as fl
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np

engine = fl.Engine(
    name="towercopter",
    description="landing a towercopter gently"
)
engine.input_variables = [
    fl.InputVariable(
        name="dist",
        description="distance to the ground",
        enabled=True,
        minimum=0.000,  # Centimeters
        maximum=30.000,  # Centimeters
        lock_range=True,
        terms=[
            fl.Triangle("tocant", 0.000, 0.000, 2.000),
            fl.Trapezoid("a_prop", 0.000, 2.000, 4.000, 6.000),
            fl.Trapezoid("lluny", 4.000, 10.000, 15.000, 21.000),
            fl.Trapezoid("molt_lluny", 15.000, 17.000, 30.000, 30.000)
        ]
    ),
    fl.InputVariable(
        name="var_dist",
        description="distance variation, actual distance to the ground minus previous one",
        enabled=True,
        minimum=-10.000,  # Centimetres
        maximum=3.000,  # Centimetres
        lock_range=True,
        terms=[
            fl.Trapezoid("molt_gran_neg", -10.000, -10.000, -7.000, -5.000),
            fl.Trapezoid("gran_neg", -7.000, -6.000, -4.000, -3.000),
            fl.Trapezoid("petita_neg", -4.000, -3.000, -1.000, 0.000),
            fl.Triangle("zero", -1.000, 0.000, 1.000),
            fl.Trapezoid("positiva", 0.000, 1.000, 3.000, 3.000)
        ]
    )
]
engine.output_variables = [
    fl.OutputVariable(
        name="POWER",
        description="Power sent to the motor of the towercopter",
        enabled=True,
        minimum=0.000,  # Potencia 0 significa que el el dron caura en picat
        maximum=10.000,  # Potencia 10, la màxima, es la que fa que el dron s'estigui quiet, sense pujar ni baixar
        lock_range=True,
        aggregation=fl.Maximum(),
        defuzzifier=fl.Centroid(100),
        terms=[
            fl.Triangle("res", 0.000, 0.000, 1.000),
            fl.Trapezoid("una_mica", 0.000, 1.000, 2.000, 3.000),
            fl.Trapezoid("bastant", 2.000, 3.000, 4.000, 6.000),
            fl.Trapezoid("molta", 5.000, 7.000, 9.000, 10.000),
            fl.Triangle("max", 9.000, 10.000, 10.000)
        ]
    )
]
engine.rule_blocks = [
    fl.RuleBlock(
        name="mamdani",
        description="mamdani inference",
        enabled=True,
        conjunction=fl.Minimum(),
        disjunction=fl.Maximum(),
        implication=fl.Minimum(),
        activation=fl.General(),
        rules=[
            fl.Rule.create("if dist is tocant and var_dist is molt_gran_neg then POWER is max", engine),
            fl.Rule.create("if dist is tocant and var_dist is gran_neg then POWER is molta", engine),
            fl.Rule.create("if dist is tocant and var_dist is petita_neg then POWER is bastant", engine),
            fl.Rule.create("if dist is tocant and var_dist is zero then POWER is una_mica", engine),
            fl.Rule.create("if dist is tocant and var_dist is positiva then POWER is res", engine),
            fl.Rule.create("if dist is a_prop and var_dist is molt_gran_neg then POWER is molta", engine),
            fl.Rule.create("if dist is a_prop and var_dist is gran_neg then POWER is bastant", engine),
            fl.Rule.create("if dist is a_prop and var_dist is petita_neg then POWER is una_mica", engine),
            fl.Rule.create("if dist is a_prop and var_dist is zero then POWER is una_mica", engine),
            fl.Rule.create("if dist is a_prop and var_dist is positiva then POWER is res", engine),
            fl.Rule.create("if dist is lluny and var_dist is molt_gran_neg then POWER is bastant", engine),
            fl.Rule.create("if dist is lluny and var_dist is gran_neg then POWER is una_mica", engine),
            fl.Rule.create("if dist is lluny and var_dist is petita_neg then POWER is una_mica", engine),
            fl.Rule.create("if dist is lluny and var_dist is zero then POWER is res", engine),
            fl.Rule.create("if dist is lluny and var_dist is positiva then POWER is res", engine),
            fl.Rule.create("if dist is molt_lluny and var_dist is molt_gran_neg then POWER is una_mica", engine),
            fl.Rule.create("if dist is molt_lluny and var_dist is gran_neg then POWER is una_mica", engine),
            fl.Rule.create("if dist is molt_lluny and var_dist is petita_neg then POWER is una_mica", engine),
            fl.Rule.create("if dist is molt_lluny and var_dist is zero then POWER is res", engine),
            fl.Rule.create("if dist is molt_lluny and var_dist is positiva then POWER is res", engine)
        ]
    )
]

# Assign the engine variables
# Assignem les variables d'entrada i sortida del engine a variables
distance = engine.input_variable("dist")
var_dist = engine.input_variable("var_dist")
power = engine.output_variable("POWER")


# Show graphs with the activation of the differents variables
# Mostrem els grafics d'activacio de les variables d'entrada i sortida
y_triangle = [0, 1, 0]  # Coordenades y per als triangles
y_trapezoid = [0, 1, 1, 0]  # Coordenades y per als trapezoides
colors = ['m-', 'g-', 'r-', 'y-', 'b-', 'c-', ] # Colors per a triar al dibuixar les figures, aixi es diferencia millor

variables = [distance, var_dist, power] # Llista de llistes de les variables
for v in variables: # Per cada variable es mostra un grafic
    t = v.terms
    for i in range(len(t)):  # Per cada etiqueta linguistica es dibuixa la seva figura
        paraules = str(t[i]).split()  # Es separa el resultat en una llista per poder agafar les paraules i punts per separat
        nom_etiqueta = paraules[1]  # S'agafa el nom de l'etiqueta lingüistica
        figura = paraules[2]  # S'agafa el tipus de la figura
        if figura == "Trapezoid":
            x = [paraules[3], paraules[4], paraules[5], paraules[6]]
            plt.plot(x, y_trapezoid, colors[i], label=nom_etiqueta)  # Es dibuixen les lines entre els punts
        elif figura == "Triangle":
            x = [paraules[3], paraules[4], paraules[5]]
            plt.plot(x, y_triangle, colors[i], label=nom_etiqueta)  # Es dibuixen les lines entre els punts
        else:
            print("Error")
    if v.name == "dist":
        plt.title("Distancia")
        plt.xlabel(v.name + " (cm)")
    elif v.name == "var_dist":
        plt.title("Variacio de distancia")
        plt.xlabel(v.name + " (cm)")
    elif v.name == "POWER":
        plt.title("Potencia enviada al motor")
        plt.xlabel(v.name + " (W)")
    else:
        plt.title("XX")
        plt.xlabel("xx")
    plt.ylabel("Grau de pertanyença")
    plt.axis(ymax=1.5)
    plt.grid()
    plt.legend()
    plt.show()

# Example to fuzzify
# Exemple per fuzzificar i mostrar el resultat defuzzificat
distance.value = 1
print("distance ", distance.fuzzify(distance.value))
var_dist.value = -7.5
print("var_dist ", var_dist.fuzzify(var_dist.value))
engine.process()
print(power.value)

# Preparem per mostrar
RESOLUTION = 30
distance_range = distance.maximum - distance.minimum
inc_distance = distance_range / RESOLUTION
var_dist_range = var_dist.maximum - var_dist.minimum
inc_var_dist = var_dist_range / RESOLUTION

powers = np.zeros((RESOLUTION + 1, RESOLUTION + 1), dtype=np.float64)
for i in range(RESOLUTION + 1):
    distance.value = i * inc_distance
    for j in range(-RESOLUTION - 1, 0):
        var_dist.value = j * inc_var_dist
        engine.process()
        powers[i][j] = power.value

# Mostrem el gràfic de la funció amb diferents valors que poden prendre les variables
X = np.arange(distance.minimum, distance.maximum, inc_distance)
X = np.append(X, X[RESOLUTION-1]+inc_distance) # Si no es fa aixi dona un error perque suma dos cops el mateix valor
Y = np.arange(var_dist.minimum, var_dist.maximum + inc_var_dist, inc_var_dist)

X, Y = np.meshgrid(X, Y)
fig = plt.figure()
ax = fig.gca(projection='3d')
surf = ax.plot_surface(X, Y, powers, cmap=cm.coolwarm)
fig.colorbar(surf, shrink=0.5, aspect=5)
plt.xlabel('distance')
plt.ylabel('var_distance')
plt.show()
