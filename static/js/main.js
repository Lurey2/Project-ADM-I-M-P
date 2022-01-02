localhost = "http://localhost:5000/";

listDataMovie = [];
listshowDataMovie = [];
indexShow = 0;
user = [];
slideIndex = 1;
const movieChat= (MovieId) => {
  window.location.href = localhost + "movie/" + MovieId;

}
function change(n) {
  showSlides(slideIndex += n);
}

const  showSlides = (n) => {
  var i;
  var slides = document.getElementsByClassName("panel_r_movie");
  console.log(slides.length)
  if (n > slides.length) {slideIndex = 1}    
  if (n < 1) {slideIndex = slides.length}
  for (i = 0; i < slides.length; i++) {
      slides[i].style.display = "none"; 
  }
  slides[slideIndex-1].style.display = "block";
}
const aumentar = (index) => {
  indexShow = index;
  valueMaxIndex = 0;
  valueMaxIndex = indexShow * 6;
  if (valueMaxIndex > listshowDataMovie.length ) {
    valueMaxIndex = listshowDataMovie.length;
    indexShow=indexShow-1;
    alert("MAXIMO DE ITEMS " + listshowDataMovie.length )
  }
  nodeAll = "";
  for (let indexValue = 0; indexValue < valueMaxIndex; indexValue++) {
    nodeAll += nodeAdd(listshowDataMovie[indexValue]);
  }
  document.getElementById("pane-movie-list").innerHTML = nodeAll;
};

var isNumber = function isNumber(value) {
  return typeof value === 'number' && isFinite(value);
}

const existPuntaje = (idMovie) => {

  moviePuntaje =  user.find(mov => mov[0] == idMovie )
  
  if (moviePuntaje) {
    return moviePuntaje[1];
  }
  return '--';
}

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
            window.location.reload();
          });
      } else {
        alert("Introduzca Correctamente el numero > 0 y <= 5")
      }
  } 
}



const filtrado = (value) => {
  listshowDataMovie = listDataMovie.filter((data) => data[1].toLowerCase().includes(value.toLowerCase()));
  aumentar(1);

};

const nodeAdd = (listContent) => {
  return (
    `<div class="panel">
  <div class="Tittle">
    <div class="tittle-1">
      <h3>` +
    listContent[1] +
    `</h3>
    </div>
    <div class="tittle-watch">
      <div class="button-style-play" id="watch-movie-buttom" onclick="movieChat(` + listContent[0]+`)" >
        <i class="gg-play-button"></i>
      </div>
    </div>
  </div>
  <div class="content-movie">
    <div class="tag-movie">` +
    listContent[2].replaceAll("|", "-") +
    `
    </div>
    <div class="score-movie">
      <div style="cursor:pointer" onclick="puntuar(`+listContent[0]+`)" >` +
      existPuntaje(listContent[0]) +
      `</div>
    </div>
  </div>
  <div class="argumento-movie">
    <p> ` +
    listContent[3] +
    `
    </p>
  </div>
</div>`
  );
};

window.onload = () => {
  document
    .getElementById("buttonaument")
    .addEventListener("click", () => aumentar(indexShow + 1));
  fetch(localhost + "result", {
    method: "GET", // or 'PUT'
  })
    .then((res) => res.json())
    .catch((error) => console.error("Error:", error))
    .then((response) => {
      listDataMovie = response.list;
      listshowDataMovie = listDataMovie;
      user = response.user;
      console.log(response)
      aumentar(1);
    });

  var input = document.getElementById("filtrado-movie");

  // Execute a function when the user releases a key on the keyboard
  input.addEventListener("keyup", function (event) {
    // Number 13 is the "Enter" key on the keyboard

    if (event.key === "Enter") {
      // Cancel the default action, if needed
      event.preventDefault();
      // Trigger the button element with a click
      filtrado(input.value);
    }
  });
  showSlides(1);
};
