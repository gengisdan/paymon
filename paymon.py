# Paymon 1.0 #

# Magical Art should yet that must not be evil or subject to contempt or scorne...
#(Lemegeton Clavicula Salomonis, Ars Goetia)

###########
## SPECS ##
###########

#Introduce las cadenas de búsqueda
#Selecciona las opciones de búsqueda deseadas (País y Años)
#Recoge la cantidad de resultados
#Recoge los códigos de cada ejemplo para recuperar después el texto y los metadatos.

def specs(lista, anoDesde = 0, anoHasta = 0, pais = []):

    def cachitos(texto, resultados = True, ultima = True, codigos = True):
        import re

        respuesta = []
        fragmentos = []

        encontrados = re.compile(r"Encontrados (.+?) casos")
        max = re.compile(r"max=\"(\d+?)\"")
        chunks = re.compile(r"\"(file=.+?)\", \"(&start=\d+&from=\d+&to=\d+&end=\d+)\"")

        if resultados == True:
            for resultado in encontrados.finditer(texto):
                contextosTotales = resultado.group(1)
        else:
            contextosTotales = ""
        
        if ultima == True:
            for cantidad in max.finditer(texto):
                paginaFinal = cantidad.group(1)
        else:
            paginaFinal = ""

        if codigos == True:
            for chunk in chunks.finditer(texto):
                nArchivo = chunk.group(1)
                codeFicha = chunk.group(2)
                fragmentos.append([nArchivo, codeFicha])
        
        for elemento in [contextosTotales, paginaFinal, fragmentos]:
            if len(elemento) > 0:
                respuesta.append(elemento)
        
        return(respuesta)


    from selenium import webdriver
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    from html import unescape
    from selenium.webdriver.common.keys import Keys

    busqueda = []

    paises = [["ARG", "BEL", "BOL", "CHI", "COL", "CR", "CUB", "ECU", "EUA", "GUA", "GUY", "HON"], ["JAM", "MEX", "NIC", "PAN", "PAR", "PER", "PR", "RD", "SAL", "URU", "TYT", "VEN"]]

    cordiam = "http://cordiam.org/0045.version/left.php"

    driver = webdriver.Chrome()

    for i in range(len(lista)):
        busqueda.append([])
        print(lista[i])

        driver.get(cordiam)
        driver.find_element_by_css_selector("#set_focus_here").send_keys(lista[i]) #Introduce el término de búsqueda

        #Si hay parámetros de búsqueda, abre el cuadro de opciones e introduce los parámetros.
        if (anoDesde > 0 and anoHasta > 0) or len(pais) > 0:
            opciones = driver.find_element_by_xpath("/html/body/div[2]/table/tbody/tr[2]/td/table/tbody/tr/td/form/table/tbody/tr/td/span[3]/span[1]")
            hover = ActionChains(driver).move_to_element(opciones)
            hover.perform()

            if anoDesde > 0 and anoHasta > 0:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#year_from"))).send_keys(anoDesde)
                driver.find_element_by_css_selector("#year_to").send_keys(anoHasta)

            if len(pais) > 0:
                for p in pais:
                    p = p.upper()
                    for j in range(len(paises)):
                        if p in paises[j]:
                            xpathPais = "#metadata-options-dialog > table:nth-child(4) > tbody:nth-child(1) > tr:nth-child(" + str(j+1) + ") > td:nth-child(" + str(paises[j].index(p)+1) + ")"
                            driver.find_element_by_css_selector(xpathPais).click()
            
            ActionChains(driver).move_by_offset(-500, 20).perform()
        
        #Envía la búsqueda
        driver.find_element_by_xpath("/html/body/div[2]/table/tbody/tr[2]/td/table/tbody/tr/td/form/table/tbody/tr/td/input[2]").click()

        #Busca en el código: La cantidad total de resultados, el número máximo de páginas y los primeros codigos de ficha.

        codigo = unescape(unescape(driver.page_source))

        resBusqueda = cachitos(codigo)
        #print(resBusqueda)
        
        print("Resultados totales:", resBusqueda[0])

        for ficha in resBusqueda[2]:
            busqueda[i].append(ficha)

        # Bucle: Itera sobre todas las páginas de resultados para obtener el código y buscar los códigos de ficha.

        pagina = 2
        while pagina <= int(resBusqueda[1]):
            pagesBox = driver.find_element_by_xpath("/html/body/div[3]/div/table/tbody/tr/td[3]/input")
            pagesBox.click()
            pagesBox.send_keys(pagina)
            pagesBox.send_keys(Keys.ENTER)

            codigo1 = unescape(unescape(driver.page_source))

            respuestas = cachitos(codigo1, resultados = False, ultima = False, codigos = True)

            for ficha in respuestas[0]:
                busqueda[i].append(ficha)

            pagina = pagina + 1
    
    driver.close()
    return(busqueda) #Estructura: [KEY [Forma1 [Elelento1] [Elemento2]]]

#############
## FICHADO ##
#############

def fichado(lista):

    def cleanNflip(cadena,regexvar, flip = True):
        import re
        cadena = re.sub(r'<.+?>','', cadena)
        if flip == True:
            cadena = cadena[::-1]
            cadena = regexvar.match(cadena)
            cadena = cadena.group(0)
            cadena = cadena[::-1]
            return(cadena)
        else:
            cadena = regexvar.match(cadena)
            cadena = cadena.group(0)
            return(cadena)
    
    import re
    from html import unescape
    from selenium import webdriver

    driver = webdriver.Chrome()

    dirP1 = "https://www.cordiam.org/0045.version/show_document.php?" 
    dirP2 = "&tab="

    fichitas = []
    fichas = []
    textInfo = []

    parrafo = re.compile(r"(</script>(.+?)<a name=.word. style=.text-decoration:none.>)(<b style=.+?>(.+?)<.b>)(</a>(.+?)<br.*?><br.*?>)")
    contextito = re.compile(r"(^(\W*?\w+){1,10})")

    metaSpecs = [re.compile(r"<em>Año:<\/em> (\d+?)<\/p>"), re.compile(r"<em>País actual:</em> (.+?)</p>"), re.compile(r"<em>Tipo textual:</em> (.+?)</p>"), re.compile(r"<em>Créditos:</em> (.+?)</p>")]

    campo2 = re.compile(r"<em>Autor \(nombre\):</em> (.+?)</p>") 
    campo3 = re.compile(r"<em>Nombre:</em> (.+?)</p>")
    campo35 = re.compile(r"<em>Periódico:</em> (.+)</p>")

    print("Fichando...")

    for token in lista:
        for elemento in ["text", "meta"]: #Tipo de ficha
            url = dirP1 + token[0] + dirP2 + elemento + token[1] +  "#word"
            driver.get(url)
            codigo = driver.page_source

            if elemento == "text":
                #print(codigo)
                #print(url)
                chunks = parrafo.finditer(codigo)
                for chunk in chunks:
                    previo = chunk.group(2)
                    acierto = chunk.group(4)
                    posterior = chunk.group(6)

                    ficha = chunk.group(0)
                    ficha = re.sub(r'<.+?>','', ficha)
                    ficha = re.sub(r'& ','', ficha)
                    #print(ficha)

                    fichas.append(ficha)
                    #print(cleanNflip(previo, contextito) + acierto + cleanNflip(posterior, contextito, flip = False))
                    fichitas.append(cleanNflip(previo, contextito) + acierto + cleanNflip(posterior, contextito, flip = False))
            
            if elemento == "meta":
                #print(codigo)
                imprenta = []
                
                for spec in metaSpecs:
                    datoEd = spec.finditer(codigo)
                    for dato in datoEd:
                        imprenta.append(dato.group(1))
                
                if "Autor (nombre)" in codigo:
                    campox = campo2.finditer(codigo)
                    for cam in campox:
                        autor = cam.group(1)
                else:
                    autor = "---"

                if "<em>Periódico:" in codigo:
                    campoz = campo35.finditer(codigo)
                    for c in campoz:
                        titulo = c.group(1)
                else:
                    campoy = campo3.finditer(codigo)
                    for ca in campoy:
                        titulo = ca.group(1)
                
                imprenta.insert(1, autor)
                imprenta.insert(2, titulo)

                textInfo.append(imprenta)

    print(acierto, ". Fichas recuperadas:", len(fichas))
    #print(len(fichitas))
    #print(len(textInfo))
    return(acierto, fichas, fichitas, textInfo)

############
## PAYMON ##
############

#Oh Thou Paimon, King most glorious, who holds powerful dominion in the Western Regions of the Heavens.
#The Keys of Rabbi Solomon.

import csv

datos = []

lema_forma = {"ahora" : ["aora", "agora"]}

for i, key in enumerate(lema_forma):
    directorio = []
    fichero = []
    directorio = specs(lema_forma[key], anoDesde=1700, anoHasta=1724, pais=["Mex"])
    #print(directorio)
    for forma in directorio:
        fichero = fichado(forma)

        for j in range(len(fichero[1])):
            #print(key, fichero[0], fichero[1][j], fichero[2][j], fichero[3][j][0], fichero[3][j][1], fichero[3][j][2], fichero[3][j][3], fichero[3][j][4], fichero[3][j][5])
            datos.append([key.capitalize(), fichero[0].capitalize(), fichero[1][j], fichero[2][j], fichero[3][j][0], fichero[3][j][1], fichero[3][j][2], fichero[3][j][3], fichero[3][j][4], fichero[3][j][5]])

with open("fichas-cordiam.csv", 'w+', newline='', encoding = 'Windows-1252') as csvfile:
    salida = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
    salida.writerow(["Lema", "Forma", "Contexto", "Ejemplo", "Año", "Autor", "Título", "País", "Tema", "Publicación"])

    #Aquí se pueden poner algunas líneas si se quisiera hacer una muestra aleatoria de todos los datos recuperados.

    for dato in datos:
        salida.writerow(dato)

print("CÓMO CITAR ESTE SOFTWARE: Granados, Daniel. 2021. Paymon. Versión: 1.0. Lenguaje: Python. México. https://github.com/gengisdan/paymon")
