# Implementation of fuzzy logic with fuzzylite
# Sergi Magret Goy - 12/05/2020
# This program decides what tip should give the waiter/restaurant based on the service and the quality of food,
# logic of this program extracted from the examples of the library fuzzylite
#
# At the end plots a graph showing the values that would take the function with matplotlib

import fuzzylite as fl
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np

engine = fl.Engine(
    name="tipper",
    description="(service and food) -> (tip)"
)
engine.input_variables = [
    fl.InputVariable(
        name="service",
        description="quality of service",
        enabled=True,
        minimum=0.000,
        maximum=10.000,
        lock_range=True,
        terms=[
            fl.Trapezoid("poor", 0.000, 0.000, 2.500, 5.000),
            fl.Triangle("good", 2.500, 5.00, 7.500),
            fl.Trapezoid("excellent", 5.000, 7.500, 10.000, 10.000)
        ]
    ),
    fl.InputVariable(
        name="food",
        description="quality of service",
        enabled=True,
        minimum=0.000,
        maximum=10.000,
        lock_range=True,
        terms=[
            fl.Trapezoid("rancid", 0.000, 0.000, 2.500, 7.500),
            fl.Trapezoid("delicious", 2.500, 7.500, 10.000, 10.000)
        ]
    )
]
engine.output_variables = [
    fl.OutputVariable(
        name="Tip",
        description="tip based on mamdani inference",
        enabled=True,
        minimum=0.000,
        maximum=30.000,
        lock_range=False,
        aggregation=fl.Maximum(),
        defuzzifier=fl.Centroid(100),
        terms=[
            fl.Triangle("cheap", 0.000, 5.000, 10.000),
            fl.Triangle("average", 10.000, 15.000, 20.000),
            fl.Triangle("generous", 20.000, 25.000, 30.000)
        ]
    )
]
engine.rule_blocks = [
    fl.RuleBlock(
        name="mamdani",
        description="Mamdani inference",
        enabled=True,
        conjunction=fl.Minimum(),
        disjunction=fl.Maximum(),
        implication=fl.Minimum(),
        activation=fl.General(),
        rules=[
            fl.Rule.create("if service is poor or food is rancid then Tip is cheap", engine),
            fl.Rule.create("if service is good then Tip is average", engine),
            fl.Rule.create("if service is excellent or food is delicious then Tip is generous with 0.500", engine),
            fl.Rule.create("if service is excellent and food is delicious then Tip is generous", engine)
        ]
    )
]

service = engine.input_variable("service")
food = engine.input_variable("food")
propina = engine.output_variable("Tip")

# Fill a 50 * 50 matrix with the tips of 250 possible combinations of service-food
# S'emplena una matriu 50 * 50 amb les propines per 250 possibles combinacions de parells puntuacions service-food
RESOLUTION = 50

inc_service = (service.maximum - service.minimum) / RESOLUTION
inc_food = (food.maximum - food.minimum) / RESOLUTION
propines = np.zeros((RESOLUTION + 1, RESOLUTION + 1), dtype=np.float64)

for i in range(RESOLUTION + 1):
    service.value = i * inc_service
    for j in range(RESOLUTION + 1):
        food.value = j * inc_food
        engine.process()
        propines[i][j] = propina.value


# Show graph of the function
# Mostrem el gràfic de la funció

X = np.arange(0, 10 + 10 / RESOLUTION, 10 / RESOLUTION)
Y = np.arange(0, 10 + 10 / RESOLUTION, 10 / RESOLUTION)
X, Y = np.meshgrid(X, Y)
fig = plt.figure()
ax = fig.gca(projection='3d')
surf = ax.plot_surface(X, Y, propines, cmap=cm.coolwarm)
fig.colorbar(surf, shrink=0.5, aspect=5)
plt.show()