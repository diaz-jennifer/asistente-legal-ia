#load_pdfs.py
import os
from llama_index.core import SimpleDirectoryReader

def load_documents(pdf_folder="leyesIA"):
    """
    Carga todos los documentos PDF de la carpeta indicada.
    
    Args:
        pdf_folder: nombre de la carpeta relativa al directorio de ejecución.
                    Por defecto 'leyesIA'.
    
    Returns:
        Lista de documentos cargados por LlamaIndex.
    """
    # Construir la ruta absoluta para evitar errores según desde dónde se ejecute
    pdf_path = os.path.join(os.getcwd(), pdf_folder)
    print(f"Cargando PDFs desde: {pdf_path}")

    # SimpleDirectoryReader lee automáticamente todos los archivos de la carpeta
    # y los convierte al formato Document que usa LlamaIndex internamente
    documents = SimpleDirectoryReader(pdf_path).load_data()
    print(f"Documentos cargados: {len(documents)}")

    return documents