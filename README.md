# 🇵🇪 Capacitaciones RegistraMEF - Visualizador Nacional y Cursos del Día

Este proyecto permite visualizar **todos los cursos de capacitación del Ministerio de Economía y Finanzas (MEF)** de las **27 regiones del Perú** en una sola pantalla, **sin necesidad de entrar a cada región una por una**.

---

## 🚀 Cómo iniciar el sistema

Simplemente haz doble clic en el archivo:
```
iniciar_servidor.bat
```
Esto abrirá automáticamente tu navegador en:
👉 **http://localhost:8000**

---

## ✨ Características Principales

1. **🌟 Cursos del Día (HOY)**:
   - Panel destacado en la parte superior que muestra inmediatamente todas las capacitaciones programadas para la fecha actual en todo el país.
   - Indica el estado en tiempo real: *¡En vivo ahora!*, *Hoy (Por iniciar)* o *Finalizó hoy*.

2. **🗺️ Las 27 Regiones en un solo lugar**:
   - Extrae automáticamente las capacitaciones de Amazonas, Áncash, Apurímac, Arequipa, Ayacucho, Cajamarca, Cusco, Huancavelica, Huánuco, Ica, Junín, La Libertad, Lambayeque, Lima, Loreto, Madre de Dios, Moquegua, Pasco, Piura, Puno, San Martín, Tacna, Tumbes, Ucayali, etc.

3. **🔍 Buscador y Filtros Inteligentes**:
   - **Búsqueda instantánea:** Escribe cualquier palabra clave (ej. *SIAF*, *AIRHSP*, *Inversión*, *Presupuesto*, *Contrataciones*, *Patrimonio*).
   - **Filtros rápidos:** Solo Cursos de Hoy, Solo Virtuales, Presenciales, o por Región específica.
   - **Vistas intercambiables:** Vista de Tarjetas modernas o Vista de Tabla compacta.

4. **🔄 Actualización en 1 Clic & Sincronización Automática**:
   - Botón **"Actualizar Cursos"** en la interfaz que consulta el portal oficial del MEF en tiempo real con barra de progreso.
   - Sincronización automática periódica en segundo plano.

5. **📋 Herramientas de Compartir e Inscripción**:
   - **Compartir por WhatsApp/Teams:** Copia con un clic un resumen formateado del curso con horarios y enlace.
   - **Guía de Inscripción:** Al hacer clic en "Inscribirme en MEF", te indica la región y código exacto y te dirige al portal oficial para registrar tu DNI.

---

## 📁 Estructura del Proyecto

- `iniciar_servidor.bat`: Lanzador rápido para Windows con 1 doble clic.
- `server.py`: Servidor FastAPI que gestiona los datos, el cálculo de estados y los endpoints.
- `scraper.py`: Motor de extracción automatizada con Edge Headless para las 27 regiones.
- `static/index.html`: Interfaz web moderna (Tailwind CSS, diseño responsivo, iconos Lucide).
- `data/cursos.json`: Base de datos local en caché de todas las capacitaciones activas.
