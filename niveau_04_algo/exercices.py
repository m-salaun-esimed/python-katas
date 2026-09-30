"""
NIVEAU 4 — Algorithmique de base
================================

Objectifs : recherche, tris classiques, complexité (O(n), O(n log n), O(n²)),
piles, deux pointeurs, tables de hachage.
INTERDIT dans les tris : sorted() et list.sort() (les tests le vérifient).
Les tests de performance échouent si ta complexité est mauvaise.
Lance :  pytest niveau_04_algo
"""


def recherche_lineaire(elements: list, cible) -> int:
    """Index de la première occurrence de `cible`, -1 si absente (sans .index())."""
    raise NotImplementedError


def recherche_binaire(elements_tries: list, cible) -> int:
    """Recherche dichotomique dans une liste TRIÉE. Retourne un index de `cible`
    ou -1. Doit être en O(log n) : pas de `in`, pas de .index(), pas de boucle sur tout.
    """
    raise NotImplementedError


def tri_bulles(elements: list) -> list:
    """Tri à bulles. Retourne une NOUVELLE liste triée (ne modifie pas l'entrée)."""
    raise NotImplementedError


def tri_insertion(elements: list) -> list:
    """Tri par insertion. Retourne une NOUVELLE liste triée."""
    raise NotImplementedError


def tri_fusion(elements: list) -> list:
    """Tri fusion (merge sort), O(n log n). Retourne une NOUVELLE liste triée."""
    raise NotImplementedError


def tri_rapide(elements: list) -> list:
    """Tri rapide (quicksort). Retourne une NOUVELLE liste triée.
    Attention au pire cas sur une liste déjà triée : choisis bien ton pivot.
    """
    raise NotImplementedError


def pgcd(a: int, b: int) -> int:
    """Plus grand commun diviseur par l'algorithme d'Euclide (sans math.gcd)."""
    raise NotImplementedError


def est_premier(n: int) -> bool:
    """Test de primalité en O(√n)."""
    raise NotImplementedError


def crible_eratosthene(n: int) -> list[int]:
    """Tous les nombres premiers <= n avec le crible d'Ératosthène."""
    raise NotImplementedError


def parentheses_equilibrees(s: str) -> bool:
    """Vrai si les (), [], {} sont bien équilibrées et imbriquées.
    Les autres caractères sont ignorés.   "(a[b]{c})" -> True ; "([)]" -> False
    Indice : une pile.
    """
    raise NotImplementedError


def deux_sommes(nombres: list[int], cible: int) -> tuple[int, int] | None:
    """Retourne (i, j) avec i < j et nombres[i] + nombres[j] == cible,
    la première paire trouvée en parcourant j de gauche à droite. None si aucune.
    Doit être en O(n) (dictionnaire valeur -> index).
    """
    raise NotImplementedError


def somme_max_sous_tableau(nombres: list[int]) -> int:
    """Plus grande somme d'un sous-tableau CONTIGU non vide (algorithme de Kadane, O(n)).
    [-2, 1, -3, 4, -1, 2, 1, -5, 4] -> 6  (sous-tableau [4, -1, 2, 1])
    """
    raise NotImplementedError


def rotation(elements: list, k: int) -> list:
    """Rotation vers la droite de k positions (k peut être > len ou négatif).
    rotation([1, 2, 3, 4, 5], 2) -> [4, 5, 1, 2, 3]
    """
    raise NotImplementedError


def en_binaire(n: int) -> str:
    """Convertit un entier >= 0 en binaire SANS bin() ni format(). 10 -> "1010", 0 -> "0"."""
    raise NotImplementedError


def depuis_binaire(s: str) -> int:
    """Convertit "1010" -> 10 SANS int(s, 2)."""
    raise NotImplementedError


def fusionner_listes_triees(a: list, b: list) -> list:
    """Fusionne deux listes triées en une liste triée, en O(len(a) + len(b)) (deux pointeurs)."""
    raise NotImplementedError


def premier_caractere_unique(s: str) -> str | None:
    """Premier caractère qui n'apparaît qu'une seule fois. "aabbcdc" -> "d". None si aucun."""
    raise NotImplementedError


def est_anagramme(a: str, b: str) -> bool:
    """Vrai si a et b sont anagrammes (casse et espaces ignorés), en O(n)."""
    raise NotImplementedError
