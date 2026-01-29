#!/usr/bin/env python3
"""
Script para probar la API POST /api/channels/check
Mide el tiempo de respuesta y captura todos los errores
"""
import requests
import time
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:6880"
USERNAME = "admin"
PASSWORD = "Admin2024!Secure"

def test_channel_check():
    """Probar la API de verificación de canales"""
    
    print("=" * 80)
    print("TEST: POST /api/channels/check")
    print("=" * 80)
    print(f"Fecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"URL: {BASE_URL}/api/channels/check")
    print(f"Usuario: {USERNAME}")
    print("-" * 80)
    
    # Iniciar cronómetro
    start_time = time.time()
    
    try:
        print("\n⏳ Iniciando verificación de canales...")
        print("   (Esto puede tardar varios minutos dependiendo del número de canales)\n")
        
        # Hacer la petición
        response = requests.post(
            f"{BASE_URL}/api/channels/check",
            auth=(USERNAME, PASSWORD),
            timeout=900  # 15 minutos de timeout
        )
        
        # Calcular tiempo transcurrido
        elapsed_time = time.time() - start_time
        
        print(f"✅ Respuesta recibida en {elapsed_time:.2f} segundos")
        print(f"   Status Code: {response.status_code}")
        print("-" * 80)
        
        # Parsear respuesta JSON
        if response.status_code == 200:
            data = response.json()
            
            print("\n📊 RESULTADOS:")
            print("-" * 80)
            print(f"Status: {data.get('status', 'N/A')}")
            print(f"Mensaje: {data.get('message', 'N/A')}")
            
            if 'details' in data:
                details = data['details']
                print(f"\n📈 ESTADÍSTICAS:")
                print(f"   Total canales: {details.get('total_channels', 0)}")
                print(f"   Total verificados: {details.get('total_checked', 0)}")
                print(f"   Online: {details.get('online', 0)} ✅")
                print(f"   Offline: {details.get('offline', 0)} ❌")
                print(f"   Omitidos: {details.get('skipped', 0)} ⏭️")
                print(f"   Tiempo de ejecución: {details.get('elapsed_seconds', 0):.2f}s")
                print(f"   Tiempo promedio por canal: {details.get('average_time_per_channel', 0):.2f}s")
                
                # Calcular porcentajes
                total = details.get('total_checked', 0)
                if total > 0:
                    online_pct = (details.get('online', 0) / total) * 100
                    offline_pct = (details.get('offline', 0) / total) * 100
                    print(f"\n   Porcentaje Online: {online_pct:.1f}%")
                    print(f"   Porcentaje Offline: {offline_pct:.1f}%")
            
            # Mostrar lista de canales
            if 'channels' in data and data['channels']:
                print(f"\n📺 CANALES VERIFICADOS ({len(data['channels'])}):")
                print("-" * 80)
                for i, ch in enumerate(data['channels'], 1):
                    status_icon = {
                        'online': '✅',
                        'offline': '❌',
                        'skipped': '⏭️',
                        'error': '⚠️'
                    }.get(ch.get('status', 'unknown'), '❓')
                    
                    print(f"\n{i}. {status_icon} {ch.get('name', 'N/A')}")
                    print(f"   ID: {ch.get('id', 'N/A')}")
                    print(f"   AceStream ID: {ch.get('acestream_id', 'N/A')}")
                    print(f"   Estado: {ch.get('status', 'N/A').upper()}")
                    print(f"   Progreso: {ch.get('progress', 'N/A')}")
                    
                    if 'check_time' in ch:
                        print(f"   Tiempo de verificación: {ch['check_time']:.2f}s")
                    
                    if 'reason' in ch:
                        print(f"   Razón: {ch['reason']}")
                    
                    if 'error' in ch:
                        print(f"   Error: {ch['error']}")
            
            # Mostrar errores si los hay
            if 'errors' in data and data['errors']:
                print(f"\n⚠️  ERRORES ENCONTRADOS ({data.get('error_count', 0)}):")
                print("-" * 80)
                for i, error in enumerate(data['errors'], 1):
                    print(f"\n{i}. Canal ID: {error.get('channel_id', 'N/A')}")
                    print(f"   Nombre: {error.get('channel_name', 'N/A')}")
                    print(f"   Error: {error.get('error', 'N/A')}")
            else:
                print("\n✅ No se encontraron errores")
            
            # Mostrar JSON completo
            print("\n" + "=" * 80)
            print("RESPUESTA JSON COMPLETA:")
            print("=" * 80)
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
        else:
            print(f"\n❌ ERROR: Status code {response.status_code}")
            print(f"Respuesta: {response.text}")
        
        print("\n" + "=" * 80)
        print(f"⏱️  TIEMPO TOTAL: {elapsed_time:.2f} segundos ({elapsed_time/60:.2f} minutos)")
        print("=" * 80)
        
        return True
        
    except requests.exceptions.Timeout:
        elapsed_time = time.time() - start_time
        print(f"\n❌ TIMEOUT: La petición tardó más de 15 minutos")
        print(f"   Tiempo transcurrido: {elapsed_time:.2f} segundos")
        return False
        
    except requests.exceptions.ConnectionError as e:
        elapsed_time = time.time() - start_time
        print(f"\n❌ ERROR DE CONEXIÓN: No se pudo conectar al servidor")
        print(f"   Error: {e}")
        print(f"   Tiempo transcurrido: {elapsed_time:.2f} segundos")
        return False
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"\n❌ ERROR INESPERADO: {type(e).__name__}")
        print(f"   Mensaje: {e}")
        print(f"   Tiempo transcurrido: {elapsed_time:.2f} segundos")
        return False

if __name__ == "__main__":
    test_channel_check()
