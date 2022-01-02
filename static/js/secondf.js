localhost = "http://localhost:5000/";

const puntuar = (id) => {
  
    Puntuaje = (prompt( "Introduzca Puntuaje"));
    
    if ( Puntuaje) {
        Puntuaje = Number(Puntuaje);
        if (Puntuaje > 0 && Puntuaje <= 5) {
          fetch(localhost + "result", {
            method: "POST",
            headers: {
              'Content-Type': 'application/json',
            },
            body :JSON.stringify( { id : id , puntaje : Puntuaje})
          })
            .then((res) => res.json())
            .catch((error) => console.error("Error:", error))
            .then((response) => {
                console.log("Entro")
                document.getElementById("score").innerHTML = Puntuaje;
            });
        } else {
          alert("Introduzca Correctamente el numero > 0 y <= 5")
        }
    } 
  }
  
  