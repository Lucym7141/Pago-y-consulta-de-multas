from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum, Q
from datetime import datetime
from django.contrib import messages
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from .models import Multa
from .forms import MultaForm


# Vista pública: muestra el formulario de consulta
def consulta(request):
    return render(request, "public/consulta.html")


# Vista pública: muestra los resultados de la búsqueda por placa
def resultados_consulta(request):
    q = request.GET.get("q", "").strip().upper()
    resultados = Multa.objects.none()
    total_monto = 0
    pendientes_count = 0
    
    if q:
        resultados = Multa.objects.filter(placa__icontains=q)
        total_monto = sum(multa.valor for multa in resultados)
        pendientes_count = resultados.filter(estado="Pendiente").count()
    
    return render(request, "public/resultados.html", {
        "resultados": resultados,
        "q": q,
        "total_monto": total_monto,
        "pendientes_count": pendientes_count,
    })


# Vista pública: procesar pago de multa
def pagar_multa(request, id):
    multa = get_object_or_404(Multa, id=id)
    
    # Si ya está pagada, redirigir
    if multa.estado == "Pagada":
        messages.info(request, f"La multa {multa.numero_multa} ya fue pagada anteriormente.")
        return redirect('resultados_consulta') + f'?q={multa.placa}'
    
    if request.method == "POST":
        # Aquí se procesaría el pago real (pasarela de pago, etc.)
        # Por ahora, simplemente marcamos como pagada
        
        multa.estado = "Pagada"
        multa.save()
        
        messages.success(request, f"✅ ¡Pago exitoso! La multa {multa.numero_multa} ha sido pagada correctamente.")
        return redirect('confirmacion_pago', id=multa.id)
    
    return render(request, "public/pagar_multa.html", {
        "multa": multa
    })


# Vista pública: confirmación de pago
def confirmacion_pago(request, id):
    multa = get_object_or_404(Multa, id=id)
    return render(request, "public/confirmacion_pago.html", {
        "multa": multa
    })


# Admin dashboard
def dashboard(request):
    filtro = request.GET.get("filtro", "todas")
    busqueda = request.GET.get("busqueda", "").strip()

    multas = Multa.objects.all()

    if busqueda:
        # Intentar detectar si es una fecha
        fecha_obj = None
        formatos_fecha = ['%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%Y/%m/%d']
        
        for formato in formatos_fecha:
            try:
                fecha_obj = datetime.strptime(busqueda, formato).date()
                break
            except ValueError:
                continue
        
        if fecha_obj:
            # Si es una fecha válida, buscar por fecha
            multas = multas.filter(fecha=fecha_obj)
        else:
            # Si no es fecha, buscar por placa, conductor, infracción, número de multa
            multas = multas.filter(
                Q(placa__icontains=busqueda) |
                Q(conductor__icontains=busqueda) |
                Q(infraccion__icontains=busqueda) |
                Q(numero_multa__icontains=busqueda)
            )

    if filtro == "pendientes":
        multas = multas.filter(estado="Pendiente")
    elif filtro == "pagadas":
        multas = multas.filter(estado="Pagada")

    resumen = {
        "total": Multa.objects.count(),
        "pendientes": Multa.objects.filter(estado="Pendiente").count(),
        "pagadas": Multa.objects.filter(estado="Pagada").count(),
        "recaudado": Multa.objects.filter(estado="Pagada").aggregate(total=Sum("valor"))["total"] or 0,
        "por_cobrar": Multa.objects.filter(estado="Pendiente").aggregate(total=Sum("valor"))["total"] or 0
    }

    return render(request, "admin/dashboard.html", {
        "multas": multas,
        "resumen": resumen,
        "filtro": filtro,
        "busqueda": busqueda,
    })


# Nueva función: Descargar informe PDF de una multa específica
def descargar_informe_multa(request, id):
    multa = get_object_or_404(Multa, id=id)
    
    # Crear respuesta HTTP con tipo PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Informe_Multa_{multa.numero_multa}.pdf"'
    
    # Crear documento PDF
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c5282'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2c5282'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Título
    title = Paragraph("INFORME DE MULTA DE TRÁNSITO", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.3*inch))
    
    # Información general
    info_general = Paragraph("<b>INFORMACIÓN GENERAL</b>", heading_style)
    elements.append(info_general)
    
    data_general = [
        ['Número de Multa:', multa.numero_multa or 'N/A'],
        ['Fecha de Emisión:', multa.fecha.strftime('%d/%m/%Y')],
        ['Estado:', multa.estado],
    ]
    
    table_general = Table(data_general, colWidths=[2*inch, 4*inch])
    table_general.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e2e8f0')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    elements.append(table_general)
    elements.append(Spacer(1, 0.3*inch))
    
    # Información del vehículo
    info_vehiculo = Paragraph("<b>INFORMACIÓN DEL VEHÍCULO</b>", heading_style)
    elements.append(info_vehiculo)
    
    data_vehiculo = [
        ['Placa:', multa.placa],
        ['Conductor:', multa.conductor or 'No registrado'],
        ['Documento:', multa.documento or 'No registrado'],
    ]
    
    table_vehiculo = Table(data_vehiculo, colWidths=[2*inch, 4*inch])
    table_vehiculo.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e2e8f0')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    elements.append(table_vehiculo)
    elements.append(Spacer(1, 0.3*inch))
    
    # Detalles de la infracción
    info_infraccion = Paragraph("<b>DETALLES DE LA INFRACCIÓN</b>", heading_style)
    elements.append(info_infraccion)
    
    data_infraccion = [
        ['Tipo de Infracción:', multa.infraccion],
        ['Código:', multa.codigo or 'N/A'],
        ['Valor de la Multa:', f'${multa.valor}'],
    ]
    
    table_infraccion = Table(data_infraccion, colWidths=[2*inch, 4*inch])
    table_infraccion.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e2e8f0')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    elements.append(table_infraccion)
    elements.append(Spacer(1, 0.5*inch))
    
    # Estado de pago
    if multa.estado == "Pagada":
        color_estado = colors.HexColor('#10b981')
        texto_estado = "✓ MULTA PAGADA"
    else:
        color_estado = colors.HexColor('#f59e0b')
        texto_estado = "⚠ MULTA PENDIENTE DE PAGO"
    
    estado_style = ParagraphStyle(
        'EstadoStyle',
        parent=styles['Normal'],
        fontSize=16,
        textColor=color_estado,
        alignment=TA_CENTER,
        spaceAfter=20,
        fontName='Helvetica-Bold'
    )
    
    estado = Paragraph(texto_estado, estado_style)
    elements.append(estado)
    elements.append(Spacer(1, 0.3*inch))
    
    # Nota al pie
    nota = Paragraph(
        "<i>Este documento es un informe generado electrónicamente. "
        "Para más información contacte con las autoridades de tránsito correspondientes.</i>",
        styles['Normal']
    )
    elements.append(nota)
    
    # Generar PDF
    doc.build(elements)
    return response


# Nueva función: Descargar informe general de todas las multas (para el dashboard)
def descargar_informe_general(request):
    filtro = request.GET.get("filtro", "todas")
    busqueda = request.GET.get("busqueda", "").strip()
    
    multas = Multa.objects.all()
    
    # Aplicar los mismos filtros del dashboard
    if busqueda:
        fecha_obj = None
        formatos_fecha = ['%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%Y/%m/%d']
        
        for formato in formatos_fecha:
            try:
                fecha_obj = datetime.strptime(busqueda, formato).date()
                break
            except ValueError:
                continue
        
        if fecha_obj:
            multas = multas.filter(fecha=fecha_obj)
        else:
            multas = multas.filter(
                Q(placa__icontains=busqueda) |
                Q(conductor__icontains=busqueda) |
                Q(infraccion__icontains=busqueda) |
                Q(numero_multa__icontains=busqueda)
            )
    
    if filtro == "pendientes":
        multas = multas.filter(estado="Pendiente")
    elif filtro == "pagadas":
        multas = multas.filter(estado="Pagada")
    
    # Crear respuesta HTTP
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Informe_Multas_{datetime.now().strftime("%Y%m%d")}.pdf"'
    
    # Crear documento
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#2c5282'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Título
    title = Paragraph("INFORME GENERAL DE MULTAS", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))
    
    # Resumen
    resumen_data = [
        ['Total de Multas:', str(multas.count())],
        ['Pendientes:', str(multas.filter(estado="Pendiente").count())],
        ['Pagadas:', str(multas.filter(estado="Pagada").count())],
        ['Total Recaudado:', f'${multas.filter(estado="Pagada").aggregate(total=Sum("valor"))["total"] or 0}'],
        ['Por Cobrar:', f'${multas.filter(estado="Pendiente").aggregate(total=Sum("valor"))["total"] or 0}'],
    ]
    
    table_resumen = Table(resumen_data, colWidths=[2.5*inch, 2*inch])
    table_resumen.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e2e8f0')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    elements.append(table_resumen)
    elements.append(Spacer(1, 0.3*inch))
    
    # Tabla de multas
    data = [['N° Multa', 'Placa', 'Infracción', 'Fecha', 'Valor', 'Estado']]
    
    for multa in multas:
        data.append([
            multa.numero_multa or 'N/A',
            multa.placa,
            multa.infraccion[:30] + '...' if len(multa.infraccion) > 30 else multa.infraccion,
            multa.fecha.strftime('%d/%m/%Y'),
            f'${multa.valor}',
            multa.estado
        ])
    
    table = Table(data, colWidths=[1*inch, 0.8*inch, 2*inch, 0.9*inch, 0.8*inch, 0.8*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    elements.append(table)
    
    # Generar PDF
    doc.build(elements)
    return response


# CRUD: crear / editar / eliminar
def crear_multa(request):
    form = MultaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("dashboard")
    return render(request, "admin/form_multa.html", {"form": form, "titulo": "Crear Multa"})


def editar_multa(request, id):
    multa = get_object_or_404(Multa, id=id)
    form = MultaForm(request.POST or None, instance=multa)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("dashboard")
    return render(request, "admin/form_multa.html", {"form": form, "titulo": "Editar Multa"})


def eliminar_multa(request, id):
    multa = get_object_or_404(Multa, id=id)
    if request.method == "POST":
        multa.delete()
        return redirect("dashboard")
    return render(request, "admin/eliminar_confirm.html", {"multa": multa})