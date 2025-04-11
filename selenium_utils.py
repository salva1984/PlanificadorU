import time
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait


def manejar_captcha(driver):
    try:
        # Primero intenta detectar automáticamente si aparece el CAPTCHA
        captcha = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='captcha'], .captcha-container"))
        )
        print("CAPTCHA detectado, por favor resuélvelo manualmente")

        # Espera manual (60 segundos máximo)
        time.sleep(10)

        # Verifica si el CAPTCHA sigue visible
        if captcha.is_displayed():
            print("¿Aún ves el CAPTCHA? Tienes 60 segundos más...")
            time.sleep(10)

    except:
        print("No se detectó CAPTCHA, continuando...")
        pass


def extraer_datos_tabla(driver, cursos):
    # Esperar a que la tabla esté cargada
    WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.CSS_SELECTOR, "tbody[role='alert'] tr.gradeA"))
    )

    # Marca la opcion para mostrar 100 elementos, si tienes mas de 100 cursos disponibles estas jodido
    mostrar_registros_element = driver.find_element(By.NAME, "ctl00_contenido_tbMateriasDisp_length")
    mostrar_registros = Select(mostrar_registros_element)
    mostrar_registros.select_by_value("100")

    # Gracias deepseek por esto, no se css
    # Obtiene todos los codigos de las materias de la columna
    filas = driver.find_elements(By.CSS_SELECTOR, "tbody[role='alert'] tr.gradeA")
    datos = []

    for fila in filas:

        # Extraer datos de cada columna
        codigo = fila.find_element(By.CSS_SELECTOR, "td.sorting_1").text.strip()
        if codigo in cursos:

            nombre = fila.find_element(By.CSS_SELECTOR, "td:nth-child(2)").text.strip()

            # Extraer todos los enlaces de paralelos
            enlaces = fila.find_elements(By.CSS_SELECTOR, "td:nth-child(5) a.myLink")
            paralelos = []

            for enlace in enlaces:
                texto = enlace.text.strip()
                href = enlace.get_attribute('href')
                paralelos.append({
                    'texto': texto,
                    'url': href,
                })

            datos.append({
                'Codigo': codigo,
                'Materia': nombre,
                'Número de Paralelos': len(paralelos),
                'Paralelos': paralelos
            })

    if len(datos) == 0:
        print("No se encontro ningun curso que coincida con los indicados en data.txt")

    return datos


def visitar_enlaces(driver: webdriver, datos: list):
    output = []

    for materia in datos:
        datos_materia = {
            "Nombre_materia": materia["Materia"],
            "Codigo_materia": materia["Codigo"],
            "Paralelos": []
        }

        for paralelo in materia["Paralelos"]:
            driver.get(paralelo["url"])

            # Encuentra datos relevantes
            profesor = driver.find_element(By.ID, "ctl00_contenido_LabelProfesor").text
            paralelo = driver.find_element(By.ID, "ctl00_contenido_LabelParalelo").text
            examen_parcial = driver.find_element(By.ID, "ctl00_contenido_LabelParcial").text
            examen_final = driver.find_element(By.ID, "ctl00_contenido_LabelFinal").text
            mejoramiento = driver.find_element(By.ID, "ctl00_contenido_LabelMejora").text
            cupo_disponible = driver.find_element(By.ID, "ctl00_contenido_LabelDisponible").text

            # Encuentra las filas de el horario teorico ejm,
            # Lunes	11:00:00	12:30:00	A101	11A CAMPUS GUSTAVO GALINDO
            # Miércoles	11:00:00	11:30:00	L205	11A CAMPUS GUSTAVO GALINDO
            tabla_horario_teorico = driver.find_element(By.ID, "ctl00_contenido_TableHorarios")
            fila_horalio_teorico = tabla_horario_teorico.find_elements(By.CSS_SELECTOR, "tbody tr")

            horario_teorico = {}

            datos_paralelo = {
                "Paralelo": paralelo,
                "Profesor": profesor,
                "Examen_parcial": examen_parcial,
                "Examen_final": examen_final,
                "Examen_mejoramiento": mejoramiento,
                "Horario teorico": [],
                "Paralelo_practico": [],
            }

            # Recorre cada fila para obetener el horario teorico
            for fila in fila_horalio_teorico:
                fila = fila.find_elements(By.CSS_SELECTOR, "td")
                horario_teorico[fila[0].text] = {
                    "Hora_inicio": fila[1].text,
                    "Hora_fin": fila[2].text,
                    "Aula": fila[3].text,
                    "Campus": fila[4].text,
                }

            datos_paralelo["Horario teorico"] = horario_teorico



            fila_paralelos_practicos = WebDriverWait(driver, 10).until(
                ec.presence_of_element_located(
                    (By.CSS_SELECTOR, "table.display:nth-child(1) > tbody:nth-child(1) > tr:nth-child(5)")))
            fila_paralelos_practicos = driver.find_element(By.CSS_SELECTOR,
                                                           "table.display:nth-child(1) > tbody:nth-child(1) > tr:nth-child(5)")

            # Encontrar todos los enlaces de paralelos practicos
            enlaces_paralelos = fila_paralelos_practicos.find_elements(By.CSS_SELECTOR, "a.mostrar")
            for enlace in enlaces_paralelos:
                enlace.click()



                # Selecciona la tabla y llega hasta el texto relevante ejm.
                # Jueves 	10:00:00 	11:00:00 	U002
                # 14B CAMPUS GUSTAVO GALINDO
                tabla_practico = driver.find_element(By.CSS_SELECTOR, "div.tabla_horario")
                tabla_datos_practico = tabla_practico.find_element(By.CSS_SELECTOR, ":nth-child(2)")

                # Profesor:   ASENCIO MERA JOSE LUIS 	Paralelo::  101
                fila_1 = tabla_datos_practico.find_elements(By.CSS_SELECTOR, "tbody > tr")[0]
                profesor_practico = fila_1.find_elements(By.CSS_SELECTOR, "td")[0].text.split(":")[1].strip()
                paralelo_practico = fila_1.find_elements(By.CSS_SELECTOR, "td")[1].text.split("::")[1].strip()

                # Capacidad:  32 	Cupo disponible:  32
                fila_2 = tabla_datos_practico.find_elements(By.CSS_SELECTOR, "tbody > tr")[1]
                cupos_disponibles_practico = fila_2.find_elements(By.CSS_SELECTOR, "td")[1].text.split(":")[1].strip()



                # Tabla del horario
                tabla_horario_practico = tabla_practico.find_element(By.CSS_SELECTOR, ":nth-child(4)")
                celdas = tabla_horario_practico.find_element(By.CSS_SELECTOR, "tbody tr").find_elements(By.TAG_NAME,
                                                                                                        "td")

                # Celdas tiene algo parecido a (Jueves 	10:00:00 	11:00:00 	U002 	14B CAMPUS GUSTAVO GALINDO )

                datos_paralelo_practico = {
                    "Paralelo": paralelo_practico,
                    "Profesor": profesor_practico,
                    "Cupos disponibles": cupos_disponibles_practico,
                    "Dia": celdas[0].text,
                    "Hora_inicio": celdas[1].text,
                    "Hora_fin": celdas[2].text,
                    "Aula": celdas[3].text,
                    "Ubicacion": ' '.join(celdas[4].text.split())
                }

                datos_paralelo["Paralelo_practico"].append(datos_paralelo_practico)

            datos_materia["Paralelos"].append(datos_paralelo)

        output.append(datos_materia)

    # Escribir en un archivo
    with open("datos.json", "w", encoding="utf-8") as archivo:
        json.dump(output, archivo, indent=4,ensure_ascii=False)
