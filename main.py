import requests
from bs4 import BeautifulSoup
import configparser
from constants import URL

class Model:
    def __init__(self, name, movement, toughness, saving_throw, wounds, leadership, oc, invulnerable_save, base_size):
        self.name = name
        self.movement = movement
        self.toughness = toughness
        self.saving_throw = saving_throw
        self.wounds = wounds
        self.leadership = leadership
        self.oc = oc
        self.invulnerable_save = invulnerable_save
        self.base_size = base_size

    def __str__(self):
        return f"{self.name} (M:{self.movement}, T:{self.toughness}, Sv:{self.saving_throw}, W:{self.wounds}, Ld:{self.leadership}, OC:{self.oc}, Inv Sv:{self.invulnerable_save}, Base Size:{self.base_size})"


class Unit:
    def __init__(self, name, base_size=None):
        self.name = name
        self.base_size = base_size
        self.models = []

    def add_model(self, model):
        self.models.append(model)

    def __str__(self):
        unit_str = f"{self.name}\n"
        for model in self.models:
            unit_str += f"  - {model}\n"
        return unit_str
def get_wahapedia_data(url):
    """Retrieve hrefs from Wahapedia page"""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    dropdown_menu = soup.find_all("div", class_="NavDropdown-content")
    if len(dropdown_menu) < 2:
        raise ValueError("Expected at least 2 dropdown menus")
    menu = dropdown_menu[1]
    links = menu.find_all("a")
    hrefs = [link.get("href") for link in links]
    return hrefs


def parse_href_data(href):
    response = requests.get(href)
    soup = BeautifulSoup(response.text, 'html.parser')
    army_type_div = soup.find_all('div', class_='i15 ArmyType_line clFl ASCF ASAS ASHM ASPH ASBF ASAF ASPP')
    hrefs = [div.find('a').get('href') for div in army_type_div]
    return hrefs
def extract_unit_data(section):
    unit_data = {}
    ds_h2_header = section.find('div', class_='dsH2Header')
    unit_data['name'] = ds_h2_header.find('div').text.strip()
    base_size_span = ds_h2_header.find('span', class_='dsModelBase2')
    if base_size_span:
        unit_data['base_size'] = (base_size_span.text.strip().
                                  replace('(', '').replace(')', '').replace('mm', ''))
    models = []
    model_sections = section.find_all('div', class_='dsProfileBaseWrap')
    for model_section in model_sections:
        model_data = {}
        if model_section.find('span', class_='dsModelNameTop'):
            model_data['name'] = model_section.find('span', class_='dsModelNameTop').text.strip()
        elif model_section.find('span', class_='dsModelName'):
            model_data['name'] = model_section.find('span', class_='dsModelName').text.strip()
        char_wraps = model_section.find_all('div', class_='dsCharWrap')
        if not char_wraps:
            continue
        char_values = [char_wrap.find('div', class_='dsCharValue').text.strip() for char_wrap in char_wraps]
        model_data['movement'] = char_values[0]
        model_data['toughness'] = char_values[1]
        model_data['saving_throw'] = char_values[2]
        model_data['wounds'] = char_values[3]
        model_data['leadership'] = char_values[4]
        model_data['oc'] = char_values[5]
        invul_wrap = model_section.find_next_sibling('div', class_='dsInvulWrap')
        if invul_wrap:
            invul_value = invul_wrap.find('div', class_='dsCharInvulValue').text.strip()
            model_data['invulnerable_save'] = invul_value
        models.append(model_data)
    unit_data['models'] = models
    return unit_data
def parse_data_from_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all datasheet sections
    datasheet_sections = soup.find_all('div', class_='dsBannerWrap')
    units = []
    for section in datasheet_sections:
        unit_data = extract_unit_data(section)
        units.append(unit_data)
    return units

def main():
    url = URL.WAHAPEIDA_QUICK_START_GUIDE.value
    hrefs = get_wahapedia_data(url)
    for href in hrefs:
        print(URL.WAHAPEIDA_ROOT.value + href + '/' + URL.WAHAPEDIA_DATASHEETS.value)
        units = parse_data_from_page(URL.WAHAPEIDA_ROOT.value + href + '/' + URL.WAHAPEDIA_DATASHEETS.value)
        print(units)

if __name__ == "__main__":
    main()
