from fastapi import FastAPI, Path, Request, Query,HTTPException,status,Depends,Form
import json
from fastapi.responses import HTMLResponse,JSONResponse
from fastapi.templating import Jinja2Templates
from typing_extensions import Annotated
from mysql_connection import get_database_connection,initialize_db
import mysql.connector

app = FastAPI(debug=True)

templates = Jinja2Templates(directory="templates")


#11- Connecting your server with this db.
try:
    initialize_db()
    print("Database initialization successful")
except Exception as e:
    print(f"Error initializing the database: {e}")



@app.get("/")
async def index():
    return "Ahalan!"


#14  /admin/saint/age/10/130 - /admin/notsaint/age/10/130 
# get saints between min and max ages from mysql , HTMLResponse with html template
@app.get("/admin/{saint_status}/age/{min_age}/{max_age}", response_class=HTMLResponse)
async def get_customers(request: Request, min_age: int, max_age: int, saint_status: str = Path(..., title="Saint Status", description="Specify 'saint' or 'notsaint'")):
    try:
        # Get the database connection
        connection = get_database_connection()

        # Create a cursor object to interact with the database
        cursor = connection.cursor()

        # Select customers within the specified age range based on saint_status
        if saint_status == "saint":
            select_query = """
                SELECT c.id, c.name, c.age, o.name AS occupation_name, o.isSaint
                FROM customers c
                JOIN occupations o ON c.occupation_id = o.id
                WHERE c.age BETWEEN %s AND %s AND o.isSaint = 1
            """
            cursor.execute(select_query, (min_age, max_age))
        elif saint_status == "notsaint":
            select_query = """
                SELECT c.id, c.name, c.age, o.name AS occupation_name, o.isSaint
                FROM customers c
                JOIN occupations o ON c.occupation_id = o.id
                WHERE c.age BETWEEN %s AND %s AND o.isSaint = 0
            """
            cursor.execute(select_query, (min_age, max_age))

        customers = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        # Convert the results to a list of dictionaries
        parsed_customers = []
        for customer in customers:
            parsed_customer = {
                "id": customer[0],
                "name": customer[1],
                "age": customer[2],
                "occupation": {
                    "name": customer[3],  
                    "isSaint": customer[4] 
                }
            }
            parsed_customers.append(parsed_customer)

        return templates.TemplateResponse("customers.html", {"request": request, "customers": parsed_customers})
  
    except mysql.connector.Error as e:
        return {"message": f"Error retrieving customers: {e}"}


# 14 /admin/name/ra - returns saints with name containing ra
# get customers by name, HTMLResponse with html template
@app.get("/admin/name/{name_contains}", response_class=HTMLResponse)
async def get_data_by_name(request:Request,name_contains: str = Path(..., title="Customer Name contains", description="Name of the customer")):

    try:
            # Get the database connection
            connection = get_database_connection()

            # Create a cursor object to interact with the database
            cursor = connection.cursor()

    
            select_query = """
                SELECT c.id, c.name, c.age, o.name AS occupation_name, o.isSaint
                FROM customers c
                JOIN occupations o ON c.occupation_id = o.id
                WHERE LOWER(c.name) LIKE %s
            """
            cursor.execute(select_query, (f"%{name_contains.lower()}%",))


            customers = cursor.fetchall()

            # Close the cursor and connection
            cursor.close()
            connection.close()

            # Convert the results to a list of dictionaries
            parsed_customers = []
            for customer in customers:
                parsed_customer = {
                    "id": customer[0],
                    "name": customer[1],
                    "age": customer[2],
                    "occupation": {
                        "name": customer[3],  
                        "isSaint": customer[4]  
                    }
                }
                parsed_customers.append(parsed_customer)

            return templates.TemplateResponse("customers.html", {"request": request, "customers": parsed_customers})
    
    except mysql.connector.Error as e:
            return {"message": f"Error retrieving customers: {e}"}



#14 /admin/average - returns the average ages of saints and not saints.
# get customers by name, HTMLResponse with html template
@app.get("/admin/average",  response_class=JSONResponse)
async def get_average_age(request:Request):

    try:
            # Get the database connection
            connection = get_database_connection()

            # Create a cursor object to interact with the database
            cursor = connection.cursor()

    
            select_query = """
                SELECT AVG(age)
                FROM customers 
            """
            cursor.execute(select_query)

            avg_age = cursor.fetchone()[0]

            # Close the cursor and connection
            cursor.close()
            connection.close()


            return {"Average age":f"{avg_age}"}
    
    except mysql.connector.Error as e:
            return {"message": f"Error retrieving avg age: {e}"}


    
#12- Adding the customers in the json to database  - 15: Add validations!
#post a new saint to mysql database:
@app.post("/saints")
async def add_new_saint(request: Request, new_customer: dict):
   try:
        
         # Check for required fields
        required_fields = ["name", "age", "occupation"]
        if not all(field in new_customer for field in required_fields):
            raise HTTPException(status_code=400, detail="Required fields are missing")

        # Check occupation information
        if "occupation" not in new_customer:
            raise HTTPException(status_code=400, detail="Occupation information is missing")

        occupation_info = new_customer["occupation"]
        required_occupation_fields = ["name", "isSaint"]
        if not all(field in occupation_info for field in required_occupation_fields):
            raise HTTPException(status_code=400, detail="Occupation information is incomplete")

        # Validate isSaint value
        is_saint = occupation_info.get("isSaint")
        if not isinstance(is_saint, bool):
            raise HTTPException(status_code=400, detail="Invalid isSaint value. It should be a boolean.")
        
           # Validate name length and alphabetic characters
        name = new_customer["name"]
        if not (2 <= len(name) <= 11 and name.isalpha()):
            raise HTTPException(status_code=400, detail="Name should be between 2 and 11 characters and contain only alphabetic characters.")


        # Get the database connection
        connection = get_database_connection()

        # Create a cursor object to interact with the database
        cursor = connection.cursor()

        # Check if the customer with the given name already exists in the database
        cursor.execute("SELECT id FROM customers WHERE name = %s", (new_customer["name"],))
        existing_customer = cursor.fetchone()

        if existing_customer:
            raise HTTPException(status_code=400, detail="Customer with the specified name already exists")

       # Check if the customer is a saint (isSaint = true)
        # is_saint = new_customer["occupation"]["isSaint"]

        # if is_saint:
                   # Check if the age is greater than 0 before executing the query
        if new_customer["age"] > 0:
            # Insert the new occupation into the occupations table (if it doesn't exist)
            add_occupation_query = "INSERT INTO occupations (name, isSaint) VALUES (%s, %s)"
            cursor.execute(add_occupation_query, (new_customer["occupation"]["name"], new_customer["occupation"]["isSaint"]))

            # Commit the changes to the database
            connection.commit()

            # Get the ID of the newly inserted occupation
            occupation_id = cursor.lastrowid

            # Insert the new customer into the customers table
            add_customer_query = "INSERT INTO customers (name, age, occupation_id) VALUES (%s, %s, %s)"

        
    
            cursor.execute(add_customer_query, (new_customer["name"], new_customer["age"], occupation_id))
            connection.commit()
            print("New customer added successfully")
        else:
            return {"message": f"Age must be greater than 0. Customer not added."}

            # print("Age must be greater than 0. Customer not added.")

        # Commit the changes to the database
        connection.commit()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        return {"message": f"New saint {new_customer['name']} added successfully"}
        # else:
        #     return {"message": "Customer is not a saint. Only saints can be added."}
    
   except mysql.connector.Error as e:
        return {"message": f"Error adding the new saint: {e}"}
   



# 5  get saints whit parm: is_saint =true , HTMLResponse with html template
# @app.get("/saints", response_class=HTMLResponse)
# async def get_saint(request: Request, is_saint: bool = Query(..., title="Customer isSaint", description="If the customer occupation isSaint")):
#     with open('./files/customers.json', 'r') as file:
#         content = json.load(file)
#     customers = []
#     for customer in content:
#         if customer["occupation"]["isSaint"] == is_saint:
#             parsed_customer = {
#                 "id": customer["id"],
#                 "name": customer["name"],
#                 "age": customer["age"],
#                 "occupation": {
#                     "name": customer["occupation"]["name"],
#                     "isSaint": customer["occupation"]["isSaint"],
#                 }
#             }
#             customers.append(parsed_customer)

#     return templates.TemplateResponse("customers.html", {"request": request, "customers": customers})
   

#6 - post a new saint to json-file:
# @app.post("/saints")
# async def add_new_saint(request: Request, new_customer: dict):
#     try:
#         with open('./files/customers.json', 'r') as file:
#             content = json.load(file)
#     except FileNotFoundError:
#         content = []

#     # Check if the customer with the given name already exists
#     if any(customer["name"].lower() == new_customer["name"].lower() for customer in content):
#         raise HTTPException(status_code=400, detail="Customer with the specified name already exists")

#     # Add the new customer to the content
#     new_customer["id"] = len(content) + 1  # Assign a new ID (you may need to adjust this based on your actual data)
#     content.append(new_customer)

#     # Write the updated content back to the file
#     with open('./files/customers.json', 'w') as file:
#         json.dump(content, file, indent=2)

#     return {"message": f"New saint {new_customer['name']} added successfully"}



#6 with html - post a new saint to json-file using HTMLResponse and forms:
# @app.post("/saints", response_class=HTMLResponse)
# async def add_new_saint(request: Request, name: str = Form(...), age: int = Form(...), is_saint: bool = Form(...)):
#     try:
#         with open('./files/customers.json', 'r') as file:
#             content = json.load(file)
#     except FileNotFoundError:
#         content = []

#     # Check if the customer with the given name already exists
#     if any(customer["name"].lower() == name.lower() for customer in content):
#         raise HTTPException(status_code=400, detail="Customer with the specified name already exists")

#     # Assign a new ID
#     new_id = len(content) + 1 if content else 1

#     # Create the new customer dictionary
#     new_customer = {
#         "id": new_id,
#         "name": name,
#         "age": age,
#         "occupation": {
#             "name": "saint",  # You may adjust this based on your actual data
#             "isSaint": is_saint,
#         }
#     }

#     # Add the new customer to the content
#     content.append(new_customer)

#     # Write the updated content back to the file
#     with open('./files/customers.json', 'w') as file:
#         json.dump(content, file, indent=2)

#     return JSONResponse(content={"message": f"New saint {name} added successfully"}, status_code=201)




# 2 with html - get saints if is_saint =true, HTMLResponse
# @app.get("/saints",response_class=HTMLResponse)
# async def getSaints(request: Request):
#     with open('./files/customers.json', 'r') as file:
#         content = json.load(file)
#     customers = []
#     for customer in content:
#         if customer['occupation']['isSaint'] == True:
#             parsed_customer = {
#                 "id": customer["id"],
#                 "name": customer["name"],
#                 "age": customer["age"],
#                 "occupation": {
#                 "name": customer["occupation"]["name"],
#                 "isSaint":  customer["occupation"]["isSaint"],
#             }
#             }
#             customers.append(parsed_customer)
#     return  templates.TemplateResponse("customers.html", {"request": request, "customers": customers})


# #4 with html - get customers by name, HTMLResponse with html template + 9 adding limitation for params
# @app.get("/who", response_class=HTMLResponse)
# async def get_data_by_name(request:Request,name: str = Query(..., title="Customer Name", description="Name of the customer",min_length=2,max_length=11,regex="^[a-zA-Z]+$")):
#     with open('./files/customers.json', 'r') as file:
#         content = json.load(file)
#      # Create a dictionary with customer names as keys
#     customers_dict = {customer["name"].lower(): customer for customer in content}

#     # Find the customer with the specified name
#     customer = customers_dict.get(name.lower())

#     if customer:
#         parsed_customer = {
#             "id": customer["id"],
#             "name": customer["name"],
#             "age": customer["age"],
#             "occupation": {
#                 "name": customer["occupation"]["name"],
#                 "isSaint": customer["occupation"]["isSaint"],
#             }
#         }
#         return templates.TemplateResponse("customer.html", {"request": request, "customer": parsed_customer})
#     else:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
   

#1 with html: get customers, HTMLResponse with html template + 8 the name linkable
# @app.get("/customers", response_class=HTMLResponse)
# async def get_data(request: Request):
#     # Read the JSON file
#     with open('./files/customers.json', 'r') as file:
#         content = json.load(file)
#     # Parse and manipulate the content
#     customers = []
#     for customer in content:
#         parsed_customer = {
#             "id": customer["id"],
#             "name": customer["name"],
#             "age": customer["age"],
#             "occupation": {
#                 "name": customer["occupation"]["name"],
#                 "isSaint": customer["occupation"]["isSaint"],
#             }
#         }
#         customers.append(parsed_customer)

#     # Render the HTML template with the parsed data
#     return templates.TemplateResponse("customers.html", {"request": request, "customers": customers})


#3 with html - get customers short-desc, HTMLResponse with html template
# @app.get("/short-desc", response_class=HTMLResponse)
# async def getData(request: Request):
#     with open('./files/customers.json', 'r') as file:
#         content = json.load(file)
#     customers = []
#     for customer in content:
#         parsed_customer = {
#             "name": customer["name"],
#             "occupation": {
#             "name": customer["occupation"]["name"],
#             "isSaint":  customer["occupation"]["isSaint"],
#         }
#         }
#         customers.append(parsed_customer)
#     return templates.TemplateResponse("short_desc.html", {"request": request, "customers": customers})