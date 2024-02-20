from fastapi import APIRouter, Form, Path as FastAPIPath, Request,HTTPException,Depends,UploadFile, File
from fastapi.responses import HTMLResponse,JSONResponse
from fastapi.templating import Jinja2Templates
import mysql.connector
from models.models import Customer
from middlewares import get_current_user_from_cookie  
from mysql_connection import get_database_connection
import shutil
from pathlib import Path

router = APIRouter()
templates = Jinja2Templates(directory="templates")
UPLOAD_DIR_PATH = "assets"
UPLOAD_DIR = Path(UPLOAD_DIR_PATH)


@router.get("/")
async def get_admin(current_user: dict = Depends(get_current_user_from_cookie)):
    # Your existing code for handling GET requests
    return {"message": f"Hello, {current_user['role']} {current_user['username']}!"}

@router.post("/")
async def post_admin():
    # Your code for handling POST requests
    return {"message": "Received a POST request to /admin/"}



@router.get("/upload", response_class=HTMLResponse)
async def show_upload_form(request: Request):
    return templates.TemplateResponse("upload_photo.html", {"request": request})
   

@router.post("/upload")
async def handle_upload(request: Request, file_name: str = Form(...), file: UploadFile = File(...)):
    try:
        # Ensure the upload directory exists
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

        # Extract the file extension from the original filename
        file_extension = Path(file.filename).suffix

        # Save the file to the assets directory with the specified file name
        file_path = UPLOAD_DIR / (file_name + file_extension)
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {"file_name": file_name, "file_content_type": file.content_type, "file_path": str(file_path)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {e}")


#14  /admin/saint/age/10/130 - /admin/notsaint/age/10/130 
# get saints between min and max ages from mysql , HTMLResponse with html template
@router.get("/{saint_status}/age/{min_age}/{max_age}", response_class=HTMLResponse)
async def get_customers(request: Request, min_age: int, max_age: int, saint_status: str = FastAPIPath(..., title="Saint Status", description="Specify 'saint' or 'notsaint'")):
    try:
        # Get the database connection
        connection = get_database_connection()

        # Create a cursor object to interact with the database
        cursor = connection.cursor()
        cursor.callproc("GetCustomersByAgeRange", (min_age, max_age, saint_status))
        result = next(cursor.stored_results())
        customers = result.fetchall()


        # Close the cursor and connection
        cursor.close()
        connection.close()
        parsed_customers = []

        for customer in customers:
            customer_data = {
                "id": customer[0],
                "name": customer[1],
                "age": customer[2],
                "occupation": {
                    "name": customer[3],
                    "isSaint": customer[4]
                }
            }
            customer_instance = Customer(**customer_data)
            parsed_customers.append(customer_instance)

        return templates.TemplateResponse("customers.html", {"request": request, "customers": parsed_customers})
  
    except mysql.connector.Error as e:
        return {"message": f"Error retrieving customers: {e}"}



# 14 /admin/name/ra - returns saints with name containing ra
# get customers by name, HTMLResponse with html template
@router.get("/name/{name_contains}", response_class=HTMLResponse)
async def get_data_by_name(request:Request,name_contains: str = FastAPIPath(..., title="Customer Name contains", description="Name of the customer")):

    try:
            # Get the database connection
            connection = get_database_connection()

      
             # Create a cursor object to interact with the database
            cursor = connection.cursor()
            cursor.callproc("GetCustomersByName", (name_contains,))
            result = next(cursor.stored_results())
            customers = result.fetchall()

            # Close the cursor and connection
            cursor.close()
            connection.close()

            parsed_customers = []

            for customer in customers:
                customer_data = {
                    "id": customer[0],
                    "name": customer[1],
                    "age": customer[2],
                    "occupation": {
                        "name": customer[3],
                        "isSaint": customer[4]
                    }
                }
                customer_instance = Customer(**customer_data)
                parsed_customers.append(customer_instance)

            return templates.TemplateResponse("customers.html", {"request": request, "customers": parsed_customers})
    
    except mysql.connector.Error as e:
            return {"message": f"Error retrieving customers: {e}"}



#14 /admin/average - returns the average ages of saints and not saints.
# get customers by name, HTMLResponse with html template
@router.get("/average",  response_class=JSONResponse)
async def get_average_age(request:Request):

    try:
            # Get the database connection
            connection = get_database_connection()

            # Create a cursor object to interact with the database
            cursor = connection.cursor()
            cursor.callproc("GetAverageAge", ())
            result = next(cursor.stored_results())
            avg_age = result.fetchone()[0]

            # Close the cursor and connection
            cursor.close()
            connection.close()


            return {"Average age":f"{avg_age}"}
    
    except mysql.connector.Error as e:
            return {"message": f"Error retrieving avg age: {e}"}

    
#12- Adding the customers in the json to database  - 15: Add validations!
#post a new saint to mysql database:
@router.post("/saints")
async def add_new_saint(request: Request, new_customer: dict):
    try:
        validate_required_fields(new_customer)
        validate_occupation_info(new_customer["occupation"])
        validate_is_saint(new_customer["occupation"]["isSaint"])
        validate_name(new_customer["name"])

        connection = get_database_connection()
        cursor = connection.cursor()

        if customer_exists(cursor, new_customer["name"]):
            raise HTTPException(status_code=400, detail="Customer with the specified name already exists")

        if new_customer["age"] <= 0:
            raise HTTPException(status_code=400, detail="Age must be greater than 0. Customer not added.")

        insert_occupation(cursor, new_customer["occupation"]["name"], new_customer["occupation"]["isSaint"])
        occupation_id = cursor.lastrowid

        insert_customer(cursor, new_customer["name"], new_customer["age"], occupation_id)

        connection.commit()
        cursor.close()
        connection.close()

        return {"message": f"New saint {new_customer['name']} added successfully"}

    except HTTPException as he:
        return {"message": f"Error adding the new saint: {he.detail}"}
    except mysql.connector.Error as e:
        return {"message": f"Error adding the new saint: {e}"}
    


def validate_required_fields(new_customer):
    required_fields = ["name", "age", "occupation"]
    if not all(field in new_customer for field in required_fields):
        raise HTTPException(status_code=400, detail="Required fields are missing")

def validate_occupation_info(occupation_info):
    required_occupation_fields = ["name", "isSaint"]
    if not all(field in occupation_info for field in required_occupation_fields):
        raise HTTPException(status_code=400, detail="Occupation information is incomplete")

def validate_is_saint(is_saint):
    if not isinstance(is_saint, bool):
        raise HTTPException(status_code=400, detail="Invalid isSaint value. It should be a boolean.")

def validate_name(name):
    if not (2 <= len(name) <= 11 and name.isalpha()):
        raise HTTPException(status_code=400, detail="Name should be between 2 and 11 characters and contain only alphabetic characters.")

def customer_exists(cursor, customer_name):
    cursor.execute("SELECT id FROM customers WHERE name = %s", (customer_name,))
    return bool(cursor.fetchone())

def insert_occupation(cursor, name, is_saint):
    add_occupation_query = "INSERT INTO occupations (name, isSaint) VALUES (%s, %s)"
    cursor.execute(add_occupation_query, (name, is_saint))

def insert_customer(cursor, name, age, occupation_id):
    add_customer_query = "INSERT INTO customers (name, age, occupation_id) VALUES (%s, %s, %s)"
    cursor.execute(add_customer_query, (name, age, occupation_id))