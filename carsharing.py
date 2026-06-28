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
async def get_cars(size:str|None = None, doors:int|None = None):
    cars = db
    if size:
        cars = [car for car in cars if car["size"] == size]
    if doors:
        cars = [car for car in cars if car["doors"] == doors]

    return cars;


@app.get("/api/cars/{id}")
async def get_car(id:int):
    for car in db:
        if car["id"] == id:
            return car
    return {"message": "car not found"}





