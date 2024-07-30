import requests

# Obtener todas las películas
response = requests.get('http://localhost:5000/peliculas')
peliculas = response.json()
print("Películas existentes:")
for pelicula in peliculas:
    print(
        f"ID: {pelicula['id']}, Título: {pelicula['titulo']}, Género: {pelicula['genero']}")
print()

# Agregar una nueva película
nueva_pelicula = {
    'titulo': 'Pelicula de prueba',
    'genero': 'Acción'
}
response = requests.post(
    'http://localhost:5000/peliculas',
    json=nueva_pelicula)
if response.status_code == 201:
    pelicula_agregada = response.json()
    print("Película agregada:")
    print(
        f"ID: {pelicula_agregada['id']}, Título: {pelicula_agregada['titulo']}, Género: {pelicula_agregada['genero']}")
else:
    print("Error al agregar la película.")
print()

# Obtener detalles de una película específica
id_pelicula = 1  # ID de la película a obtener
response = requests.get(f'http://localhost:5000/peliculas/{id_pelicula}')
if response.status_code == 200:
    pelicula = response.json()
    print("Detalles de la película:")
    print(
        f"ID: {pelicula['id']}, Título: {pelicula['titulo']}, Género: {pelicula['genero']}")
else:
    print("Error al obtener los detalles de la película.")
print()

# Actualizar los detalles de una película
id_pelicula = 1  # ID de la película a actualizar
datos_actualizados = {
    'titulo': 'Nuevo título',
    'genero': 'Comedia'
}
response = requests.put(
    f'http://localhost:5000/peliculas/{id_pelicula}',
    json=datos_actualizados)
if response.status_code == 200:
    pelicula_actualizada = response.json()
    print("Película actualizada:")
    print(
        f"ID: {pelicula_actualizada['id']}, Título: {pelicula_actualizada['titulo']}, Género: {pelicula_actualizada['genero']}")
else:
    print("Error al actualizar la película.")
print()

# Eliminar una película
id_pelicula = 1  # ID de la película a eliminar
response = requests.delete(f'http://localhost:5000/peliculas/{id_pelicula}')
if response.status_code == 200:
    print("Película eliminada correctamente.")
else:
    print("Error al eliminar la película.")

# Obtener películas por género
genero = 'Acción'  # Género de las películas a obtener
response = requests.get(f'http://localhost:5000/peliculas/genero/{genero}')
print()
if response.status_code == 200:
    peliculas_genero = response.json()
    print(f"Películas de género '{genero}':")
    for pelicula in peliculas_genero:
        print(
            f"ID: {pelicula['id']}, Título: {pelicula['titulo']}, Género: {pelicula['genero']}")
else:
    print("Error al obtener las películas por género.")
print()

# Obtener pelicula por titulo
titulo = 'in'  # Título de la película a obtener
response = requests.get(f'http://localhost:5000/peliculas/titulo/{titulo}')
if response.status_code == 200:
    peliculas = response.json()
    print("Películas con el título proporcionado:")
    for pelicula in peliculas:
        print(
            f"ID: {pelicula['id']}, Título: {pelicula['titulo']}, Género: {pelicula['genero']}")
else:
    print("Error al obtener la película por título.")
print()

# Obtener película aleatoria
response = requests.get('http://localhost:5000/peliculas/aleatoria')
if response.status_code == 200:
    pelicula_aleatoria = response.json()
    print("Película aleatoria:")
    print(
        f"ID: {pelicula_aleatoria['id']}, Título: {pelicula_aleatoria['titulo']}, Género: {pelicula_aleatoria['genero']}")
else:
    print("Error al obtener la película aleatoria.")
print()

# Obtener película aleatoria por género
genero = 'Acción'  # Género de la película aleatoria a obtener
response = requests.get(
    f'http://localhost:5000/peliculas/genero/aleatoria/{genero}')
if response.status_code == 200:
    pelicula_aleatoria = response.json()
    print(f"Película aleatoria de género '{genero}':")
    print(
        f"ID: {pelicula_aleatoria['id']}, Título: {pelicula_aleatoria['titulo']}, Género: {pelicula_aleatoria['genero']}")
else:
    print("Error al obtener la película aleatoria por género.")
print()


# Obtener pelicula para feriado
genero = 'Acción'  # Género de la película aleatoria a obtener
response = requests.get(
    f'http://localhost:5000/peliculas/para_feriado/{genero}')
if response.status_code == 200:
    pelicula_feriado = response.json()
    print("Película para feriado:")
    print(f"Proximo feriado: {pelicula_feriado['proximo_feriado']}, Motivo: {pelicula_feriado['motivo']}, Título: {pelicula_feriado['pelicula_recomendada']['titulo']}, Género: {pelicula_feriado['pelicula_recomendada']['genero']}")
else:
    print("Error al obtener la película para feriado.")
