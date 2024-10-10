import requests
from bs4 import BeautifulSoup
import json
import re


def grab_produce(url):
    r = requests.get(url)
    if r.status_code  == requests.codes.ok:
        with open('site_dump.txt','w') as file:
            file.write(r.text)
        
def parse_datatable_attributes(html):
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    
    # Initialize a list to store the extracted data
    items = []

    for row in soup.find_all('tr'):
        # Extract the name of the item (usually within the first div with a specific class)
        name_div = row.find('div', class_='col-sm-12 col-xs-6')
        if name_div:
            full_name = name_div.get_text(strip=True)
            # Split the name into 'name' and 'brand'
            if '-' in full_name:
                name, brand = [part.strip() for part in full_name.split('-', 1)]  # Split at first hyphen
            else:
                name = full_name
                brand = full_name  # If no hyphen, set brand equal to name
        else:
            continue  # If there's no name, skip this row
        
        # Extract the price and unit (usually in the second div with a specific class)
        price_div = row.find('div', class_='visible-xs-block col-xs-6')
        if price_div:
            # Use regex to correctly extract the price and unit
            price_match = re.search(r'(\$\d+\.\d{2})\s*(.*)', price_div.get_text(strip=True))
            if price_match:
                price = price_match.group(1)  # Extract the price (e.g., $3.29)
                other_info = price_match.group(2)  # Extract the rest of the information
                # Now, extract the price unit (if available)
                unit_div = price_div.find('div', class_='pbasis')
                unit = unit_div.get_text(strip=True) if unit_div else other_info.strip()  # Use other info as fallback
            else:
                continue  # If no valid price found, skip
        else:
            continue  # If there's no price information, skip this row

        # Append the extracted data to the items list
        items.append({
            'name': name,
            'brand': brand,
            'price': price,
            'unit': unit
        })

    return items

# grab_produce('https://www.foodcoop.com/produce/')
with open('site_dump.txt','r') as file:
    res = parse_datatable_attributes(file)
    if res:     
        with open('item_dump.json','w') as file:
            json.dump(res,file)
