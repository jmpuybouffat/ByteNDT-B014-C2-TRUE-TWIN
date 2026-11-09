# C2 — publication séparée de C1

Dépôt : `jmpuybouffat/ByteNDT-B014-C2-TRUE-TWIN`
Branche : `publication/c2-3aubes-fr-en`
Fichier principal : `app.py`
Python : `3.12`
Sous-domaine proposé : `bytendt-lsb941-c2-fr-en` (disponibilité à vérifier au déploiement).

Créer une nouvelle application Streamlit. Ne pas modifier C1 ni l'application C2 historique. Le champ URL prend le sous-domaine seul, sans `https://` ni `.streamlit.app`.

Repère visible de cette version : `C2 · Trois aubes · Gorge intrados · 199 positions · R2`.

Sens : PA EXTRADOS vers première gorge INTRADOS. Six références EDM_06 à EDM_11. Les réponses encodées, les maxima d'examen figés et les matrices TFM/voxel proviennent du code C2 original. Omission de lecture `path_range_mm` corrigée sans changer les valeurs. Les six maxima ne sont pas de nouvelles détections issues du détecteur encodé.

La vue utilise des transformations rigides par pose, un contact sur le maillage, une orientation transportée et une lecture continue. Les exports sont des données d'étude du guidage. La fabrication et les collisions ne sont pas qualifiées. Le champ de gain cohérent n'est pas le champ rétrodiffusé complet. Aucun calcul de rupture matériau/chargement non défini n'est revendiqué.

Ne pas mettre en service une révision qui échoue aux contrôles du dossier reference_c2. La présence du code sur GitHub ne confirme pas, à elle seule, la révision exécutée dans Streamlit.

R2 : le bouton Lecture attend la disponibilité de la vue, la commande est confirmée et réémise en cas de perte, et le départ/arrivée utilisent une rampe bornée à600ms. Pause/reprise et fin199/199 testées. Les sept blocs de données sources/mécaniques sont identiques àR1. Le temps de lecture est animé, pas une acquisition physique.
