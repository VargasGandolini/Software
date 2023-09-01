import sqlite3
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os

def crear_tablas(titulos,conexion):
    for titulo in titulos:
        cursor = conexion.cursor()

        cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {titulo} (
            id INTEGER PRIMARY KEY,
            Producto TEXT,
            Valor TEXT,
            Imagen TEXT
        )
        ''')

        conexion.commit()

def cambiar_sub_pagina_imagenes(imagenes_sublista,soup,base_url,page):
    siguientes = soup.find_all('ul', class_='list--inline pagination')
    for siguiente in siguientes:
        lis_sin_atributo_ni_clase = siguiente.find_all('li', {'aria-hidden': None, 'class': None}) 
        
        for lis in lis_sin_atributo_ni_clase:
            html = lis.prettify()

            soup = BeautifulSoup(html,'html.parser')

            links = soup.find_all('a', class_='btn btn--tertiary btn--narrow')
            for link in links:
                derecha = soup.find('svg',class_='icon icon--wide icon-arrow-right')
                
                if derecha:
                    nuevo = base_url + link['href']

                    page.goto(nuevo)
                    
                    contenido = page.content()

                    soup = BeautifulSoup(contenido, 'html.parser')

                    imagenes = soup.find_all('div', class_='product-card__image-with-placeholder-wrapper')
                    
                    productos_nombres = soup.find_all('div', class_='h4 grid-view-item__title product-card__title')

                    for producto,nombres in zip(imagenes,productos_nombres):
                        nombre_producto = nombres.get_text()
                        
                        html = producto.decode_contents()

                        soup_1 = BeautifulSoup(html, 'html.parser')

                        productos_1 = soup_1.find_all('div', class_='grid-view-item__image-wrapper product-card__image-wrapper js')

                        for product_1 in productos_1:
                            html = product_1.decode_contents()

                            soup_2 = BeautifulSoup(html, 'html.parser')

                            productos_2 = soup_2.find_all('img', class_=lambda value: value and "grid-view-item__image" in value and "lazy" in value)
                            
                            for product_2 in productos_2:
                                if 'data-src' in product_2.attrs:
                                    imagenes_sublista.append([product_2['data-src'].replace('//','').replace('_{width}x',''),page.title(),nombre_producto])
                                
                                elif 'data-srcset' in product_2.attrs:
                                    imagenes_sublista.append([product_2['data-srcset'].replace('//',''),page.title(),nombre_producto])

                    base_url = base_url.replace('/collection','')
                    
                    cambiar_sub_pagina_imagenes(imagenes_sublista,soup,base_url,page)

def imagenes():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        
        page = browser.new_page()

        base_url = 'https://www.alogar.cl'

        page.goto(base_url)

        contenido = page.content()

        soup = BeautifulSoup(contenido, 'html.parser')

        generales = []
        
        links_generales = []

        nombres_generales = soup.find_all('a', class_='collection-grid-item__link')

        for nombre_generales in nombres_generales:
            generales.append(nombre_generales.get_text().lower().replace('\n','').replace(' ',''))
            links_generales.append(base_url + nombre_generales['href'])
        
        imagenes_lista = []
        productos_lista = []
        
        for link_general in links_generales:
            page.goto(link_general)
            
            contenido_pagina = page.content()

            soup = BeautifulSoup(contenido_pagina, 'html.parser')
            
            imagenes_sublista = []

            imagenes = soup.find_all('div', class_='product-card__image-with-placeholder-wrapper')
            
            productos_nombres = soup.find_all('div', class_='h4 grid-view-item__title product-card__title')

            for producto,nombres in zip(imagenes,productos_nombres):
                nombre_producto = nombres.get_text()
                
                html = producto.decode_contents()

                soup_1 = BeautifulSoup(html, 'html.parser')

                productos_1 = soup_1.find_all('div', class_='grid-view-item__image-wrapper product-card__image-wrapper js')

                for product_1 in productos_1:
                    html = product_1.decode_contents()

                    soup_2 = BeautifulSoup(html, 'html.parser')

                    productos_2 = soup_2.find_all('img', class_=lambda value: value and "grid-view-item__image" in value and "lazy" in value)
                    
                    for product_2 in productos_2:
                        if 'data-src' in product_2.attrs:
                            imagenes_sublista.append([product_2['data-src'].replace('//','').replace('_{width}x',''),page.title(),nombre_producto])
                        
                        elif 'data-srcset' in product_2.attrs:
                            imagenes_sublista.append([product_2['data-srcset'].replace('//',''),page.title(),nombre_producto])
            
            cambiar_sub_pagina_imagenes(imagenes_sublista,soup,base_url,page)
            
            imagenes_lista.append(imagenes_sublista)
        
        conexion = sqlite3.connect('mi_base_de_datos.sql')
        
        for general in generales:
            for imagen_list in imagenes_lista:
                for img in imagen_list:
                    if general[0:6] in img[1].lower().replace(' ',''):
                        cursor = conexion.cursor()
                        
                        cursor.execute(f'''UPDATE {general} SET Imagen = ? WHERE Producto = ?''',(img[0],img[2],))
                        
                        conexion.commit() 

def cambiar_sub_pagina_producto(productos_sublist,soup,base_url,page):
    siguientes = soup.find_all('ul', class_='list--inline pagination')
    for siguiente in siguientes:
        lis_sin_atributo_ni_clase = siguiente.find_all('li', {'aria-hidden': None, 'class': None}) 
        
        for lis in lis_sin_atributo_ni_clase:
            html = lis.prettify()

            soup = BeautifulSoup(html,'html.parser')

            links = soup.find_all('a', class_='btn btn--tertiary btn--narrow')
            for link in links:
                derecha = soup.find('svg',class_='icon icon--wide icon-arrow-right')
                if derecha:
                    nuevo = base_url + link['href']

                    page.goto(nuevo)
                    
                    contenido = page.content()

                    soup = BeautifulSoup(contenido, 'html.parser')

                    productos = soup.find_all('div', class_='h4 grid-view-item__title product-card__title')

                    precios = soup.find_all('span', class_='price-item price-item--regular')
                            
                    for precio,producto in zip(precios,productos):
                        nombre = producto.get_text()
                        titulo_pagina = page.title()
                        valor = precio.get_text()
                        productos_sublist.append([nombre,titulo_pagina,valor]) 
                    base_url = base_url.replace('/collection','')
                    cambiar_sub_pagina_producto(productos_sublist,soup,base_url,page)
                       
def productos():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        base_url = 'https://www.alogar.cl'

        page.goto(base_url)

        contenido = page.content()

        soup = BeautifulSoup(contenido, 'html.parser')

        links_productos = soup.find_all('a', class_='collection-grid-item__link')

        links = []
        generales = []
        for link in links_productos:
            links.append(base_url + link['href'])
            generales.append(link.get_text().lower().replace(" ","").replace('\n',''))

        productos_list = []  # Lista principal para almacenar sublistas de elementos
        for link in links:
            page.goto(link)
            
            contenido = page.content()

            soup = BeautifulSoup(contenido, 'html.parser')

            productos = soup.find_all('div', class_='h4 grid-view-item__title product-card__title')
            
            precios = soup.find_all('span', class_='price-item price-item--regular')
            
            productos_sublist = []  # Sublista para almacenar elementos encontrados en esta página

            for precio,producto in zip(precios,productos):
                nombre = producto.get_text()
                titulo_pagina = page.title()
                valor = precio.get_text()
                productos_sublist.append([nombre,titulo_pagina,valor]) # Agregar contenido a la sublista
            
            cambiar_sub_pagina_producto(productos_sublist,soup,base_url,page)
            productos_list.append(productos_sublist)  # Agregar la sublista a la lista principal
        if os.path.exists('mi_base_de_datos.sql'):
            os.remove('mi_base_de_datos.sql')
        conexion = sqlite3.connect('mi_base_de_datos.sql')
        crear_tablas(generales,conexion)
        
        for general in generales:
            for producto in productos_list:
                for product in producto:
                    if general[0:6] in (product[1].lower().replace(' ','')):
                        cursor = conexion.cursor()
                        cursor.execute(f'''INSERT INTO {general} (Producto,Valor) VALUES(?,?)''',(product[0],product[2]))
                        conexion.commit()         

def main():
    productos()
    imagenes()

if __name__ == "__main__":
    main()
