from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("maps_api_key")

app = FastAPI(
    title="API de Direcciones para Medellín",
    description="Esta API consulta rutas entre direcciones y formatea las instrucciones de la ruta utilizando la API de Google Routes.",
    version="1.0.0"
)

# Modelos para estructurar el request
class Location(BaseModel):
    address: str

class DirectionsRequest(BaseModel):
    origin: Location
    destination: Location
    travelMode: str = "TRANSIT"

# Funciones para extraer y formatear la información de la ruta
def extract_route_info(route: dict) -> list:
    instructions = []
    for leg in route.get('legs', []):
        for step in leg.get('steps', []):
            try:
                instruction = {
                    "instructions": step['navigationInstruction']['instructions'],
                    "distance": step['localizedValues']['distance']['text'],
                    "duration": step['localizedValues']['staticDuration']['text'],
                    "travelMode": step['travelMode']
                }
                instructions.append(instruction)
            except KeyError:
                # Si alguna llave no se encuentra, saltamos ese paso.
                continue
    return instructions

def format_instructions(instructions: list) -> str:
    formatted_text = ""
    for instr in instructions:
        formatted_text += f"{instr['instructions']}\n"
        formatted_text += f"Distancia: {instr['distance']}, Duración: {instr['duration']}\n"
        formatted_text += f"Modo de transporte: {instr['travelMode']}\n\n"
    return formatted_text

@app.post("/computeRoutes", tags=["Direcciones"])
def compute_routes(directions: DirectionsRequest):
    """
    Endpoint que recibe los datos de origen y destino, consulta la API de Google Routes
    y retorna tanto la respuesta cruda como las instrucciones formateadas.
    """
    google_api_url = "https://routes.googleapis.com/directions/v2:computeRoutes"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,  # Reemplaza con tu API Key real
        "X-Goog-FieldMask": "routes.*"
    }
    payload = directions.dict()
    response = requests.post(google_api_url, headers=headers, json=payload)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    
    data = response.json()
    
    # Procesar la respuesta para extraer y formatear las instrucciones
    if "routes" in data and data["routes"]:
        route_info = extract_route_info(data["routes"][0])
        formatted_instructions = format_instructions(route_info)
    else:
        formatted_instructions = "No se encontraron rutas en la respuesta."
    
    return {
        "raw_response": data,
        "formatted_instructions": formatted_instructions
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)