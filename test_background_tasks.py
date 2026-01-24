"""
Test para verificar que las APIs largas NO bloquean el servidor
"""
import requests
import time
import threading
from datetime import datetime

BASE_URL = "http://localhost:6880"
USERNAME = "admin"
PASSWORD = "Admin2024!Secure"

def print_separator(title=""):
    print("\n" + "="*80)
    if title:
        print(title)
        print("="*80)

def test_concurrent_requests():
    """
    Prueba que el servidor puede responder a múltiples peticiones
    mientras ejecuta tareas largas en background
    """
    print_separator("TEST: APIs en Background NO Bloquean el Servidor")
    
    print(f"Fecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}")
    print(f"Usuario: {USERNAME}")
    print("-" * 80)
    
    # 1. Iniciar tarea larga en background (Channel Check)
    print("\n1️⃣ Iniciando Channel Check en background...")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/channels/check",
            auth=(USERNAME, PASSWORD),
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Respuesta inmediata recibida: {data['status']}")
            print(f"   Mensaje: {data['message']}")
            print(f"   Tiempo de respuesta: {time.time() - start_time:.2f}s")
        else:
            print(f"❌ Error: {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # 2. Mientras la tarea corre en background, hacer peticiones al servidor
    print("\n2️⃣ Haciendo peticiones al servidor mientras Channel Check corre en background...")
    
    test_endpoints = [
        ("/health", "Health Check"),
        ("/api/dashboard/stats", "Dashboard Stats"),
        ("/api/channels?limit=5", "Lista de Canales"),
    ]
    
    for i in range(3):
        print(f"\n   Ronda {i+1}/3:")
        for endpoint, name in test_endpoints:
            try:
                req_start = time.time()
                resp = requests.get(f"{BASE_URL}{endpoint}", timeout=3)
                req_time = time.time() - req_start
                
                if resp.status_code == 200:
                    print(f"   ✅ {name}: {resp.status_code} ({req_time:.3f}s)")
                else:
                    print(f"   ⚠️  {name}: {resp.status_code} ({req_time:.3f}s)")
                    
            except requests.exceptions.Timeout:
                print(f"   ❌ {name}: TIMEOUT - ¡El servidor está BLOQUEADO!")
            except Exception as e:
                print(f"   ❌ {name}: Error - {e}")
        
        time.sleep(2)  # Esperar 2 segundos entre rondas
    
    total_time = time.time() - start_time
    print(f"\n✅ TEST COMPLETADO en {total_time:.2f}s")
    print("\n📊 RESULTADO:")
    print("   Si todas las peticiones respondieron rápido (<1s), el servidor NO está bloqueado ✅")
    print("   Si hubo timeouts o respuestas lentas (>3s), el servidor SÍ está bloqueado ❌")

def test_scraper_background():
    """
    Prueba que el Scraper se ejecuta en background
    """
    print_separator("TEST: Scraper en Background")
    
    print(f"\n1️⃣ Iniciando Scraper en background...")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/scraper/trigger",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            response_time = time.time() - start_time
            print(f"✅ Respuesta inmediata recibida: {data['status']}")
            print(f"   Mensaje: {data['message']}")
            print(f"   Tiempo de respuesta: {response_time:.2f}s")
            
            if response_time < 2:
                print(f"   ✅ Respuesta rápida - Ejecutándose en background correctamente")
            else:
                print(f"   ⚠️  Respuesta lenta - Puede estar bloqueando")
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_epg_background():
    """
    Prueba que EPG Update se ejecuta en background
    """
    print_separator("TEST: EPG Update en Background")
    
    print(f"\n1️⃣ Iniciando EPG Update en background...")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/epg/update",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            response_time = time.time() - start_time
            print(f"✅ Respuesta inmediata recibida: {data['status']}")
            print(f"   Mensaje: {data['message']}")
            print(f"   Tiempo de respuesta: {response_time:.2f}s")
            
            if response_time < 2:
                print(f"   ✅ Respuesta rápida - Ejecutándose en background correctamente")
            else:
                print(f"   ⚠️  Respuesta lenta - Puede estar bloqueando")
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print_separator("PRUEBA DE BACKGROUND TASKS - NO BLOQUEO DEL SERVIDOR")
    print("Este test verifica que las APIs largas NO bloquean el servidor")
    print("cuando se ejecutan en background.")
    
    # Test 1: Verificar que el servidor responde mientras hay tareas en background
    test_concurrent_requests()
    
    # Test 2: Verificar Scraper en background
    test_scraper_background()
    
    # Test 3: Verificar EPG Update en background
    test_epg_background()
    
    print_separator("TESTS COMPLETADOS")
