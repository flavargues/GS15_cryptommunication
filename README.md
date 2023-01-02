# GS15_cryptommunication

This project is for a secure messaging application.
It uses eXtended Triple Diffie Hellman (X3DH), Triple Data Encryption Standard (3DES) and A5_1.

## Retiur d'experience

ddddddd

### Sockets

Nous avons fait le choix d'utiiser des sockets afin de pouvoir connecter plusieurs clients au serveur. La difficulté de cet objectif résidait dans la gestion des erreurs et aussi dans les soucis de synchronisation des communications entre les clients et le serveur.

Dans un premier temps, il a fallu mettre en place un thread pour chaque nouveau client afin de permettre au serveur d'être à l'écoute de tous les clients de la même manière. De ce fait, les clients sont servis sans préférence constamment, presque  sans latence.

Le serveur interprête quatre types de messages :

- La connexion: le client envoie un premier message et le serveur lui renvoie le nombre premier et un générateur de ce dernier pour que le client génère ses clés.
- L'échange de clés: une fois que le client a généré ses clés, il renvoie ses deux clés publiques au serveur (clé d'identité et clé présignée).
- La demande de clés: lors s'un envoi de message si le client n'a jamais contacté le destinataire, il va demander les clés publiques (clé d'identité et clé présignée) de ce dernier au serveur.
- La déconnexion: si le serveur reçoit un message de déconnexion, il supprime le socket du client et cesse d'écouter dessus. Le thread dédié prend fin.

### Extended Triple Diffie Hellman (X3DH)

Pour l'implémentation, nous avons décidé d'attribuer à chaque client un objet X3DH qui gérera le stockage et la génération des clés et aussi le chiffrement et le déchiffrement des messages texte .  

### Triple Data Encryption Strandard (3DES)

La première étape pour mettre en place 3DES, ça a été de faire DES. Les entrées et les sorties de ces deux classes sont des chaines binaires. Pour DES, il a fallu comprendre l'algorithme de chiffrement et gérer les blocs entre chacun des seize itérations. Une fois que cela a été fait, il a juste fallu coder les différentes étapes.

### A5_1

ici

### SHA256

Pour SHA256, l'algorithme était plus complexe à comprendre et la récursion sur les messages schedules aussi. Il a fallu plus de temps pour donner un fonction qui retourne un hash correct.

## Usage

here

## Credits

Felix IENNY
Flavien VARGUES
