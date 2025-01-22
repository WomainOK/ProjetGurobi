import time
from functools import partial

import gurobipy as gp
from gurobipy import GRB


class CallbackData:
    def __init__(self):
        self.last_gap_change_time = -GRB.INFINITY
        self.last_gap = GRB.INFINITY


def callback(model, where, *, cbdata):
    if where != GRB.Callback.MIP:
        return
    #if model.cbGet(GRB.Callback.MIP_SOLCNT) == 0:
    #    return

    # Use model.terminate() to end the search when required...
# Vérifier si une solution admissible a été trouvée
    sol_count = model.cbGet(GRB.Callback.MIP_SOLCNT)
    if sol_count == 0:
        return

    # Récupérer la meilleure solution et les bornes
    best_obj = model.cbGet(GRB.Callback.MIP_OBJBST)
    best_bound = model.cbGet(GRB.Callback.MIP_OBJBND)

    # Calculer le gap
    if best_obj == GRB.INFINITY or best_obj == -GRB.INFINITY:
        return  # Pas encore de solution admissible
    current_gap = abs(best_obj - best_bound) / max(abs(best_obj), 1e-10)

    # Récupérer le temps courant
    current_time = time.time()

    # Initialiser le temps lors de la première solution trouvée
    if cbdata.last_gap_change_time == -GRB.INFINITY:
        cbdata.last_gap_change_time = current_time
        cbdata.last_gap = current_gap
        return

    # Vérifier si le gap a changé de manière significative
    if abs(cbdata.last_gap - current_gap) > epsilon_to_compare_gap:
        cbdata.last_gap_change_time = current_time
        cbdata.last_gap = current_gap

    # Vérifier si le temps écoulé dépasse la limite sans amélioration significative
    if current_time - cbdata.last_gap_change_time > time_from_best:
        print("Terminating optimization: MIPGap did not improve significantly for 50 seconds.")
        model.terminate()


with gp.read("data/mkp.mps.bz2") as model:
    # Global variables used in the callback function
    time_from_best = 50
    epsilon_to_compare_gap = 1e-4

    # Initialize data passed to the callback function
    callback_data = CallbackData()
    callback_func = partial(callback, cbdata=callback_data)

    model.optimize(callback_func)

