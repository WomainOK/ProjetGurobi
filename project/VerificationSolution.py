from typing import List, Set, Tuple
from dataclasses import dataclass

@dataclass
class Photo:
    id: int  # Identifiant unique de la photo
    is_horizontal: bool  # Indique si la photo est horizontale
    tags: Set[str]  # Ensemble des tags associés à la photo

class SolutionChecker:
    def __init__(self, photos: List[Photo]):
        """Initialise le vérificateur avec une liste de photos."""
        self.photos = {photo.id: photo for photo in photos}  # Stocker les photos par ID pour un accès rapide
        self.n_photos = len(photos)

    @staticmethod
    def read_input_file(filepath: str) -> List[Photo]:
        """Lit les données d'entrée depuis un fichier et retourne une liste d'objets Photo."""
        photos = []
        with open(filepath, 'r') as f:
            n = int(f.readline().strip())  # Nombre total de photos
            for i in range(n):
                line = f.readline().strip().split()
                is_horizontal = line[0] == 'H'  # Vérifie si la photo est horizontale
                tags = set(line[2:])  # Ensemble des tags de la photo
                photos.append(Photo(i, is_horizontal, tags))
        return photos

    @staticmethod
    def read_solution_file(filepath: str) -> List[List[int]]:
        """Lit le fichier de solution et retourne une liste de diapositives contenant des IDs de photos."""
        slides = []
        with open(filepath, 'r') as f:
            try:
                n_slides = int(f.readline().strip())  # Nombre total de diapositives
            except ValueError:
                raise ValueError(
                    "Format invalide : la première ligne doit contenir un nombre entier (nombre de slides).")

            for _ in range(n_slides):
                line = f.readline().strip().split()
                if len(line) not in [1, 2]:
                    raise ValueError(f"Format invalide : une ligne doit contenir 1 ou 2 IDs, trouvé : {line}")
                slides.append(list(map(int, line)))
        return slides

    def is_valid_solution(self, slides: List[List[int]]) -> Tuple[bool, str]:
        """Vérifie si la solution est valide."""
        used_photos = set()

        for i, slide in enumerate(slides):
            if len(slide) not in [1, 2]:
                return False, f"Slide {i} a un nombre invalide de photos ({len(slide)})."

            for photo_id in slide:
                if photo_id in used_photos:
                    return False, f"Photo {photo_id} est utilisée plusieurs fois."
                if photo_id not in self.photos:
                    return False, f"ID de photo invalide : {photo_id}."
                used_photos.add(photo_id)

            if len(slide) == 1 and not self.photos[slide[0]].is_horizontal:
                return False, f"Slide {i} contient une seule photo verticale."

            if len(slide) == 2:
                if self.photos[slide[0]].is_horizontal or self.photos[slide[1]].is_horizontal:
                    return False, f"Slide {i} contient une photo horizontale dans une paire verticale."

        return True, "Solution valide."

    def get_slide_tags(self, slide: List[int]) -> Set[str]:
        """Retourne l'ensemble des tags associés à une diapositive."""
        return set().union(*(self.photos[photo_id].tags for photo_id in slide))

    def compute_transition_score(self, tags1: Set[str], tags2: Set[str]) -> int:
        """Calcule le score de transition entre deux ensembles de tags."""
        common_tags = len(tags1 & tags2)  # Nombre de tags communs
        unique_tags_1 = len(tags1 - tags2)  # Nombre de tags uniques au premier ensemble
        unique_tags_2 = len(tags2 - tags1)  # Nombre de tags uniques au second ensemble
        return min(common_tags, unique_tags_1, unique_tags_2)

    def compute_score(self, slides: List[List[int]]) -> int:
        """Calcule le score total d'une séquence de diapositives."""
        if not slides:
            return 0

        total_score = 0
        previous_tags = self.get_slide_tags(slides[0])

        for i in range(1, len(slides)):
            current_tags = self.get_slide_tags(slides[i])
            total_score += self.compute_transition_score(previous_tags, current_tags)
            previous_tags = current_tags

        return total_score

def main():
    """Fonction principale pour lire les fichiers et exécuter les vérifications."""
    input_file = "PetPics-20.txt"
    solution_file = "slideshow.sol"

    # Lire les données d'entrée et la solution
    photos = SolutionChecker.read_input_file(input_file)
    checker = SolutionChecker(photos)
    slides = checker.read_solution_file(solution_file)

    # Vérification de la solution
    is_valid, message = checker.is_valid_solution(slides)
    if not is_valid:
        print(f"Solution invalide : {message}")
        return

    # Calcul du score
    score = checker.compute_score(slides)
    print("Solution valide !")
    print(f"Score total : {score}")

if __name__ == "__main__":
    main()