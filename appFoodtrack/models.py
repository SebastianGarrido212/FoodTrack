# foodtrack/models.py
from django.db import models
from django.utils import timezone

# =====================================================
# 1. USUARIO (Modelo base para autenticación)
# =====================================================
class Usuario(models.Model):
    TIPO_USUARIO_CHOICES = [
        ('donador', 'Donador'),
        ('organizacion', 'Organización'),
    ]
    
    email = models.EmailField(unique=True, max_length=100)
    password = models.CharField(max_length=255)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    tipo_usuario = models.CharField(
        max_length=20,
        choices=TIPO_USUARIO_CHOICES,
        default='donador'
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.tipo_usuario})"


# =====================================================
# 2. DONADOR
# =====================================================
class Donador(models.Model):
    TIPO_DONADOR_CHOICES = [
        ('empresa', 'Empresa'),
        ('restaurant', 'Restaurante'),
        ('productor', 'Productor Agrícola'),
        ('persona', 'Persona Natural'),
        ('otro', 'Otro'),
    ]
    
    usuario = models.OneToOneField(Usuario, on_delete=models.RESTRICT, related_name='donador_profile')
    nombre_negocio = models.CharField(max_length=100, blank=True, null=True)
    tipo_donador = models.CharField(
        max_length=20,
        choices=TIPO_DONADOR_CHOICES
    )
    ciudad = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'donador'
        verbose_name = 'Donador'
        verbose_name_plural = 'Donadores'
    
    def __str__(self):
        return f"{self.nombre_negocio or self.usuario.nombre} - {self.get_tipo_donador_display()}"


# =====================================================
# 3. ORGANIZACION
# =====================================================
class Organizacion(models.Model):
    TIPO_ORGANIZACION_CHOICES = [
        ('junta_vecinos', 'Junta de Vecinos'),
        ('distribuidora', 'Distribuidora'),
        ('recolectora', 'Recolectora'),
        ('otra', 'Otra'),
    ]
    
    usuario = models.OneToOneField(Usuario, on_delete=models.RESTRICT, related_name='organizacion_profile')
    nombre_organizacion = models.CharField(max_length=100)
    tipo_organizacion = models.CharField(
        max_length=20,
        choices=TIPO_ORGANIZACION_CHOICES
    )
    ciudad = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    capacidad = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'organizacion'
        verbose_name = 'Organización'
        verbose_name_plural = 'Organizaciones'
    
    def __str__(self):
        return f"{self.nombre_organizacion} - {self.get_tipo_organizacion_display()}"


# =====================================================
# 4. DONACION
# =====================================================
class Donacion(models.Model):
    ESTADO_DONACION_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_transito', 'En Tránsito'),
        ('entregada', 'Entregada'),
        ('cancelada', 'Cancelada'),
    ]
    
    UNIDAD_MEDIDA_CHOICES = [
        ('kg', 'Kilogramos'),
        ('litros', 'Litros'),
        ('unidades', 'Unidades'),
        ('paquetes', 'Paquetes'),
        ('cajas', 'Cajas'),
    ]
    
    donador = models.ForeignKey(Donador, on_delete=models.CASCADE, related_name='donaciones')
    fecha_donacion = models.DateTimeField(auto_now_add=True)
    tipo_alimento = models.CharField(max_length=100)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    unidad_medida = models.CharField(
        max_length=20,
        choices=UNIDAD_MEDIDA_CHOICES,
        default='kg'
    )
    fecha_vencimiento = models.DateField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_DONACION_CHOICES,
        default='pendiente'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'donacion'
        verbose_name = 'Donación'
        verbose_name_plural = 'Donaciones'
        ordering = ['-fecha_donacion']
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['fecha_donacion']),
            models.Index(fields=['donador']),
        ]
    
    def __str__(self):
        return f"{self.tipo_alimento} - {self.cantidad} {self.get_unidad_medida_display()} ({self.get_estado_display()})"


# =====================================================
# 5. RECEPCION DE DONACION
# =====================================================
class RecepcionDonacion(models.Model):
    donacion = models.ForeignKey(Donacion, on_delete=models.CASCADE, related_name='recepciones')
    organizacion = models.ForeignKey(Organizacion, on_delete=models.CASCADE, related_name='recepciones')
    fecha_recepcion = models.DateTimeField(auto_now_add=True)
    cantidad_recibida = models.DecimalField(max_digits=10, decimal_places=2)
    responsable_name = models.CharField(max_length=100, blank=True, null=True)
    comentarios = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'recepciondonacion'
        verbose_name = 'Recepción de Donación'
        verbose_name_plural = 'Recepciones de Donaciones'
        unique_together = ('donacion', 'organizacion')
    
    def __str__(self):
        return f"Recepción {self.donacion.tipo_alimento} - {self.organizacion.nombre_organizacion}"


# =====================================================
# 6. SEGUIMIENTO DE ENTREGA (Trazabilidad)
# =====================================================
class SeguimientoEntrega(models.Model):
    ESTADO_ENTREGA_CHOICES = [
        ('recogida', 'Recogida'),
        ('en_transito', 'En Tránsito'),
        ('entregada_destino', 'Entregada en Destino'),
        ('rechazada', 'Rechazada'),
        ('extraviada', 'Extraviada'),
    ]
    
    donacion = models.ForeignKey(Donacion, on_delete=models.CASCADE, related_name='seguimientos')
    organizacion = models.ForeignKey(Organizacion, on_delete=models.CASCADE, related_name='seguimientos')
    fecha_seguimiento = models.DateTimeField(auto_now_add=True)
    estado_entrega = models.CharField(
        max_length=30,
        choices=ESTADO_ENTREGA_CHOICES
    )
    ubicacion = models.CharField(max_length=255, blank=True, null=True)
    latitud = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    longitud = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    temperatura = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    humedad = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    comentarios = models.TextField(blank=True, null=True)
    usuario_actualizador = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='seguimientos_actualizados'
    )
    
    class Meta:
        db_table = 'seguimientoentrega'
        verbose_name = 'Seguimiento de Entrega'
        verbose_name_plural = 'Seguimientos de Entrega'
        ordering = ['-fecha_seguimiento']
        indexes = [
            models.Index(fields=['donacion', 'fecha_seguimiento']),
        ]
    
    def __str__(self):
        return f"Seguimiento {self.donacion.tipo_alimento} - {self.get_estado_entrega_display()}"


# =====================================================
# 7. HISTORIAL DE TRANSACCIONES (Auditoría)
# =====================================================
class HistorialTransacciones(models.Model):
    TIPO_ACCION_CHOICES = [
        ('crear_donacion', 'Crear Donación'),
        ('actualizar_donacion', 'Actualizar Donación'),
        ('recepcionar_donacion', 'Recepción de Donación'),
        ('actualizar_seguimiento', 'Actualizar Seguimiento'),
        ('entregar_donacion', 'Entregar Donación'),
        ('cancelar_donacion', 'Cancelar Donación'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('crear_usuario', 'Crear Usuario'),
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='transacciones')
    tipo_accion = models.CharField(max_length=50, choices=TIPO_ACCION_CHOICES)
    donacion = models.ForeignKey(
        Donacion,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='historial'
    )
    descripcion = models.TextField()
    fecha_accion = models.DateTimeField(auto_now_add=True)
    detalles_json = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'historialtransacciones'
        verbose_name = 'Historial de Transacción'
        verbose_name_plural = 'Historial de Transacciones'
        ordering = ['-fecha_accion']
        indexes = [
            models.Index(fields=['fecha_accion']),
            models.Index(fields=['usuario']),
        ]
    
    def __str__(self):
        return f"{self.usuario.nombre} - {self.get_tipo_accion_display()} ({self.fecha_accion})"