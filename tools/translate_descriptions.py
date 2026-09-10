import os
import struct
import zlib
from build_french_mod import (
    clean_retro_text,
    compress_and_scramble,
    VariantReader,
    VariantWriter,
    SCRATCH_DIR,
    DECOMP_DIR,
    MOD_STAGING
)
from translate_phase1 import encode_radec, stage_file

ITEM_DESCRIPTIONS_FR = {
    0: "Cette arme a une puissance d'attaque de base de 1 (+/-).",
    1: "Cette arme a une puissance d'attaque de base de 2 (+/-). Elle se vend a bon prix.",
    2: "Cette arme a une puissance d'attaque de base de 3 (+/-).",
    3: "Cette arme a une puissance d'attaque de base de 4 (+/-).",
    4: "Cette arme a une puissance d'attaque de base de 5 (+/-). Tres efficace contre les dragons.",
    5: "Cette arme a une puissance d'attaque de base de 7 (+/-).",
    6: "Cette arme a une puissance d'attaque de base de 10 (+/-).",
    7: "Ce bouclier a une defense de base de 2 (+/-). Ne rouille pas et reduit la faim.",
    8: "Ce bouclier a une defense de base de 3 (+/-).",
    9: "Ce bouclier a une defense de base de 4 (+/-). Protege contre le poison.",
    10: "Ce bouclier a une defense de base de 5 (+/-). Ne rouille pas.",
    11: "Ce bouclier a une defense de base de 6 (+/-).",
    12: "Ce bouclier a une defense de base de 7 (+/-). Reduit les degats de feu des dragons.",
    13: "Ce bouclier a une defense de base de 10 (+/-).",
    14: "Cet anneau influe sur votre force.",
    15: "Cet anneau vous protege contre le poison.",
    16: "Cet anneau vous empeche de vous endormir.",
    17: "Cet anneau vous teleporte parfois a un autre endroit.",
    18: "Cet anneau empeche votre satiete de diminuer.",
    19: "Cet anneau permet d'entrer dans les pieces sans reveiller les monstres.",
    20: "Cet anneau peut etre revendu a tres bon prix a la surface.",
    21: "Cet anneau permet de voir les monstres invisibles.",
    22: "Cet anneau augmente la vitesse a laquelle la faim se fait sentir.",
    23: "Cet anneau vous empeche de tomber dans les pieges.",
    24: "Cet anneau vous protege contre la magie des pantins.",
    25: "Cet anneau reveille tous les monstres lorsque vous entrez dans une piece.",
    26: "Ces fleches permettent d'attaquer a distance. Appuyez sur \x02)\x03\xeb#\x03 pour tirer.",
    27: "Ces fleches permettent d'attaquer a distance. Appuyez sur \x02)\x03\xeb#\x03 pour tirer.",
    28: "Ces fleches percent les ennemis et les murs. Appuyez sur \x02)\x03\xeb#\x03 pour tirer.",
    29: "Ce petit en-cas restaure un peu de satiete.",
    30: "Ce gros pain restaure completement votre satiete.",
    31: "Ce pain moisi rassasie, mais reduit votre force avec son poison.",
    32: "Cette herbe restaure quelques points de vie.",
    33: "Cette herbe restaure une grande quantite de points de vie.",
    34: "Cette herbe guerit le poison et restaure la force perdue.",
    35: "Cette graine augmente votre force maximale.",
    36: "Cette graine augmente votre niveau d'un cran.",
    37: "Cette graine double votre vitesse de deplacement temporairement.",
    38: "Cette herbe ameliore la vision pour tout l'etage en cours.",
    39: "Cette herbe nocive reduit vos PV et votre force.",
    40: "Lancer cette herbe sur un monstre lui fait perdre la vue.",
    41: "Lancer cette herbe sur un monstre le fait fuir en panique.",
    42: "Lancer cette herbe sur un monstre provoque la confusion.",
    43: "Lancer cette herbe sur un monstre le plonge dans le sommeil.",
    44: "Cette herbe vous teleporte a un endroit aleatoire de l'etage.",
    45: "Cette herbe vous permet de cracher une gerbe de flammes.",
    46: "Ce parchemin Decuplo augmente la puissance de l'arme equipee.",
    47: "Ce parchemin Megaprotection ameliore la defense du bouclier equipe.",
    48: "Ce parchemin d'armure protege le bouclier contre la rouille.",
    49: "Ce parchemin benit vos equipements et dissipe les souillures.",
    50: "Ce parchemin d'identification revele la vraie nature d'un objet inconnu.",
    51: "Ce parchemin de lumiere devoile l'integralite de la carte de l'etage.",
    52: "Ce parchemin paralyse les monstres proches tant qu'ils ne sont pas frappes.",
    53: "Pose a vos pieds, ce parchemin de sanctuaire empeche les monstres d'attaquer.",
    54: "Vous avez brave les profondeurs du Grand Donjon Mystere. Gloire a vous !",
    55: "Felicitations pour avoir atteint le 50e etage du Donjon Mystere !",
    56: "Ce parchemin de clairvoyance revele la position de tous les objets.",
    57: "Ce parchemin de sonar revele la position de tous les monstres de l'etage.",
    58: "Ce parchemin de boulangerie transforme n'importe quel objet en gros pain.",
    59: "Ce parchemin d'amelioration augmente le nombre de charges d'une baguette.",
    60: "Ce parchemin Megabang declenche une terrible explosion dans la piece.",
    61: "Ce parchemin de silence bloque l'usage de votre bouche pour tout l'etage.",
    62: "Ce parchemin du temps vous renvoie a l'arrivee au debut de l'etage actuel.",
    63: "Ce parchemin fait apparaitre une quantite de pieges supplementaires.",
    64: "Ce parchemin d'Aleato provoque des effets magiques completement aleatoires.",
    65: "Ce parchemin d'Evac vous extrait immediatement du donjon.",
    66: "Cette baguette d'Eclair frappe les ennemis a distance sans jamais faillir.",
    67: "Cette baguette d'Entrave reduit de moitie la vitesse d'un monstre.",
    68: "Cette baguette de Sommeil endort un monstre pour un certain temps.",
    69: "Cette baguette de Confusion desoriente completement un monstre.",
    70: "Cette baguette de Blocage empeche un monstre d'utiliser ses capacites.",
    71: "Cette baguette d'Ejection teleporte un monstre dans une autre piece.",
    72: "Cette baguette de Mutation transforme un monstre en une autre creature.",
    73: "Cette baguette d'Acceleration accelere la vitesse de deplacement d'un monstre.",
    74: "Cette baguette d'Invisibilite rend le monstre cible invisible.",
    75: "Cette baguette d'Equilibre vous empeche de perdre l'equilibre.",
    76: "Cette baguette de Clonage produit un clone exact d'un monstre.",
    77: "Cette baguette de Mort terrifie et aneantit un monstre sur le coup.",
    78: "Cette baguette a double tranchant reduit les PV du monstre a 1 et divise les votres.",
    79: "Cette baguette sacrificielle transfere la moitie de vos PV a un monstre.",
    80: "Un sac de pieces d'or. Amassez-en le plus possible pour financer votre boutique !",
    81: "Ce coffre-fort d'acier evite de perdre la moitie de son or apres une defaite.",
    82: "Donnez ces joyaux royaux au Roi pour obtenir l'acces au Donjon Mystere !",
    83: "La boite du bonheur ! C'est le tresor inestimable que vous convoitiez !",
    84: "Une etrange boite dont s'echappe une odeur singuliere...",
    85: "",
    86: "",
    87: "Cet objet mysterieux et translucide cache d'inestimables secrets.",
    88: "",
    89: "Ce gros pain restaure completement votre satiete.",
    90: "Ce parchemin Megafoudre rassemble les esprits pour une frappe titanesque.",
    91: "Cette boite a miracles se negociera tres cher a la surface. Prenez-en soin !"
}

UNIDENTIFIED_DESC_FR = "Identifiez cet objet pour reveler sa veritable nature."

def translate_item_descriptions():
    src_bin = os.path.join(DECOMP_DIR, "1362871123.bin")
    with open(src_bin, 'rb') as fp:
        tree = VariantReader(fp.read()).parse()
    rows = dict(tree[1])['rows'][1]

    for i in range(len(rows)):
        if i in ITEM_DESCRIPTIONS_FR:
            fr_text = ITEM_DESCRIPTIONS_FR[i]
        elif i >= 100 and i <= 159:
            fr_text = UNIDENTIFIED_DESC_FR
        else:
            fr_text = ""

        clean_bytes = fr_text.encode('latin1')
        rows[i][1][0] = ('str', encode_radec(clean_bytes))

    writer = VariantWriter()
    writer.write(tree)
    stage_file("1362871123", bytes(writer.buf))
    print("Item descriptions (160 items) translated and staged!")

if __name__ == "__main__":
    translate_item_descriptions()
