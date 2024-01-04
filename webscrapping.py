from bs4 import BeautifulSoup
import httpx
from fastapi import FastAPI ,Depends ,status ,Response ,HTTPException
import json
from fastapi.responses import JSONResponse

async def scrape_upc(upc_number: str ):
    url = f"https://go-upc.com/search?q={upc_number}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch data")

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extracting information
        product_name = soup.find('h1', class_='product-name').text
        image_source = soup.find('figure', class_='product-image').find('img')['src']
        ean = soup.find('td', class_='metadata-label', text='EAN').find_next('td').text
        brand = soup.find('td', class_='metadata-label', text='Brand').find_next('td').text
        category = soup.find('td', class_='metadata-label', text='Category').find_next('td').text

        data = {
            'product_name' : product_name,
            'image_source' : image_source,
            'ean' : ean,
            'brand' : brand,
            'category' : category
        }
        #print(data)
     
        return data

    except Exception as e:
        # Handle exceptions here
        print(f"Sorry, we were not able to find a product for EAN {upc_number}")
        # raise HTTPException(status_code=500, detail="Internal Server Error")