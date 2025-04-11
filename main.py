from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import file_utils as fu
import selenium_utils as su

driver = webdriver.Chrome()

data = fu.leer_archivo()
correo = data[0]
password = data[1]
cursos = fu.procesar_cursos(data[2])
 
# Visitar la pagina del login incial
driver.get(
    "https://www.academico.espol.edu.ec/login.aspx?ReturnUrl=%2fUI%2fInformacionAcademica%2finformaciongeneral.aspx")
print(f"Accediendo a login inical")

# Ingresar el correo
input_correo = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "ctl00_contenido_txtuser")))
input_correo.send_keys(correo)
print("Ingresado correo")

# Dar click en siguiente
boton = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "ctl00_contenido_btnSigte"))
)
boton.click()
print("Botón clickeado")

# Ingresar la contraseña
input_pass = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "ctl00_contenido_txtpsw")))
input_pass.send_keys(password)
print("Ingresado contraseña")

# Manejar captcha
su.manejar_captcha(driver)

# Iniciar sesion
boton = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "ctl00_contenido_btnIniciarSesion"))
)
boton.click()
print("Botón de iniciar sesion clickeado")

# Va a la pagina donde estan las materias disponibles
driver.get("https://www.academico.espol.edu.ec/UI/Registros/materiasdisponibles.aspx")

# Analiza la tabla
su.visitar_enlaces(driver,su.extraer_datos_tabla(driver,cursos))




time.sleep(10)

driver.quit()

# # Ejemplo 2: Buscar por nombre
# input2 = WebDriverWait(driver, 10).until(
#     EC.presence_of_element_located((By.NAME, "nombre_del_segundo_input"))
# )
# input2.send_keys("Texto para el segundo input")
# print("Segundo input encontrado y texto ingresado")
#
# # 3. Esperar 10 segundos
# print("Esperando 10 segundos...")
# time.sleep(10)
#
# # 4. Hacer click en un botón
# # Ejemplo: Buscar botón por XPath
# boton = WebDriverWait(driver, 10).until(
#     EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Enviar')]"))
# )
# boton.click()
# print("Botón clickeado")


# finally:
# Cerrar el navegador al finalizar
# driver.quit()
# print("Navegador cerrado")
