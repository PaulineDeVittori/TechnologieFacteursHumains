# Rééducation Ludique de la Cheville : Jeu de Football

## Description du projet

**Objectif** : Application motivante sous forme d’un petit jeu qui permet aux personnes qui ont besoin d’une rééducation de la cheville de faire une rééducation de manière ludique.

Le jeu est composé d’un but de foot et d’un ballon. Lorsque la personne fait un mouvement de la cheville, le capteur capte la contraction des muscles du mollet et le ballon accélère. L'objectif est de mettre le ballon dans le but. Il y a un petit personnage qui est le gardien de but qui se déplace de gauche à droite pour empêcher le ballon de rentrer. 

### Fonctionnalités principales :
- **Rééducation de la cheville** : Le jeu utilise des capteurs musculaires pour détecter les mouvements de la cheville et ajuste la vitesse du ballon.
- **Capteur de rythme cardiaque et de respiration** : Le stress et l'effort physique sont mesurés pour ajuster la difficulté du jeu.
- **Gardien de but** : Un gardien de but se déplace pour empêcher au joueur de marquer. Sa vitesse varie en fonction du niveau de stress du joueur.
- **Objectif du jeu** : Marquer des buts pour faire les exercices de rééducation de la cheville.

## Technologies utilisées

- **Pygame** : Pour créer l'environnement de jeu et gérer les animations.
- **Electromyographe (EMG)** : Utilisée pour mesurer l'activité musculaire et détecter la contraction des muscles du mollet.
- **Photopléthysmogramme (PPG)** : Pour mesurer l'activité cardiaque et déterminer l'effort physique de l'utilisateur.
- **Senseur de respiration** : Pour détecter le niveau d'effort en fonction de la respiration du joueur.

## Fonctionnement du jeu

Le jeu se déroule sur un terrain de football virtuel avec les éléments suivants :
- Un **but** pour marquer des points
- Un **ballon** contrôlé par les mouvements de la cheville du joueur.
- Un **gardien** (ou plusieurs) qui se déplace pour empêcher le joueur de marquer.

### Mécanique du jeu :
1. **Détection des mouvements de la cheville** : Un capteur électromyographe capte la contraction des muscles du mollet et accélère le ballon en fonction de ces contractions.
2. **Capteurs de stress** : Un photopletysmogramme (ECG) et un senseur de respiration mesurent l'effort du joueur. Si le joueur est stressé, c’est-à-dire que les capteurs de rythme cardiaque et de respiration captent des signaux élevés, alors le jeu module sa difficulté en faisant se déplacer le petit personnage gardien de but moins vite. Mettre le ballon dans le but sera ainsi plus facile.
3. **Rééducation** : Le jeu permet à l'utilisateur de s'exercer de manière ludique, tout en faisant des mouvements spécifiques de la cheville.
4. **Gagner des points** : A chaque but, le joueur marque un point. Le nombre de points nécessaires pour gagner peut être personnalisé pour chaque séance de rééducation.

## Installation

### Prérequis :
- Python 3.10.16
- Pygame
- Bibliothèques pour la gestion des capteurs (EMG, ECG/PPG, respiration)

### Étapes d'installation :

1. Clonez ce dépôt sur votre machine locale :

   ```bash
   git clone https://github.com/PaulineDeVittori/TechnologieFacteursHumains
