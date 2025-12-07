from flask import Flask, render_template, request, redirect
from datetime import datetime
import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from flask import send_file
from io import BytesIO

app = Flask(__name__)

# Precios fijos
PRECIOS = {
    "Virgen": 12000,
    "Orgasmo": 13000,
    "Fantasía": 13000,
    "Placer": 13000,
    "Revolcón": 13000,
    "Sixnine": 13000,
    "Travesura": 13000,
    "Seducción": 15000,
    "Coco": 15000,
    "Alpinito": 15000
}

# Contador en memoria
ventas = {nombre: 0 for nombre in PRECIOS}

@app.route("/")
def index():
    total_vendidos = sum(ventas.values())
    ganancia = sum(ventas[nombre] * precio for nombre, precio in PRECIOS.items())
    return render_template("index.html", ventas=ventas, precios=PRECIOS,
                           total=total_vendidos, ganancia=ganancia)

@app.route("/modificar", methods=["POST"])
def modificar():
    nombre = request.form["nombre"]
    accion = request.form["accion"]
    if nombre in ventas:
        if accion == "sumar":
            ventas[nombre] += 1
        elif accion == "restar" and ventas[nombre] > 0:
            ventas[nombre] -= 1
    return redirect("/")

# @app.route("/guardar")
# def guardar():
#     fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     total = sum(ventas.values())
#     ganancia = sum(ventas[nombre] * PRECIOS[nombre] for nombre in PRECIOS)

#     archivo = "ventas.csv"
#     nuevo = False
#     try:
#         with open(archivo, "r", encoding="utf-8"):
#             pass
#     except FileNotFoundError:
#         nuevo = True

#     with open(archivo, "a", newline="", encoding="utf-8") as f:
#         writer = csv.writer(f)
#         if nuevo:
#             writer.writerow(["Fecha", *ventas.keys(), "Total", "Ganancia"])
#         writer.writerow([fecha, *ventas.values(), total, ganancia])

#     return redirect("/")

@app.route("/guardar")
def guardar():
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fecha_archivo = datetime.now().strftime("%Y%m%d_%H%M%S")

    total = sum(ventas.values())
    ganancia = sum(ventas[nombre] * PRECIOS[nombre] for nombre in PRECIOS)

    # -------------------------
    # GENERAR PDF EN MEMORIA
    # -------------------------
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)

    # Título
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, 750, "Reporte de Ventas - Granizados")

    # Fecha
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 720, f"Fecha de generación: {fecha}")

    # Encabezado tabla
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, 690, "Producto")
    pdf.drawString(250, 690, "Cantidad")
    pdf.drawString(350, 690, "Subtotal")

    pdf.line(50, 685, 500, 685)

    # Filas
    y = 660
    pdf.setFont("Helvetica", 12)

    for nombre, cantidad in ventas.items():
        if cantidad > 0:
            pdf.drawString(50, y, nombre)
            pdf.drawString(250, y, str(cantidad))
            pdf.drawString(350, y, f"${cantidad * PRECIOS[nombre]:,}")
            y -= 20

    # Totales
    y -= 20
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, f"Total Granizados: {total}")
    y -= 20
    pdf.drawString(50, y, f"Total Venta: ${ganancia:,}")

    pdf.save()

    buffer.seek(0)

    # -------------------------
    # ENVIAR PDF PARA DESCARGA
    # -------------------------
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"reporte_{fecha_archivo}.pdf",
        mimetype="application/pdf"
    )

@app.route("/reiniciar")
def reiniciar():
    for nombre in ventas:
        ventas[nombre] = 0
    return redirect("/")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
