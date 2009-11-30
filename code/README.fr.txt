===UltimateSmashFriends:===
UltimateSmashFriends est un jeu basé sur pygame, le projet vise a créer un jeu multijoueur rapide et amusant a jouer. Le jeu est designé pour qu'un maximum du moteur soit réutilisable dans des jeux 2d simples.

Graphismes en 2d avec une jouabilité orienté arcade, pour des heures d'amusement.

L'ajout de personnages et d'arènes est prévu pour être simple, il suffit de créer les images et d'éditer un fichier xml pour chaque personnage. Pour le niveau le fichier est encore plus simple.

==Commment Jouer:=
Le jeu nécessite python (>=2.4) et pygame(>=1.7) (versions plus anciennes non testés).
Sous python inférieur a 2.5 le module elementtree est necessaire.
(sous debian/ubuntu installez python-pygame)

Lancez juste ultimate-smash-friends.py, en le double cliquant ou depuis un terminal avec ./ultimate-smash-friends.py depuis le dossier d'ultimate smash friends.

==Controles==
Les contrôles par défaut sont  ←↑→ et l,m pour le joueur 1, zqsd et c,v pour le joueur 2, ijkn et yt pour le joueur 3, vous pouvez redéfinir toutes les touches dans le fichier UltimateSmashFriends.cfg, reportez vous au fichier et a sa documentation en ligne:
http://code.google.com/p/ultimate-smash-friends/w/list

Certaines actions sont déclenchés par des séquences de touches, par exemple les smash et les coups spéciaux.
une touche de direction puis l (pour le joueur 1) feras un smash dans la direction.
une touche de direction puis m (joueur 1) feras une attaque spéciale.

Ces combinaisons sont disponibles pour les autres personnages bien sur, en se reportant au touches correspondantes.

Pour quitter le jeu depuis le menu (à la fin du jeu ou en tapant sur "echap") appuyer sur la touche "a". Cette touche est paramétrable dans le fichier UltimateSmashFriends.cfg.

==Comment gagner:==
Les règles sont simples, quand vous frappez quelqu'un, son pourcentage augmente, et il est projetté un petit peu plus loin, le but est de frapper les ennemis pour les faire sortir de la carte. Vous avez trois vies.

Enjoy :)

==Bugs:==
Cette version est une Alpha: Si vous relevez quelques bugs et/ou des manques de fonctionnalités, je vous prie d'envoyer vos rapports, suggestions ou patchs à :
http://code.google.com/p/ultimate-smash-friends/issues/list

