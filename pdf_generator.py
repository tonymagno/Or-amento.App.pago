# pdf_generator.py

from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def gerar_pdf_bytes(cliente, negocio, itens, subtotal, desconto, taxa_extra, total):
    """
    Gera um PDF de orçamento com ReportLab e retorna como BytesIO.
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    x, y = 50, 800
    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawString(x, y, "ORÇAMENTO PREMIUM")
    y -= 30
    c.setFont("Helvetica", 12)
    # Informações de cliente e negócio
    c.drawString(x, y, f"Cliente: {cliente}")
    y -= 20
    c.drawString(x, y, f"Negócio: {negocio}")
    y -= 30
    # Lista de serviços
    c.drawString(x, y, "Serviços:")
    y -= 20
    for i, item in enumerate(itens, start=1):
        total_item = item["quantidade"] * item["preco_unitario"]
        line = f"{i}. {item['servico']} | Qtd: {item['quantidade']} | R$ {total_item:.2f}"
        c.drawString(x+10, y, line)
        y -= 20
        if y < 100:  # página cheia, cria nova
            c.showPage()
            c.setFont("Helvetica", 12)
            y = 800
    # Subtotais e total
    y -= 10
    c.drawString(x, y, f"Subtotal: R$ {subtotal:.2f}")
    y -= 20
    c.drawString(x, y, f"Desconto: R$ {desconto:.2f}")
    y -= 20
    c.drawString(x, y, f"Taxa extra: R$ {taxa_extra:.2f}")
    y -= 25
    c.setFont("Helvetica-Bold", 14)
    c.drawString(x, y, f"TOTAL: R$ {total:.2f}")
    # Finaliza o PDF
    c.save()
    buffer.seek(0)
    return buffer
