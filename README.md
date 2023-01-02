# GS15_cryptommunication

This project is for a secure messaging application.
It uses eXtended Triple Diffie Hellman (X3DH), Triple Data Encryption Standard (3DES) and A5/1.

## Retour d'experience

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

Les ressources utiles:

- [Complément : Le protocole Signal (comment Whatsapp et Signal sécurisent les messages)](https://www.youtube.com/watch?v=6YVQOyhzGx4)
- [Demystifying the Signal Protocol for End-to-End Encryption (E2EE)](https://medium.com/@justinomora/demystifying-the-signal-protocol-for-end-to-end-encryption-e2ee-ad6a567e6cb4)

### A5/1

Pour A5/1, la plus grande difficulté était de trouver une source fiable pour le fonctionnement de l'algorithme. En effet, l'algorithme n'est pas officiellement publié et il existe de multiples sources surtout peu fiables et détaillées. Finalement, j'ai trouvé une source fiable dans la papier de recherche :
>A5 Encryption in GSM
>
>Oliver Damsgaard Jensen
>
>Kristoffer Alvern Andersen

Après avoir trouvé cette source, il a fallu implémenter cette algorithme de chiffrement. Nous l'avons mis en place pour les messages, c'est-à-dire, dans un sens uniquement. Or, A5/1 est un algorithme de chiffrement pour les appels téléphoniques GSM, c'est-à-dire en actif-actif. Notre système de messagerie est actif-passif et donc il a fallu adapter l'algorithme pour qu'il puisse fonctionner malgré tout.

### SHA256

Pour SHA256, l'algorithme était plus complexe à comprendre et la récursion sur les messages schedules aussi. Il a fallu plus de temps pour donner un fonction qui retourne un hash correct.

Les ressources utiles:

- [Sha256algorithm](https://sha256algorithm.com/)
- [What is SHA-256?](https://blog.boot.dev/cryptography/how-sha-2-works-step-by-step-sha-256/)

## Usage

1. Lancer le serveur.

    ```console
    python3 server.py
    ```

2. Connecter `n` clients dans d'autres consoles puis saisir leur nom d'utilisateur qui doit être unique.

    ```console
    python3 client.py
    ```

3. Communiquer

    Les clients peuvent chacun s'envoyer des messages.
    Si le client n'a pas les clés du destinataire, il les demande au serveur au serveur et ensuite il peut écrire un message.

    ```console
    Send message to (q to quit, l to list): user1
    Message: Hello
    ```

4. Fermer le serveur et les clients.

Dans l'entrée des clients taper 'q' pour les déconnecter un à un puis faites le sur le serveur.

## Credits

Felix IENNY
Flavien VARGUES
