"""
NIVEAU 1 — Les bases de Python
==============================

Objectifs : variables, conditions, boucles, chaînes, listes simples, exceptions.
Règle du jeu : remplace chaque `raise NotImplementedError` par ton code,
puis lance :  pytest niveau_01_bases

Contrainte : n'utilise PAS les fonctions toutes faites quand l'énoncé l'interdit
(ex : max(), sum(), reversed()...). Le but est d'écrire la boucle toi-même.
"""


def somme_pairs(nombres: list[int]) -> int:
    """Retourne la somme des nombres pairs de la liste.

    >>> somme_pairs([1, 2, 3, 4])
    6
    >>> somme_pairs([])
    0
    """
    somme = 0
    for n in nombres:
        if n % 2 == 0:
            somme += n
    return somme

def inverser_chaine(s: str) -> str:
    """Retourne la chaîne à l'envers (sans utiliser reversed() ni [::-1], fais une boucle).

    >>> inverser_chaine("python")
    'nohtyp'
    """
    raise NotImplementedError


def est_palindrome(s: str) -> bool:
    """Vrai si `s` se lit pareil dans les deux sens, en ignorant la casse,
    les espaces et la ponctuation (on ne garde que les caractères alphanumériques).

    >>> est_palindrome("Esope reste ici et se repose")
    True
    >>> est_palindrome("bonjour")
    False
    """
    raise NotImplementedError


def fizzbuzz(n: int) -> list[str]:
    """Retourne la liste des valeurs de 1 à n incluses, en remplaçant :
    - les multiples de 3 par "Fizz"
    - les multiples de 5 par "Buzz"
    - les multiples de 15 par "FizzBuzz"
    Les autres nombres sont convertis en str.

    >>> fizzbuzz(5)
    ['1', '2', 'Fizz', '4', 'Buzz']
    """
    raise NotImplementedError


def compter_voyelles(s: str) -> int:
    """Compte les voyelles (a, e, i, o, u, y), majuscules comprises.

    >>> compter_voyelles("Python")
    2
    """
    raise NotImplementedError


def maximum(nombres: list[float]) -> float:
    """Retourne le plus grand élément SANS utiliser max().
    Lève ValueError si la liste est vide.

    >>> maximum([3, 9, 2])
    9
    """
    raise NotImplementedError


def celsius_vers_fahrenheit(celsius: float) -> float:
    """Convertit des degrés Celsius en Fahrenheit, arrondi à 1 décimale.
    Formule : F = C * 9/5 + 32

    >>> celsius_vers_fahrenheit(100)
    212.0
    """
    raise NotImplementedError


def annee_bissextile(annee: int) -> bool:
    """Une année est bissextile si elle est divisible par 4,
    sauf si elle est divisible par 100, sauf si elle est divisible par 400.

    >>> annee_bissextile(2024), annee_bissextile(1900), annee_bissextile(2000)
    (True, False, True)
    """
    raise NotImplementedError


def factorielle(n: int) -> int:
    """n! calculée avec une boucle (pas de récursion, pas de math.factorial).
    Lève ValueError si n < 0.  factorielle(0) == 1.
    """
    raise NotImplementedError


def fibonacci(n: int) -> list[int]:
    """Retourne les n premiers termes de la suite de Fibonacci.

    >>> fibonacci(7)
    [0, 1, 1, 2, 3, 5, 8]
    >>> fibonacci(0)
    []
    """
    raise NotImplementedError


def mention(note: float) -> str:
    """Retourne la mention correspondant à une note sur 20 :
    - < 10          -> "Ajourné"
    - [10, 12[      -> "Passable"
    - [12, 14[      -> "Assez bien"
    - [14, 16[      -> "Bien"
    - >= 16         -> "Très bien"
    Lève ValueError si la note n'est pas entre 0 et 20.
    """
    raise NotImplementedError


def nettoyer_nom(nom: str) -> str:
    """Supprime les espaces en trop (début, fin ET multiples au milieu)
    et met chaque mot avec une majuscule.

    >>> nettoyer_nom("   jean    DUPONT  ")
    'Jean Dupont'
    """
    raise NotImplementedError


def compter_mots(phrase: str) -> int:
    """Retourne le nombre de mots (séparés par un ou plusieurs espaces).

    >>> compter_mots("  le   chat dort ")
    3
    """
    raise NotImplementedError


def table_multiplication(n: int, jusqua: int = 10) -> list[str]:
    """Retourne les lignes de la table de n, au format "n x i = résultat".

    >>> table_multiplication(3, 2)
    ['3 x 1 = 3', '3 x 2 = 6']
    """
    raise NotImplementedError
