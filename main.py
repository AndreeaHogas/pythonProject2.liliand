import json
import re
import time
from bs4 import BeautifulSoup
import requests


# https://youtube.com/playlist?list=PLzMcBGfZo4-n40rB1XaJ0ak1bemvlqumQ

base_url = "https://www.elefant.ro/filter/1?PageNumber={}&PageSize=60&SortingAttribute=bestseller-desc&ViewType=&SearchTerm=star+wars&SearchParameter=%26%40QueryTerm%3Dstar%2Bwars%26AvailableFlag%3D1%26isMaster%3D0"
current_page = 1
cartii = []

while current_page <= 13:
    page = requests.get(base_url.format(current_page))
    soup = BeautifulSoup(page.content, "html.parser")

    script_element = soup.find_all("script", {"type": "text/javascript"})[22]
    script_data = script_element.string

    regex = r"\{([^}]*)\}"
    matches = re.findall(regex, script_data)

    def format_info(info):
        return info.split(":")[-1].replace(",", "")

    def extract_data(product):
        result = {}
        for info in product.split("\n"):
            if info.startswith("'name'"):
                result["title"] = format_info(info)
            elif info.startswith("'price'"):
                result["price"] = format_info(info)
            elif info.startswith("'producttitleloader'"):
                result["producttitleloader"] = format_info(info)
            elif "'category'" in info and "'Carti\\/Carte straina\\/Fiction & related items\\/Science fiction'" in info:
                result["category"] = format_info(info)
            elif "'category'" in info and "'Carti\\/Carte straina\\/Fiction & related items'" in info:
                result["category"] = "Carti/Carte straina/Fiction & related items"
            elif "'category'" in info and "'Carti\\/Carte straina\\/Children\\'s, Teenage & Educational'" in info:
                result["category"] = "Carti/Carte straina/Children's, Teenage & Educational"
            elif info.startswith("'brand'"):
                result["brand"] = format_info(info)
            elif "'product-sold-out'" in info:
                return None
        return result

    for match in matches:
        book = extract_data(match)
        if book is not None and "category" in book:
            if book not in cartii:
                cartii.append(book)

    print(f"Verifying page: {current_page}")
    current_page += 1
    time.sleep(1)  # Pauză de 1 secundă între cereri pentru a nu suprasolicita serverul

    next_page_link = soup.find("a", title="La pagina următoare")
    if next_page_link is None:
        break
    next_page_url = next_page_link["href"]
    # Extragem numărul paginii următoare din URL
    current_page = int(re.search(r"PageNumber=(\d+)", next_page_url).group(1))

with open("star_wars_cartii.json", "w+", encoding="utf8") as json_file:
    json.dump({"cartii": cartii}, json_file, indent=4)

print("Codul a fost executat cu succes și fișierul JSON a fost generat.")