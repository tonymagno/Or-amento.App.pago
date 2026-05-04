# pdf_generator.py

from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def gerar_pdf_bytes(cliente, negocio, itens, subtotal, desconto, taxa_extra, total):
    """
    Gera um PDF de orçamento em memória e retorna como BytesIO.
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    text = c.beginText(40, 800)
    text.setFont("Helvetica", 12)
    text.textLine("ORÇAMENTO PREMIUM")
    text.textLine("")
    text.textLine(f"Cliente: {cliente}")
    text.textLine(f"Negócio: {negocio}")
    text.textLine("")
    text.textLine("Serviços:")
    for item in itens:
        total_item = item["quantidade"] * item["preco_unitario"]
        text.textLine(f"- {item['servico']} | Qtd: {item['quantidade']} | R$ {total_item:.2f}")
    text.textLine("")
    text.textLine(f"Subtotal: R$ {subtotal:.2f}")
    text.textLine(f"Desconto: R$ {desconto:.2f}")
    text.textLine(f"Taxa extra: R$ {taxa_extra:.2f}")
    text.textLine(f"TOTAL: R$ {total:.2f}")
    c.drawText(text)
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
