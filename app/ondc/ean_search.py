from bs4 import BeautifulSoup
import httpx
from fastapi import FastAPI ,Depends ,status ,Response ,HTTPException
import json
from fastapi.responses import JSONResponse


async def scrape_upc(upc_number: str):
    url = f"https://go-upc.com/search?q={upc_number}"
    print(url)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch data")

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extracting information with error handling
        try:
            product_name = soup.find('h1', class_='product-name').text
        except AttributeError:
            product_name = None

        try:
            image_source = soup.find('figure', class_='product-image').find('img')['src']
        except AttributeError:
            image_source = None

        try:
            ean = soup.find('td', class_='metadata-label', text='EAN').find_next('td').text
        except AttributeError:
            ean = None

        try:
            brand = soup.find('td', class_='metadata-label', text='Brand').find_next('td').text
        except AttributeError:
            brand = None

        try:
            category = soup.find('td', class_='metadata-label', text='Category').find_next('td').text
        except AttributeError:
            category = None

        data = {
            'name': product_name,
            'image_url': image_source,
            'ean': ean,
            'brand': brand,
            'category': category
        }
        
        return data

    except Exception as e:
        print(f"Sorry, we were not able to find a product for EAN {upc_number}")
        raise HTTPException(status_code=500, detail="Internal Server Error")