const ipadress = 'http://192.168.80.177:9001'//'http://127.0.0.1:9001'


document.getElementById('open').addEventListener('click', function () {
    // Créer une instance de l'objet XMLHttpRequest
    var xhr = new XMLHttpRequest();

    // Configurer la requête HTTP GET avec l'URL du service que vous souhaitez appeler
    xhr.open('GET', ipadress + '/open', true);

    // Gérer la réponse de la requête
    xhr.onload = function () {
        if (xhr.status >= 200 && xhr.status < 300) {
            console.log(xhr.responseText);
        } else {    
            console.log('Erreur lors de la requête. Veuillez réessayer.');
        }
    };

    // Gérer les erreurs de réseau
    xhr.onerror = function () {
        document.getElementById('response').textContent = 'Erreur réseau. Veuillez vérifier votre connexion.';
    };

    // Envoyer la requête
    xhr.send();
});

document.getElementById('appairing').addEventListener('click', function () {
    // Créer une instance de l'objet XMLHttpRequest
    var xhr = new XMLHttpRequest();

    // Configurer la requête HTTP GET avec l'URL du service que vous souhaitez appeler
    xhr.open('GET',  ipadress + '/add', true);

    // Gérer la réponse de la requête
    xhr.onload = function () {
        if (xhr.status >= 200 && xhr.status < 300) {
            console.log(xhr.responseText);
        } else {    
            console.log('Erreur lors de la requête. Veuillez réessayer.');
        }
    };

    // Gérer les erreurs de réseau
    xhr.onerror = function () {
        document.getElementById('response').textContent = 'Erreur réseau. Veuillez vérifier votre connexion.';
    };

    // Envoyer la requête
    xhr.send();
});

function load(){
    var xhr = new XMLHttpRequest();

    // Configurer la requête HTTP GET avec l'URL du service que vous souhaitez appeler
    xhr.open('GET',  ipadress + '/mac', true);

    // Gérer la réponse de la requête
    xhr.onload = function () {
        if (xhr.status >= 200 && xhr.status < 300) {
            // La requête a réussi, mettre à jour le contenu de l'élément avec la réponse reçue
            createElements(JSON.parse(xhr.responseText))
        } else {
            // La requête a échoué, afficher un message d'erreur
            document.getElementById('response').textContent = 'Erreur lors de la requête. Veuillez réessayer.';
        }
    };

    // Gérer les erreurs de réseau
    xhr.onerror = function () {
        document.getElementById('response').textContent = 'Erreur réseau. Veuillez vérifier votre connexion.';
    };

    // Envoyer la requête
    xhr.send();
}

function createElements(elements) {
    var responseContainer = document.getElementById("response");

    elements.forEach(function (element, index) {
        var elementContainer = document.createElement("div");
        elementContainer.classList.add("element-container");
        elementContainer.id = "element" + (index + 1);

        var elementSpan = document.createElement("span");
        elementSpan.textContent = element;
        elementSpan.id = "span" + (index + 1);

        var removeButton = document.createElement("button");
        removeButton.textContent = "Supprimer";
        removeButton.onclick = function () {
            removeElement(index+1);
        };

        elementContainer.appendChild(elementSpan);
        elementContainer.appendChild(removeButton);
        responseContainer.appendChild(elementContainer);
    });
}

//TODO: send request to remove element
function removeElement(Id) {
    var element = document.getElementById("element" + Id);
    var span = document.getElementById("span" + Id);
    var texteDuSpan = span.innerText;
    if (element) {

        var xhr = new XMLHttpRequest();

        // Configurer la requête HTTP GET avec l'URL du service que vous souhaitez appeler
        xhr.open('GET',  ipadress + '/delete/' + texteDuSpan, true);

        // Gérer la réponse de la requête
        xhr.onload = function () {
            if (xhr.status >= 200 && xhr.status < 300) {
                // La requête a réussi, mettre à jour le contenu de l'élément avec la réponse reçue
                createElements(JSON.parse(xhr.responseText))
            } else {
                // La requête a échoué, afficher un message d'erreur
                document.getElementById('response').textContent = 'Erreur lors de la requête. Veuillez réessayer.';
            }
        };

        // Gérer les erreurs de réseau
        xhr.onerror = function () {
            document.getElementById('response').textContent = 'Erreur réseau. Veuillez vérifier votre connexion.';
        };

        // Envoyer la requête
        xhr.send();

        //Enleve l'element du HTML
        element.remove();
    }
}