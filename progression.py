"""Tableau de bord de ta progression.

    python progression.py            # tous les niveaux
    python progression.py 1 4 8      # seulement certains niveaux
"""
import re
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).parent
NIVEAUX = sorted(p for p in RACINE.glob("niveau_*") if p.is_dir())
VERT, JAUNE, ROUGE, GRIS, RESET = "\033[32m", "\033[33m", "\033[31m", "\033[90m", "\033[0m"


def lancer(niveau: Path) -> dict:
    sortie = subprocess.run(
        [sys.executable, "-m", "pytest", str(niveau), "-o", "addopts=-p no:cacheprovider", "-q", "--tb=no", "-rN", "-p", "no:warnings"],
        cwd=RACINE, capture_output=True, text=True,
    ).stdout
    derniere = sortie.strip().splitlines()[-1] if sortie.strip() else ""
    compte = {k: int(v) for v, k in re.findall(r"(\d+) (passed|failed|errors?|skipped)", derniere)}
    compte["error"] = compte.pop("errors", 0) + compte.pop("error", 0)
    return compte


def barre(ok: int, total: int, largeur: int = 30) -> str:
    plein = round(largeur * ok / total) if total else 0
    return "█" * plein + "░" * (largeur - plein)


def main() -> None:
    choix = {int(a) for a in sys.argv[1:]}
    total_ok = total = 0
    print()
    for niveau in NIVEAUX:
        numero = int(niveau.name.split("_")[1])
        if choix and numero not in choix:
            continue
        c = lancer(niveau)
        ok, n = c.get("passed", 0), sum(c.values())
        total_ok, total = total_ok + ok, total + n
        if c.get("skipped") and not ok:
            couleur, statut = GRIS, "ignoré (docker compose up -d ?)"
        else:
            couleur = VERT if n and ok == n else JAUNE if ok else ROUGE
            statut = "✔ terminé" if n and ok == n else f"{ok}/{n}"
        print(f"{couleur}{niveau.name:<26} {barre(ok, n)} {statut}{RESET}")
    print(f"\nTotal : {total_ok}/{total} tests réussis ({100 * total_ok / max(total, 1):.0f} %)\n")


if __name__ == "__main__":
    main()
