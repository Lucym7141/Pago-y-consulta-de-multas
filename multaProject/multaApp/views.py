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
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

# Vista: Página principal (landing page)
def home(request):
    if request.user.is_authenticated:
        return redirect('user_dashboard')  # Si ya está logueado, va a su dashboard
    return render(request, "home.html")


# Vista: Registro de usuario (Signup)
def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        nombre_completo = request.POST.get('nombre_completo')
        documento = request.POST.get('documento')
        
        # Validaciones
        if password != password_confirm:
            messages.error(request, "Las contraseñas no coinciden")
            return render(request, "auth/signup.html")
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya está en uso")
            return render(request, "auth/signup.html")
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "El correo electrónico ya está registrado")
            return render(request, "auth/signup.html")
        
        # Crear usuario
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=nombre_completo
        )
        
        # Login automático después de registro
        login(request, user)
        messages.success(request, f"¡Bienvenido {nombre_completo}! Tu cuenta ha sido creada exitosamente.")
        return redirect('user_dashboard')
    
    return render(request, "auth/signup.html")


# Vista: Login de usuario
def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"¡Bienvenido de nuevo, {user.first_name or user.username}!")
            return redirect('user_dashboard')
        else:
            messages.error(request, "Usuario o contraseña incorrectos")
    
    return render(request, "auth/login.html")


# Vista: Logout
def user_logout(request):
    logout(request)
    messages.success(request, "Has cerrado sesión exitosamente")
    return redirect('home')


# Vista: Dashboard de usuario (solo para usuarios autenticados)
@login_required(login_url='user_login')
def user_dashboard(request):
    # Aquí mostrarás las multas del usuario
    user_multas = Multa.objects.filter(archivada=False)  # Por ahora todas
    
    return render(request, "user/dashboard.html", {
        "user_multas": user_multas
    })

# Vista pública: muestra el formulario de consulta
def consulta(request):
    return render(request, "public/consulta.html")


# Vista pública: muestra los resultados de la búsqueda por placa
# NO filtra por archivada, muestra TODAS las multas
def resultados_consulta(request):
    q = request.GET.get("q", "").strip().upper()
    resultados = Multa.objects.none()
    total_monto = 0
    pendientes_count = 0
    
    if q:
        # NO filtramos por archivada=False, mostramos todas
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


# Admin dashboard - SOLO muestra multas NO archivadas
# Admin dashboard - Muestra multas NO archivadas (accesible para usuarios autenticados)

# Vista: Dashboard de usuario (solo para usuarios autenticados)
@login_required(login_url='user_login')
def user_dashboard(request):
    # Solo multas del usuario actual
    user_multas = Multa.objects.filter(usuario=request.user, archivada=False)
    
    # Calcular estadísticas
    total_multas = user_multas.count()
    pendientes = user_multas.filter(estado="Pendiente").count()
    pagadas = user_multas.filter(estado="Pagada").count()
    total_a_pagar = user_multas.filter(estado="Pendiente").aggregate(total=Sum("valor"))["total"] or 0
    
    return render(request, "user/dashboard.html", {
        "user_multas": user_multas,
        "total_multas": total_multas,
        "pendientes": pendientes,
        "pagadas": pagadas,
        "total_a_pagar": total_a_pagar,
    })
@login_required(login_url='user_login')
def dashboard(request):
    filtro = request.GET.get("filtro", "todas")
    busqueda = request.GET.get("busqueda", "").strip()

    # Solo multas del usuario actual
    multas = Multa.objects.filter(usuario=request.user, archivada=False)

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

    # Resumen solo del usuario actual
    resumen = {
        "total": Multa.objects.filter(usuario=request.user, archivada=False).count(),
        "pendientes": Multa.objects.filter(usuario=request.user, archivada=False, estado="Pendiente").count(),
        "pagadas": Multa.objects.filter(usuario=request.user, archivada=False, estado="Pagada").count(),
        "recaudado": Multa.objects.filter(usuario=request.user, archivada=False, estado="Pagada").aggregate(total=Sum("valor"))["total"] or 0,
    }

    return render(request, "admin/dashboard.html", {
        "multas": multas,
        "resumen": resumen,
        "filtro": filtro,
        "busqueda": busqueda,
    })

# Descargar informe PDF de una multa específica
def descargar_informe_multa(request, id):
    multa = get_object_or_404(Multa, id=id)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Informe_Multa_{multa.numero_multa}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    
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
    
    title = Paragraph("INFORME DE MULTA DE TRÁNSITO", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.3*inch))
    
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
    
    nota = Paragraph(
        "<i>Este documento es un informe generado electrónicamente. "
        "Para más información contacte con las autoridades de tránsito correspondientes.</i>",
        styles['Normal']
    )
    elements.append(nota)
    
    doc.build(elements)
    return response


# Descargar informe general
def descargar_informe_general(request):
    filtro = request.GET.get("filtro", "todas")
    busqueda = request.GET.get("busqueda", "").strip()
    
    # Solo multas NO archivadas
    multas = Multa.objects.filter(archivada=False)
    
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
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Informe_Multas_{datetime.now().strftime("%Y%m%d")}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#2c5282'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    title = Paragraph("INFORME GENERAL DE MULTAS", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))
    
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


# Nueva función: "Eliminar" (archivar) multa del dashboard
def eliminar_multa(request, id):
    multa = get_object_or_404(Multa, id=id)
    if request.method == "POST":
        # No eliminamos, solo archivamos
        multa.archivada = True
        multa.save()
        messages.success(request, f"La multa {multa.numero_multa} ha sido archivada del historial.")
        return redirect("dashboard")
    return render(request, "admin/eliminar_confirm.html", {"multa": multa})