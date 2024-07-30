from flask import Flask, jsonify, request, abort
import random
from unidecode import unidecode
from proximo_feriado import NextHoliday, months

app = Flask(__name__)
peliculas = [
    {'id': 1, 'titulo': 'Indiana Jones', 'genero': 'Acción'},
    {'id': 2, 'titulo': 'Star Wars', 'genero': 'Acción'},
    {'id': 3, 'titulo': 'Interstellar', 'genero': 'Ciencia ficción'},
    {'id': 4, 'titulo': 'Jurassic Park', 'genero': 'Aventura'},
    {'id': 5, 'titulo': 'The Avengers', 'genero': 'Acción'},
    {'id': 6, 'titulo': 'Back to the Future', 'genero': 'Ciencia ficción'},
    {'id': 7, 'titulo': 'The Lord of the Rings', 'genero': 'Fantasía'},
    {'id': 8, 'titulo': 'The Dark Knight', 'genero': 'Acción'},
    {'id': 9, 'titulo': 'Inception', 'genero': 'Ciencia ficción'},
    {'id': 10, 'titulo': 'The Shawshank Redemption', 'genero': 'Drama'},
    {'id': 11, 'titulo': 'Pulp Fiction', 'genero': 'Crimen'},
    {'id': 12, 'titulo': 'Fight Club', 'genero': 'Drama'}
]


def obtener_peliculas():
    return jsonify(peliculas), 200


def obtener_pelicula(id):
    for pelicula in peliculas:
        if pelicula['id'] == id:
            pelicula_encontrada = pelicula
            return jsonify(pelicula_encontrada), 200
    abort(404, description="Película no encontrada")


def agregar_pelicula():
    nueva_pelicula = {
        'id': obtener_nuevo_id(),
        'titulo': request.json['titulo'],
        'genero': request.json['genero']
    }
    peliculas.append(nueva_pelicula)
    print(peliculas)
    return jsonify(nueva_pelicula), 201


def actualizar_pelicula(id):
    for pelicula in peliculas:
        if pelicula['id'] == id:
            pelicula['titulo'] = request.json['titulo']
            pelicula['genero'] = request.json['genero']
            return jsonify(pelicula), 200
    return jsonify({'mensaje': 'Película no encontrada'}), 404


def eliminar_pelicula(id):
    for pelicula in peliculas:
        if pelicula['id'] == id:
            peliculas.remove(pelicula)
            return jsonify(
                {'mensaje': 'Película eliminada correctamente'}), 200
    abort(404, description="Película no encontrada")


def obtener_nuevo_id():
    if len(peliculas) > 0:
        ultimo_id = peliculas[-1]['id']
        return ultimo_id + 1
    else:
        return 1


def normalizar_string(s):
    return unidecode(s.lower().replace('-', ' '))


def listar_peliculas_por_genero(genero):
    peliculas_por_genero = [pelicula for pelicula in peliculas if normalizar_string(
        genero) in normalizar_string(pelicula['genero'])]
    return peliculas_por_genero


def obtener_peliculas_por_genero(genero):
    peliculas_por_genero = listar_peliculas_por_genero(genero)
    if peliculas_por_genero == []:
        abort(404, description="Películas no encontradas")
    return jsonify(listar_peliculas_por_genero(genero)), 200


def obtener_peliculas_por_titulo(titulo):
    peliculas_por_titulo = []
    for pelicula in peliculas:
        if titulo.lower() in pelicula['titulo'].lower():
            peliculas_por_titulo.append(pelicula)
    if peliculas_por_titulo == []:
        abort(404, description="Películas no encontradas")
    return jsonify(peliculas_por_titulo), 200


def obtener_pelicula_aleatoria():
    if len(peliculas) > 0:
        return jsonify(random.choice(peliculas)), 200
    return jsonify({'mensaje': 'No hay películas para sugerir :('}), 404


def obtener_pelicula_aleatoria_por_genero(genero):
    peliculas_por_genero = listar_peliculas_por_genero(genero)
    if peliculas_por_genero == []:
        abort(404, description="Películas no encontradas")
    pelicula_aleatoria = random.choice(peliculas_por_genero)
    return jsonify(pelicula_aleatoria), 200


def obtener_pelicula_para_feriado(genero):
    next_holiday = NextHoliday()
    next_holiday.fetch_holidays()
    if next_holiday.holiday:
        proximo_feriado = f"{next_holiday.holiday['dia']} de {months[next_holiday.holiday['mes'] - 1]}"
        peliculas_por_genero = listar_peliculas_por_genero(genero)
        if peliculas_por_genero:
            pelicula_aleatoria = random.choice(peliculas_por_genero)
            return jsonify({
                'proximo_feriado': proximo_feriado,
                'motivo': next_holiday.holiday['motivo'],
                'pelicula_recomendada': pelicula_aleatoria
            }), 200
        else:
            return jsonify(
                {'mensaje': f'No hay películas de {genero} para recomendar'}), 404
    else:
        return jsonify(
            {'mensaje': 'No se pudo obtener información sobre el próximo feriado'}), 500


# GET methods:
app.add_url_rule(
    '/peliculas',
    'obtener_peliculas',
    obtener_peliculas,
    methods=['GET'])
app.add_url_rule(
    '/peliculas/<int:id>',
    'obtener_pelicula',
    obtener_pelicula,
    methods=['GET'])
app.add_url_rule(
    '/peliculas/genero/<string:genero>',
    'obtener_peliculas_por_genero',
    obtener_peliculas_por_genero,
    methods=['GET'])
app.add_url_rule(
    '/peliculas/titulo/<string:titulo>',
    'obtener_peliculas_por_titulo',
    obtener_peliculas_por_titulo,
    methods=['GET'])
app.add_url_rule(
    '/peliculas/aleatoria',
    'obtener_pelicula_aleatoria',
    obtener_pelicula_aleatoria,
    methods=['GET'])
app.add_url_rule(
    '/peliculas/genero/aleatoria/<string:genero>',
    'obtener_pelicula_aleatoria_por_genero',
    obtener_pelicula_aleatoria_por_genero,
    methods=['GET'])
app.add_url_rule(
    '/peliculas/para_feriado/<string:genero>',
    'obtener_pelicula_para_feriado',
    obtener_pelicula_para_feriado,
    methods=['GET'])

# POST methods:
app.add_url_rule(
    '/peliculas',
    'agregar_pelicula',
    agregar_pelicula,
    methods=['POST'])

# PUT methods:
app.add_url_rule(
    '/peliculas/<int:id>',
    'actualizar_pelicula',
    actualizar_pelicula,
    methods=['PUT'])

# DELETE methods:
app.add_url_rule(
    '/peliculas/<int:id>',
    'eliminar_pelicula',
    eliminar_pelicula,
    methods=['DELETE'])

if __name__ == '__main__':
    app.run()
