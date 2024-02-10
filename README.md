# Catalog Digitization


### The Problem Statement:
The challenge is to develop innovative solutions that leverage cutting-edge technologies to seamlessly digitalize and enhance product catalogs, offering a user-friendly experience for sellers and seller apps.
Consider a sample catalog with at least 1000 SKUs, with attributes such as SKU id, product name, description, price, image, inventory, colour, size, brand, etc.
This catalog is to be digitized using a combination of intuitive interfaces such as text / voice / image input, with text & voice input using any of the Indic languages.
In some cases, a combination of these interfaces are required to digitize an SKU e.g. scan image which pre-fills the product name from the repository, with the remaining attributes filled using text or voice input.

### Project Architecture :
![14](https://github.com/shantanu1905/Catalog_digitization/assets/59206895/9c32d52f-68f0-4d26-9e2d-3f0380fe362c)



### Use Cases :

**Scan and Add -**
Scan Barcode: Add products by scanning barcodes, fetching details automatically.

**Image Recognition-**
Take Picture: Utilize image similarity search for product recognition and catalog entry.

**Voice Recognition-**
Search by Voice: Utilize voice by similarity search for product recognition and catalog entry.

**Create/Edit Catalog-**
Manual Entry: Input details manually for product creation or editing.

**Review and Modify-**
Catalog Management: Review, modify, or delete entries in the catalog.

**Export Catalog-**
- CSV Format: Download catalog in CSV format for external use.
- PDF Format: Generate a PDF version for sharing or printing.

### Project Setup Instructions

- Fork and Clone the repo using
```
 git clone https://github.com/shantanu1905/Hackathon-Project.git
```
- Install the Dependencies from `requirements.txt`
- Make sure your system has python 3.11.8 installed and before installing dependencies make sure your virtual environment is activated .
```
 pip install -r requirements.txt 
```
- Run the Server and see the demo at [http://localhost:8000/](http://localhost:8000/)
```
uvicorn main:app --reload
```

## API Documentation
### Authorization

All API requests require the use of a generated access token / bearar token. You can generate a new access token, by navigating to the **/api/token** endpoint.

To authenticate an API request, you should provide your access token / bearar token in the `Authorization` header.

#### 1. Generate Access Token (/api/token)
- **Endpoint Description** - Generate access token by providing `username` and `password` .
- - **Method** - POST

#####  Request Body
```JSON Content
{
  "username" : "test@gmail.com",
  "password":"test123"
}
```
#####  Response Body
```
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3RAZ21haWwuY29tIiwiaWQiOjN9.tZ8HUgpX9kH3jRCXVhporsM5wPfz4dfw9tyhK5LtLf8",
  "token_type": "bearer"
}
```

<hr>

#### 2. Register New User (/api/users)
- **Endpoint Description** - Register new user by providing `email` and `password` .
- **Method** - POST

#####  Request Body
```JSON Content
{
  "email" : "test2@gmail.com",
  "password":"test123"
}
```
#####  Response Body
```
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3QyQGdtYWlsLmNvbSIsImlkIjo4fQ.6W9pVOUEUmSOd1FHBiTiy6YTlMEy2VjD53WgVRiNZbI",
  "token_type": "bearer"
}
```


<hr>

#### 3. Get User Details (/api/users/me)
- **Endpoint Description** - Get User Details by providing `access token ` in authentication header as bearer token.
- **Method** - GET

| Parameter | Type | Description |
| :--- | :--- | :--- |
| ` Bearer Token ` | `string` | **Required**. access token |

#####  Response Body
```
{
  "email": "test2@gmail.com",
  "id": 8,
  "date_created": "2024-02-08T18:12:20.499908"
}
```
<hr>

### Retail Product 
#### 1. Get All Retail Products  (/get_products)
- **Endpoint Description** - Get all products added my user.
- **Method** - GET

| Parameter | Type | Description |
| :--- | :--- | :--- |
| ` Bearer Token ` | `string` | **Required**. access token |

#####  Response Body
```
{
  "products": [
    {
      "ean": 8690632016474,
      "id": 9,
      "category": "Soups & Broths",
      "price": 50,
      "owner_id": 3,
      "name": "Maggi Chicken Oat Soup 65g",
      "image_url": "https://go-upc.s3.amazonaws.com/images/73498628.jpeg",
      "brand": "Maggi",
      "description": "Tasty 65 grams healthy chicken oats with "
    }]
}
```

#### 2. Get Product by ID  (/products/{product_id})
- **Endpoint Description** -  Get Product by user id.
- **Method** - GET

| Parameter | Type | Description |
| :--- | :--- | :--- |
| ` Bearer Token ` | `string` | **Required**. access token |

#####  Response Body
```
{
  "ean": 8901207040795,
  "id": 18,
  "category": "Makeup",
  "price": 50,
  "owner_id": 3,
  "name": "Dabur Gulabari Premium Rose Water 120Ml",
  "image_url": "https://go-upc.s3.amazonaws.com/images/81278639.jpeg",
  "brand": "Dabur",
  "description": "Skin Care"
}
```
#### 3. Delete Product by ID  (/products/{product_id})
- **Endpoint Description** -  Delete Product by user id.
- **Method** - DELETE

| Parameter | Type | Description |
| :--- | :--- | :--- |
| ` Bearer Token ` | `string` | **Required**. access token |

#####  Response Body
```
{
  "message": "Product deleted successfully"
}
```


#### 4. Update Product by ID  (/products/{product_id})
- **Endpoint Description** -  Update Product by user id.
- **Method** - PUT

| Parameter | Type | Description |
| :--- | :--- | :--- |
| ` Bearer Token ` | `string` | **Required**. access token |

#####  Request Body
```
{
  "name": "updated product name",
  "image_url": "updated image url",
  "ean": "updated ean",
  "brand": "updated brand",
  "category": "updated category",
  "price": "updated price",
  "description": "updated description"
}
```

#####  Response Body
```
{
  "status": "Product Details Updated Successfully",
  "product_details": {
    "ean": "updated ean",
    "id": 22,
    "category": "updated category",
    "price": "updated price",
    "owner_id": 3,
    "name": "updated product name",
    "image_url": "updated image url",
    "brand": "updated brand",
    "description": "updated description"
  }
}
```




#### 5. Add Product   (/products_add)
- **Endpoint Description** -  add Product to catalog.
- **Method** - POST

| Parameter | Type | Description |
| :--- | :--- | :--- |
| ` Bearer Token ` | `string` | **Required**. access token |

#####  Request Body
```
{
  "name": "add product",
  "image_url": "add image url",
  "ean": "add ean",
  "brand": "add brand",
  "category": "add category",
  "price": "add price",
  "description": "add description"
}
```

#####  Response Body
```
{
  "status": "Product Details Added Successfully",
  "product_details": {
    "ean": "add ean",
    "id": 25,
    "category": "add category",
    "price": "add price",
    "owner_id": 3,
    "name": "add product",
    "image_url": "add image url",
    "brand": "add brand",
    "description": "add description"
  }
}
```
#### 5. Add Product by scanning barcode   (/search_ean)
- **Endpoint Description** -  Add retail product by scanning `barcode` or `EAN`. This Endpoint works on third party api, which provides products details by providing EAN .
- **Method** - POST

| Parameter | Type | Description |
| :--- | :--- | :--- |
| ` Bearer Token ` | `string` | **Required**. access token |

#####  Request Body
```
{
  "ean":8901207040795
}
```

#####  Response Body
```
{
  "name": "Dabur Gulabari Premium Rose Water 120Ml",
  "image_url": "https://go-upc.s3.amazonaws.com/images/81278639.jpeg",
  "ean": "8901207040795",
  "brand": "Dabur",
  "category": "Makeup"
}
```

#### 6. Add product by clicking product image   (/product_search_by_image)
- **Endpoint Description** -  This endpoint provides products details stored in vector database (Postgres Vector Database) in request of product image provided by user.
- - This feature works on **exact and approximate nearest neighbor search** ,**L2 distance, inner product, and cosine distance** between vectors(embedding of images or text).
  - refer this for more information : [https://github.com/pgvector/pgvector] [https://www.analyticsvidhya.com/blog/2022/07/recommending-similar-images-using-image-embedding/]
  - --
- **Method** - POST

| Parameter | Type | Description |
| :--- | :--- | :--- |
| ` Bearer Token ` | `string` | **Required**. access token |
| ` form data ` | 'field name' `image` | **Required**. form field [files] |

#####  Response Body
```
{
  "status": "success",
  "product_details": {
    "id": 15,
    "name": "Maggi Masala 2-Minute Noodles India Snack",
    "image_url": "https://m.media-amazon.com/images/I/71Y7pDHbi8L._SX679_PIbundle-24,TopRight,0,0_AA679SH20_.jpg",
    "ean": null,
    "brand": null,
    "category": "Grocery & Gourmet Food",
    "price": 12.0,
    "description": "Need a quick meal on the go? Reach for Maggi Masala Noodles! Maggi is spreading happiness with its instant, tasty, and healthy noodles. Bringing you a classic snack directly from India. 2-Minute Masala Noodles are perfectly convenient for the snacking occasion. Delicious Masala flavor brought to with convenience. Maggi Masala Noodles Contain: Wheat Flour, Edible Vegetable Oil, Salt, Mineral (Calcium Carbonate), Guar Gum. Masala Tastemaker : Hydrolyzed Groundnut Protein, Mixed Spices 23.6% (Onion Powder, Coriander, Chili Powder, Turmeric, Garlic Powder, Cumin, Aniseed, Fenugreek, Ginger, Black Pepper, Clove, Nutmeg, Cardamom), Noodle Powder (Wheat Flour, Edible Vegetable Oil, Salt, Wheat Gluten, Mineral (Calcium Carbonate), Guar Gum), Sugar, Edible Starch, Salt, Edible Vegetable Oil, Acidifying Agent (330), Mineral (Potassium Chloride), Color (150d), Flavor Enhancer (635), Raising Agent (500(ii))."
  }
}
```


#### 6. Download products catalog   (/get_catalog)
- **Endpoint Description** -  Download products catalog in csv file.
- **Method** - GET

| Parameter | Type | Description |
| :--- | :--- | :--- |
| ` Bearer Token ` | `string` | **Required**. access token |


#####  Response Body
```
id,name,brand,category,price,image_url,description
9,Maggi Chicken Oat Soup 65g,Maggi,Soups & Broths,50,https://go-upc.s3.amazonaws.com/images/73498628.jpeg,Tasty 65 grams healthy chicken oats with 
10,Maggi Chicken Oat Soup 65g,Maggi,Soups & Broths,50,https://go-upc.s3.amazonaws.com/images/73498628.jpeg,Tasty 65 grams healthy chicken oats 
11,Samsung SD card,samsung,electronic,500,https://www.googleadservices.com/pagead/aclk?sa=L&ai=DChcSEwi1jaSq4IqEAxWALXsHHWNXANgYABAOGgJ0bQ&ase=2&gclid=Cj0KCQiAn-2tBhDVARIsAGmStVktFBIWf-YdMsdMIa-GfzYFObn37yRloyFsw4FDWw3owDjEqwBfKuQaAoI3EALw_wcB&sph=&ohost=www.google.com&cid=CAESVuD2dnQMXYeGDjCSF0YyCPIfFzYwOHnXJ3t4SsJF8wcL65eE1e_C_rkW-yPHyCA4VeC9qhQGFP3w-lHGw6M9y1IvV-N73Kmx22x34Rymw91TgRrxz-AC&sig=AOD64_20kiUjxyqZJ6Axv1Is6-yOGM8iqg&ctype=5&q=&nis=4&ved=2ahUKEwjWwJ2q4IqEAxUHQPUHHQiDB70Qwg8oAHoECAUQDA&adurl=,no desc
13,Maggi Chicken Oat Soup 65g,Maggi,Soups & Broths,40,https://go-upc.s3.amazonaws.com/images/73498628.jpeg,Tasty 65 grams healthy chicken oats with 4 serving 
14,Maggi Chicken Oat Soup 65g,Maggi,Soups & Broths,50,https://go-upc.s3.amazonaws.com/images/73498628.jpeg,Tasty 65 grams healthy chicken oats with 4 serving 
19,Dabur Gulabari Premium Rose Water 120Ml,Dabur,Skin care,50,https://go-upc.s3.amazonaws.com/images/81278639.jpeg,Good for skin
20,Dabur Gulabari Premium Rose Water 120Ml,Dabur,Makeup,,https://go-upc.s3.amazonaws.com/images/81278639.jpeg,
21,Dabur Gulabari Premium Rose Water 120Ml,Dabur,Makeup,15,https://go-upc.s3.amazonaws.com/images/81278639.jpeg,Test
22,updated product name,updated brand,updated category,updated price,updated image url,updated description
23,stjhgjring,samer,sameer case,1525455465,stkmjbkjbkring,stmjbmbring
24,Himalaya Septilin Syrup 200 Ml,Himalaya,Vitamins & Supplements,50,https://go-upc.s3.amazonaws.com/images/55936563.jpeg,Medicine 
25,add product,add brand,add category,add price,add image url,add description
```

#### 7. Add product by voice   (/product_voice_search)
- **Endpoint Description** -  This endpoint provides products details stored in vector database (Postgres Vector Database) in request of voice/audio file provided by user.
- - This feature works on **exact and approximate nearest neighbor search** ,**L2 distance, inner product, and cosine distance** between vectors(embedding of images or text).
  - refer this for more information : [https://github.com/pgvector/pgvector] [https://www.analyticsvidhya.com/blog/2022/07/recommending-similar-images-using-image-embedding/]
  - --
- **Method** - POST

| Parameter | Type | Description |
| :--- | :--- | :--- |
| ` Bearer Token ` | `string` | **Required**. access token |
| ` form data ` | 'field name' `audio` | **Required**. form field [files] |

#####  Response Body
```
{
  "status": "success",
  "product_details": {
    "id": 15,
    "name": "Maggi Masala 2-Minute Noodles India Snack",
    "image_url": "https://m.media-amazon.com/images/I/71Y7pDHbi8L._SX679_PIbundle-24,TopRight,0,0_AA679SH20_.jpg",
    "ean": null,
    "brand": null,
    "category": "Grocery & Gourmet Food",
    "price": 12.0,
    "description": "Need a quick meal on the go? Reach for Maggi Masala Noodles! Maggi is spreading happiness with its instant, tasty, and healthy noodles. Bringing you a classic snack directly from India. 2-Minute Masala Noodles are perfectly convenient for the snacking occasion. Delicious Masala flavor brought to with convenience. Maggi Masala Noodles Contain: Wheat Flour, Edible Vegetable Oil, Salt, Mineral (Calcium Carbonate), Guar Gum. Masala Tastemaker : Hydrolyzed Groundnut Protein, Mixed Spices 23.6% (Onion Powder, Coriander, Chili Powder, Turmeric, Garlic Powder, Cumin, Aniseed, Fenugreek, Ginger, Black Pepper, Clove, Nutmeg, Cardamom), Noodle Powder (Wheat Flour, Edible Vegetable Oil, Salt, Wheat Gluten, Mineral (Calcium Carbonate), Guar Gum), Sugar, Edible Starch, Salt, Edible Vegetable Oil, Acidifying Agent (330), Mineral (Potassium Chloride), Color (150d), Flavor Enhancer (635), Raising Agent (500(ii))."
  }
}
```
