from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from datetime import datetime

# Initialize FastAPI app
app = FastAPI(
    title="Sample API",
    description="A sample FastAPI server with basic CRUD operations",
    version="1.0.0",
)


# Pydantic models for request/response
class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# In-memory storage
items_db = []
item_id_counter = 1


# Dependencies
async def get_item_by_id(item_id: int) -> Item:
    item = next((item for item in items_db if item["id"] == item_id), None)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found",
        )
    return item


# Routes
@app.get("/")
async def root():
    return {"message": "Welcome to the Sample API"}


@app.get("/items/", response_model=List[Item])
async def get_items(skip: int = 0, limit: int = 10):
    return items_db[skip : skip + limit]


@app.get("/items/{item_id}", response_model=Item)
async def get_item(item: dict = Depends(get_item_by_id)):
    return item


@app.post("/items/", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate):
    global item_id_counter
    new_item = {
        **item.model_dump(),
        "id": item_id_counter,
        "created_at": datetime.now(),
    }
    items_db.append(new_item)
    item_id_counter += 1
    return new_item


@app.put("/items/{item_id}", response_model=Item)
async def update_item(
    item_id: int, item_update: ItemBase, item: dict = Depends(get_item_by_id)
):
    item.update(**item_update.model_dump())
    return item


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item: dict = Depends(get_item_by_id)):
    items_db.remove(item)
    return None


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {"detail": exc.detail, "status_code": exc.status_code}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
