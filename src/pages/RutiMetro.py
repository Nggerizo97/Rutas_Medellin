# streamlit_page: "Nombre Personalizado" 🏠

import streamlit as st
import os
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

from dotenv import load_dotenv

from langchain_community.document_loaders import JSONLoader


load_dotenv()

st.title("MetroBot 🚆 - Tu asistente del Metro de Medellín")
st.write("Haz una pregunta sobre rutas y servicios del Metro de Medellín")

loader = JSONLoader(
    file_path=r'C:\Users\cuent\Desktop\Rutas_Medellin\data\datos.jsonl',
    jq_schema='.contenido', # Extrae el valor de la clave 'contenido'
    text_content=True, # Asegura que el resultado sea el texto directamente
    json_lines=True     # ¡Importante para formato .jsonl!
    )

documentos_texto = loader.load()

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

vectorstore = FAISS.from_documents(documentos_texto, embeddings)


retriever = vectorstore.as_retriever(search_kwargs={'k': 1}) # 'k' es el número de documentos a recuperar

# --- 4. Definir el Prompt Template ---
# Este template guiará al LLM sobre cómo usar el contexto recuperado
template = """
Eres un asistente virtual amable y servicial del Metro de Medellín. Tu nombre es MetroBot.
Responde la pregunta del usuario basándote únicamente en el siguiente contexto recuperado de tu base de datos de rutas.
Adopta un tono similar al de los ejemplos del contexto (usa emojis si es apropiado, sé claro con las instrucciones).
Si el contexto no contiene la información para responder la pregunta, di amablemente que no tienes esa ruta específica en tu información actual.

Contexto Recuperado:
{context}

Pregunta del Usuario:
{question}

Tu Respuesta:
"""
prompt = ChatPromptTemplate.from_template(template)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.3,
    max_tokens=3000,
    timeout=None,
    max_retries=2,
    # other params...
)

rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()} # Pasa la pregunta y recupera contexto
    | prompt                                               # Llena el prompt con contexto y pregunta
    | llm                                                  # Pasa el prompt al LLM
    | StrOutputParser()                                    # Parsea la salida del LLM a string
)

# while True:
#     pregunta_usuario = input("\nTu pregunta: ")
#     if pregunta_usuario.lower() == 'salir':
#         break

#     # Invocar la cadena RAG con la pregunta
#     print("Generando respuesta...")
#     respuesta = rag_chain.invoke(pregunta_usuario)

#     print("\nMetroBot:", respuesta)

# print("\n¡Hasta luego!")
# Interfaz de usuario con Streamlit
pregunta_usuario = st.text_input("Escribe tu pregunta aquí:")
if st.button("Preguntar") and pregunta_usuario:
    st.write("Generando respuesta...")
    respuesta = rag_chain.invoke(pregunta_usuario)
    st.subheader("MetroBot:")
    st.write(respuesta)