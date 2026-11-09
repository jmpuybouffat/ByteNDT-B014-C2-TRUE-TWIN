# Faisceau incident et rétrodiffusé — étape demandée pour formation/VR

Le volume actuel est calculé par le noyau cohérent C2, avec les 64 éléments et les 85 lois de chaque pose. Il ne représente pas une propagation élastodynamique complète ni la rétrodiffusion Green/Kirchhoff/Born/GTD.

Le raccordement doit conserver les repères source et mécanique documentés, utiliser le même modèle physique que les réponses de référence, et synchroniser le trajet PA, la loi active, le temps de vol, le champ incident, le champ retourné et le signal reçu. Les deux champs doivent porter des unités et une référence d'amplitude explicites. Une enveloppe décorative ou des particules de retour arbitraires ne satisfont pas cette demande.

Les fichiers C2 figés contiennent des contributions scalaires Kirchhoff/GTD/Born par indication. Elles ne suffisent pas à elles seules à reconstruire un champ 3D complexe et temporel complet. Le démonstrateur B006 dispose de fonctions de diffusion réduites dans un autre repère et un autre jeu de lois ; il doit être raccordé et vérifié, sans substitution silencieuse aux résultats C2.

Contrôles avant affichage comme résultat : phase et signe, unité millimètre appliquée une fois, parcours aller/retour, temps de vol, amplitude de référence, réciprocité applicable, limites des approximations, correspondance avec la loi active et les signaux de référence. Préserver les matrices validées et distinguer toute nouvelle simulation.

Statut : prévu, non raccordé à la présente version. L'interface et la notice le déclarent explicitement.
