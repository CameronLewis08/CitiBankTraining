# required libraries

from log import Logger
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


# create an instance of the FastAPI class that contains all the routes and configurations for the application

app = FastAPI()
logger = Logger("API")

# define a Pydantic model for the item so that we can validate the data sent in the request body

class Item(BaseModel):
    name: str = None
    is_done: bool = False

# define a route for the root endpoint so that we can test if the application is running correctly

@app.get("/")
def root():
    return {"message": "Hello, World!"}

# adding routes to an application

# define a list to store the items in memory

items = []

"""

This is a simple API for managing a list of items.

HTTP Methods:
    POST: Create a new item and add it to the list of items.
    GET: Retrieve an item by its ID or get the list of items with an optional limit parameter.
    DELETE: Delete an item by its ID from the list of items.
    UPDATE: Update an item by its ID in the list of items.

Use response models to validate the data sent in the request body and to define the structure of the response data.

Use HTTPException to handle errors and return appropriate status codes and error messages.

route names should be descriptive and follow RESTful conventions.

RESTful conventions:
    Use plural nouns for resource names (e.g., /items instead of /item).
    Use HTTP methods to indicate the action being performed (e.g., GET, POST, PUT, DELETE).
    Use path parameters to identify specific resources (e.g., /items/{item_id}).
    Use query parameters to filter or sort the list of resources (e.g., /items?limit=10).
    Use proper status codes to indicate the outcome of each request.
    Use consistent and meaningful naming conventions for routes and parameters.
    Use descriptive names for parameters and variables.
    Use proper documentation to explain the purpose and usage of each route.
    Use versioning to manage changes to the API over time.

Other best practices:
    Use proper error handling to return meaningful error messages and status codes.
    Use proper logging to track the application's behavior and performance.
    Use proper testing to ensure the application works as expected and to catch bugs early.
    Use proper security measures to protect the application from attacks and vulnerabilities.
    Use proper performance optimization techniques to improve the application's speed and responsiveness.
    Use proper scalability techniques to handle increased traffic and load on the application.


"""

# define a route to create an item and add it to the list of items

@app.post("/items")
def create_item(item: Item):
    items.append(item)
    logger.info(f"Item Created: {item.name}")

    return f"Item Created Successfully {item.name}"

# define a route to get an item by its ID from the list of items

@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int) -> Item:
    if 0 <= item_id < len(items):
        logger.info(f"Item Retrieved: {items[item_id].name}")
        return items[item_id]
    else:
        logger.error(f"Item Not Found: {item_id}")
        raise HTTPException(status_code=404, detail="Item not found")

# define a route to get the list of items with an optional limit parameter to limit the number of items returned

@app.get("/items", response_model=list[Item])
def list_items(limit: int = 10) -> list:
    if limit is not None:
        logger.info(f"Items Retrieved: {len(items[:limit])} items")
        return items[:limit]
    
    logger.info(f"Items Retrieved: {len(items)} items")
    return items


    
    




