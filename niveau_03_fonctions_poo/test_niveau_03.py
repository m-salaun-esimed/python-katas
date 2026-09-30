import itertools
import time

import pytest

from niveau_03_fonctions_poo.exercices import (
    CacheLRU,
    Chronometre,
    CompteBancaire,
    Panier,
    Pile,
    Produit,
    SoldeInsuffisantError,
    Vecteur,
    compter_appels,
    lire_par_lots,
    memoize,
    nombres_premiers,
    parser_ligne,
    reessayer,
)


# --- CompteBancaire --------------------------------------------------------
def test_compte_depot_retrait():
    c = CompteBancaire("Alice", 100)
    c.deposer(50)
    c.retirer(30)
    assert c.solde == 120
    assert c.titulaire == "Alice"
    assert c.historique == [("depot", 50), ("retrait", 30)]


def test_compte_solde_par_defaut():
    assert CompteBancaire("Bob").solde == 0


def test_compte_solde_lecture_seule():
    c = CompteBancaire("Alice", 100)
    with pytest.raises(AttributeError):
        c.solde = 1_000_000


def test_compte_erreurs():
    c = CompteBancaire("Alice", 100)
    with pytest.raises(SoldeInsuffisantError):
        c.retirer(101)
    with pytest.raises(ValueError):
        c.deposer(0)
    with pytest.raises(ValueError):
        c.retirer(-5)
    assert c.solde == 100
    assert c.historique == []


def test_solde_insuffisant_est_une_exception():
    assert issubclass(SoldeInsuffisantError, Exception)


def test_virement():
    a, b = CompteBancaire("A", 100), CompteBancaire("B", 0)
    a.virer(b, 40)
    assert (a.solde, b.solde) == (60, 40)
    with pytest.raises(SoldeInsuffisantError):
        a.virer(b, 1000)
    assert (a.solde, b.solde) == (60, 40)


# --- Vecteur ---------------------------------------------------------------
def test_vecteur_operations():
    assert Vecteur(1, 2) + Vecteur(3, 4) == Vecteur(4, 6)
    assert Vecteur(1, 2) * 3 == Vecteur(3, 6)
    assert 3 * Vecteur(1, 2) == Vecteur(3, 6)
    assert abs(Vecteur(3, 4)) == 5.0
    assert Vecteur(1, 2) != Vecteur(2, 1)


def test_vecteur_repr():
    assert repr(Vecteur(4, 6)) == "Vecteur(4, 6)"


def test_vecteur_hashable():
    d = {Vecteur(1, 1): "a"}
    assert d[Vecteur(1, 1)] == "a"
    assert len({Vecteur(0, 0), Vecteur(0, 0), Vecteur(1, 0)}) == 2


def test_vecteur_egalite_autre_type():
    assert (Vecteur(1, 2) == (1, 2)) is False


# --- Générateurs -----------------------------------------------------------
def test_lire_par_lots():
    assert list(lire_par_lots(range(5), 2)) == [[0, 1], [2, 3], [4]]
    assert list(lire_par_lots([], 3)) == []


def test_lire_par_lots_est_un_generateur_paresseux():
    lots = lire_par_lots(itertools.count(), 3)  # itérable INFINI
    assert next(lots) == [0, 1, 2]
    assert next(lots) == [3, 4, 5]


def test_nombres_premiers():
    assert list(itertools.islice(nombres_premiers(), 10)) == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]


def test_nombres_premiers_millieme():
    assert next(itertools.islice(nombres_premiers(), 999, None)) == 7919


# --- Décorateurs -----------------------------------------------------------
def test_memoize_cache():
    appels = []

    @memoize
    def carre(x):
        """doc"""
        appels.append(x)
        return x * x

    assert carre(4) == 16
    assert carre(4) == 16
    assert carre(5) == 25
    assert appels == [4, 5]
    assert carre.__name__ == "carre"
    assert carre.__doc__ == "doc"


def test_memoize_fibonacci_rapide():
    @memoize
    def fib(n):
        return n if n < 2 else fib(n - 1) + fib(n - 2)

    debut = time.perf_counter()
    assert fib(90) == 2880067194370816120
    assert time.perf_counter() - debut < 0.5


def test_compter_appels():
    @compter_appels
    def f(a, b=0):
        return a + b

    assert f.appels == 0
    f(1)
    f(1, b=2)
    assert f(2, 3) == 5
    assert f.appels == 3


def test_reessayer_finit_par_reussir():
    tentatives = []

    @reessayer(3, exceptions=(ConnectionError,))
    def instable():
        tentatives.append(1)
        if len(tentatives) < 3:
            raise ConnectionError("réseau")
        return "ok"

    assert instable() == "ok"
    assert len(tentatives) == 3


def test_reessayer_abandonne():
    tentatives = []

    @reessayer(2, exceptions=(ConnectionError,))
    def toujours_ko():
        tentatives.append(1)
        raise ConnectionError("réseau")

    with pytest.raises(ConnectionError):
        toujours_ko()
    assert len(tentatives) == 2


def test_reessayer_ne_rattrape_pas_les_autres_exceptions():
    tentatives = []

    @reessayer(5, exceptions=(ConnectionError,))
    def bug():
        tentatives.append(1)
        raise KeyError("bug")

    with pytest.raises(KeyError):
        bug()
    assert len(tentatives) == 1


# --- Chronometre -----------------------------------------------------------
def test_chronometre():
    with Chronometre() as c:
        time.sleep(0.05)
    assert 0.04 < c.duree < 0.5


def test_chronometre_n_avale_pas_les_exceptions():
    c = Chronometre()
    with pytest.raises(ZeroDivisionError):
        with c:
            1 / 0
    assert c.duree is not None and c.duree >= 0


# --- Dataclasses -----------------------------------------------------------
def test_produit():
    p = Produit("stylo", 1.5, 4)
    assert p.total == 6.0
    assert Produit("gomme", 2).quantite == 1
    assert Produit("a", 1) == Produit("a", 1)


@pytest.mark.parametrize("prix, quantite", [(-1, 1), (1, 0)])
def test_produit_invalide(prix, quantite):
    with pytest.raises(ValueError):
        Produit("x", prix, quantite)


def test_panier():
    panier = Panier()
    panier.ajouter(Produit("stylo", 1.5, 4))
    panier.ajouter(Produit("cahier", 3.99))
    assert len(panier) == 5
    assert panier.total() == 9.99
    assert panier.total(remise_pct=10) == 8.99


def test_panier_pas_de_liste_partagee():
    p1, p2 = Panier(), Panier()
    p1.ajouter(Produit("x", 1))
    assert len(p2) == 0, "Piège de la valeur par défaut mutable !"


# --- Pile ------------------------------------------------------------------
def test_pile():
    p = Pile()
    assert p.est_vide()
    p.empiler(1)
    p.empiler(2)
    assert len(p) == 2
    assert p.sommet() == 2
    assert p.depiler() == 2
    assert p.depiler() == 1
    assert p.est_vide()
    with pytest.raises(IndexError):
        p.depiler()
    with pytest.raises(IndexError):
        p.sommet()


# --- CacheLRU --------------------------------------------------------------
def test_cache_lru():
    c = CacheLRU(2)
    c.put("a", 1)
    c.put("b", 2)
    assert c.get("a") == 1  # "a" devient récent
    c.put("c", 3)  # éjecte "b"
    assert c.get("b") is None
    assert c.get("a") == 1
    assert c.get("c") == 3
    assert len(c) == 2


def test_cache_lru_mise_a_jour():
    c = CacheLRU(2)
    c.put("a", 1)
    c.put("b", 2)
    c.put("a", 10)  # met à jour ET rend "a" récent
    c.put("c", 3)  # éjecte "b"
    assert c.get("a") == 10
    assert c.get("b") is None


# --- parser_ligne ----------------------------------------------------------
def test_parser_ligne():
    assert parser_ligne(" Jean ; 34 ; Brest ; 2500,50 ") == {
        "nom": "Jean",
        "age": 34,
        "ville": "Brest",
        "salaire": 2500.5,
    }
    assert parser_ligne("Ana;20;Lyon;1800")["salaire"] == 1800.0


@pytest.mark.parametrize("ligne", ["Jean;34;Brest", "Jean;trente;Brest;10", "Jean;-3;Brest;10", "a;1;b;c;d"])
def test_parser_ligne_invalide(ligne):
    with pytest.raises(ValueError):
        parser_ligne(ligne)
