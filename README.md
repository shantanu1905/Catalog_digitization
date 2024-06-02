# Catalog Digitization


### The Problem Statement:
The challenge is to develop innovative solutions that leverage cutting-edge technologies to seamlessly digitalize and enhance product catalogs, offering a user-friendly experience for sellers and seller apps.
Consider a sample catalog with at least 1000 SKUs, with attributes such as SKU id, product name, description, price, image, inventory, colour, size, brand, etc.
This catalog is to be digitized using a combination of intuitive interfaces such as text / voice / image input, with text & voice input using any of the Indic languages.
In some cases, a combination of these interfaces are required to digitize an SKU e.g. scan image which pre-fills the product name from the repository, with the remaining attributes filled using text or voice input.

### Project Architecture :
![14](https://github.com/shantanu1905/Catalog_digitization/assets/59206895/d1c25694-2662-42d1-9943-8dea39e79768)


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
CSV Format: Download catalog in CSV format for external use.
  
**Share Catalog-**
Share your catalog with just single click and share catalog using public link

**User registration and login-**
login and registration with account activation feature .



## Technologies Used 
[![My Skills](https://skillicons.dev/icons?i=py,pytorch,sqlite,tensorflow,docker,github,&perline=7)](https://skillicons.dev)


### Project Setup Instructions
- **pgvector database setup using docker**
  -- Make sure that system has docker installed on it.
  -- The below command is used to start Docker containers defined in a docker-compose.yml file in detached mode, meaning the containers run in the background.
```
 compose up -d
```
- open cmd and enter below command
```
docker exec -it postgres-pgvector psql -U postgres -d postgres -c 'CREATE EXTENSION vector'
```
- open cmd and enter below command to create table in *pgvector* database running in docker
```
docker exec -it postgres-pgvector psql -U postgres -d postgres -c 'CREATE TABLE products (id SERIAL PRIMARY KEY,name VARCHAR(255),image_url VARCHAR(255),ean VARCHAR(255),brand VARCHAR(255),category VARCHAR(255),price REAL,description TEXT ,name_embedding VECTOR(384));'
```
- Fork and Clone the repo using
```
https://github.com/shantanu1905/Catalog_digitization.git
```
- Install the Dependencies from `requirements.txt`
- Make sure your system has python 3.11.8 installed and before installing dependencies make sure your virtual environment is activated .
```
 pip install -r requirements.txt 
```
- Run main server
```
uvicorn app.main:app --reload 
```
- Running ml_services server. open ml_services folder and create a virtualenv and activate it then install requirements.txt file and run below command to start server
```
python main.py
```

### Access API endpoint documentation this URL
```
http://127.0.0.1:8000/docs
```

**Note** - THis repo contanins two server, main server(**app**) and mlservices server(**ml_services**). above process is to start main server .

### Application Demo link 
https://youtu.be/2lB753zlCOg?si=7xN-HTd5k6588GDp

### To view frontend code checkout this repo 
https://github.com/sam-79/CatalogDigitization

