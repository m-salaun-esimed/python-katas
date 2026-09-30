import ast
import inspect
import itertools
import random
import statistics
import textwrap
import time

import pytest

from niveau_05_algo_avance import exercices as ex


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


def chrono(f, *args):
    debut = time.perf_counter()
    r = f(*args)
    return r, time.perf_counter() - debut


# --- DP --------------------------------------------------------------------
@pytest.mark.parametrize("n, attendu", [(0, 0), (1, 1), (2, 1), (10, 55), (90, 2880067194370816120)])
def test_fibonacci_rapide(n, attendu):
    assert ex.fibonacci_rapide(n) == attendu


def test_fibonacci_rapide_tres_grand():
    r, duree = chrono(ex.fibonacci_rapide, 10_000)
    assert str(r).startswith("336447648764317832666216120051075433103021484606800639")
    assert duree < 0.5


@pytest.mark.parametrize(
    "montant, pieces, attendu",
    [(11, [1, 2, 5], 3), (6, [1, 3, 4], 2), (3, [2], -1), (0, [1], 0), (7, [2, 4], -1), (100, [1, 5, 10, 25], 4)],
)
def test_rendu_monnaie(montant, pieces, attendu):
    assert ex.rendu_monnaie(montant, pieces) == attendu


def test_rendu_monnaie_performance():
    r, duree = chrono(ex.rendu_monnaie, 10_000, [7, 13, 29, 101])
    assert r == 104
    assert duree < 2


@pytest.mark.parametrize("a, b, attendu", [("ABCBDAB", "BDCABA", 4), ("", "abc", 0), ("abc", "abc", 3), ("abc", "def", 0)])
def test_lcs(a, b, attendu):
    assert ex.plus_longue_sous_sequence_commune(a, b) == attendu


def test_lcs_performance():
    random.seed(1)
    a = "".join(random.choice("ACGT") for _ in range(600))
    b = "".join(random.choice("ACGT") for _ in range(600))
    r, duree = chrono(ex.plus_longue_sous_sequence_commune, a, b)
    assert 350 < r < 450
    assert duree < 3, "Utilise un tableau DP, pas une récursion exponentielle"


@pytest.mark.parametrize(
    "a, b, attendu",
    [("chien", "chiot", 2), ("", "abc", 3), ("kitten", "sitting", 3), ("same", "same", 0), ("flaw", "lawn", 2)],
)
def test_levenshtein(a, b, attendu):
    assert ex.distance_levenshtein(a, b) == attendu


def test_sac_a_dos():
    objets = [(1, 1), (3, 4), (4, 5), (5, 7)]
    assert ex.sac_a_dos(7, objets) == 9
    assert ex.sac_a_dos(0, objets) == 0
    assert ex.sac_a_dos(10, []) == 0
    assert ex.sac_a_dos(50, [(10, 60), (20, 100), (30, 120)]) == 220


def test_sac_a_dos_performance():
    random.seed(3)
    objets = [(random.randint(1, 50), random.randint(1, 100)) for _ in range(200)]
    r, duree = chrono(ex.sac_a_dos, 1000, objets)
    assert r == 4995
    assert duree < 3


def test_chemins_grille():
    assert ex.nombre_chemins_grille(3, 3) == 6
    assert ex.nombre_chemins_grille(1, 1) == 1
    assert ex.nombre_chemins_grille(3, 3, {(1, 1)}) == 2
    assert ex.nombre_chemins_grille(3, 3, {(0, 1), (1, 0)}) == 0
    assert ex.nombre_chemins_grille(18, 18) == 2333606220


# --- Graphes ---------------------------------------------------------------
GRAPHE = {
    "A": ["B", "C"],
    "B": ["A", "D"],
    "C": ["A", "D", "E"],
    "D": ["B", "C", "F"],
    "E": ["C", "F"],
    "F": ["D", "E"],
    "Z": [],
}


def test_plus_court_chemin():
    chemin = ex.plus_court_chemin(GRAPHE, "A", "F")
    assert len(chemin) == 4 and chemin[0] == "A" and chemin[-1] == "F"
    for u, v in itertools.pairwise(chemin):
        assert v in GRAPHE[u]
    assert ex.plus_court_chemin(GRAPHE, "A", "A") == ["A"]
    assert ex.plus_court_chemin(GRAPHE, "A", "Z") is None


def test_plus_court_chemin_grand_graphe():
    # grille 300x300 : un DFS récursif exploserait, il faut un BFS
    n = 300
    g = {}
    for i in range(n):
        for j in range(n):
            g[(i, j)] = [(i + di, j + dj) for di, dj in ((1, 0), (0, 1), (-1, 0), (0, -1)) if 0 <= i + di < n and 0 <= j + dj < n]
    chemin, duree = chrono(ex.plus_court_chemin, g, (0, 0), (n - 1, n - 1))
    assert len(chemin) == 2 * n - 1
    assert duree < 5


def test_composantes_connexes():
    g = {1: [2], 2: [1, 3], 3: [2], 4: [5], 5: [4], 6: [], 7: [8]}
    assert ex.composantes_connexes(g) == [{1, 2, 3}, {4, 5}, {7, 8}, {6}]


def test_dijkstra():
    g = {
        "A": [("B", 4), ("C", 1)],
        "C": [("B", 2), ("D", 7)],
        "B": [("D", 1)],
        "D": [],
        "X": [("A", 1)],
    }
    assert ex.dijkstra(g, "A") == {"A": 0, "B": 3, "C": 1, "D": 4}


def test_dijkstra_performance():
    random.seed(7)
    n = 20_000
    g = {i: [(random.randrange(n), random.randint(1, 100)) for _ in range(5)] for i in range(n)}
    for i in range(n - 1):
        g[i].append((i + 1, 1000))
    dist, duree = chrono(ex.dijkstra, g, 0)
    assert len(dist) == n
    assert duree < 3, "Utilise heapq"


def test_tri_topologique():
    deps = {"deploy": ["test", "build"], "test": ["build"], "build": [], "lint": []}
    assert ex.tri_topologique(deps) == ["build", "lint", "test", "deploy"]


def test_tri_topologique_dependance_non_declaree():
    assert ex.tri_topologique({"b": ["a"]}) == ["a", "b"]


def test_tri_topologique_cycle():
    with pytest.raises(ValueError):
        ex.tri_topologique({"a": ["b"], "b": ["c"], "c": ["a"]})


def test_contient_cycle():
    assert ex.contient_cycle({1: [2], 2: [3], 3: [1]}) is True
    assert ex.contient_cycle({1: [2], 2: [3], 3: []}) is False
    assert ex.contient_cycle({1: [2, 3], 2: [4], 3: [4], 4: []}) is False, "Un losange n'est pas un cycle !"
    assert ex.contient_cycle({1: [1]}) is True


# --- Backtracking ----------------------------------------------------------
def test_permutations():
    assert ex.permutations([1, 2, 3]) == [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]
    assert ex.permutations([]) == [[]]
    assert len(ex.permutations(list(range(7)))) == 5040
    source = inspect.getsource(ex)
    assert "itertools.permutations" not in source and "from itertools import permutations" not in source


def test_sous_ensembles_somme():
    assert ex.sous_ensembles_somme([2, 3, 5, 7, 8], 10) == [[2, 3, 5], [2, 8], [3, 7]]
    assert ex.sous_ensembles_somme([1, 2], 10) == []


@pytest.mark.parametrize("n, attendu", [(1, 1), (4, 2), (6, 4), (8, 92)])
def test_n_reines(n, attendu):
    assert ex.n_reines(n) == attendu


# --- Tas / files -----------------------------------------------------------
def test_k_plus_grands():
    assert ex.k_plus_grands([5, 1, 9, 3, 7, 9], 3) == [9, 9, 7]
    assert ex.k_plus_grands([1], 5) == [1]
    random.seed(0)
    gros = [random.random() for _ in range(500_000)]
    assert ex.k_plus_grands(gros, 5) == sorted(gros, reverse=True)[:5]


def test_max_fenetre_glissante():
    assert ex.max_fenetre_glissante([1, 3, -1, -3, 5, 3, 6, 7], 3) == [3, 3, 5, 5, 6, 7]
    assert ex.max_fenetre_glissante([4, 2], 1) == [4, 2]


def test_max_fenetre_glissante_lineaire():
    nombres = list(range(300_000, 0, -1))
    r, duree = chrono(ex.max_fenetre_glissante, nombres, 50_000)
    assert r[0] == 300_000 and r[-1] == 50_000
    assert duree < 2, "O(n·k) est trop lent : utilise une deque monotone"


def test_fusionner_intervalles():
    assert ex.fusionner_intervalles([(1, 3), (2, 6), (8, 10), (10, 12), (15, 18)]) == [(1, 6), (8, 12), (15, 18)]
    assert ex.fusionner_intervalles([(5, 6), (1, 2)]) == [(1, 2), (5, 6)]
    assert ex.fusionner_intervalles([(1, 10), (2, 3)]) == [(1, 10)]
    assert ex.fusionner_intervalles([]) == []


def test_mediane_flux():
    assert ex.mediane_flux([5, 15, 1, 3]) == [5, 10.0, 5, 4.0]
    random.seed(5)
    flux = [random.randint(0, 1000) for _ in range(200)]
    attendu = [statistics.median(flux[: i + 1]) for i in range(len(flux))]
    assert ex.mediane_flux(flux) == attendu


def test_mediane_flux_performance():
    random.seed(9)
    flux = [random.random() for _ in range(100_000)]
    r, duree = chrono(ex.mediane_flux, flux)
    assert len(r) == 100_000
    assert duree < 3, "Utilise deux tas (heapq)"
