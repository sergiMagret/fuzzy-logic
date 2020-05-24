# Implementation of fuzzy logic with fuzzylite
# Sergi Magret Goy - 12/05/2020
# This program tries to control an industrial oven to be around 180 ºC based on the temperature of the oven and the
# variation of temperature at a specific time.
#
# At the end plots a graph showing the values that would take the function with matplotlib

import fuzzylite as fl
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np

engine = fl.Engine(
    name="oven",
    description="controlling the temperature of an oven to be around 180"
)

engine.input_variables = [
    fl.InputVariable(
        name="temp",
        description="oven temperature",
        enabled=True,
        minimum=150,
        maximum=210,
        lock_range=True,
        terms=[
            fl.Trapezoid("baixa", 150.000, 150.000, 160.000, 175.000),
            fl.Trapezoid("correcte", 160.000, 175.000, 185.000, 200.000),
            fl.Trapezoid("alta", 185.000, 200.000, 210.000, 210.000),
        ]
    ),
    fl.InputVariable(
        name="var_temp",
        description="temperature variation",
        minimum=-2.000,
        maximum=2.000,
        lock_range=True,
        terms=[
            fl.Trapezoid("negativa", -2.000, -2.000, -1.000, 0.000),
            fl.Triangle("zero", -1.000, 0.000, 1.000),
            fl.Trapezoid("positiva", 0.000, 1.000, 2.000, 2.000)
        ]
    )
]
engine.output_variables = [
    fl.OutputVariable(
        name="INTENSITAT",
        description="oven intensity",
        enabled=True,
        minimum=0.000,
        maximum=30.000,
        lock_range=True,
        aggregation=fl.Maximum(),
        defuzzifier=fl.Centroid(100),
        terms=[
            fl.Triangle("zero", 0.000, 0.000, 5.000),
            fl.Triangle("petita", 0.000, 5.000, 10.000),
            fl.Triangle("mitja", 5.000, 10.000, 20.000),
            fl.Trapezoid("gran", 10.000, 20.000, 30.000, 30.000)
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
            fl.Rule.create("if temp is baixa and var_temp is negativa then INTENSITAT is gran", engine),
            fl.Rule.create("if temp is baixa and var_temp is zero then INTENSITAT is gran", engine),
            fl.Rule.create("if temp is baixa and var_temp is positiva then INTENSITAT is petita", engine),
            fl.Rule.create("if temp is correcte and var_temp is negativa then INTENSITAT is mitja", engine),
            fl.Rule.create("if temp is correcte and var_temp is zero then INTENSITAT is mitja", engine),
            fl.Rule.create("if temp is correcte and var_temp is positiva then INTENSITAT is zero", engine),
            fl.Rule.create("if temp is alta and var_temp is negativa then INTENSITAT is petita", engine),
            fl.Rule.create("if temp is alta and var_temp is zero then INTENSITAT is zero", engine),
            fl.Rule.create("if temp is alta and var_temp is positiva then INTENSITAT is zero", engine)
        ]
    )
]

temp = engine.input_variable("temp")
var_temp = engine.input_variable("var_temp")
intensity = engine.output_variable("INTENSITAT")

# S'emplena una matriu 50 * 50 amb les propines per 250 possibles combinacions de parells puntuacions service-food
RESOLUTION = 50

inc_service = (temp.maximum - temp.minimum) / RESOLUTION
inc_food = (var_temp.maximum - var_temp.minimum) / RESOLUTION
propines = np.zeros((RESOLUTION + 1, RESOLUTION + 1), dtype=np.float64)

for i in range(RESOLUTION + 1):
    temp.value = i * inc_service
    for j in range(RESOLUTION + 1):
        var_temp.value = j * inc_food
        engine.process()
        propines[i][j] = intensity.value


# Mostrem el gràfic de la funció
temp_range = temp.maximum - temp.minimum
var_temp_range = var_temp.maximum - var_temp.minimum
X = np.arange(temp.minimum, temp.maximum + temp_range/RESOLUTION, temp_range / RESOLUTION)

X2 = np.arange(temp.minimum, temp.maximum, temp_range / RESOLUTION)

Y = np.arange(var_temp.minimum, var_temp.maximum + var_temp_range/RESOLUTION, var_temp_range / RESOLUTION)
X, Y = np.meshgrid(X, Y)
fig = plt.figure()
ax = fig.gca(projection='3d')
surf = ax.plot_surface(X, Y, propines, cmap=cm.coolwarm)
fig.colorbar(surf, shrink=0.5, aspect=5)
plt.xlabel('temp')
plt.ylabel('var_temp')
plt.show()