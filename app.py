from flask import Flask, request, render_template , jsonify

import numpy as np
import pandas as pd
from itertools import combinations ## [[1] , [2] , [3]] = [[1] , [2] , [3] , [1 ,2] , [1,3] , [2,3]]
from sklearn.feature_extraction.text import TfidfTransformer,CountVectorizer 
from sklearn.metrics.pairwise import cosine_similarity ## [1, 2 ,3 ,4 ] [ 1,2,3, 4 ]= 
import re
## hola como estas = vectorizer() = [[hola] , [como] , [estas]]

app = Flask(__name__, template_folder='template')

localhostUrl = "http://localhost:5000/"
DATASPANISH = []

## data importante para  pronostico
dataInglesDiccionary = {}
orden_pelis_cosine_por_fila = []
cosine_sims_ordenadas= []
dataIngles = []
##
reymer = pd.DataFrame({"movieId": [1,106696,1240,1580,597],
                       "rating": [5,3,5,4,1]})
@app.template_filter("is_in_list_dict")
def is_any(search="", list_dict=None, dict_key=""):
    if any(search in element[dict_key] for element in list_dict):
        return True
    return False

@app.route("/")
def hello():
    dataIngles = pd.read_csv('./MovieLens_con_argumento.csv', sep=",")
    dataSpanish = pd.read_csv('./BD_Peliculas_2021 - Hoja 1 (1).csv', sep=",").to_numpy().tolist()
    movieRecomendation = (recomendar_a_usuario(reymer,dataIngles))
    ListIndiceMovie = (getIndiceMovie(movieRecomendation))
   
    Peli= [dataSpanish[valor] for clave, valor in ListIndiceMovie.items()]
    response = {'movieRecomend' : Peli}
    
    return render_template("index.html" , result = response )

@app.route('/movie/<id>')  # /landingpageA
def landing_page(id):
    dataSpanish = pd.read_csv('./BD_Peliculas_2021 - Hoja 1 (1).csv', sep=",").to_numpy().tolist()
   
    index = dataInglesDiccionary[int(id)]
   
    dataMovieView = dataSpanish[int(index)]

    dataMovieSimilarity = top_k_similares(int(id) , 15)
    dictListPeliRecomend = getIndiceMovie(dataMovieSimilarity)
    Peli= [dataSpanish[valor] for clave, valor in dictListPeliRecomend.items()]
    dict = {clave:valor for clave, valor in reymer.to_numpy().tolist()}
    response = { "movieID" : dataMovieView , "similarity" :  Peli , 'user' : reymer.to_numpy().tolist() , 'dict' : dict } ## [ 1, 2, 3] 
    
    return render_template("SecondField.html" ,result = response)


@app.route('/result', methods=['GET' , 'POST'])
def result():
    
    if request.method == 'GET':
        
        dataIngles = pd.read_csv('./BD_Peliculas_2021 - Hoja 1 (1).csv', sep=",")
        
        message = {'list': dataIngles.to_numpy().tolist() , 'user' : reymer.to_numpy().tolist()}

        return message
    if request.method == 'POST':
       
        content = request.json
        lenRey = len(reymer)
        if(len(reymer.loc[reymer['movieId']== content['id']]) > 0):
            reymer.loc[(reymer['movieId'] == content['id']),'rating']= content['puntaje']
            return jsonify({'user' : reymer.to_numpy().tolist()})

        reymer.loc[lenRey] = [content['id'] , content['puntaje']]
        return jsonify({'user' : reymer.to_numpy().tolist()})


def getIndiceMovie(dataCsv):
    dicc_indice_movieid = dataCsv["movieId"].to_dict()
    return  {valor: clave for clave, valor in dicc_indice_movieid.items()}


def quitar_numeros(argumento):
  s = argumento.lower() 
  s = re.sub(r"\d+", "", s) #ssutituye los numeros por nada
  return s    

def tokenizador_generos(string_generos): ## ayuda a obtener una combinacion de generos 
  generos_separados = string_generos.split("|")
  resultado =[]
  for tamaño in [1, 2]:
    combs = ["Generos - " + "|".join(sorted(tupla))
    for tupla in combinations(generos_separados, r=tamaño)]
    resultado = resultado + combs
  
  return sorted(resultado)
## COMEDIA | DRAMA | HORROR  -> [[GENERO : NIGUNO ] , [GENERO: DRAMA] ... [GENERO : DRAMA | HORROR]]


def top_k_similares(movieId, k):
  fila_cosine_sims = dataInglesDiccionary[movieId]
 
  lista_ordenada_pelis_sim=orden_pelis_cosine_por_fila[fila_cosine_sims]
  lista_ordenada_sims = cosine_sims_ordenadas[fila_cosine_sims]

  top_k = lista_ordenada_pelis_sim[:k]
  consine_sims_top_k = lista_ordenada_sims[:k]

  top_k_df=dataIngles.loc[top_k].copy()
  top_k_df["similaridad"] = consine_sims_top_k

  return top_k_df

def estimar_rating(ratings_usuario, peli, vecindario=50):
  
    top_vecinos_peli_a_estimar = (top_k_similares(peli, vecindario)
                                  [["movieId", "similaridad"]]
                                 )
    

    pelis_vecinas_puntuadas = ratings_usuario.merge(top_vecinos_peli_a_estimar,
                                                    how="inner",
                                                    on=["movieId"])

    if len(pelis_vecinas_puntuadas) < 2:
        return np.nan
 
    rating_numerador = (pelis_vecinas_puntuadas["rating"] * pelis_vecinas_puntuadas["similaridad"]).sum()
    rating_denominador = pelis_vecinas_puntuadas["similaridad"].sum()
    
    return rating_numerador / rating_denominador

def recomendar_a_usuario(ratings_usuario , pelis_movielens, n=10):

    print("Cargando recomendacion de usuario")
    # El catálogo completo de películas es:
    listado_pelis_disponibles = pelis_movielens
    
    # Quitamos del catálogo aquellas que el
    # usuario ya ha visto (rateado):
    listado_pelis_no_vistas = (listado_pelis_disponibles
                               [~listado_pelis_disponibles["movieId"].isin(ratings_usuario["movieId"])]
                               .copy()
                              )
    print("cargado 1/3")
    # Estimamos el rating que le daría
    # el usuario a todas las pelis que
    # no ha visto:
    listado_pelis_no_vistas["rating estimado"] = (listado_pelis_no_vistas["movieId"]
                                                  .apply(lambda x: estimar_rating(ratings_usuario, x)) ## 
                                                 )
    print("cargado 2/3")
    # Ordenamos las películas de mayor a menor
    # rating estimado, y nos quedamos con el 
    # top n:
    listado_ordenado_para_usuario = (listado_pelis_no_vistas
                                     .dropna(subset=["rating estimado"])
                                     .sort_values(by="rating estimado", ascending=False)
                                     [:n]
                                    )
    print("cargado 3/3")
    return listado_ordenado_para_usuario
def mainPronostic():
    print("iniciando funcionamiento de pronostico :")
    global dataIngles
    dataIngles = pd.read_csv('./MovieLens_con_argumento.csv', sep=",")
    global dataInglesDiccionary 
    dataInglesDiccionary = getIndiceMovie(dataIngles)

    print("Datos cargados:")
    ## separador de palabras
    ## BANCO DE PALABRAS DE ARGUMENTO
    contador_argumento = CountVectorizer(preprocessor=quitar_numeros, min_df=5)
    argumentos_bag_of_words = (contador_argumento.fit_transform(dataIngles["argumento"]).toarray())
    columnas_argumentos = [tup[0] for tup in sorted(contador_argumento.vocabulary_.items(), key=lambda x: x[1])]
    
    ## BANCO DE PALABRAS DE GENEROS
    contador_generos = CountVectorizer(tokenizer=tokenizador_generos,
                                   token_pattern=None,
                                   lowercase=None)
    contador_generos.fit(dataIngles["genres"])
    generos_bag_of_words = contador_generos.fit_transform(dataIngles["genres"]).toarray()

    columnas_generos = [tup[0] for tup in
                    sorted(contador_generos.vocabulary_.items(),
                           key=lambda x: x[1])]

    ##Combinacion de argumentos y generos
    
    bag_of_words_ambos = np.hstack((argumentos_bag_of_words, generos_bag_of_words))
    bag_of_words_ambos_df = pd.DataFrame(bag_of_words_ambos,
                                         columns=columnas_argumentos + columnas_generos,
                                     index=dataIngles["title"])
    print("Cargado completo de vectorizado generos y argumentos...")
    ##Obteniendo el peso de cada palabra tf-idf
    
    tf_idf = TfidfTransformer()


    tf_idf_pelis = tf_idf.fit_transform(bag_of_words_ambos_df).toarray()

    
    tf_idf_pelis_df=pd.DataFrame(tf_idf_pelis, index=dataIngles["title"],
                                columns=columnas_argumentos + columnas_generos)
    print("Cargado completo  de pesos de cada palabra")
    ## obtenemos la similaridad entre las peliculas

    cosine_sims = cosine_similarity(tf_idf_pelis_df)
## obtiene el coseno de diferente entre todo los puntos de la matrix de cada palabra
    matriz_similaridades_df = pd.DataFrame(cosine_sims,
                                            index=dataIngles["title"],
                                            columns=dataIngles["title"])

    print("Cargado completo  de  similaridad entre cada pelicula")
    np.fill_diagonal(matriz_similaridades_df.values, np.nan) ## limpiamos las 1 
    global orden_pelis_cosine_por_fila
    orden_pelis_cosine_por_fila = np.argsort((-cosine_sims), axis=1)

    global cosine_sims_ordenadas
    cosine_sims_ordenadas=np.sort(-cosine_sims, axis=1)
    print("Cargado completo el pronostico listo para su uso...")



def estimar_rating(ratings_usuario, peli, vecindario=50):
   

    top_vecinos_peli_a_estimar = (top_k_similares(peli, vecindario)
                                  [["movieId", "similaridad"]]
                                 )

    pelis_vecinas_puntuadas = ratings_usuario.merge(top_vecinos_peli_a_estimar,
                                                    how="inner",
                                                    on=["movieId"])

    if len(pelis_vecinas_puntuadas) < 2:
        return np.nan 
  
    rating_numerador = (pelis_vecinas_puntuadas["rating"] * pelis_vecinas_puntuadas["similaridad"]).sum()
    rating_denominador = pelis_vecinas_puntuadas["similaridad"].sum()
    
    return rating_numerador / rating_denominador


if __name__ == ("__main__"):
    mainPronostic()
    app.run()
