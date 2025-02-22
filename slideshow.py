from typing import List, Set, Tuple
import gurobipy as gp
from gurobipy import GRB
from dataclasses import dataclass
import itertools

@dataclass
class Photo:
    id: int  # Identifiant unique de la photo
    is_horizontal: bool  # Indique si la photo est horizontale
    tags: Set[str]  # Ensemble de tags associés à la photo

def read_input(filepath: str) -> List[Photo]:
    """Lit les données d'entrée depuis un fichier et crée une liste d'objets Photo."""
    photos = []
    with open(filepath, 'r') as f:
        n = int(f.readline())  # Nombre total de photos
        for i in range(n):
            line = f.readline().strip().split()
            is_horizontal = line[0] == 'H'  # Vérifie si la photo est horizontale
            n_tags = int(line[1])  # Nombre de tags
            tags = set(line[2:2 + n_tags])  # Ensemble des tags
            photos.append(Photo(i, is_horizontal, tags))
    return photos

def get_transition_score(tags1: Set[str], tags2: Set[str]) -> int:
    """Calcule le score de transition entre deux ensembles de tags."""
    common_tags = len(tags1.intersection(tags2))  # Nombre de tags communs
    tags_only_in_1 = len(tags1.difference(tags2))  # Nombre de tags uniques dans le premier ensemble
    tags_only_in_2 = len(tags2.difference(tags1))  # Nombre de tags uniques dans le second ensemble
    return min(common_tags, tags_only_in_1, tags_only_in_2)

class PhotoSlideshowOptimizer:
    def __init__(self, photos: List[Photo]):
        """Initialise l'optimiseur avec la liste des photos et pré-calcule les scores de transition."""
        self.photos = photos
        self.n_photos = len(photos)

        # Séparer les photos horizontales et verticales
        self.horizontal_photos = [p.id for p in photos if p.is_horizontal]
        self.vertical_photos = [p.id for p in photos if not p.is_horizontal]

        # Pré-calcul des paires de photos verticales et de leurs tags combinés
        self.vertical_pairs = []
        self.vertical_pair_tags = {}
        for i, j in itertools.combinations(self.vertical_photos, 2):
            self.vertical_pairs.append((i, j))
            combined_tags = photos[i].tags.union(photos[j].tags)
            self.vertical_pair_tags[(i, j)] = combined_tags

        # Pré-calcul des scores de transition entre toutes les combinaisons possibles
        self.transition_scores = {}

        # Scores entre photos horizontales
        for i in self.horizontal_photos:
            for j in self.horizontal_photos:
                if i != j:
                    score = get_transition_score(photos[i].tags, photos[j].tags)
                    self.transition_scores[(i, j)] = score

        # Scores entre photos horizontales et paires verticales
        for i in self.horizontal_photos:
            for pair in self.vertical_pairs:
                score = get_transition_score(photos[i].tags, self.vertical_pair_tags[pair])
                self.transition_scores[(i, pair)] = score
                self.transition_scores[(pair, i)] = score

        # Scores entre paires verticales
        for pair1 in self.vertical_pairs:
            for pair2 in self.vertical_pairs:
                if pair1 != pair2:
                    score = get_transition_score(self.vertical_pair_tags[pair1], self.vertical_pair_tags[pair2])
                    self.transition_scores[(pair1, pair2)] = score

    def optimize(self, time_limit: int = 3600) -> Tuple[List[List[int]], float]:
        """Optimise la séquence des diapositives pour maximiser le score total."""
        m = gp.Model("photoSlideshow")

        # Variables de décision : x[i, p] = 1 si la photo/pair i est placée à la position p
        x = {}
        for p in range(self.n_photos):
            for i in self.horizontal_photos:
                x[i, p] = m.addVar(vtype=GRB.BINARY, name=f'x_{i}_{p}')
            for pair in self.vertical_pairs:
                x[pair, p] = m.addVar(vtype=GRB.BINARY, name=f'x_{pair[0]}_{pair[1]}_{p}')

        # Contraintes : chaque position contient au plus une photo/pair
        for p in range(self.n_photos):
            m.addConstr(
                gp.quicksum(x[i, p] for i in self.horizontal_photos) +
                gp.quicksum(x[pair, p] for pair in self.vertical_pairs) <= 1
            )

        # Contraintes : chaque photo est utilisée au plus une fois
        for i in range(self.n_photos):
            if i in self.horizontal_photos:
                m.addConstr(
                    gp.quicksum(x[i, p] for p in range(self.n_photos)) <= 1
                )
            else:  # Contraintes pour les photos verticales
                m.addConstr(
                    gp.quicksum(x[pair, p] for pair in self.vertical_pairs if i in pair
                                for p in range(self.n_photos)) <= 1
                )

        # Objectif : maximiser la somme des scores de transition
        obj = gp.quicksum(
            self.transition_scores.get((i, j), 0) * x[i, p] * x[j, p + 1]
            for p in range(self.n_photos - 1)
            for i in list(self.horizontal_photos) + list(self.vertical_pairs)
            for j in list(self.horizontal_photos) + list(self.vertical_pairs)
            if i != j
        )
        m.setObjective(obj, GRB.MAXIMIZE)

        # Définition du temps limite pour l'optimisation
        m.setParam('TimeLimit', time_limit)

        # Lancer l'optimisation
        m.optimize()

        # Extraction de la solution optimale
        if m.status == GRB.OPTIMAL or m.status == GRB.TIME_LIMIT:
            solution = []
            for p in range(self.n_photos):
                for i in self.horizontal_photos:
                    if x[i, p].X > 0.5:
                        solution.append([i])
                for pair in self.vertical_pairs:
                    if x[pair, p].X > 0.5:
                        solution.append(list(pair))
            return solution, m.objVal
        else:
            return None, 0

def main():
    """Fonction principale pour exécuter l'optimisation."""
    input_file = "PetPics-20.txt"
    photos = read_input(input_file)

    optimizer = PhotoSlideshowOptimizer(photos)
    solution, score = optimizer.optimize(time_limit=120)

    if solution:
        with open("slideshow.sol", "w") as f:
            f.write(f"{len(solution)}\n")
            for slide in solution:
                f.write(" ".join(map(str, slide)) + "\n")
        print(f"Solution trouvée avec un score de : {score}")
    else:
        print("Aucune solution trouvée")

if __name__ == "__main__":
    main()
