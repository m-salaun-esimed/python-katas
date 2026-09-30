import pytest

from niveau_02_structures.exercices import (
    aplatir,
    compresser,
    decompresser,
    decouper,
    dedoublonner,
    frequence_mots,
    fusionner_dicts,
    grouper_anagrammes,
    grouper_par,
    intersection_triee,
    inverser_dict,
    mots_les_plus_frequents,
    paires_somme,
    top_n_par_categorie,
    transposer,
)


def test_frequence_mots():
    assert frequence_mots("Le chat. le CHIEN, le chat !") == {"le": 3, "chat": 2, "chien": 1}


def test_frequence_mots_vide():
    assert frequence_mots("") == {}
    assert frequence_mots("  !! ") == {}


def test_mots_les_plus_frequents():
    assert mots_les_plus_frequents("b a b c a b", 2) == [("b", 3), ("a", 2)]


def test_mots_les_plus_frequents_egalite_alphabetique():
    assert mots_les_plus_frequents("z y x z y x w", 3) == [("x", 2), ("y", 2), ("z", 2)]


def test_mots_les_plus_frequents_k_trop_grand():
    assert mots_les_plus_frequents("a b", 10) == [("a", 1), ("b", 1)]


def test_dedoublonner():
    assert dedoublonner([3, 1, 3, 2, 1]) == [3, 1, 2]
    assert dedoublonner([]) == []
    assert dedoublonner(["b", "a", "b"]) == ["b", "a"]


def test_dedoublonner_rapide():
    # Avec `if x not in resultat` sur une liste, c'est O(n²) : utilise un set !
    grosse = list(range(200_000)) * 2
    assert dedoublonner(grosse) == list(range(200_000))


def test_intersection_triee():
    assert intersection_triee([5, 1, 3, 3], [3, 5, 7]) == [3, 5]
    assert intersection_triee([1, 2], [3]) == []


def test_grouper_par():
    assert grouper_par(["ane", "bob", "alice"], lambda s: s[0]) == {"a": ["ane", "alice"], "b": ["bob"]}
    assert grouper_par(range(6), lambda n: n % 2) == {0: [0, 2, 4], 1: [1, 3, 5]}
    assert grouper_par([], len) == {}


@pytest.mark.parametrize(
    "entree, attendu",
    [
        ([1, [2, [3, [4]], 5], []], [1, 2, 3, 4, 5]),
        ([], []),
        ([[[[["profond"]]]]], ["profond"]),
        ([1, 2, 3], [1, 2, 3]),
    ],
)
def test_aplatir(entree, attendu):
    assert aplatir(entree) == attendu


def test_inverser_dict():
    assert inverser_dict({"a": 1, "b": 2, "c": 1}) == {1: ["a", "c"], 2: ["b"]}
    assert inverser_dict({"z": 0, "a": 0}) == {0: ["a", "z"]}


def test_transposer():
    assert transposer([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]]
    assert transposer([[1]]) == [[1]]
    assert transposer([]) == []


def test_fusionner_dicts():
    assert fusionner_dicts({"a": 1, "b": 2}, {"b": 3, "c": 4}) == {"a": 1, "b": 5, "c": 4}
    assert fusionner_dicts() == {}
    assert fusionner_dicts({"x": 1}, {"x": 1}, {"x": 1}) == {"x": 3}


def test_fusionner_dicts_ne_modifie_pas_les_entrees():
    d1 = {"a": 1}
    fusionner_dicts(d1, {"a": 5})
    assert d1 == {"a": 1}


def test_grouper_anagrammes():
    mots = ["chien", "niche", "rat", "art", "tar", "seul"]
    assert grouper_anagrammes(mots) == [["art", "rat", "tar"], ["chien", "niche"], ["seul"]]


def test_decouper():
    assert decouper([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]
    assert decouper([1, 2], 5) == [[1, 2]]
    assert decouper([], 3) == []
    with pytest.raises(ValueError):
        decouper([1], 0)


def test_top_n_par_categorie():
    ventes = [
        {"categorie": "fruit", "produit": "pomme", "montant": 10},
        {"categorie": "fruit", "produit": "poire", "montant": 15},
        {"categorie": "fruit", "produit": "pomme", "montant": 10},
        {"categorie": "fruit", "produit": "kiwi", "montant": 1},
        {"categorie": "legume", "produit": "carotte", "montant": 5},
        {"categorie": "legume", "produit": "chou", "montant": 5},
        {"categorie": "legume", "produit": "ail", "montant": 2},
    ]
    assert top_n_par_categorie(ventes, 2) == {
        "fruit": ["pomme", "poire"],
        "legume": ["carotte", "chou"],
    }


def test_paires_somme():
    assert paires_somme([1, 2, 3, 4, 3], 6) == {(2, 4), (3, 3)}
    assert paires_somme([3], 6) == set(), "un élément ne peut pas être pris deux fois"
    assert paires_somme([5, 1, 5, 1], 6) == {(1, 5)}


@pytest.mark.parametrize(
    "brut, compresse",
    [("aaabccdddd", "a3b1c2d4"), ("", ""), ("a", "a1"), ("aaaaaaaaaaaa", "a12"), ("abab", "a1b1a1b1")],
)
def test_compression(brut, compresse):
    assert compresser(brut) == compresse
    assert decompresser(compresse) == brut
