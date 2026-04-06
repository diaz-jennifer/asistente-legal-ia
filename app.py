# app.py

from flask import Flask, render_template, request, send_file, jsonify
from rag_engine import ask_question
from pdf_generator import save_answer_to_pdf, save_report_to_pdf
import requests
import json

app = Flask(__name__)

# Historial en memoria (se resetea al reiniciar el servidor)
historial = []


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    question = request.form["question"]
    answer = ask_question(question)
    return jsonify({"answer": answer})


# ── OPCIÓN 1: PDF de la respuesta actual ──────────────────────
@app.route("/generate_pdf", methods=["POST"])
def generate_pdf():
    answer   = request.form["answer"]
    question = request.form.get("question", "")
    pdf_path = save_answer_to_pdf(answer, question)
    return send_file(pdf_path, as_attachment=True)


# ── HISTORIAL ─────────────────────────────────────────────────
@app.route("/save_to_history", methods=["POST"])
def save_to_history():
    data = request.get_json()
    historial.append({
        "question": data.get("question", ""),
        "answer":   data.get("answer", "")
    })
    return jsonify({"count": len(historial)})


@app.route("/get_history", methods=["GET"])
def get_history():
    return jsonify(historial)


@app.route("/remove_from_history", methods=["POST"])
def remove_from_history():
    idx = request.get_json().get("index")
    if idx is not None and 0 <= idx < len(historial):
        historial.pop(idx)
    return jsonify({"count": len(historial)})


@app.route("/clear_history", methods=["POST"])
def clear_history():
    historial.clear()
    return jsonify({"count": 0})


# ── OPCIÓN 2: INFORME FINAL con Ollama ────────────────────────
@app.route("/generate_report", methods=["POST"])
def generate_report():
    if not historial:
        return jsonify({"error": "El historial está vacío."}), 400

    # Construir el contexto para Ollama
    bloques = []
    for i, item in enumerate(historial, 1):
        bloques.append(f"--- Consulta {i} ---\nPregunta: {item['question']}\nRespuesta: {item['answer']}")

    contexto = "\n\n".join(bloques)

    prompt = (
        "Eres un asistente jurídico experto en legislación española y europea. "
        "A partir de las siguientes consultas y respuestas, redacta un informe legal "
        "estructurado, claro y profesional. "
        "Organiza el informe con una introducción, los puntos principales agrupados por tema "
        "y una conclusión. "
        "Cita SOLO artículos y reglamentos (ejemplo: Artículo 17 RGPD, Art. 18.4 CE). "
        "NO menciones números de página ni nombres de archivo. "
        "Responde SOLO con el texto del informe, sin comentarios adicionales.\n\n"
        f"{contexto}"
    )

    print("Generando informe con Ollama…")
    try:
        # stream=True para evitar timeout en respuestas largas
        resp = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "gemma3:4b",
                "messages": [{"role": "user", "content": prompt}],
                "stream": True
            },
            timeout=600,
            stream=True
        )
        resp.raise_for_status()

        informe_texto = ""
        for line in resp.iter_lines():
            if line:
                chunk = json.loads(line)
                informe_texto += chunk.get("message", {}).get("content", "")
                if chunk.get("done"):
                    break

    except Exception as e:
        print("Error llamando a Ollama:", e)
        return jsonify({"error": str(e)}), 500

    pdf_path = save_report_to_pdf(informe_texto, historial)
    return send_file(pdf_path, as_attachment=True)


if __name__ == "__main__":
    print("✅ Servidor listo. Abre http://localhost:5000 en tu navegador.")
    app.run(debug=False)