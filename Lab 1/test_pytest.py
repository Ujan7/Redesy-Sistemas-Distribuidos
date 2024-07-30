import requests
import pytest
import requests_mock
from proximo_feriado import NextHoliday


@pytest.fixture
def mock_response():
    with requests_mock.Mocker() as m:
        # Simulamos la respuesta para obtener todas las películas
        m.get('http://localhost:5000/peliculas', json=[
            {'id': 1, 'titulo': 'Indiana Jones', 'genero': 'Acción'},
            {'id': 2, 'titulo': 'Star Wars', 'genero': 'Acción'}
        ])

        # Simulamos la respuesta para agregar una nueva película
        m.post(
            'http://localhost:5000/peliculas',
            status_code=201,
            json={
                'id': 3,
                'titulo': 'Pelicula de prueba',
                'genero': 'Acción'})

        # Simulamos la respuesta para obtener detalles de una película
        # específica
        m.get(
            'http://localhost:5000/peliculas/1',
            json={
                'id': 1,
                'titulo': 'Indiana Jones',
                'genero': 'Acción'})

        # Simulamos la respuesta para actualizar los detalles de una película
        m.put(
            'http://localhost:5000/peliculas/1',
            status_code=200,
            json={
                'id': 1,
                'titulo': 'Nuevo título',
                'genero': 'Comedia'})

        # Simulamos la respuesta para eliminar una película
        m.delete('http://localhost:5000/peliculas/1', status_code=200)

        # Simulamos la respuesta para obtener películas por género
        m.get('http://localhost:5000/peliculas/genero/Acción', json=[
            {'id': 1, 'titulo': 'Indiana Jones', 'genero': 'Acción'},
            {'id': 2, 'titulo': 'Star Wars', 'genero': 'Acción'},
            {'id': 5, 'titulo': 'The Avengers', 'genero': 'Acción'}
        ])

        # Simulamos la respuesta para obtener películas por género no
        # encontrado
        m.get('http://localhost:5000/peliculas/genero/Drama',
              status_code=404, json={'message': 'Películas no encontradas'})

        # Simulamos la respuesta para obtener película por título
        m.get('http://localhost:5000/peliculas/titulo/Indiana Jones',
              json={'id': 1, 'titulo': 'Indiana Jones', 'genero': 'Acción'})

        # Simulamos la respuesta para obtener película por título no encontrada
        m.get('http://localhost:5000/peliculas/titulo/Star Wars',
              status_code=404, json={'message': 'Películas no encontradas'})

        # Simulamos la respuesta para obtener película aleatoria
        m.get(
            'http://localhost:5000/peliculas/aleatoria',
            json={
                'id': 1,
                'titulo': 'Indiana Jones',
                'genero': 'Acción'})

        # Simulamos la respuesta para obtener película aleatoria por género
        m.get('http://localhost:5000/peliculas/genero/aleatoria/Acción',
              json={'id': 1, 'titulo': 'Indiana Jones', 'genero': 'Acción'})

        # Simulamos la respuesta para obtener los feriados
        m.get('https://nolaborables.com.ar/api/v2/feriados/2024',
              json=[{'motivo': 'Feriado de prueba 1',
                     'dia': 1,
                     'mes': 1,
                     'tipo': 'inamovible'},
                    {'motivo': 'Feriado de prueba 2',
                     'dia': 15,
                     'mes': 2,
                     'tipo': 'puente'}])

        yield m


def test_obtener_peliculas(mock_response):
    response = requests.get('http://localhost:5000/peliculas')
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_agregar_pelicula(mock_response):
    nueva_pelicula = {'titulo': 'Pelicula de prueba', 'genero': 'Acción'}
    response = requests.post(
        'http://localhost:5000/peliculas',
        json=nueva_pelicula)
    assert response.status_code == 201
    assert response.json()['id'] == 3


def test_obtener_detalle_pelicula(mock_response):
    response = requests.get('http://localhost:5000/peliculas/1')
    assert response.status_code == 200
    assert response.json()['titulo'] == 'Indiana Jones'


def test_actualizar_detalle_pelicula(mock_response):
    datos_actualizados = {'titulo': 'Nuevo título', 'genero': 'Comedia'}
    response = requests.put(
        'http://localhost:5000/peliculas/1',
        json=datos_actualizados)
    assert response.status_code == 200
    assert response.json()['titulo'] == 'Nuevo título'


def test_eliminar_pelicula(mock_response):
    response = requests.delete('http://localhost:5000/peliculas/1')
    assert response.status_code == 200


def test_obtener_peliculas_por_genero(mock_response):
    response = requests.get('http://localhost:5000/peliculas/genero/Acción')
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_obtener_peliculas_por_genero_no_encontrado(mock_response):
    response = requests.get('http://localhost:5000/peliculas/genero/Drama')
    assert response.status_code == 404
    assert response.json()['message'] == 'Películas no encontradas'


def test_obtener_pelicula_por_titulo(mock_response):
    response = requests.get(
        'http://localhost:5000/peliculas/titulo/Indiana Jones')
    assert response.status_code == 200
    assert response.json()['id'] == 1


def test_obtener_pelicula_por_titulo_no_encontrado(mock_response):
    response = requests.get('http://localhost:5000/peliculas/titulo/Star Wars')
    assert response.status_code == 404
    assert response.json()['message'] == 'Películas no encontradas'


def test_obtener_pelicula_aleatoria(mock_response):
    response = requests.get('http://localhost:5000/peliculas/aleatoria')
    assert response.status_code == 200
    assert 'id' in response.json()
    assert 'titulo' in response.json()
    assert 'genero' in response.json()


def test_obtener_pelicula_aleatoria_por_genero(mock_response):
    response = requests.get(
        'http://localhost:5000/peliculas/genero/aleatoria/Acción')
    assert response.status_code == 200
    assert 'id' in response.json()
    assert 'titulo' in response.json()
    assert 'genero' in response.json()
    assert response.json()['genero'] == 'Acción'


def test_obtener_feriados_por_tipo(mock_response):
    next_holiday = NextHoliday()
    next_holiday.fetch_holidays_by_type('inamovible')
    assert next_holiday.holiday is not None
    assert next_holiday.loading == False
    assert next_holiday.holiday[0]['tipo'] == 'inamovible'


def test_render_feriados_por_tipo(mock_response, capsys):
    next_holiday = NextHoliday()
    next_holiday.fetch_holidays_by_type('puente')
    next_holiday.render_by_type()
    captured = capsys.readouterr()
    assert "Feriados por tipo" in captured.out
