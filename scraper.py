import os
import sys
import time
import re
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By

MEF_URL = "https://apps4.mineco.gob.pe/registramef/servicioInscripcion/dtCapacitacionExtView.htm"

REGION_CLEAN_MAP = {
    "AMAZONAS": "Amazonas",
    "NCASH - HUARAZ": "Áncash - Huaraz",
    "NCASH - SANTA": "Áncash - Santa",
    "APURMAC - ABANCAY": "Apurímac - Abancay",
    "APURMAC - ANDAHUAYLAS": "Apurímac - Andahuaylas",
    "AREQUIPA": "Arequipa",
    "AYACUCHO": "Ayacucho",
    "CAJAMARCA": "Cajamarca",
    "CUSCO": "Cusco",
    "HUANCAVELICA": "Huancavelica",
    "HUNUCO": "Huánuco",
    "ICA": "Ica",
    "JUNN": "Junín",
    "LA LIBERTAD": "La Libertad",
    "LAMBAYEQUE": "Lambayeque",
    "LIMA - HUACHO": "Lima - Huacho",
    "LORETO": "Loreto",
    "MADRE DE DIOS": "Madre de Dios",
    "MOQUEGUA": "Moquegua",
    "PASCO": "Pasco",
    "PIURA": "Piura",
    "PUNO": "Puno",
    "SAN MARTN - MOYOBAMBA": "San Martín - Moyobamba",
    "SAN MARTN - TARAPOTO": "San Martín - Tarapoto",
    "TACNA": "Tacna",
    "TUMBES": "Tumbes",
    "UCAYALI": "Ucayali"
}

LATIN1_CHAR_MAP = {
    '\xd3': 'Ó',
    '\xda': 'Ú',
    '\xcd': 'Í',
    '\xc1': 'Á',
    '\xc9': 'É',
    '\xd1': 'Ñ',
    '\xf3': 'ó',
    '\xfa': 'ú',
    '\xed': 'í',
    '\xe1': 'á',
    '\xe9': 'é',
    '\xf1': 'ñ',
    '\xba': '°',
    '\x96': '-',
    '\uFFFD': ''
}

def clean_spanish_text(text: str) -> str:
    if not text:
        return ""
    res = text
    for k, v in LATIN1_CHAR_MAP.items():
        res = res.replace(k, v)
    # Common fixes
    res = res.replace("N° ", "N° ").replace("Nº", "N°")
    res = re.sub(r'\s+', ' ', res).strip()
    return res

def clean_region_name(raw_text: str) -> str:
    raw = (raw_text or "").strip()
    for pattern, clean_name in REGION_CLEAN_MAP.items():
        if pattern in raw:
            return clean_name
    return clean_spanish_text(raw).title()

def init_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Edge(options=options)
    driver.set_page_load_timeout(35)
    return driver

def scrape_all_courses(progress_callback=None):
    """
    Scrapes all training courses from all 27 regions of RegistraMEF.
    Returns a dict with metadata and list of courses.
    """
    start_time = time.time()
    driver = None
    all_courses = []
    
    now = datetime.now()
    today_str = now.strftime("%d/%m/%Y")
    today_iso = now.strftime("%Y-%m-%d")

    try:
        if progress_callback:
            progress_callback(5, "Iniciando navegador y conectando a RegistraMEF...")
        
        driver = init_driver()
        driver.get(MEF_URL)
        time.sleep(2.5)

        buttons = driver.find_elements(By.CSS_SELECTOR, "#idFormMenu button")
        region_list = []
        for btn in buttons:
            btn_id = btn.get_attribute("id")
            btn_txt = btn.get_attribute("textContent")
            clean_name = clean_region_name(btn_txt)
            region_list.append({"id": btn_id, "name": clean_name, "raw": (btn_txt or "").strip()})

        total_regions = len(region_list)
        if progress_callback:
            progress_callback(15, f"Detectadas {total_regions} regiones. Extrayendo cursos...")

        for idx, reg in enumerate(region_list):
            try:
                driver.execute_script(f'document.getElementById("{reg["id"]}").click();')
                time.sleep(0.5)

                rows = driver.find_elements(By.CSS_SELECTOR, "#idformDtUsuarioExterno-iddata_data > tr.ui-widget-content")
                for r in rows:
                    try:
                        text = r.get_attribute("innerText").strip()
                    except Exception:
                        continue
                    
                    if not text or "No se han programado capacitaciones" in text:
                        continue

                    # Extract CAPACITACIÓN
                    cap_match = re.search(r'CAPACITACI[ÓO\?\xd3]+N:\s*(\d+)?\s*-?\s*([^\n\r]+)', text)
                    codigo = cap_match.group(1).strip() if cap_match and cap_match.group(1) else ""
                    titulo = cap_match.group(2).strip() if cap_match and cap_match.group(2) else ""
                    
                    if not codigo and not titulo:
                        first_line = text.split("\n")[0].strip()
                        parts = first_line.split("-", 1)
                        if len(parts) == 2 and parts[0].strip().isdigit():
                            codigo = parts[0].strip()
                            titulo = parts[1].strip()
                        else:
                            titulo = first_line

                    titulo = clean_spanish_text(titulo)

                    # Extract FECHA
                    fec_match = re.search(r'FECHA:\s*(\d{2}/\d{2}/\d{4})\s*(\d{1,2}:\d{2})?\s*(?:A|a)?\s*(\d{1,2}:\d{2})?', text)
                    fecha = fec_match.group(1) if fec_match else ""
                    hora_ini = fec_match.group(2) if fec_match and fec_match.group(2) else ""
                    hora_fin = fec_match.group(3) if fec_match and fec_match.group(3) else ""

                    # Extract LUGAR
                    lug_match = re.search(r'LUGAR:\s*([^\n\r]+)', text)
                    lugar = clean_spanish_text(lug_match.group(1).strip()) if lug_match else "CAPACITACION VIRTUAL"
                    es_virtual = "VIRTUAL" in lugar.upper()
                    modalidad = "Virtual" if es_virtual else "Presencial"

                    # ISO date for sorting
                    fecha_iso = ""
                    if fecha:
                        fp = fecha.split("/")
                        if len(fp) == 3:
                            fecha_iso = f"{fp[2]}-{fp[1]}-{fp[0]}"

                    is_today = (fecha == today_str)

                    # Calculate status
                    estado = "Próximamente"
                    if fecha_iso:
                        if fecha_iso < today_iso:
                            estado = "Finalizado"
                        elif fecha_iso == today_iso:
                            if hora_ini and hora_fin:
                                cur_hm = now.strftime("%H:%M")
                                if cur_hm < hora_ini:
                                    estado = "Hoy (Por iniciar)"
                                elif hora_ini <= cur_hm <= hora_fin:
                                    estado = "¡En vivo ahora!"
                                else:
                                    estado = "Finalizó hoy"
                            else:
                                estado = "Hoy"

                    all_courses.append({
                        "id": f"{codigo}_{reg['id']}" if codigo else f"c_{idx}_{len(all_courses)}",
                        "codigo": codigo,
                        "titulo": titulo,
                        "region": reg["name"],
                        "region_id": reg["id"],
                        "fecha": fecha,
                        "fecha_iso": fecha_iso,
                        "hora_inicio": hora_ini,
                        "hora_fin": hora_fin,
                        "horario": f"{hora_ini} a {hora_fin}" if hora_ini and hora_fin else (hora_ini or "Por confirmar"),
                        "lugar": lugar,
                        "modalidad": modalidad,
                        "es_virtual": es_virtual,
                        "es_hoy": is_today,
                        "estado": estado,
                        "mef_url": MEF_URL
                    })

            except Exception as e:
                print(f"Error procesando región {reg['name']}: {e}", file=sys.stderr)

            pct = 15 + int(((idx + 1) / total_regions) * 80)
            if progress_callback:
                progress_callback(pct, f"Consultando {reg['name']} ({idx + 1}/{total_regions})...")

        # Sort courses: Today first, then ascending by date and start hour
        def sort_key(c):
            order = 0 if c["es_hoy"] else (1 if c["fecha_iso"] >= today_iso else 2)
            return (order, c["fecha_iso"], c["hora_inicio"], c["region"])

        all_courses.sort(key=sort_key)

        elapsed = round(time.time() - start_time, 1)
        today_courses_count = sum(1 for c in all_courses if c["es_hoy"])
        virtual_count = sum(1 for c in all_courses if c["es_virtual"])
        presencial_count = len(all_courses) - virtual_count
        regions_with_courses = len(set(c["region"] for c in all_courses))

        result = {
            "success": True,
            "last_updated": now.strftime("%Y-%m-%d %H:%M:%S"),
            "last_updated_human": now.strftime("%d/%m/%Y %I:%M %p"),
            "today_date": today_str,
            "elapsed_seconds": elapsed,
            "total_courses": len(all_courses),
            "today_courses_count": today_courses_count,
            "virtual_count": virtual_count,
            "presencial_count": presencial_count,
            "regions_with_courses_count": regions_with_courses,
            "courses": all_courses
        }

        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        with open(os.path.join(data_dir, "cursos.json"), "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        if progress_callback:
            progress_callback(100, f"Completado exitosamente. {len(all_courses)} cursos encontrados ({today_courses_count} hoy).")

        return result

    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

if __name__ == "__main__":
    def print_progress(pct, msg):
        print(f"[{pct}%] {msg}")

    print("=== EXTRACTOR DE CAPACITACIONES MEF ===")
    res = scrape_all_courses(print_progress)
    print("\n=== RESUMEN ===")
    print(f"Total Cursos: {res['total_courses']}")
    print(f"Cursos de HOY ({res['today_date']}): {res['today_courses_count']}")
    print(f"Tiempo: {res['elapsed_seconds']} segundos")
    print(f"Archivo guardado en: data/cursos.json")
