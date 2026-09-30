"""
NIVEAU 3 — Fonctions avancées, POO, exceptions, générateurs, décorateurs
========================================================================

Objectifs : classes, méthodes spéciales (__add__, __eq__, __len__...),
@property, @dataclass, exceptions personnalisées, générateurs (yield),
décorateurs, context managers.
Lance :  pytest niveau_03_fonctions_poo
"""
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Iterator


# ---------------------------------------------------------------------------
# 1. Exceptions + classe
# ---------------------------------------------------------------------------
class SoldeInsuffisantError(Exception):
    """Levée quand on retire plus que le solde disponible."""


class CompteBancaire:
    """Un compte bancaire.

    - `CompteBancaire("Alice", solde_initial=100)`
    - `.titulaire` : str
    - `.solde` : PROPRIÉTÉ en lecture seule (@property) -> impossible de faire `compte.solde = 5`
    - `.deposer(montant)` : ValueError si montant <= 0
    - `.retirer(montant)` : ValueError si montant <= 0, SoldeInsuffisantError si montant > solde
    - `.historique` : liste de tuples ("depot" | "retrait", montant), dans l'ordre
    - `.virer(autre_compte, montant)` : retrait ici + dépôt là-bas
      (si le retrait échoue, rien ne doit changer sur l'autre compte)
    """

    def __init__(self, titulaire: str, solde_initial: float = 0):
        raise NotImplementedError


# ---------------------------------------------------------------------------
# 2. Méthodes spéciales
# ---------------------------------------------------------------------------
class Vecteur:
    """Vecteur 2D.

    >>> v = Vecteur(1, 2) + Vecteur(3, 4)
    >>> v
    Vecteur(4, 6)
    >>> Vecteur(1, 2) * 3
    Vecteur(3, 6)
    >>> 3 * Vecteur(1, 2)          # __rmul__
    Vecteur(3, 6)
    >>> abs(Vecteur(3, 4))         # norme
    5.0
    >>> Vecteur(1, 2) == Vecteur(1, 2)
    True

    Les vecteurs doivent aussi être utilisables comme clés de dict (__hash__).
    """

    def __init__(self, x: float, y: float):
        raise NotImplementedError


# ---------------------------------------------------------------------------
# 3. Générateurs
# ---------------------------------------------------------------------------
def lire_par_lots(iterable: Iterable, taille: int) -> Iterator[list]:
    """GÉNÉRATEUR qui produit des listes de `taille` éléments.
    Doit fonctionner sur un itérable infini (donc pas de list(iterable) !).

    >>> list(lire_par_lots(range(5), 2))
    [[0, 1], [2, 3], [4]]
    """
    raise NotImplementedError


def nombres_premiers() -> Iterator[int]:
    """GÉNÉRATEUR INFINI des nombres premiers : 2, 3, 5, 7, 11, ..."""
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 4. Décorateurs
# ---------------------------------------------------------------------------
def memoize(fonction: Callable) -> Callable:
    """Décorateur qui met en cache les résultats selon les arguments positionnels.
    Doit conserver le nom et la docstring de la fonction (functools.wraps).
    """
    raise NotImplementedError


def compter_appels(fonction: Callable) -> Callable:
    """Décorateur : la fonction décorée a un attribut `.appels` (int)
    qui compte le nombre de fois où elle a été appelée.
    """
    raise NotImplementedError


def reessayer(tentatives: int, exceptions: tuple = (Exception,)) -> Callable:
    """Décorateur PARAMÉTRÉ : rappelle la fonction jusqu'à `tentatives` fois
    si elle lève une des `exceptions`. Si toutes les tentatives échouent,
    la dernière exception est relevée. Les autres exceptions passent directement.

    @reessayer(3, exceptions=(ConnectionError,))
    def appeler_api(): ...
    """
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 5. Context manager
# ---------------------------------------------------------------------------
class Chronometre:
    """Context manager qui mesure la durée du bloc (time.perf_counter).

    with Chronometre() as c:
        faire_un_truc()
    print(c.duree)   # float en secondes, disponible après le bloc

    Il ne doit PAS avaler les exceptions du bloc (mais la durée doit être remplie).
    """

    def __init__(self):
        raise NotImplementedError


# ---------------------------------------------------------------------------
# 6. Dataclasses
# ---------------------------------------------------------------------------
@dataclass
class Produit:
    """Un produit : nom (str), prix (float), quantite (int, défaut 1).
    Dans __post_init__ : ValueError si prix < 0 ou quantite < 1.
    Propriété `total` = prix * quantite.
    """

    nom: str
    prix: float
    # TODO: quantite, __post_init__, total


@dataclass
class Panier:
    """Panier de produits.

    - `produits` : liste (ATTENTION au piège de la valeur par défaut mutable -> field(default_factory=...))
    - `ajouter(produit)`
    - `total(remise_pct=0)` : somme des totaux, remise en % appliquée, arrondi à 2 décimales
    - `len(panier)` : nombre total d'ARTICLES (somme des quantités)
    """

    # TODO


# ---------------------------------------------------------------------------
# 7. Structures maison
# ---------------------------------------------------------------------------
class Pile:
    """Pile LIFO : empiler(x), depiler() -> x, sommet() -> x, est_vide(), len().
    depiler/sommet sur une pile vide -> IndexError("pile vide").
    """

    def __init__(self):
        raise NotImplementedError


class CacheLRU:
    """Cache LRU (Least Recently Used) de capacité fixe.

    - `get(cle)` -> valeur ou None ; un get rend la clé "récemment utilisée"
    - `put(cle, valeur)` ; si la capacité est dépassée, on supprime la clé
      la moins récemment utilisée.
    - `len(cache)`
    Indice : collections.OrderedDict (move_to_end, popitem(last=False)).
    """

    def __init__(self, capacite: int):
        raise NotImplementedError


def parser_ligne(ligne: str) -> dict[str, Any]:
    """Parse une ligne "nom;age;ville;salaire" en dict typé :
    {"nom": str, "age": int, "ville": str, "salaire": float}
    - supprime les espaces autour des champs
    - le salaire peut utiliser une virgule décimale : "2500,50"
    - lève ValueError avec un message clair si nb de champs incorrect,
      âge non entier ou négatif.
    """
    raise NotImplementedError
