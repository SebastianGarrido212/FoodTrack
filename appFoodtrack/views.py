from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Donacion, Donador
import json
from appFoodtrack.models import Usuario, Donador, Organizacion, HistorialTransacciones

# =====================================================
# VISTA: MENÚ INICIAL / PÁGINA PRINCIPAL
# =====================================================
def inicio(request):
    return render(request, 'templatesApp/Inicio.html')


# =====================================================
# VISTA: INICIO DE SESIÓN
# =====================================================
@csrf_exempt
@require_http_methods(["GET", "POST"])
def inicioSesion(request):
    """
    Maneja el login de usuarios
    GET: Renderiza el formulario
    POST: Procesa el login
    """
    if request.method == 'GET':
        return render(request, 'templatesApp/IniciarSesion.html')
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            remember = data.get('remember', False)
            
            # Validaciones
            if not email or not password:
                return JsonResponse({
                    'success': False,
                    'message': 'Email y contraseña son requeridos'
                }, status=400)
            
            # Buscar usuario
            try:
                usuario = Usuario.objects.get(email=email)
            except Usuario.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Usuario o contraseña incorrectos'
                }, status=401)
            
            # Verificar contraseña
            if not check_password(password, usuario.password):
                return JsonResponse({
                    'success': False,
                    'message': 'Usuario o contraseña incorrectos'
                }, status=401)
            
            # Verificar que usuario esté activo
            if not usuario.activo:
                return JsonResponse({
                    'success': False,
                    'message': 'Usuario inactivo'
                }, status=403)
            
            # Registrar en historial
            HistorialTransacciones.objects.create(
                usuario=usuario,
                tipo_accion='login',
                descripcion=f'Inicio de sesión - {email}'
            )
            
            # Crear sesión
            request.session['usuario_id'] = usuario.id
            request.session['usuario_email'] = usuario.email
            request.session['usuario_tipo'] = usuario.tipo_usuario
            
            if remember:
                request.session.set_expiry(7 * 24 * 60 * 60)  # 7 días
            
            return JsonResponse({
                'success': True,
                'message': 'Sesión iniciada correctamente',
                'usuario': {
                    'id': usuario.id,
                    'nombre': usuario.nombre,
                    'apellido': usuario.apellido,
                    'email': usuario.email,
                    'tipo': usuario.tipo_usuario
                }
            }, status=200)
        
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Datos inválidos'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error en el servidor: {str(e)}'
            }, status=500)


# =====================================================
# VISTA: CREAR USUARIO (REGISTRO)
# =====================================================

@csrf_exempt
@require_http_methods(["GET", "POST"])
def crearUsuario(request):
    """
    Maneja el registro de nuevos usuarios
    GET: Renderiza el formulario
    POST: Crea un nuevo usuario (donador u organización)
    """
    if request.method == 'GET':
        return render(request, 'templatesApp/CrearUsuario.html')
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            tipo_usuario = data.get('type')
            password = data.get('password')

            # Hacemos la vista más inteligente:
            # Primero, determinamos de dónde sacar los datos según el tipo de usuario
            if tipo_usuario == 'donor':
                email = data.get('email')
                nombre = data.get('firstName')
                apellido = data.get('lastName')
                telefono = data.get('phone')
            elif tipo_usuario == 'organization':
                # Para la organización, usamos los nombres de campos correctos
                email = data.get('orgEmail')
                nombre = data.get('orgFirstName')
                apellido = data.get('orgLastName')
                telefono = data.get('orgPhone')
            else:
                return JsonResponse({'success': False, 'message': 'Tipo de usuario no válido'}, status=400)

            # Validaciones comunes
            if not all([email, password, nombre, apellido, tipo_usuario]):
                return JsonResponse({'success': False, 'message': 'Faltan campos requeridos'}, status=400)
            
            if Usuario.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'message': 'El email ya está registrado'}, status=400)
            
            if len(password) < 8:
                return JsonResponse({'success': False, 'message': 'La contraseña debe tener al menos 8 caracteres'}, status=400)
            
            # Crear el objeto Usuario base
            usuario = Usuario.objects.create(
                email=email,
                password=make_password(password),
                nombre=nombre,
                apellido=apellido,
                telefono=telefono,
                tipo_usuario='donador' if tipo_usuario == 'donor' else 'organizacion',
                activo=True
            )
            
            # Crear el perfil específico
            if tipo_usuario == 'donor':
                Donador.objects.create(
                    usuario=usuario,
                    nombre_negocio=data.get('businessName'),
                    tipo_donador=data.get('donationType'),
                    ciudad=data.get('city')
                )
            
            elif tipo_usuario == 'organization':
                Organizacion.objects.create(
                    usuario=usuario,
                    nombre_organizacion=data.get('orgName'),
                    tipo_organizacion=data.get('orgType'),
                    ciudad=data.get('orgCity'),
                    descripcion=data.get('description')
                )
            
            HistorialTransacciones.objects.create(
                usuario=usuario,
                tipo_accion='crear_usuario',
                descripcion=f'Nuevo usuario registrado - {email}'
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Usuario creado exitosamente',
                'usuario': {
                    'id': usuario.id,
                    'nombre': usuario.nombre,
                    'email': usuario.email,
                    'tipo': usuario.tipo_usuario
                }
            }, status=201)
        
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Datos inválidos'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error en el servidor: {str(e)}'}, status=500)
# =====================================================
# VISTA: LOGOUT
# =====================================================
def logout(request):
    """Cierra la sesión del usuario"""
    if 'usuario_id' in request.session:
        try:
            usuario = Usuario.objects.get(id=request.session['usuario_id'])
            HistorialTransacciones.objects.create(
                usuario=usuario,
                tipo_accion='logout',
                descripcion=f'Cierre de sesión - {usuario.email}'
            )
        except Usuario.DoesNotExist:
            pass
    
    request.session.flush()
    return redirect('templatesApp/Inicio.html')


# =====================================================
# VISTA: DASHBOARD
# =====================================================

def dashboard(request):
    """Dashboard del usuario logueado"""
    if 'usuario_id' not in request.session:
        return redirect('inicioSesion')
    
    try:
        usuario = Usuario.objects.get(id=request.session['usuario_id'])
        context = {'usuario': usuario}
        
        if usuario.tipo_usuario == 'donador':
            perfil = Donador.objects.get(usuario=usuario)
            context['perfil'] = perfil
            
            # --- LÍNEA CLAVE AQUÍ ---
            # Buscamos las últimas 5 donaciones y las añadimos al contexto.
            ultimas_donaciones = Donacion.objects.filter(donador=perfil).order_by('-fecha_creacion')[:5]
            context['ultimas_donaciones'] = ultimas_donaciones

        elif usuario.tipo_usuario == 'organizacion':
            perfil = Organizacion.objects.get(usuario=usuario)
            context['perfil'] = perfil
            donaciones_disponibles = Donacion.objects.filter(estado='pendiente').order_by('-fecha_creacion')[:5]
            context['donaciones_disponibles'] = donaciones_disponibles
            
        return render(request, 'templatesApp/dashboard.html', context)
        
    except (Usuario.DoesNotExist, Donador.DoesNotExist, Organizacion.DoesNotExist):
        request.session.flush()
        return redirect('inicioSesion')
    

# =====================================================
# VISTA: CREAR UNA NUEVA DONACIÓN
# =====================================================
def crear_donacion(request):
    # Primero, verificamos que el usuario haya iniciado sesión
    if 'usuario_id' not in request.session:
        return redirect('inicioSesion')

    # Verificamos que el usuario sea un donador
    try:
        usuario = Usuario.objects.get(id=request.session['usuario_id'])
        if usuario.tipo_usuario != 'donador':
            # Si no es donador, no debería estar aquí. Lo mandamos a su dashboard.
            return redirect('dashboard')
        
        # Buscamos el perfil del donador para asociarlo a la donación
        donador = Donador.objects.get(usuario=usuario)
    except (Usuario.DoesNotExist, Donador.DoesNotExist):
        # Si hay algún problema, cerramos sesión por seguridad
        request.session.flush()
        return redirect('inicioSesion')


    # Si el método es POST, significa que el usuario envió el formulario
    if request.method == 'POST':
        # Obtenemos los datos del formulario
        tipo_alimento = request.POST.get('tipo_alimento')
        cantidad = request.POST.get('cantidad')
        unidad = request.POST.get('unidad_medida')
        vencimiento = request.POST.get('fecha_vencimiento')
        descripcion = request.POST.get('descripcion')

        # Creamos la donación en la base de datos
        Donacion.objects.create(
            donador=donador,
            tipo_alimento=tipo_alimento,
            cantidad=cantidad,
            unidad_medida=unidad,
            fecha_vencimiento=vencimiento if vencimiento else None,
            descripcion=descripcion,
            estado='pendiente' # El estado inicial es siempre pendiente
        )
        
        # Redirigimos al usuario a su dashboard después de crear la donación
        return redirect('dashboard')

    # Si el método es GET, solo mostramos la página con el formulario
    # Pasamos las opciones de 'unidad_medida' desde el modelo para usarlas en el HTML
    context = {
        'unidades': Donacion.UNIDAD_MEDIDA_CHOICES
    }
    return render(request, 'templatesApp/crearDonacion.html', context)

# =====================================================
# VISTA: VER EL HISTORIAL DE DONACIONES DE UN DONADOR
# =====================================================
def ver_donaciones(request):
    # Verificamos que el usuario haya iniciado sesión y sea un donador
    if 'usuario_id' not in request.session:
        return redirect('inicioSesion')

    try:
        usuario = Usuario.objects.get(id=request.session['usuario_id'])
        if usuario.tipo_usuario != 'donador':
            return redirect('dashboard')
        
        donador = Donador.objects.get(usuario=usuario)
    except (Usuario.DoesNotExist, Donador.DoesNotExist):
        request.session.flush()
        return redirect('inicioSesion')

    # Esta es la línea clave:
    # Filtramos todas las donaciones para obtener solo las del donador actual
    # y las ordenamos por fecha, de la más nueva a la más antigua.
    donaciones = Donacion.objects.filter(donador=donador).order_by('-fecha_creacion')

    # Preparamos los datos para enviarlos a la plantilla
    context = {
        'donaciones': donaciones
    }
    
    # Renderizamos la nueva plantilla que crearemos a continuación
    return render(request, 'templatesApp/verDonaciones.html', context)

# =====================================================
# VISTA: EDITAR UNA DONACIÓN EXISTENTE
# =====================================================
def editar_donacion(request, donacion_id):
    # Usamos get_object_or_404 para obtener la donación. Si no existe, dará un error 404.
    donacion = get_object_or_404(Donacion, id=donacion_id)

    # Verificamos que el usuario sea el dueño de la donación y que esté pendiente
    if 'usuario_id' not in request.session or donacion.donador.usuario.id != request.session['usuario_id']:
        return redirect('inicioSesion') # No es su donación, fuera.
    if donacion.estado != 'pendiente':
        return redirect('verDonaciones') # No se puede editar si ya no está pendiente.

    if request.method == 'POST':
        # Si el formulario se envía, actualizamos los campos del objeto 'donacion'
        donacion.tipo_alimento = request.POST.get('tipo_alimento')
        donacion.cantidad = request.POST.get('cantidad')
        donacion.unidad_medida = request.POST.get('unidad_medida')
        donacion.fecha_vencimiento = request.POST.get('fecha_vencimiento') if request.POST.get('fecha_vencimiento') else None
        donacion.descripcion = request.POST.get('descripcion')
        donacion.save() # Guardamos los cambios en la base de datos
        return redirect('verDonaciones')

    # Si es GET, mostramos el formulario pre-cargado con los datos de la donación
    context = {
        'unidades': Donacion.UNIDAD_MEDIDA_CHOICES,
        'donacion': donacion # Pasamos el objeto donación a la plantilla
    }
    # Reutilizaremos la misma plantilla de creación, ¡muy eficiente!
    return render(request, 'templatesApp/editar_donacion.html', context)


# =====================================================
# VISTA: CANCELAR UNA DONACIÓN
# =====================================================
def cancelar_donacion(request, donacion_id):
    donacion = get_object_or_404(Donacion, id=donacion_id)

    # Verificamos seguridad: que sea el dueño y que esté pendiente
    if 'usuario_id' not in request.session or donacion.donador.usuario.id != request.session['usuario_id']:
        return redirect('inicioSesion')
    if donacion.estado != 'pendiente':
        return redirect('verDonaciones')

    # En lugar de borrarla (lo cual es destructivo), cambiamos su estado.
    donacion.estado = 'cancelada'
    donacion.save()

    return redirect('verDonaciones')

# =====================================================
# VISTA: VER TODAS LAS DONACIONES DISPONIBLES (PARA ORGANIZACIONES)
# =====================================================
def ver_donaciones_disponibles(request):
    # Verificamos que el usuario haya iniciado sesión y sea una organización
    if 'usuario_id' not in request.session:
        return redirect('inicioSesion')

    try:
        usuario = Usuario.objects.get(id=request.session['usuario_id'])
        if usuario.tipo_usuario != 'organizacion':
            # Si no es una organización, no debería estar aquí.
            return redirect('dashboard')
    except Usuario.DoesNotExist:
        request.session.flush()
        return redirect('inicioSesion')

    # Buscamos todas las donaciones con estado 'pendiente'
    donaciones = Donacion.objects.filter(estado='pendiente').order_by('-fecha_creacion')

    context = {
        'donaciones': donaciones
    }
    
    # Renderizamos la nueva plantilla que crearemos a continuación
    return render(request, 'templatesApp/donaciones_disponibles.html', context)