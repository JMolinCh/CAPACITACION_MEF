# 🇵🇪 Capacitaciones RegistraMEF - Visualizador Nacional y Cursos del Día

Este proyecto permite visualizar **todos los cursos de capacitación del Ministerio de Economía y Finanzas (MEF)** de las **27 regiones del Perú** en una sola pantalla, **sin necesidad de entrar a cada región una por una**.

---

## 🌐 Ver en línea (GitHub Pages)

Puedes acceder a la versión web directamente sin instalar nada:
👉 **[https://vidos3010.github.io/CAPACITACION_MEF/](https://vidos3010.github.io/CAPACITACION_MEF/)**

> ⚙️ **Configuración en GitHub Pages (solo una vez):**
> 1. Ve a la pestaña **Settings** de este repositorio en GitHub.
> 2. En el menú izquierdo, haz clic en **Pages**.
> 3. En **Build and deployment > Branch**, selecciona `main` y la carpeta `/ (root)`.
> 4. Haz clic en **Save**. ¡Listo! En 1 minuto tu aplicación web estará activa.

---

## 🚀 Cómo iniciar el sistema localmente en Windows

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

4. **🔄 Actualización Automática con GitHub Actions**:
   - Un flujo automatizado (`.github/workflows/actualizar_cursos.yml`) ejecuta el extractor todos los días a las **06:00 AM** y **12:00 PM** (hora de Perú), actualizando la base de datos automáticamente.

5. **📋 Modal de Instrucciones y Enlace MEF**:
   - Al hacer clic en cualquier curso, se abre una ventana con los 4 pasos claros para inscribirse en RegistraMEF y el botón directo para abrir el portal oficial.

---

## 📁 Estructura del Proyecto

- `index.html`: Aplicación web principal (Tailwind CSS, diseño responsivo, iconos Lucide).
- `server.py`: Servidor FastAPI para ejecución local con scheduler de fondo.
- `scraper.py`: Motor de extracción automatizada compatible con Edge y Chrome.
- `data/cursos.json`: Base de datos de capacitaciones activas.
- `iniciar_servidor.bat`: Lanzador rápido para Windows.
- `.github/workflows/actualizar_cursos.yml`: Automatización diaria de extracción en GitHub.
- `requirements.txt`: Dependencias del proyecto.
