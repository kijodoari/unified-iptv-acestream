#!/usr/bin/env python3
"""
Script para probar TODAS las APIs del sistema
Identifica cuáles responden en tiempo real y cuáles están vacías
"""
import requests
import time
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:6880"
USERNAME = "admin"
PASSWORD = "Admin2024!Secure"

# Lista completa de APIs a probar
APIS = [
    # Dashboard (HTML)
    {"method": "GET", "url": "/", "name": "Dashboard Home", "type": "html", "auth": True},
    {"method": "GET", "url": "/channels", "name": "Channels Page", "type": "html", "auth": True},
    {"method": "GET", "url": "/users", "name": "Users Page", "type": "html", "auth": True},
    {"method": "GET", "url": "/scraper", "name": "Scraper Page", "type": "html", "auth": True},
    {"method": "GET", "url": "/epg", "name": "EPG Page", "type": "html", "auth": True},
    {"method": "GET", "url": "/settings", "name": "Settings Page", "type": "html", "auth": True},
    
    # Health & Stats
    {"method": "GET", "url": "/health", "name": "Health Check", "type": "json", "auth": False},
    {"method": "GET", "url": "/api/dashboard/stats", "name": "Dashboard Stats", "type": "json", "auth": True},
    
    # Channels API
    {"method": "GET", "url": "/api/channels?limit=5", "name": "List Channels", "type": "json", "auth": True},
    {"method": "GET", "url": "/api/channels/1", "name": "Get Channel Details", "type": "json", "auth": True},
    
    # Users API
    {"method": "GET", "url": "/api/users", "name": "List Users", "type": "json", "auth": True},
    {"method": "GET", "url": "/api/users/1", "name": "Get User Details", "type": "json", "auth": True},
    
    # Settings API
    {"method": "GET", "url": "/api/settings", "name": "List Settings", "type": "json", "auth": True},
    
    # Xtream Codes API
    {"method": "GET", "url": f"/player_api.php?username={USERNAME}&password={PASSWORD}", "name": "Xtream Player API", "type": "json", "auth": False},
    {"method": "GET", "url": f"/player_api.php?username={USERNAME}&password={PASSWORD}&action=get_live_categories", "name": "Xtream Live Categories", "type": "json", "auth": False},
    {"method": "GET", "url": f"/player_api.php?username={USERNAME}&password={PASSWORD}&action=get_live_streams", "name": "Xtream Live Streams", "type": "json", "auth": False},
    {"method": "GET", "url": f"/get.php?username={USERNAME}&password={PASSWORD}&type=m3u_plus&output=ts", "name": "M3U Playlist", "type": "text", "auth": False},
    {"method": "GET", "url": f"/xmltv.php?username={USERNAME}&password={PASSWORD}", "name": "XMLTV EPG", "type": "xml", "auth": False},
    
    # EPG API
    {"method": "GET", "url": "/epg/status", "name": "EPG Status", "type": "json", "auth": True},
    {"method": "GET", "url": "/epg/channel/1", "name": "Channel EPG", "type": "json", "auth": True},
    
    # Logs API
    {"method": "GET", "url": "/api/logs/tail?lines=5", "name": "Tail Logs", "type": "json", "auth": True},
    
    # AceProxy API (from aceproxy.py)
    {"method": "GET", "url": "/api/aceproxy/streams", "name": "AceProxy Streams", "type": "json", "auth": True},
    {"method": "GET", "url": "/api/aceproxy/stats", "name": "AceProxy Stats", "type": "json", "auth": True},
    
    # APIs largas (POST)
    {"method": "POST", "url": "/api/scraper/trigger", "name": "Trigger Scraper", "type": "json", "auth": True, "slow": True},
    {"method": "POST", "url": "/api/epg/update", "name": "Update EPG", "type": "json", "auth": True, "slow": True},
    {"method": "POST", "url": "/api/channels/check", "name": "Check Channels (POST)", "type": "json", "auth": True, "slow": True},
    
    # SSE API (tiempo real)
    {"method": "GET", "url": "/api/channels/check/stream", "name": "Check Channels (SSE)", "type": "sse", "auth": True, "realtime": True},
]

def test_api(api):
    """Probar una API individual"""
    url = BASE_URL + api["url"]
    method = api["method"]
    name = api["name"]
    api_type = api["type"]
    needs_auth = api.get("auth", False)
    is_slow = api.get("slow", False)
    is_realtime = api.get("realtime", False)
    
    auth = (USERNAME, PASSWORD) if needs_auth else None
    
    try:
        start_time = time.time()
        
        if method == "GET":
            if is_realtime:
                # Para SSE, solo verificamos que conecta
                response = requests.get(url, auth=auth, stream=True, timeout=5)
                # Leer solo el primer evento
                for line in response.iter_lines():
                    if line:
                        break
                response.close()
            else:
                response = requests.get(url, auth=auth, timeout=30 if is_slow else 10)
        elif method == "POST":
            response = requests.post(url, auth=auth, json={}, timeout=60 if is_slow else 10)
        else:
            return {"name": name, "status": "SKIP", "reason": "Method not supported"}
        
        elapsed = time.time() - start_time
        
        # Analizar respuesta
        status_code = response.status_code
        
        if status_code == 200:
            # Verificar si está vacía
            is_empty = False
            content_info = ""
            
            if api_type == "json":
                try:
                    data = response.json()
                    if isinstance(data, list) and len(data) == 0:
                        is_empty = True
                        content_info = "Empty array"
                    elif isinstance(data, dict) and len(data) == 0:
                        is_empty = True
                        content_info = "Empty object"
                    else:
                        content_info = f"{len(data)} items" if isinstance(data, list) else f"{len(data)} keys"
                except:
                    content_info = "Invalid JSON"
            elif api_type == "html":
                content_length = len(response.text)
                content_info = f"{content_length} bytes"
                is_empty = content_length < 100
            elif api_type == "text":
                lines = response.text.count('\n')
                content_info = f"{lines} lines"
                is_empty = lines < 5
            elif api_type == "xml":
                content_length = len(response.text)
                content_info = f"{content_length} bytes"
                is_empty = content_length < 100
            elif api_type == "sse":
                content_info = "SSE stream"
                is_empty = False
            
            return {
                "name": name,
                "status": "OK",
                "code": status_code,
                "time": round(elapsed, 2),
                "content": content_info,
                "empty": is_empty,
                "realtime": is_realtime,
                "slow": is_slow
            }
        else:
            return {
                "name": name,
                "status": "ERROR",
                "code": status_code,
                "time": round(elapsed, 2),
                "reason": response.text[:100]
            }
    
    except requests.exceptions.Timeout:
        return {"name": name, "status": "TIMEOUT", "reason": "Request timed out"}
    except requests.exceptions.ConnectionError:
        return {"name": name, "status": "CONNECTION_ERROR", "reason": "Cannot connect"}
    except Exception as e:
        return {"name": name, "status": "EXCEPTION", "reason": str(e)[:100]}

def main():
    print("=" * 100)
    print("PRUEBA COMPLETA DE TODAS LAS APIs")
    print("=" * 100)
    print(f"Fecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}")
    print(f"Total APIs: {len(APIS)}")
    print("=" * 100)
    print()
    
    results = []
    
    for i, api in enumerate(APIS, 1):
        print(f"[{i}/{len(APIS)}] Probando: {api['name']}...", end=" ")
        result = test_api(api)
        results.append(result)
        
        if result["status"] == "OK":
            emoji = "✅"
            if result.get("empty"):
                emoji = "⚠️ "
            elif result.get("realtime"):
                emoji = "🔄"
            elif result.get("slow"):
                emoji = "🐌"
            
            print(f"{emoji} {result['code']} ({result['time']}s) - {result['content']}")
        else:
            print(f"❌ {result['status']}")
    
    print()
    print("=" * 100)
    print("RESUMEN")
    print("=" * 100)
    
    ok_count = sum(1 for r in results if r["status"] == "OK")
    error_count = sum(1 for r in results if r["status"] != "OK")
    empty_count = sum(1 for r in results if r.get("empty", False))
    realtime_count = sum(1 for r in results if r.get("realtime", False))
    slow_count = sum(1 for r in results if r.get("slow", False) and r["status"] == "OK")
    
    print(f"\n📊 ESTADÍSTICAS:")
    print(f"   Total APIs: {len(APIS)}")
    print(f"   Funcionando: {ok_count} ✅")
    print(f"   Con errores: {error_count} ❌")
    print(f"   Vacías: {empty_count} ⚠️")
    print(f"   Tiempo real: {realtime_count} 🔄")
    print(f"   Lentas (>5s): {slow_count} 🐌")
    
    # APIs vacías
    if empty_count > 0:
        print(f"\n⚠️  APIs VACÍAS ({empty_count}):")
        for r in results:
            if r.get("empty", False):
                print(f"   - {r['name']}: {r['content']}")
    
    # APIs con errores
    if error_count > 0:
        print(f"\n❌ APIs CON ERRORES ({error_count}):")
        for r in results:
            if r["status"] != "OK":
                print(f"   - {r['name']}: {r['status']} - {r.get('reason', 'N/A')}")
    
    # APIs lentas sin tiempo real
    slow_no_realtime = [r for r in results if r.get("slow", False) and not r.get("realtime", False) and r["status"] == "OK"]
    if slow_no_realtime:
        print(f"\n🐌 APIs LENTAS SIN TIEMPO REAL ({len(slow_no_realtime)}):")
        for r in slow_no_realtime:
            print(f"   - {r['name']}: {r['time']}s")
    
    # APIs con tiempo real
    if realtime_count > 0:
        print(f"\n🔄 APIs CON TIEMPO REAL ({realtime_count}):")
        for r in results:
            if r.get("realtime", False):
                print(f"   - {r['name']}: SSE implementado ✅")
    
    print("\n" + "=" * 100)

if __name__ == "__main__":
    main()
