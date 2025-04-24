# Módulo de Gestión de Salas y Préstamo de Elementos Recreativos

Este módulo permite la gestión eficiente de la reserva de salas de descanso y 
recreación, así como el préstamo y la devolución de elementos recreativos como 
juegos de mesa y equipos disponibles en dichas salas. Está diseñado para ser 
utilizado por los miembros de la comunidad académica de la Escuela, 
permitiendo una experiencia organizada, accesible y alineada con la promoción 
del bienestar universitario.

# Requisitos funcionales:

## 1. Reserva de salas y elementos recreativos:
- Los usuarios podrán consultar la disponibilidad de salas de descanso o 
  recreación, así como de elementos recreativos asociados a estas.
- El sistema permitirá realizar reservas según los horarios establecidos por el área 
  de Bienestar.
- Las reservas incluirán la selección de la sala, el horario deseado y los elementos 
  recreativos que se desean utilizar.

## 2. Registro de datos por reserva:
Cada reserva deberá incluir los siguientes campos:
- ID único de la reserva.
- Nombre completo del usuario.
- Número de identificación.
- Rol dentro de la institución (Estudiante, Docente, Administrativo, Servicios Generales).
- Fecha y hora de la reserva.
- Sala asignada.
- Ubicación dentro del campus.
- Elementos prestados (juegos de mesa, equipos, etc.).
- Estado de la reserva (Confirmada, Cancelada, Terminada).
- Registro de devolución de los elementos prestados.

## 3. Gestión de horarios y disponibilidad:
- El sistema debe mostrar en tiempo real los horarios disponibles para cada sala.
- También debe mostrar la disponibilidad y cantidad de elementos recreativos por sala.
- En caso de alta demanda, el sistema debe evitar reservas superpuestas y permitir 
  notificaciones de disponibilidad futura si un espacio se libera.

## 4. Devolución de elementos:
- El sistema permitirá registrar la devolución de los elementos prestados por parte 
  del usuario.
- En caso de elementos no devueltos o con daño, el sistema deberá generar una 
  notificación al administrador para su seguimiento.

## 5. Panel de administración:
- Los funcionarios de Bienestar podrán gestionar la habilitación o deshabilitación 
  de salas y elementos, modificar horarios, y revisar el historial de reservas y 
  préstamos.
- Se incluirá un panel de control para visualizar reportes sobre el uso de salas y 
  elementos, filtrado por tipo de usuario, tipo de sala y rango de fechas.

## 6. Confirmaciones y recordatorios automáticos:
- El sistema debe enviar confirmaciones automáticas al correo institucional del 
  usuario una vez realizada la reserva.
- Asimismo, deberá enviar recordatorios previos a la hora programada y 
  notificaciones en caso de cancelaciones o cambios.

    
