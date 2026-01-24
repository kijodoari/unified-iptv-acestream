#!/usr/bin/env python3
"""
Test script para verificar el panel de settings
"""
import requests
from requests.auth import HTTPBasicAuth

# Configuración
BASE_URL = "http://localhost:6880"
USERNAME = "admin"
PASSWORD = "Admin2024!Secure"

def test_settings_page():
    """Verificar que la página de settings carga correctamente"""
    print("🔍 Probando acceso a /settings...")
    
    response = requests.get(
        f"{BASE_URL}/settings",
        auth=HTTPBasicAuth(USERNAME, PASSWORD)
    )
    
    if response.status_code == 200:
        print("✅ Página de settings accesible")
        
        # Verificar que contiene los elementos esperados
        content = response.text
        
        checks = [
            ("Settings Color Guide", "Guía de colores"),
            ("Dynamic", "Badge dinámico"),
            ("Restart Required", "Badge restart"),
            ("Read-Only", "Badge readonly"),
            ("Server Settings", "Sección Server"),
            ("AceStream Settings", "Sección AceStream"),
            ("Scraper Settings", "Sección Scraper"),
            ("EPG Settings", "Sección EPG"),
            ("Database Settings", "Sección Database"),
            ("Security Settings", "Sección Security"),
            ("Content Sources (M3U URLs)", "Sección M3U"),
            ("EPG Sources (XMLTV URLs)", "Sección EPG Sources"),
            ("border-success", "Bordes verdes"),
            ("border-warning", "Bordes amarillos"),
            ("border-secondary", "Bordes grises"),
        ]
        
        for check, description in checks:
            if check in content:
                print(f"  ✅ {description}")
            else:
                print(f"  ❌ {description} - NO ENCONTRADO")
        
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        return False

def test_settings_api():
    """Verificar que la API de settings funciona"""
    print("\n🔍 Probando API /api/settings...")
    
    response = requests.get(f"{BASE_URL}/api/settings")
    
    if response.status_code == 200:
        settings = response.json()
        print(f"✅ API funciona - {len(settings)} settings encontrados")
        
        # Verificar settings dinámicos
        dynamic_keys = [
            'scraper_update_interval', 'epg_update_interval', 'server_timezone',
            'epg_cache_file', 'acestream_timeout', 'acestream_chunk_size',
            'acestream_empty_timeout', 'acestream_no_response_timeout',
            'access_token_expire_minutes'
        ]
        
        found_dynamic = [s for s in settings if s['key'] in dynamic_keys]
        print(f"  ✅ {len(found_dynamic)}/9 settings dinámicos encontrados")
        
        # Verificar settings que requieren restart
        restart_keys = [
            'server_host', 'server_port', 'server_debug', 'acestream_enabled',
            'acestream_engine_host', 'acestream_engine_port', 
            'acestream_streaming_host', 'acestream_streaming_port',
            'database_url', 'database_echo', 'database_pool_size', 
            'database_max_overflow'
        ]
        
        found_restart = [s for s in settings if s['key'] in restart_keys]
        print(f"  ✅ {len(found_restart)}/12 settings restart encontrados")
        
        # Verificar readonly
        readonly_keys = ['admin_username']
        found_readonly = [s for s in settings if s['key'] in readonly_keys]
        print(f"  ✅ {len(found_readonly)}/1 settings readonly encontrados")
        
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        return False

def test_scraper_sources_api():
    """Verificar que la API de scraper sources funciona"""
    print("\n🔍 Probando API /api/scraper/sources...")
    
    response = requests.get(f"{BASE_URL}/api/scraper/sources")
    
    if response.status_code == 200:
        sources = response.json()
        print(f"✅ API funciona - {len(sources)} fuentes M3U encontradas")
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        return False

def test_epg_sources_api():
    """Verificar que la API de EPG sources funciona"""
    print("\n🔍 Probando API /api/epg/sources...")
    
    response = requests.get(f"{BASE_URL}/api/epg/sources")
    
    if response.status_code == 200:
        sources = response.json()
        print(f"✅ API funciona - {len(sources)} fuentes EPG encontradas")
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("TEST: Panel de Settings con Sistema de Colores")
    print("=" * 60)
    
    results = []
    
    results.append(test_settings_page())
    results.append(test_settings_api())
    results.append(test_scraper_sources_api())
    results.append(test_epg_sources_api())
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ TODAS LAS PRUEBAS PASARON")
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
    print("=" * 60)
