# rag_engine.py

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, StorageContext
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.prompts import PromptTemplate
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.vector_stores.qdrant import QdrantVectorStore
import qdrant_client
import warnings
import logging

warnings.filterwarnings("ignore")
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
# ---------------------------------------------------
# CONFIGURACIÓN DEL MODELO
# ---------------------------------------------------
Settings.llm = Ollama(
    model="gemma3:4b",        
    request_timeout=300
)

Settings.embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# ---------------------------------------------------
# PROMPT LEGAL
# ---------------------------------------------------
SYSTEM_PROMPT = (
    "Eres un asistente jurídico especializado en legislación española y europea.\n"
    "Responde en español de forma clara y detallada basándote en el contexto proporcionado.\n"
    "Si el contexto contiene información relevante, úsala y cita los artículos cuando aparezcan.\n"
    "Si el contexto no es suficiente, responde con lo que puedas extraer de él.\n\n"
    "Contexto:\n{context_str}\n\n"
    "Pregunta:\n{query_str}\n"
)

prompt_template = PromptTemplate(SYSTEM_PROMPT)

# ---------------------------------------------------
# CARGA DE DOCUMENTOS
# ---------------------------------------------------
def load_documents(pdf_folder="leyesIA"):
    print(f"Cargando documentos desde: {pdf_folder}")
    documents = SimpleDirectoryReader(pdf_folder).load_data()
    print(f"Documentos cargados: {len(documents)}")

    parser = SimpleNodeParser.from_defaults(
        chunk_size=256,     # chunks pequeños → menos RAM
        chunk_overlap=30
    )
    nodes = parser.get_nodes_from_documents(documents)
    print(f"Chunks generados: {len(nodes)}")
    return nodes

# ---------------------------------------------------
# QDRANT: cliente en memoria (no necesita servidor aparte)
# Para persistir en disco cambia a:
#   client = qdrant_client.QdrantClient(path="./qdrant_storage")
# ---------------------------------------------------
def build_index():
    nodes = load_documents()

    print("Conectando con Qdrant...")
    client = qdrant_client.QdrantClient(location=":memory:")

    vector_store = QdrantVectorStore(
        client=client,
        collection_name="leyes_espana"
    )

    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    print("Construyendo índice vectorial con Qdrant...")
    index = VectorStoreIndex(
        nodes,
        storage_context=storage_context,
    )

    print("Índice creado correctamente.")
    return index

# ---------------------------------------------------
# MOTOR DE CONSULTA
# Usamos "compact" en lugar de "tree_summarize":
#   - tree_summarize hace N llamadas al LLM → mucha RAM
#   - compact hace 1 sola llamada → mucho más ligero
# ---------------------------------------------------
print("Inicializando el motor RAG...")
index = build_index()

query_engine = index.as_query_engine(
    text_qa_template=prompt_template,
    similarity_top_k=4,
    response_mode="compact"   # evita el error de memoria
)


def ask_question(question):
    print(f"Pregunta recibida: {question}")
    response = query_engine.query(question)
    return str(response)