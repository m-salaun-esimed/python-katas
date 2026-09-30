"""
NIVEAU 5 — Algorithmique avancée
================================

Objectifs : programmation dynamique, graphes (BFS, DFS, Dijkstra, tri topologique),
backtracking, tas (heapq), files (deque), intervalles.
Plusieurs tests vérifient les performances : une solution naïve exponentielle échouera.
Lance :  pytest niveau_05_algo_avance

Représentation des graphes : dict {sommet: [voisins]}  (non pondéré)
                             dict {sommet: [(voisin, poids), ...]} (pondéré)
"""


# --- Programmation dynamique ----------------------------------------------
def fibonacci_rapide(n: int) -> int:
    """F(n) avec F(0)=0, F(1)=1. Doit calculer F(10_000) instantanément."""
    raise NotImplementedError


def rendu_monnaie(montant: int, pieces: list[int]) -> int:
    """Nombre MINIMUM de pièces pour atteindre `montant` exactement (pièces illimitées).
    -1 si impossible.  rendu_monnaie(11, [1, 2, 5]) -> 3  (5 + 5 + 1)
    Attention : l'algorithme glouton ne marche pas toujours ! ex. (6, [1, 3, 4]) -> 2
    """
    raise NotImplementedError


def plus_longue_sous_sequence_commune(a: str, b: str) -> int:
    """Longueur de la LCS (sous-séquence, pas forcément contiguë).
    ("ABCBDAB", "BDCABA") -> 4
    """
    raise NotImplementedError


def distance_levenshtein(a: str, b: str) -> int:
    """Nombre minimum d'insertions / suppressions / substitutions pour passer de a à b.
    ("chien", "chiot") -> 2
    """
    raise NotImplementedError


def sac_a_dos(capacite: int, objets: list[tuple[int, int]]) -> int:
    """Sac à dos 0/1. objets = [(poids, valeur), ...]. Retourne la valeur max
    sans dépasser `capacite` (chaque objet pris au plus une fois).
    """
    raise NotImplementedError


def nombre_chemins_grille(lignes: int, colonnes: int, obstacles: set[tuple[int, int]] = frozenset()) -> int:
    """Nombre de chemins de (0, 0) à (lignes-1, colonnes-1) en ne se déplaçant
    que vers la droite ou le bas, en évitant les cases `obstacles` (ligne, colonne).
    """
    raise NotImplementedError


# --- Graphes ---------------------------------------------------------------
def plus_court_chemin(graphe: dict, depart, arrivee) -> list | None:
    """BFS : liste des sommets du plus court chemin (en nombre d'arêtes) de depart
    à arrivee, bornes incluses. None si inatteignable. [depart] si depart == arrivee.
    """
    raise NotImplementedError


def composantes_connexes(graphe: dict) -> list[set]:
    """Graphe NON orienté. Retourne la liste des composantes (sets de sommets),
    triée par taille décroissante puis par plus petit sommet.
    Attention : un sommet peut n'apparaître que comme voisin.
    """
    raise NotImplementedError


def dijkstra(graphe: dict, source) -> dict:
    """Distances minimales depuis `source` vers tous les sommets ATTEIGNABLES.
    graphe = {"A": [("B", 4), ("C", 1)], ...}. Utilise heapq.
    """
    raise NotImplementedError


def tri_topologique(dependances: dict[str, list[str]]) -> list[str]:
    """`dependances[x]` = liste des tâches qui doivent être faites AVANT x.
    Retourne un ordre d'exécution valide. En cas de choix, prendre l'ordre alphabétique
    (le résultat est donc unique). Lève ValueError s'il y a un cycle.
    Exemple : {"deploy": ["test"], "test": ["build"], "build": []} -> ["build", "test", "deploy"]
    """
    raise NotImplementedError


def contient_cycle(graphe: dict) -> bool:
    """Vrai si le graphe ORIENTÉ contient un cycle (DFS avec 3 couleurs)."""
    raise NotImplementedError


# --- Backtracking ----------------------------------------------------------
def permutations(elements: list) -> list[list]:
    """Toutes les permutations (sans itertools), dans l'ordre lexicographique
    des positions : [1,2,3] -> [[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]]
    """
    raise NotImplementedError


def sous_ensembles_somme(nombres: list[int], cible: int) -> list[list[int]]:
    """Tous les sous-ensembles (éléments distincts, positifs) dont la somme vaut `cible`.
    Chaque sous-ensemble trié, la liste finale triée.
    ([2, 3, 5, 7, 8], 10) -> [[2, 3, 5], [2, 8], [3, 7]]
    """
    raise NotImplementedError


def n_reines(n: int) -> int:
    """Nombre de façons de placer n reines sur un échiquier n x n sans qu'elles se menacent."""
    raise NotImplementedError


# --- Tas, files, fenêtres ---------------------------------------------------
def k_plus_grands(nombres: list[int], k: int) -> list[int]:
    """Les k plus grands, triés décroissant, en O(n log k) avec heapq (pas de sorted sur tout)."""
    raise NotImplementedError


def max_fenetre_glissante(nombres: list[int], k: int) -> list[int]:
    """Max de chaque fenêtre de taille k, en O(n) avec collections.deque.
    ([1, 3, -1, -3, 5, 3, 6, 7], 3) -> [3, 3, 5, 5, 6, 7]
    """
    raise NotImplementedError


def fusionner_intervalles(intervalles: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Fusionne les intervalles qui se chevauchent ou se touchent.
    [(1, 3), (2, 6), (8, 10), (10, 12), (15, 18)] -> [(1, 6), (8, 12), (15, 18)]
    """
    raise NotImplementedError


def mediane_flux(flux: list[float]) -> list[float]:
    """Pour chaque nouvel élément du flux, la médiane des éléments vus jusque-là.
    Doit être en O(n log n) avec DEUX tas.   [5, 15, 1, 3] -> [5, 10.0, 5, 4.0]
    """
    raise NotImplementedError
