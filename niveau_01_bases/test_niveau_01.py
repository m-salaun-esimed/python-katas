import ast
import inspect
import textwrap

import pytest

from niveau_01_bases.exercices import (
    annee_bissextile,
    celsius_vers_fahrenheit,
    compter_mots,
    compter_voyelles,
    est_palindrome,
    factorielle,
    fibonacci,
    fizzbuzz,
    inverser_chaine,
    maximum,
    mention,
    nettoyer_nom,
    somme_pairs,
    table_multiplication,
)


def appels_dans(fonction) -> set[str]:
    """Noms des fonctions appelées dans le code source d'une fonction."""
    arbre = ast.parse(textwrap.dedent(inspect.getsource(fonction)))
    noms = set()
    for noeud in ast.walk(arbre):
        if isinstance(noeud, ast.Call):
            if isinstance(noeud.func, ast.Name):
                noms.add(noeud.func.id)
            elif isinstance(noeud.func, ast.Attribute):
                noms.add(noeud.func.attr)
    return noms


def utilise_slice_negatif(fonction) -> bool:
    arbre = ast.parse(textwrap.dedent(inspect.getsource(fonction)))
    return any(isinstance(n, ast.Slice) and n.step is not None for n in ast.walk(arbre))


# --- somme_pairs -----------------------------------------------------------
@pytest.mark.parametrize(
    "entree, attendu",
    [([1, 2, 3, 4], 6), ([], 0), ([1, 3, 5], 0), ([-2, -4, 3], -6), ([0], 0)],
)
def test_somme_pairs(entree, attendu):
    assert somme_pairs(entree) == attendu


# --- inverser_chaine -------------------------------------------------------
@pytest.mark.parametrize("s, attendu", [("python", "nohtyp"), ("", ""), ("a", "a"), ("été", "été"), ("abc d", "d cba")])
def test_inverser_chaine(s, attendu):
    assert inverser_chaine(s) == attendu


def test_inverser_chaine_sans_raccourci():
    assert "reversed" not in appels_dans(inverser_chaine), "Interdit : reversed()"
    assert not utilise_slice_negatif(inverser_chaine), "Interdit : s[::-1], écris la boucle !"


# --- est_palindrome --------------------------------------------------------
@pytest.mark.parametrize(
    "s, attendu",
    [
        ("kayak", True),
        ("Kayak", True),
        ("Esope reste ici et se repose", True),
        ("A man, a plan, a canal: Panama!", True),
        ("bonjour", False),
        ("", True),
        ("ab", False),
    ],
)
def test_est_palindrome(s, attendu):
    assert est_palindrome(s) is attendu


# --- fizzbuzz --------------------------------------------------------------
def test_fizzbuzz_debut():
    assert fizzbuzz(5) == ["1", "2", "Fizz", "4", "Buzz"]


def test_fizzbuzz_15():
    resultat = fizzbuzz(15)
    assert len(resultat) == 15
    assert resultat[14] == "FizzBuzz"
    assert resultat[8] == "Fizz"
    assert resultat[9] == "Buzz"


def test_fizzbuzz_zero():
    assert fizzbuzz(0) == []


# --- compter_voyelles ------------------------------------------------------
@pytest.mark.parametrize("s, attendu", [("Python", 2), ("", 0), ("AEIOUY", 6), ("bcdf", 0), ("Bonjour le monde", 6)])
def test_compter_voyelles(s, attendu):
    assert compter_voyelles(s) == attendu


# --- maximum ---------------------------------------------------------------
@pytest.mark.parametrize("entree, attendu", [([3, 9, 2], 9), ([-5, -1, -9], -1), ([4], 4), ([1.5, 1.2], 1.5)])
def test_maximum(entree, attendu):
    assert maximum(entree) == attendu


def test_maximum_vide():
    with pytest.raises(ValueError):
        maximum([])


def test_maximum_sans_max():
    assert not {"max", "sorted"} & appels_dans(maximum), "Interdit : max() et sorted()"


# --- celsius_vers_fahrenheit ----------------------------------------------
@pytest.mark.parametrize("c, f", [(0, 32.0), (100, 212.0), (-40, -40.0), (37, 98.6), (21.3, 70.3)])
def test_celsius(c, f):
    assert celsius_vers_fahrenheit(c) == f


# --- annee_bissextile ------------------------------------------------------
@pytest.mark.parametrize("annee, attendu", [(2024, True), (2023, False), (1900, False), (2000, True), (2100, False), (1600, True)])
def test_bissextile(annee, attendu):
    assert annee_bissextile(annee) is attendu


# --- factorielle -----------------------------------------------------------
@pytest.mark.parametrize("n, attendu", [(0, 1), (1, 1), (5, 120), (10, 3628800), (20, 2432902008176640000)])
def test_factorielle(n, attendu):
    assert factorielle(n) == attendu


def test_factorielle_negatif():
    with pytest.raises(ValueError):
        factorielle(-1)


def test_factorielle_sans_math():
    assert "factorial" not in appels_dans(factorielle)
    assert "factorielle" not in appels_dans(factorielle), "Pas de récursion ici, utilise une boucle"


# --- fibonacci -------------------------------------------------------------
@pytest.mark.parametrize(
    "n, attendu",
    [(0, []), (1, [0]), (2, [0, 1]), (7, [0, 1, 1, 2, 3, 5, 8])],
)
def test_fibonacci(n, attendu):
    assert fibonacci(n) == attendu


def test_fibonacci_long():
    assert fibonacci(50)[-1] == 7778742049


# --- mention ---------------------------------------------------------------
@pytest.mark.parametrize(
    "note, attendu",
    [
        (0, "Ajourné"),
        (9.99, "Ajourné"),
        (10, "Passable"),
        (11.5, "Passable"),
        (12, "Assez bien"),
        (14, "Bien"),
        (15.9, "Bien"),
        (16, "Très bien"),
        (20, "Très bien"),
    ],
)
def test_mention(note, attendu):
    assert mention(note) == attendu


@pytest.mark.parametrize("note", [-1, 20.5, 100])
def test_mention_invalide(note):
    with pytest.raises(ValueError):
        mention(note)


# --- nettoyer_nom ----------------------------------------------------------
@pytest.mark.parametrize(
    "nom, attendu",
    [
        ("   jean    DUPONT  ", "Jean Dupont"),
        ("marie", "Marie"),
        ("", ""),
        ("  ANNE   claire  martin ", "Anne Claire Martin"),
    ],
)
def test_nettoyer_nom(nom, attendu):
    assert nettoyer_nom(nom) == attendu


# --- compter_mots ----------------------------------------------------------
@pytest.mark.parametrize("phrase, attendu", [("  le   chat dort ", 3), ("", 0), ("   ", 0), ("un", 1)])
def test_compter_mots(phrase, attendu):
    assert compter_mots(phrase) == attendu


# --- table_multiplication --------------------------------------------------
def test_table_multiplication():
    assert table_multiplication(3, 2) == ["3 x 1 = 3", "3 x 2 = 6"]
    table = table_multiplication(7)
    assert len(table) == 10
    assert table[-1] == "7 x 10 = 70"
