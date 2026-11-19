"""Lecture fiable d'un prix en euros dans un texte de fiche (« 405,5€ », « 1 377,24 € », « 139 99 € » chez VidaXL)."""
import re

_PRIX = re.compile(r"(?<![\d,.])(\d{1,3}(?:[   ]\d{3})*(?:,\d{1,2})?)\s?€")
_VIDAXL = re.compile(r"(?<![\d,.])(\d{1,5}) (\d{2}) €")
# AliExpress affiche le prix deux fois de suite (« 131,69€ 131,69€ ») : ce doublon évite de coller
# la note du vendeur au prix (« 18 vendus 5 131,69€ » n'est pas 5 131,69 €).
_DOUBLE = re.compile(r"(?<![\d,.])(\d{1,3}(?:[   ]\d{3})*(?:,\d{1,2})?)\s?€\s?\1\s?€")


def premier_prix(texte):
    """Premier prix du texte : c'est le prix affiché, les suivants sont souvent des anciens prix."""
    if not texte:
        return None
    d = _DOUBLE.search(texte)
    if d:
        return float(re.sub(r"[   ]", "", d.group(1)).replace(",", "."))
    m1, m2 = _PRIX.search(texte), _VIDAXL.search(texte)
    if m2 and (not m1 or m2.start() <= m1.start()):
        return float(m2.group(1) + "." + m2.group(2))
    if m1:
        return float(re.sub(r"[   ]", "", m1.group(1)).replace(",", "."))
    return None


if __name__ == "__main__":
    assert premier_prix("Barbecue Kamado 56 cm Noir 405,5€ 405,5€ Prix le plus bas : 450,79€") == 405.5
    assert premier_prix("accessoires AP-T1 AP-T2 28,19€ 28,19€") == 28.19
    assert premier_prix("Purificateur 1 377,24€ 1 377,24€") == 1377.24
    assert premier_prix("Price: 139 99 €") == 139.99
    assert premier_prix("télécommande 18 vendus 5 131,69€ 131,69€ Prix le plus bas") == 131.69
    assert premier_prix("3926 vendus 4.5 81,39€ 81,39€ Prix") == 81.39
    assert premier_prix("Abri 1 377,24€ 1 377,24€") == 1377.24
    print("tests prix OK")
