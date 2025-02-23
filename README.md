# Rutas_Medellin
Se  buscar solucionar una problematica social sobre el uso de transporte publico en la ciudad de medellin. Con el uso de herramientas como chatbots, se busca brindar informacion clara y precisa sobre las diferentes rutas para llegar desde un punto B a un punto A con respuestas dinamicas


chatbot-metro-medellin/
│
├── data/                         # Carpeta para almacenar datos
│   ├── raw/                      # Datos crudos (por ejemplo, tweets extraídos)
│   │   └── comentarios_twitter.csv
│   ├── processed/                # Datos procesados (limpios y listos para entrenamiento)
│   │   └── comentarios_limpios.csv
│   └── embeddings/               # Embeddings precalculados (si es necesario)
│       └── embeddings_model.pkl
│
├── models/                       # Modelos entrenados
│   ├── lm_model/                 # Modelo de lenguaje (por ejemplo, fine-tuned GPT)
│   │   └── pytorch_model.bin
│   └── intent_classifier/        # Clasificador de intenciones (opcional)
│       └── intent_model.pkl
│
├── notebooks/                    # Jupyter Notebooks para exploración y experimentación
│   ├── 01_data_exploration.ipynb
│   ├── 02_model_training.ipynb
│   └── 03_chatbot_testing.ipynb
│
├── src/                          # Código fuente del proyecto
│   ├── data_processing/          # Scripts para procesar datos
│   │   └── clean_data.py
│   ├── model_training/           # Scripts para entrenar modelos
│   │   └── train_lm.py
│   ├── chatbot/                  # Lógica del chatbot
│   │   ├── chatbot.py
│   │   └── response_generator.py
│   └── utils/                    # Utilidades generales
│       └── helpers.py
│
├── tests/                        # Pruebas unitarias
│   ├── test_data_processing.py
│   └── test_chatbot.py
│
├── requirements.txt              # Dependencias del proyecto
├── README.md                     # Documentación del proyecto
└── app.py                        # Punto de entrada para la aplicación del chatbot