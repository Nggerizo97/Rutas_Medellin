import streamlit as st
import requests
from google import genai
from google.genai import types
import os

st.set_page_config(page_title="Ruti Metro", page_icon="🚀")

# Configurar el cliente de Google Gemini
client = genai.Client(api_key='API_KEY')  # Reemplaza con tu API key real

# Función para enviar el prompt a Gemini
def send_request_to_gemini(prompt):
    response = client.models.generate_content(
        model="gemma-3-27b-it",
        contents=[prompt],
        config=types.GenerateContentConfig(
            max_output_tokens=500,
            temperature=0.7,  # Un poco más alto para respuestas más creativas
            top_p=0.9
        )
    )
    return response.text  # Asumiendo que la respuesta tiene un atributo text

# Función para eliminar el texto <think>
def remove_think_text(text):
    start_tag = "<think>"
    end_tag = "</think>"
    start_index = text.find(start_tag)
    end_index = text.find(end_tag)
    
    if start_index != -1 and end_index != -1:
        # Eliminar el texto entre <think> y </think>
        text = text[:start_index] + text[end_index + len(end_tag):]
    
    return text

# Título de la aplicación
st.title("🤖 Asistente Virtual Ruti - Planificador de Rutas en Medellín")


# Campos de entrada para el origen y destino
origin = st.text_input("Origen (ej: Sabaneta, Parque sabaneta)", "")
destination = st.text_input("Destino (ej: Robledo, ITM Robledo)", "")

# Botón para calcular la ruta
if st.button("Calcular Ruta"):
    if origin and destination:
        # URL de la API de FastAPI
        api_url = "http://127.0.0.1:8000/computeRoutes"
        
        # Datos para enviar a la API
        payload = {
            "origin": {"address": origin},
            "destination": {"address": destination},
            "travelMode": "TRANSIT",
            "computeAlternativeRoutes": False,
            "transitPreferences": {
                "routingPreference": "LESS_WALKING",
                "allowedTravelModes": ["TRAIN"]
            }
        }
        
        # Encabezados de la solicitud
        headers = {
            "Content-Type": "application/json"
        }
        
        # Enviar la solicitud a la API
        response = requests.post(api_url, json=payload, headers=headers)
        
        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:
            data = response.json()
            formatted_instructions = data.get("formatted_instructions", "No se encontraron instrucciones.")
            
            # Crear el prompt para el asistente virtual
            prompt = f"""
            Eres un asistente virtual llamado Ruti que guía a las personas en la ciudad de Medellín. 
            Tu objetivo es proporcionar indicaciones claras y amigables para que los usuarios lleguen a su destino.
            
            Por favor, interpreta estas instrucciones técnicas y proporcióname una respuesta humanizada:
            
            Viaje desde {origin} hasta {destination}:
            {formatted_instructions}
            
            La respuesta debe ser:
            1. Amigable y cercana
            2. Dividida en pasos claros
            3. Incluir consejos útiles (como "lleve paraguas si va a llover")
            4. Ser positiva y alentadora
            """
            
            # Obtener la respuesta humanizada de Gemini
            try:
                gemini_response = send_request_to_gemini(prompt)
                
                # Eliminar el texto <think> si está presente
                humanized_response = remove_think_text(gemini_response)
                
                # Mostrar la respuesta humanizada
                st.subheader("Respuesta de Ruti")
                st.write(humanized_response)
                
                # Guardar la respuesta en un archivo Word (usando codificación utf-8)
                if not os.path.exists("informe"):
                    os.makedirs("informe")
                
                file_path = os.path.join("informe", "informe_ruti.txt")
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(humanized_response)
                st.success(f"El informe se ha guardado en: {file_path}")
                
            except Exception as e:
                st.error(f"Error al generar la respuesta humanizada: {e}")
        else:
            st.error(f"Error al calcular la ruta: {response.text}")
    else:
        st.warning("Por favor, ingresa un origen y un destino.")
        