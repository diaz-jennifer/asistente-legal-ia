# Asistente Legal IA — Proyecto académico con arquitectura RAG

Este proyecto implementa un asistente legal basado en RAG (Retrieval-Augmented Generation) capaz de responder preguntas en lenguaje natural a partir de legislación española y europea. Desarrollado como proyecto académico, integra un backend en Flask, un motor RAG con LlamaIndex y Qdrant, generación de respuestas con modelos locales (Ollama) y creación de informes en PDF con portada generada por IA (Flux). El objetivo principal es explorar arquitecturas RAG completas, desde la ingesta de documentos hasta la generación final de respuestas fundamentadas.


## ¿Qué hace?

- Responde preguntas legales consultando directamente los PDFs de las leyes cargadas
- Mantiene un historial de conversación estilo chat
- Permite guardar respuestas seleccionadas y generar un informe legal final redactado por IA
- Exporta las respuestas y el informe final a PDF, con portada generada por Flux

## Documentos incluidos

- Constitución Española (BOE-A-1978-31229)
- Reglamento General de Protección de Datos — RGPD (UE) 2016/679
- Ley Orgánica de Protección de Datos — LOPDGDD (BOE-A-2018-16673)
- Reglamento de Inteligencia Artificial (UE) 2024/1689
- Versión consolidada del Tratado de la Unión Europea
- Ley de Procedimiento Administrativo (BOE-A-2015-10565)

## Tecnologías utilizadas

| Componente | Tecnología |
|---|---|
| Interfaz web | Flask + HTML/CSS/JS |
| Extracción y carga de PDFs | LlamaIndex (`SimpleDirectoryReader`) |
| Embeddings semánticos | HuggingFace `sentence-transformers/all-MiniLM-L6-v2` |
| Base de datos vectorial | Qdrant (en memoria) |
| Modelo de lenguaje | Ollama (`gemma3:4b`) |
| Generación de imágenes | Flux (`flux-klein-4b`) |
| Generación de PDFs | fpdf2 |

## Requisitos previos

- Python 3.10 o superior
- [Ollama](https://ollama.com) instalado y en ejecución con el modelo `gemma3:4b`:
  ```bash
  ollama pull gemma3:4b
  ```
- [Flux](https://github.com/leejet/stable-diffusion.cpp) compilado en local (opcional, para la portada del informe)

## Instalación

```bash
# Clonar o descargar el proyecto
cd proyectoLeyesIA

# Crear y activar entorno virtual (recomendado)
python -m venv IAenv
source IAenv/bin/activate  # Linux/WSL

# Instalar dependencias
pip install -r requirements.txt
```

## Dependencias Python

```
flask
llama-index
llama-index-llms-ollama
llama-index-embeddings-huggingface
llama-index-vector-stores-qdrant
qdrant-client
sentence-transformers
fpdf2
pymupdf
requests
```

## Estructura del proyecto

```
proyectoLeyesIA/
├── app.py              # Servidor Flask y rutas
├── rag_engine.py       # Motor RAG: carga de PDFs, embeddings e índice Qdrant
├── pdf_generator.py    # Generación de PDFs con fpdf2 y portada Flux
├── load_pdfs.py        # Utilidad de carga de documentos
├── requirements.txt
├── README.md
├── leyesIA/            # PDFs de las leyes (no incluidos en el repositorio)
└── templates/
    └── index.html      # Interfaz de usuario
```

## Uso

```bash
python app.py
```

Al arrancar, el sistema carga los PDFs, genera los embeddings y construye el índice vectorial. Cuando aparezca el mensaje `Servidor listo`, abrir el navegador en:

```
http://localhost:5000
```

## Notas

- La primera vez que se ejecuta se descarga automáticamente el modelo de embeddings (~90 MB).
- La portada del informe se genera con Flux la primera vez y se reutiliza en ejecuciones posteriores. Si Flux no está disponible, el PDF se genera igualmente sin imagen.
- El historial de conversación se mantiene en memoria y se resetea al reiniciar el servidor.
