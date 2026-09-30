import ast
import inspect
import random
import textwrap
import time

import pytest

from niveau_04_algo import exercices as ex


def appels_dans(fonction) -> set[str]:
    arbre = ast.parse(textwrap.dedent(inspect.getsource(fonction)))
    noms = set()
    for noeud in ast.walk(arbre):
        if isinstance(noeud, ast.Call):
            if isinstance(noeud.func, ast.Name):
                noms.add(noeud.func.id)
            elif isinstance(noeud.func, ast.Attribute):
                noms.add(noeud.func.attr)
    return noms


class ListeEspion(list):
    """Liste qui compte les accès par index et interdit `in` / .index()."""

    def __init__(self, *a):
        super().__init__(*a)
        self.acces = 0

    def __getitem__(self, i):
        self.acces += 1
        return super().__getitem__(i)

    def __contains__(self, x):
        raise AssertionError("`in` interdit : c'est une recherche linéaire O(n) !")

    def index(self, *a):
        raise AssertionError(".index() interdit")


CAS_TRI = [
    [],
    [1],
    [2, 1],
    [5, 3, 8, 1, 9, 2],
    [3, 3, 1, 1, 2, 2],
    [-1, -5, 0, 10, -5],
    list(range(20, 0, -1)),
    [0.5, -0.25, 3.75],
]


# --- recherche -------------------------------------------------------------
def test_recherche_lineaire():
    assert ex.recherche_lineaire([4, 2, 7, 2], 2) == 1
    assert ex.recherche_lineaire([4, 2, 7], 9) == -1
    assert ex.recherche_lineaire([], 1) == -1
    assert "index" not in appels_dans(ex.recherche_lineaire)


@pytest.mark.parametrize("cible", [0, 1, 500, 998, 999])
def test_recherche_binaire_trouve(cible):
    elements = list(range(1000))
    assert ex.recherche_binaire(elements, cible) == cible


@pytest.mark.parametrize("elements, cible", [([], 3), ([1, 3, 5], 4), ([1, 3, 5], 0), ([1, 3, 5], 6)])
def test_recherche_binaire_absent(elements, cible):
    assert ex.recherche_binaire(elements, cible) == -1


def test_recherche_binaire_est_logarithmique():
    elements = ListeEspion(range(0, 2_000_000, 2))
    assert ex.recherche_binaire(elements, 1_337_336) == 668_668
    assert elements.acces <= 45, f"{elements.acces} accès : ce n'est pas du O(log n)"


# --- tris ------------------------------------------------------------------
TRIS = ["tri_bulles", "tri_insertion", "tri_fusion", "tri_rapide"]


@pytest.mark.parametrize("nom", TRIS)
@pytest.mark.parametrize("cas", CAS_TRI)
def test_tris(nom, cas):
    copie = list(cas)
    assert getattr(ex, nom)(cas) == sorted(copie)
    assert cas == copie, "La liste d'entrée ne doit pas être modifiée"


@pytest.mark.parametrize("nom", TRIS)
def test_tris_sans_sorted(nom):
    interdits = {"sorted", "sort"} & appels_dans(getattr(ex, nom))
    assert not interdits, f"Interdit dans {nom} : {interdits}"


@pytest.mark.parametrize("nom", ["tri_fusion", "tri_rapide"])
def test_tris_rapides_sur_gros_volume(nom):
    random.seed(42)
    donnees = [random.randint(-10**6, 10**6) for _ in range(200_000)]
    debut = time.perf_counter()
    resultat = getattr(ex, nom)(donnees)
    duree = time.perf_counter() - debut
    assert resultat == sorted(donnees)
    assert duree < 5, f"{nom} trop lent ({duree:.1f}s) : ce n'est pas du O(n log n)"


def test_tri_rapide_liste_deja_triee_et_doublons():
    deja_triee = list(range(50_000))
    assert ex.tri_rapide(deja_triee) == deja_triee
    que_des_doublons = [7] * 50_000
    assert ex.tri_rapide(que_des_doublons) == que_des_doublons


# --- arithmétique ----------------------------------------------------------
@pytest.mark.parametrize("a, b, attendu", [(12, 18, 6), (17, 5, 1), (0, 9, 9), (100, 10, 10), (270, 192, 6)])
def test_pgcd(a, b, attendu):
    assert ex.pgcd(a, b) == attendu
    assert "gcd" not in appels_dans(ex.pgcd)


@pytest.mark.parametrize("n, attendu", [(0, False), (1, False), (2, True), (3, True), (4, False), (97, True), (91, False), (7919, True)])
def test_est_premier(n, attendu):
    assert ex.est_premier(n) is attendu


def test_est_premier_grand_nombre_rapide():
    debut = time.perf_counter()
    assert ex.est_premier(1_000_000_007) is True
    assert time.perf_counter() - debut < 1, "Utilise la borne √n"


def test_crible():
    assert ex.crible_eratosthene(30) == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    assert ex.crible_eratosthene(1) == []
    assert len(ex.crible_eratosthene(1_000_000)) == 78498


# --- piles / hachage -------------------------------------------------------
@pytest.mark.parametrize(
    "s, attendu",
    [("(a[b]{c})", True), ("([)]", False), ("", True), ("((", False), ("))", False), ("{[()()]}", True), ("x)(", False)],
)
def test_parentheses(s, attendu):
    assert ex.parentheses_equilibrees(s) is attendu


def test_deux_sommes():
    assert ex.deux_sommes([2, 7, 11, 15], 9) == (0, 1)
    assert ex.deux_sommes([3, 2, 4], 6) == (1, 2)
    assert ex.deux_sommes([3, 3], 6) == (0, 1)
    assert ex.deux_sommes([1, 2], 10) is None


def test_deux_sommes_lineaire():
    nombres = list(range(300_000))
    debut = time.perf_counter()
    assert ex.deux_sommes(nombres, 599_997) == (299_998, 299_999)
    assert time.perf_counter() - debut < 1, "Trop lent : utilise un dictionnaire"


@pytest.mark.parametrize(
    "nombres, attendu",
    [([-2, 1, -3, 4, -1, 2, 1, -5, 4], 6), ([1], 1), ([-3, -1, -2], -1), ([5, 4, -1, 7, 8], 23)],
)
def test_kadane(nombres, attendu):
    assert ex.somme_max_sous_tableau(nombres) == attendu


@pytest.mark.parametrize(
    "k, attendu",
    [(2, [4, 5, 1, 2, 3]), (0, [1, 2, 3, 4, 5]), (5, [1, 2, 3, 4, 5]), (7, [4, 5, 1, 2, 3]), (-1, [2, 3, 4, 5, 1])],
)
def test_rotation(k, attendu):
    assert ex.rotation([1, 2, 3, 4, 5], k) == attendu


def test_rotation_vide():
    assert ex.rotation([], 3) == []


@pytest.mark.parametrize("n", [0, 1, 2, 10, 255, 1024, 123456789])
def test_binaire_aller_retour(n):
    assert ex.en_binaire(n) == bin(n)[2:]
    assert ex.depuis_binaire(bin(n)[2:]) == n


def test_binaire_sans_raccourci():
    assert not {"bin", "format"} & appels_dans(ex.en_binaire)
    assert "int" not in appels_dans(ex.depuis_binaire)


def test_fusionner_listes_triees():
    assert ex.fusionner_listes_triees([1, 4, 9], [2, 3, 10, 11]) == [1, 2, 3, 4, 9, 10, 11]
    assert ex.fusionner_listes_triees([], [1]) == [1]
    assert not {"sorted", "sort"} & appels_dans(ex.fusionner_listes_triees)


@pytest.mark.parametrize("s, attendu", [("aabbcdc", "d"), ("aabb", None), ("", None), ("z", "z")])
def test_premier_caractere_unique(s, attendu):
    assert ex.premier_caractere_unique(s) == attendu


@pytest.mark.parametrize("a, b, attendu", [("Chien", "niche", True), ("la crise", "sale cri", True), ("abc", "abd", False), ("aab", "abb", False)])
def test_est_anagramme(a, b, attendu):
    assert ex.est_anagramme(a, b) is attendu
