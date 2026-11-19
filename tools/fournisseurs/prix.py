"""Lecture fiable d'un prix en euros dans un texte de fiche (« 405,5€ », « 1 377,24 € », « 139 99 € » chez VidaXL)."""
import re

_PRIX = re.compile(r"(?<![\d,.])(\d{1,3}(?:[   ]\d{3})*(?:,\d{1,2})?)\s?€")
_VIDAXL = re.compile(r"(?<![\d,.])(\d{1,5}) (\d{2}) €")


def premier_prix(texte):
    """Premier prix du texte : c'est le prix affiché, les suivants sont souvent des anciens prix."""
    if not texte:
        return None
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
    print("tests prix OK")
