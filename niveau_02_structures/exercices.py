"""
NIVEAU 2 — Structures de données : listes, dictionnaires, sets, tuples
======================================================================

Objectifs : compréhensions de listes/dicts, collections (Counter, defaultdict),
tri avec `key=`, récursivité simple.
Lance :  pytest niveau_02_structures
"""
from typing import Any, Callable, Hashable, Iterable


def frequence_mots(texte: str) -> dict[str, int]:
    """Compte les occurrences de chaque mot, en minuscules, sans la ponctuation
    (.,;:!?'"). Les mots sont séparés par des espaces.

    >>> frequence_mots("Le chat. le CHIEN, le chat !")
    {'le': 3, 'chat': 2, 'chien': 1}
    """
    raise NotImplementedError


def mots_les_plus_frequents(texte: str, k: int) -> list[tuple[str, int]]:
    """Les k mots les plus fréquents sous forme (mot, nb), triés par nb décroissant
    puis par ordre alphabétique en cas d'égalité.

    >>> mots_les_plus_frequents("b a b c a b", 2)
    [('b', 3), ('a', 2)]
    """
    raise NotImplementedError


def dedoublonner(elements: list) -> list:
    """Supprime les doublons en GARDANT l'ordre de première apparition.

    >>> dedoublonner([3, 1, 3, 2, 1])
    [3, 1, 2]
    """
    raise NotImplementedError


def intersection_triee(a: list, b: list) -> list:
    """Éléments présents dans a ET b, sans doublon, triés.

    >>> intersection_triee([5, 1, 3, 3], [3, 5, 7])
    [3, 5]
    """
    raise NotImplementedError


def grouper_par(elements: Iterable[Any], cle: Callable[[Any], Hashable]) -> dict:
    """Regroupe les éléments dans un dict {cle(element): [elements...]},
    l'ordre des éléments dans chaque liste est préservé.

    >>> grouper_par(["ane", "bob", "alice"], lambda s: s[0])
    {'a': ['ane', 'alice'], 'b': ['bob']}
    """
    raise NotImplementedError


def aplatir(liste_imbriquee: list) -> list:
    """Aplatit une liste imbriquée de profondeur QUELCONQUE.

    >>> aplatir([1, [2, [3, [4]], 5], []])
    [1, 2, 3, 4, 5]
    """
    raise NotImplementedError


def inverser_dict(d: dict) -> dict:
    """Inverse un dict : chaque valeur devient une clé associée à la liste
    (triée) des clés qui avaient cette valeur.

    >>> inverser_dict({"a": 1, "b": 2, "c": 1})
    {1: ['a', 'c'], 2: ['b']}
    """
    raise NotImplementedError


def transposer(matrice: list[list]) -> list[list]:
    """Transpose une matrice (liste de lignes).

    >>> transposer([[1, 2, 3], [4, 5, 6]])
    [[1, 4], [2, 5], [3, 6]]
    """
    raise NotImplementedError


def fusionner_dicts(*dicts: dict[str, float]) -> dict[str, float]:
    """Fusionne plusieurs dicts en ADDITIONNANT les valeurs des clés communes.

    >>> fusionner_dicts({"a": 1, "b": 2}, {"b": 3, "c": 4})
    {'a': 1, 'b': 5, 'c': 4}
    """
    raise NotImplementedError


def grouper_anagrammes(mots: list[str]) -> list[list[str]]:
    """Regroupe les mots qui sont des anagrammes entre eux.
    Chaque groupe est trié alphabétiquement, et la liste des groupes est triée
    par son premier élément.

    >>> grouper_anagrammes(["chien", "niche", "rat", "art", "tar", "seul"])
    [['art', 'rat', 'tar'], ['chien', 'niche'], ['seul']]
    """
    raise NotImplementedError


def decouper(elements: list, taille: int) -> list[list]:
    """Découpe une liste en paquets de `taille` éléments (le dernier peut être plus petit).
    Lève ValueError si taille <= 0.

    >>> decouper([1, 2, 3, 4, 5], 2)
    [[1, 2], [3, 4], [5]]
    """
    raise NotImplementedError


def top_n_par_categorie(ventes: list[dict], n: int) -> dict[str, list[str]]:
    """`ventes` est une liste de dicts {"categorie": str, "produit": str, "montant": float}.
    Un même produit peut apparaître plusieurs fois : il faut SOMMER ses montants.
    Retourne pour chaque catégorie la liste des n produits au plus gros montant total
    (ordre décroissant ; en cas d'égalité, ordre alphabétique du produit).
    """
    raise NotImplementedError


def paires_somme(nombres: list[int], cible: int) -> set[tuple[int, int]]:
    """Toutes les paires (a, b) avec a <= b, a + b == cible, a et b pris
    à des positions différentes de la liste.

    >>> sorted(paires_somme([1, 2, 3, 4, 3], 6))
    [(2, 4), (3, 3)]
    """
    raise NotImplementedError


def compresser(s: str) -> str:
    """Compression RLE : "aaabccdddd" -> "a3b1c2d4".  "" -> "".
    """
    raise NotImplementedError


def decompresser(s: str) -> str:
    """Inverse de compresser. Les nombres peuvent avoir plusieurs chiffres : "a12b1".
    """
    raise NotImplementedError
