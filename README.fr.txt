UltimateSmashFriends
====================

UltimateSmashFriends vise a créer un jeu multijoueur rapide et amusant à jouer.
Graphismes en 2d avec une jouabilité orienté arcade, pour des heures
d'amusement.

Commment Jouer
==============

Le jeu nécessite python (>=2.4) et pygame(>=1.7) (versions plus anciennes non
testés).  Sous python inférieur a 2.5 le module elementtree est necessaire.
(sous debian/ubuntu installez python-pygame)

Lancez juste ultimate-smash-friends.py, en le double cliquant ou depuis un
terminal avec ./ultimate-smash-friends.py depuis le dossier d'ultimate smash
friends.

Contrôles
=========

Chaque joueur dispose de 4 touches de directions, de deux touches d'actions nommées ici A et B, et d'une touche BOUCLIER.

Actions basique:

  * Les touches DROITES et GAUCHE permettent de marcher
  * La touche HAUT permet de sauter
  * La touche BAS permet de ramasser un objet
  * La touche A déclenche un coup de pied
  * La touche B déclenche un coup simple
  * La touche BOUCLIER permet d'activer le bouclier jusqu'à ce qu'ils soit
  épuisé ou que la touche soit relâchée

Actions combinées:
  * Pendant un saut, la touche HAUT, déclenchera un double saut
  * Si la touche BAS vient d'être poussée, un appuis sur GAUCHE ou DROITE,
  déclenchera une roulade
  * Si la touche B est appuyé après un déplacement dans une direction, un smash
  sera déclenché dans cette direction
  * Si A est appuyé suivit de BAS une attaque spécial est déclenchée, si
  disponible
  * Si BAS est appuyé deux fois, suivit de A, une autre attaque spéciale est
  déclenchée, si disponible


Comment gagner
==============

Les règles sont simples, quand vous frappez quelqu'un, son pourcentage
augmente, et il est projeté un petit peu plus loin, le but est de frapper les
ennemis pour les faire sortir de la carte. Vous avez trois vies.

Enjoy :)

Contribuer
==========

L'ajout de personnages et d'arènes est prévu pour être simple, il suffit de
créer les images des animations et d'éditer un fichier xml pour chaque
personnage, un programme, utils/cv.py, permet de voir en temps réel l'effet des
modifications du xml, il peut aussi créer un fichier xml simple, quand celui ci
n'existe pas. Pour les niveaux le fichier est encore plus simple, et un editeur
complet existe (utils/level_editor/usf-level-editor.py).


Bugs:
=====

Cette version est une Beta: Si vous relevez quelques bugs et/ou des manques de
fonctionnalités, je vous prie d'envoyer vos rapports, suggestions ou patchs à :
https://bugs.launchpad.net/ultimate-smash-friends

Dernière mise à jour: mercredi 27 avril 2011, 18:46:08 (UTC+0200)
