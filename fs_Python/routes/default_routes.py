
from ast import List
from fastapi import Path, Request, Query,HTTPException,status,Depends,Form,APIRouter
import json
from fastapi.responses import HTMLResponse,JSONResponse
from fastapi.templating import Jinja2Templates
from middlewares import get_current_user_from_cookie
from mysql_connection import initialize_db
from models.models import Customer, Short_Customer

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def load_content_from_file():
    with open('./files/customers.json', 'r') as file:
        content = json.load(file)
    return content


@router.get("/")
async def get_default(current_user: dict = Depends(get_current_user_from_cookie)):
    return {"message": f"Hello, {current_user['role']} {current_user['username']}!"}


@router.post("/")
async def post_default():
    # Your code for handling POST requests
    return {"message": "Received a POST request to /default/"}

# 5  get saints whit parm: is_saint =true , HTMLResponse with html template
@router.get("/saints", response_class=HTMLResponse)
async def get_saint(request: Request, is_saint: bool = Query(..., title="Customer isSaint", description="If the customer occupation isSaint")):
    content = load_content_from_file()

    customers: List[Customer] = []
    for customer_data in content:
        customer = Customer(**customer_data)
        if customer.occupation.isSaint == is_saint:
            customers.append(customer)


    return templates.TemplateResponse("customers.html", {"request": request, "customers": customers})

    

# # 2 with html - gets only saints, HTMLResponse
@router.get("/saints", response_class=HTMLResponse)
async def get_saints(request: Request):
    content = load_content_from_file()
    
    customers: List[Customer] = []
    for customer_data in content:
        customer = Customer(**customer_data)
        if customer.occupation.isSaint == 1:
            customers.append(customer)

    return templates.TemplateResponse("customers.html", {"request": request, "customers": customers})


# #4 with html - get customers by name, HTMLResponse with html template + 9 adding limitation for params
@router.get("/who", response_class=HTMLResponse)
async def get_data_by_name(request:Request,name: str = Query(..., title="Customer Name", description="Name of the customer",min_length=2,max_length=11,regex="^[a-zA-Z]+$")):
    content = load_content_from_file()

     # Create a dictionary with customer names as keys
    customers_dict = {customer["name"].lower(): customer for customer in content}

    # Find the customer with the specified name
    customer = customers_dict.get(name.lower())
       
    if customer:
        parsed_customer = Customer(**customer)
        return templates.TemplateResponse("customer.html", {"request": request, "customer": parsed_customer})
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
   

#1 with html: get customers, HTMLResponse with html template + 8 the name linkable
@router.get("/customers", response_class=HTMLResponse)
async def get_data(request: Request):
    # Read the JSON file
    content = load_content_from_file()

    # Parse and manipulate the content
    customers = []
    for customer_data in content:
        customer = Customer(**customer_data)
        customers.append(customer)

    # Render the HTML template with the parsed data
    return templates.TemplateResponse("customers.html", {"request": request, "customers": customers})


#3 with html - get customers short-desc, HTMLResponse with html template
@router.get("/short-desc", response_class=HTMLResponse)
async def getData(request: Request):
    content = load_content_from_file()

    customers = []
    for customer_data in content:
        customer = Short_Customer(**customer_data)
        customers.append(customer)

    return templates.TemplateResponse("short_desc.html", {"request": request, "customers": customers})



#6 - post a new saint to json-file:
@router.post("/saints")
async def add_new_saint(request: Request, new_customer: dict):
    try:
        content = load_content_from_file()

    except FileNotFoundError:
        content = []

    # Check if the customer with the given name already exists
    if any(customer["name"].lower() == new_customer["name"].lower() for customer in content):
        raise HTTPException(status_code=400, detail="Customer with the specified name already exists")

    # Add the new customer to the content
    new_customer["id"] = len(content) + 1  # Assign a new ID 
    content.append(new_customer)

    # Write the updated content back to the file
    with open('./files/customers.json', 'w') as file:
        json.dump(content, file, indent=2)

    return {"message": f"New saint {new_customer['name']} added successfully"}



#6 with html - post a new saint to json-file using HTMLResponse and forms:
@router.post("/saints", response_class=HTMLResponse)
async def add_new_saint(request: Request, name: str = Form(...), age: int = Form(...), is_saint: bool = Form(...)):
    try:
        content = load_content_from_file()

    except FileNotFoundError:
        content = []

    # Check if the customer with the given name already exists
    if any(customer["name"].lower() == name.lower() for customer in content):
        raise HTTPException(status_code=400, detail="Customer with the specified name already exists")

    # Assign a new ID
    new_id = len(content) + 1 if content else 1

    # Create the new customer dictionary
    new_customer = {
        "id": new_id,
        "name": name,
        "age": age,
        "occupation": {
            "name": "saint",  
            "isSaint": is_saint,
        }
    }

    # Add the new customer to the content
    content.append(new_customer)

    # Write the updated content back to the file
    with open('./files/customers.json', 'w') as file:
        json.dump(content, file, indent=2)

    return JSONResponse(content={"message": f"New saint {name} added successfully"}, status_code=201)



#11- Connecting your server with this db.
def connect_database():
    try:
        initialize_db()
        print("Database initialization successful")
    except Exception as e:
        print(f"Error initializing the database: {e}")

