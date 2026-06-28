from unittest import result

from fastapi import FastAPI



db= [
    {"id": 1, "size": "s", "fuel": "Gasoline", "doors": 3, "transmission": "auto"},
    {"id": 2, "size": "s", "fuel": "electric", "doors": 3, "transmission": "auto"},
    {"id": 3, "size": "s", "fuel": "Gasoline", "doors": 5, "transmission": "manual"},
    {"id": 4, "size": "m", "fuel": "electric", "doors": 3, "transmission": "auto"},
    {"id": 5, "size": "m", "fuel": "Gasoline", "doors": 4, "transmission": "manual"},
    {"id": 6, "size": "m", "fuel": "hybrid", "doors": 3, "transmission": "auto"},
    {"id": 7, "size": "l", "fuel": "electric", "doors": 5, "transmission": "manual"},
    {"id": 8, "size": "l", "fuel": "hybrid", "doors": 4, "transmission": "manual"},
    {"id": 9, "size": "l", "fuel": "Gasoline", "doors": 3, "transmission": "auto"}
]
app = FastAPI()
@app.get("/")
async def root(name: str):
    return {"message": f"Hello World {name}"}


@app.get("/api/cars")
async def get_cars(size: str|None, doors: int|None) -> dict:
    result = db
    if size:
        result = [car for car in result if car["size"] == size]
    if doors:
        result = [car for car in result if car["doors"] >= doors]

    return result

