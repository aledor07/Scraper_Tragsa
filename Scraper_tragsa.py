import requests, os, telebot
from bs4 import BeautifulSoup
from dateparser.search import search_dates

# Página web de la que queremos extraer las ofertas
webpage = "https://www.tragsa.es/es/equipo-humano/trabaja-con-nosotros/ofertas-empleo-temporal/Paginas/ofertas-especificas.aspx"
webpage_class = "ofertas-empleo"


def crawling(link_web, link_class):
    # Obtenemos el contenido de la página web
    website_request = requests.get(link_web, timeout=5)
    website_content = BeautifulSoup(website_request.content, "html.parser")

    # Extraemos la lista de trabajos de la tabla
    jobs_link = website_content.find_all(class_=link_class)

    return jobs_link


def search_offers(html):
    # FBúsqueda de ofertas en TRAGSA en función de las keywords asociadas #

    offers_list = []
    offers_dates = []
    indexes = []
    results = []
    vacancies = []
    offers = []
    links = []
    dates = []
    keywords = ["Agrícola", "Agrónomo"]  # Array de keywords

    for row in html:
        cells = row.findChildren("tr")

        for c in cells:
            offers.append(c)

    for x in range(1, len(offers)):
        for tag in offers[x].find_all("a"):
            vacancies.append(tag.contents[0])

    for keyword in keywords:
        for vacancy in vacancies:
            if keyword in vacancy:
                results.append(vacancy)
                indexes.append(vacancies.index(vacancy))

    for offer in offers:
        link = offer.find("a", href=True)

        if link is None:
            continue

        links.append("https://www.tragsa.es" + link["href"])

    links.pop(0)

    for n in range(1, len(offers)):
        for tag in offers[n].find_all("td"):
            dates.append(tag.contents[0])

    for d in dates:
        offer_date = search_dates(d)

        if offer_date is None:
            continue

        offers_dates.append(offer_date)

    for i in range(0, len(indexes)):
        offers_list.append(
            "Oferta: "
            + results[i]
            + ". Fecha límite de envío de CV: "
            + offers_dates[int(indexes[i])][0][0]
            + ". Enlace: "
            + links[int(indexes[i])]
        )

    return offers_list, links, indexes


def ids_check():
    current_ids = []
    saved_ids = []
    send_ids = []
    send_offers = []
    file_name = "ID_OFERTAS.txt" #Nombre archivo txt con id de ofertas enviadas
    sav_id = ""

    # Se comprueban los identificadores actuales #

    for i in indexes:
        start = links[i].find("jobid=") + len("jobid=")
        end = links[i].find("&")
        substring = links[i][start:end]
        current_ids.append(substring)

    # Se comprueban los identificadores archivados #

    with open(file_name) as f:
        saved_ids = f.readlines()
        saved_ids = [int(identifier) for identifier in saved_ids]

    # Se comprueban los identificadores a enviar #

    send_ids = [
        identifier for identifier in current_ids if int(identifier) not in saved_ids
    ]

    for identifier in send_ids:
        send_offers.append(current_ids.index(identifier))
        sav_id += str(identifier) + "\n"

    with open(file_name, "a") as f:
        f.write(sav_id)
        f.close()

    return send_offers


# Ejecución de las funciones #

html = crawling(webpage, webpage_class)
links = search_offers(html)[1]
offers_list = search_offers(html)[0]
indexes = search_offers(html)[2]
telegram_offers = ids_check()

# SE ENVÍAN LOS MENSAJES AL CANAL DE TELEGRAM #

TOKEN = ""  # Ponemos nuestro Token generado con el @BotFather

tb = telebot.TeleBot(
    TOKEN
)  # Combinamos la declaración del Token con la función de la API

for offer in telegram_offers:
    tb.send_message(
        "", offers_list[offer]
    )  # Introducir el identificador del canal por el que enviar las ofertas
