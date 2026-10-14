import os
import sys
import json
import threading
import time
from datetime import datetime
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

import scraper

app = FastAPI(title="MEF Capacitaciones - Cursos del Día", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "cursos.json")
STATIC_DIR = os.path.join(BASE_DIR, "static")
os.makedirs(STATIC_DIR, exist_ok=True)

scraping_state = {
    "is_running": False,
    "progress": 0,
    "message": "En espera",
    "last_run": None,
    "error": None
}
scraping_lock = threading.Lock()

def run_scraper_thread():
    global scraping_state
    with scraping_lock:
        scraping_state["is_running"] = True
        scraping_state["progress"] = 0
        scraping_state["message"] = "Iniciando extracci\u00f3n de capacitaciones..."
        scraping_state["error"] = None

    def progress_callback(pct, msg):
        scraping_state["progress"] = pct
        scraping_state["message"] = msg

    try:
        res = scraper.scrape_all_courses(progress_callback=progress_callback)
        with scraping_lock:
            scraping_state["is_running"] = False
            scraping_state["progress"] = 100
            scraping_state["message"] = f"Listo. Se encontraron {res['total_courses']} cursos."
            scraping_state["last_run"] = datetime.now().strftime("%d/%m/%Y %I:%M %p")
    except Exception as e:
        with scraping_lock:
            scraping_state["is_running"] = False
            scraping_state["message"] = f"Error: {str(e)}"
            scraping_state["error"] = str(e)

def recalculate_live_states(data: dict) -> dict:
    now = datetime.now()
    today_str = now.strftime("%d/%m/%Y")
    today_iso = now.strftime("%Y-%m-%d")
    cur_hm = now.strftime("%H:%M")

    courses = data.get("courses", [])
    today_count = 0

    for c in courses:
        fecha = c.get("fecha", "")
        fecha_iso = c.get("fecha_iso", "")
        h_ini = c.get("hora_inicio", "")
        h_fin = c.get("hora_fin", "")

        is_today = (fecha == today_str)
        c["es_hoy"] = is_today
        if is_today:
            today_count += 1

        estado = "Pr\u00f3ximamente"
        if fecha_iso:
            if fecha_iso < today_iso:
                estado = "Finalizado"
            elif fecha_iso == today_iso:
                if h_ini and h_fin:
                    if cur_hm < h_ini:
                        estado = "Hoy (Por iniciar)"
                    elif h_ini <= cur_hm <= h_fin:
                        estado = "\u00a1En vivo ahora!"
                    else:
                        estado = "Finaliz\u00f3 hoy"
                else:
                    estado = "Hoy"
        c["estado"] = estado

    data["today_courses_count"] = today_count
    data["today_date"] = today_str
    return data

def launch_course_registration(region_id: str, course_code: str, region_name: str):
    """
    Automates opening the browser and directly navigating to the registration form
    for the specific course in MEF's portal.
    """
    from selenium import webdriver
    from selenium.webdriver.edge.options import Options
    from selenium.webdriver.common.by import By

    print(f"Abriendo inscripci\u00f3n para curso {course_code} en regi\u00f3n {region_name} ({region_id})...")
    options = Options()
    options.add_experimental_option("detach", True)
    options.add_argument("--window-size=1280,950")
    options.add_argument("--disable-gpu")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = None
    try:
        driver = webdriver.Edge(options=options)
        driver.get(scraper.MEF_URL)
        time.sleep(1.8)

        # Click region button
        if region_id:
            try:
                reg_btn = driver.find_element(By.ID, region_id)
                driver.execute_script("arguments[0].click();", reg_btn)
                time.sleep(0.7)
            except Exception as e:
                print(f"Error al hacer clic en regi\u00f3n: {e}")

        # Find specific course row
        rows = driver.find_elements(By.CSS_SELECTOR, "#idformDtUsuarioExterno-iddata_data > tr.ui-widget-content")
        target_btn = None
        for r in rows:
            text = r.get_attribute("innerText")
            if course_code and course_code in text:
                btns = r.find_elements(By.CSS_SELECTOR, ".btnRegistrar")
                if btns:
                    target_btn = btns[0]
                    break

        if not target_btn and rows:
            btns = rows[0].find_elements(By.CSS_SELECTOR, ".btnRegistrar")
            if btns:
                target_btn = btns[0]

        if target_btn:
            driver.execute_script("arguments[0].click();", target_btn)
            time.sleep(1.2)
            print(f"Inscripci\u00f3n abierta con \u00e9xito. URL final: {driver.current_url}")
        else:
            print("No se encontr\u00f3 el bot\u00f3n de inscripci\u00f3n del curso.")
    except Exception as e:
        print(f"Error en launch_course_registration: {e}")

# Background auto-sync scheduler thread (every 2 hours)
def background_scheduler():
    while True:
        time.sleep(3600)
        now = datetime.now()
        if now.hour in [7, 10, 13, 16] and not scraping_state["is_running"]:
            run_scraper_thread()

threading.Thread(target=background_scheduler, daemon=True).start()

class InscriptionRequest(BaseModel):
    codigo: str
    region_id: str
    region_name: str

@app.get("/", response_class=HTMLResponse)
def get_index():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Cursos MEF - Panel en preparaci\u00f3n</h1>")

@app.get("/api/cursos")
def get_cursos():
    if not os.path.exists(DATA_FILE):
        if not scraping_state["is_running"]:
            threading.Thread(target=run_scraper_thread, daemon=True).start()
        return {
            "success": False,
            "message": "Los datos se est\u00e1n extrayendo por primera vez. Por favor espere unos segundos.",
            "is_loading": True,
            "courses": []
        }

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        data = recalculate_live_states(data)
        data["scraping_status"] = scraping_state
        return JSONResponse(content=data)
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.post("/api/actualizar")
def trigger_actualizar(background_tasks: BackgroundTasks):
    if scraping_state["is_running"]:
        return {
            "success": True,
            "status": "already_running",
            "message": "Ya hay una actualizaci\u00f3n en curso."
        }

    thread = threading.Thread(target=run_scraper_thread, daemon=True)
    thread.start()
    return {
        "success": True,
        "status": "started",
        "message": "Actualizaci\u00f3n iniciada en segundo plano."
    }

@app.get("/api/actualizar/status")
def get_update_status():
    return scraping_state

@app.post("/api/abrir_inscripcion")
def abrir_inscripcion(req: InscriptionRequest):
    """
    Directly opens the registration form for the specific course in a browser window.
    """
    threading.Thread(
        target=launch_course_registration,
        args=(req.region_id, req.codigo, req.region_name),
        daemon=True
    ).start()
    return {
        "success": True,
        "message": f"Abriendo formulario de inscripci\u00f3n para el curso #{req.codigo} ({req.region_name})..."
    }

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

if __name__ == "__main__":
    print("=" * 60)
    print("  SERVIDOR DE CAPACITACIONES MEF INICIADO")
    print("  Panel disponible en: http://localhost:8000")
    print("=" * 60)
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
