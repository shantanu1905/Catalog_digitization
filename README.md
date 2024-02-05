# Catalog Digitization


### The Problem Statement:
The challenge is to develop innovative solutions that leverage cutting-edge technologies to seamlessly digitalize and enhance product catalogs, offering a user-friendly experience for sellers and seller apps.
Consider a sample catalog with at least 1000 SKUs, with attributes such as SKU id, product name, description, price, image, inventory, colour, size, brand, etc.
This catalog is to be digitized using a combination of intuitive interfaces such as text / voice / image input, with text & voice input using any of the Indic languages.
In some cases, a combination of these interfaces are required to digitize an SKU e.g. scan image which pre-fills the product name from the repository, with the remaining attributes filled using text or voice input.

### Project Architecture :
![cateloge_digitization](https://github.com/shantanu1905/Catalog_digitization/assets/59206895/e23225ac-83f8-4676-8dfd-89ff37429a57)

### Use Cases :

**Scan and Add -**
Scan Barcode: Add products by scanning barcodes, fetching details automatically.

**Image Recognition-**
Take Picture: Utilize image similarity search for product recognition and catalog entry.

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

