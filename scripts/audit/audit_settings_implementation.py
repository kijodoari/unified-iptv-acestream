#!/usr/bin/env python3
"""
Auditoría completa de implementación de settings
Verifica que cada setting esté realmente implementado y funcionando
"""
import os
import re
from pathlib import Path

# Lista de todos los settings
SETTINGS = {
    # Server Settings (4)
    'server_host': {'type': 'restart', 'files': ['main.py', 'app/config.py']},
    'server_port': {'type': 'restart', 'files': ['main.py', 'app/config.py']},
    'server_timezone': {'type': 'dynamic', 'files': ['app/config.py']},
    'server_debug': {'type': 'restart', 'files': ['main.py', 'app/config.py']},
    
    # AceStream Settings (6)
    'acestream_enabled': {'type': 'restart', 'files': ['main.py', 'app/config.py']},
    'acestream_engine_host': {'type': 'restart', 'files': ['app/config.py', 'app/services/aceproxy_service.py']},
    'acestream_engine_port': {'type': 'restart', 'files': ['app/config.py', 'app/services/aceproxy_service.py']},
    'acestream_streaming_host': {'type': 'restart', 'files': ['app/config.py', 'app/services/aiohttp_streaming_server.py']},
    'acestream_streaming_port': {'type': 'restart', 'files': ['app/config.py', 'app/services/aiohttp_streaming_server.py']},
    'acestream_timeout': {'type': 'dynamic', 'files': ['app/config.py', 'app/services/aceproxy_service.py']},
    'acestream_chunk_size': {'type': 'dynamic', 'files': ['app/config.py', 'app/services/aiohttp_streaming_server.py']},
    'acestream_empty_timeout': {'type': 'dynamic', 'files': ['app/config.py', 'app/services/aiohttp_streaming_server.py']},
    'acestream_no_response_timeout': {'type': 'dynamic', 'files': ['app/config.py', 'app/services/aiohttp_streaming_server.py']},
    
    # Scraper Settings (1)
    'scraper_update_interval': {'type': 'dynamic', 'files': ['app/config.py', 'app/services/scraper_service.py']},
    
    # EPG Settings (2)
    'epg_update_interval': {'type': 'dynamic', 'files': ['app/config.py', 'app/services/epg_service.py']},
    'epg_cache_file': {'type': 'dynamic', 'files': ['app/config.py', 'app/services/epg_service.py']},
    
    # Database Settings (4)
    'database_url': {'type': 'restart', 'files': ['app/config.py', 'app/utils/auth.py']},
    'database_echo': {'type': 'restart', 'files': ['app/config.py', 'app/utils/auth.py']},
    'database_pool_size': {'type': 'restart', 'files': ['app/config.py', 'app/utils/auth.py']},
    'database_max_overflow': {'type': 'restart', 'files': ['app/config.py', 'app/utils/auth.py']},
    
    # Security Settings (2)
    'admin_username': {'type': 'readonly', 'files': ['app/config.py', 'app/utils/auth.py']},
    'access_token_expire_minutes': {'type': 'dynamic', 'files': ['app/config.py', 'app/utils/auth.py']},
}

def search_in_file(filepath, pattern):
    """Buscar patrón en archivo"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            return bool(re.search(pattern, content, re.IGNORECASE))
    except:
        return False

def audit_setting(key, info):
    """Auditar un setting específico"""
    print(f"\n{'='*70}")
    print(f"🔍 Auditando: {key}")
    print(f"   Tipo: {info['type']}")
    print(f"   Archivos esperados: {', '.join(info['files'])}")
    
    results = []
    
    # Verificar en config.py
    config_pattern = key.upper()
    if search_in_file('app/config.py', config_pattern):
        print(f"   ✅ Definido en app/config.py")
        results.append(True)
    else:
        print(f"   ❌ NO encontrado en app/config.py")
        results.append(False)
    
    # Verificar uso en otros archivos
    key_pattern = f"config\\.{key}|get_config\\(\\)\\.{key}"
    
    for filepath in info['files']:
        if filepath == 'app/config.py':
            continue
            
        if os.path.exists(filepath):
            if search_in_file(filepath, key_pattern):
                print(f"   ✅ Usado en {filepath}")
                results.append(True)
            else:
                print(f"   ⚠️  NO usado en {filepath}")
                results.append(False)
        else:
            print(f"   ❌ Archivo {filepath} no existe")
            results.append(False)
    
    # Verificar si es dinámico que realmente se recarga
    if info['type'] == 'dynamic':
        # Buscar get_config() en los archivos de servicio
        has_reload = False
        for filepath in info['files']:
            if 'service' in filepath and os.path.exists(filepath):
                if search_in_file(filepath, r'get_config\(\)'):
                    has_reload = True
                    break
        
        if has_reload:
            print(f"   ✅ Recarga dinámica implementada (usa get_config())")
            results.append(True)
        else:
            print(f"   ❌ NO recarga dinámicamente (no usa get_config())")
            results.append(False)
    
    # Resultado final
    if all(results):
        print(f"   ✅✅✅ COMPLETAMENTE IMPLEMENTADO")
        return True
    elif any(results):
        print(f"   ⚠️⚠️⚠️ PARCIALMENTE IMPLEMENTADO")
        return False
    else:
        print(f"   ❌❌❌ NO IMPLEMENTADO")
        return False

def main():
    print("="*70)
    print("AUDITORÍA COMPLETA DE IMPLEMENTACIÓN DE SETTINGS")
    print("="*70)
    
    total = len(SETTINGS)
    implemented = 0
    partial = 0
    not_implemented = 0
    
    for key, info in SETTINGS.items():
        result = audit_setting(key, info)
        if result:
            implemented += 1
        else:
            partial += 1
    
    print("\n" + "="*70)
    print("RESUMEN DE AUDITORÍA")
    print("="*70)
    print(f"Total de settings: {total}")
    print(f"✅ Completamente implementados: {implemented}")
    print(f"⚠️  Parcialmente implementados: {partial}")
    print(f"❌ No implementados: {not_implemented}")
    print(f"\nPorcentaje de implementación: {(implemented/total)*100:.1f}%")
    
    if implemented == total:
        print("\n🎉 TODOS LOS SETTINGS ESTÁN COMPLETAMENTE IMPLEMENTADOS")
    else:
        print(f"\n⚠️  HAY {partial + not_implemented} SETTINGS QUE NECESITAN TRABAJO")

if __name__ == "__main__":
    main()
