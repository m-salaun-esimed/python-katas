"""Générateur de gros volumes pour le niveau 10 (ne pas modifier)."""
import numpy as np
import pandas as pd

REGIONS = ["Bretagne", "Pays de la Loire", "Île-de-France", "Occitanie", "Grand Est", "Normandie"]
PRODUITS = {"Clavier": 49.9, "Souris": 19.9, "Écran": 189.0, "Casque": 89.0, "Enceinte": 59.0, "Cafetière": 39.0, "Lampe": 24.5, "Aspirateur": 149.0}


def generer(n: int = 1_000_000, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    produits = np.array(list(PRODUITS))
    idx_prod = rng.integers(0, len(produits), n)
    prix = np.array(list(PRODUITS.values()))[idx_prod] * rng.choice([1.0, 1.0, 0.9, 0.8], n)
    return pd.DataFrame(
        {
            "date": pd.Timestamp("2024-01-01") + pd.to_timedelta(rng.integers(0, 366, n), unit="D"),
            "client": pd.Series(rng.integers(1, 50_000, n)).map("C{:05d}".format),
            "region": np.array(REGIONS)[rng.integers(0, len(REGIONS), n)],
            "produit": produits[idx_prod],
            "quantite": rng.integers(1, 10, n),
            "prix_unitaire": np.round(prix, 2),
        }
    )
