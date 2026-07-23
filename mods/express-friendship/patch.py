"""Amitié express — seuils de rang d'amitié ÷5 (les rangs négatifs aussi, pardon plus vite)."""
from palmod import get, rows, set_

PAK_NAME = "ExpressFriendship"
TABLES = ["Pal/Content/Pal/DataTable/Friendship/DT_FriendshipRankTable"]

DIV = 5


def patch(assets, extra):
    a = assets[TABLES[0]]
    for r in rows(a):
        points = int(get(r, "RequiredPoint"))
        set_(a, r, "RequiredPoint", int(points / DIV))
