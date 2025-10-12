# foodtrack/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
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
            tipo_usuario = data.get('type')  # 'donor' o 'organization'
            
            # Validaciones comunes
            email = data.get('email')
            password = data.get('password')
            nombre = data.get('firstName')
            apellido = data.get('lastName')
            telefono = data.get('phone')
            
            if not all([email, password, nombre, apellido, tipo_usuario]):
                return JsonResponse({
                    'success': False,
                    'message': 'Campos requeridos faltando'
                }, status=400)
            
            # Verificar que el email no exista
            if Usuario.objects.filter(email=email).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'El email ya está registrado'
                }, status=400)
            
            # Validar contraseña
            if len(password) < 8:
                return JsonResponse({
                    'success': False,
                    'message': 'La contraseña debe tener al menos 8 caracteres'
                }, status=400)
            
            # Crear usuario
            usuario = Usuario.objects.create(
                email=email,
                password=make_password(password),
                nombre=nombre,
                apellido=apellido,
                telefono=telefono,
                tipo_usuario='donador' if tipo_usuario == 'donor' else 'organizacion',
                activo=True
            )
            
            # Crear perfil según tipo
            if tipo_usuario == 'donor':
                Donador.objects.create(
                    usuario=usuario,
                    nombre_negocio=data.get('businessName'),
                    tipo_donador=data.get('donationType'),
                    ciudad=data.get('city'),
                    descripcion=data.get('description')
                )
            
            elif tipo_usuario == 'organization':
                Organizacion.objects.create(
                    usuario=usuario,
                    nombre_organizacion=data.get('orgName'),
                    tipo_organizacion=data.get('orgType'),
                    ciudad=data.get('orgCity'),
                    descripcion=data.get('description')
                )
            
            # Registrar en historial
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
# VISTA: DASHBOARD (Ejemplo - puedes expandir)
# =====================================================
def dashboard(request):
    """Dashboard del usuario logueado"""
    if 'usuario_id' not in request.session:
        return redirect('templatesApp/inicioSesion.html')
    
    try:
        usuario = Usuario.objects.get(id=request.session['usuario_id'])
        context = {
            'usuario': usuario,
            'tipo_usuario': usuario.tipo_usuario
        }
        return render(request, 'templatesApp/dashboard.html', context)
    except Usuario.DoesNotExist:
        return redirect('templatesApp/inicioSesion.html')