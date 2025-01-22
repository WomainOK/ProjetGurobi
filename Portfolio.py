import json
import pandas as pd
import numpy as np
import gurobipy as gp
from gurobipy import GRB

with open("data/portfolio-example.json", "r") as f:
    data = json.load(f)

n = data["num_assets"] # Nombre d'actif
sigma = np.array(data["covariance"]) # Risque
mu = np.array(data["expected_return"]) # Retour attendu
mu_0 = data["target_return"] # Objectif retour
k = data["portfolio_max_size"] # Taille maximal du portfolio


with gp.Model("portfolio") as model:
    # Name the modeling objects to retrieve them
        # Variable x : Investissements relatfis en actifs
    x = model.addVars(n,vtype=GRB.CONTINUOUS, name="x")
        # Variable binaire conrtôlant si l'actif i est négocié
    y = model.addVars(n, vtype=GRB.BINARY, name="y")

    # Contraintes
        # Rendement minimal : Le rendement attendu du portefeuille doit dépasser mu_0
    model.addConstr(sum(x[i] * mu[i] for i in range(n)) >= mu_0, name="return")
        # Limite d'investissement : Le portefeuille peut inclure au maximum k actif
    model.addConstr(y.sum() <= k,name="risk")
        # Lien entre xi et yi : Si un actif i n'est pas sélectionné (yi = 0), alors xi = 0
    for i in range(n):
        model.addConstr(x[i] <= y[i], name=f"asset_{i}")
        # Allocation totale : La somme des fractions investies doit être égale à 1
    model.addConstr(x.sum() == 1, name="allocation")

    model.setObjective(sum(x[i] * x[j] * sigma[i,j] for j in range(n)
                                              for i in range(n)), sense=GRB.MINIMIZE)

    model.optimize()

    # Write the solution into a DataFrame
    portfolio = [var.X for var in model.getVars() if "x" in var.VarName]
    risk = model.ObjVal
    expected_return = model.getRow(model.getConstrByName("return")).getValue()
    df = pd.DataFrame(
        data=portfolio + [risk, expected_return],
        index=[f"asset_{i}" for i in range(n)] + ["risk", "return"],
        columns=["Portfolio"],
    )
    print(df)