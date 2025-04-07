from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def manejar_captcha(driver):
    try:
        # Primero intenta detectar automáticamente si aparece el CAPTCHA
        captcha = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='captcha'], .captcha-container"))
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


def extraer_datos_tabla(driver):
    # Esperar a que la tabla esté cargada
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "tbody[role='alert'] tr.gradeA"))
    )


    # Gracias deepseek por esto, no se css
    filas = driver.find_elements(By.CSS_SELECTOR, "tbody[role='alert'] tr.gradeA")
    datos = []

    for fila in filas:

        # Extraer datos de cada columna
        codigo = fila.find_element(By.CSS_SELECTOR, "td.sorting_1").text.strip()
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
            'Código': codigo,
            'Materia': nombre,
            'Número de Paralelos': len(paralelos),
            'Paralelos': paralelos
        })

    return datos
