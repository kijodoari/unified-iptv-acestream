#!/usr/bin/env python3
"""
Script para probar la API GET /api/channels/check/stream con Server-Sent Events
Muestra el progreso en tiempo real mientras verifica los canales
"""
import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:6880"
USERNAME = "admin"
PASSWORD = "Admin2024!Secure"

def test_channel_check_sse():
    """Probar la API de verificación de canales con SSE (tiempo real)"""
    
    print("=" * 80)
    print("TEST: GET /api/channels/check/stream (Server-Sent Events)")
    print("=" * 80)
    print(f"Fecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"URL: {BASE_URL}/api/channels/check/stream")
    print(f"Usuario: {USERNAME}")
    print("-" * 80)
    print("\n🔄 PROGRESO EN TIEMPO REAL:\n")
    
    try:
        # Hacer la petición con streaming
        response = requests.get(
            f"{BASE_URL}/api/channels/check/stream",
            auth=(USERNAME, PASSWORD),
            stream=True,
            timeout=900  # 15 minutos de timeout
        )
        
        if response.status_code != 200:
            print(f"❌ ERROR: Status code {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
        
        # Procesar eventos en tiempo real
        stats = {'checked': 0, 'online': 0, 'offline': 0, 'skipped': 0}
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                
                # Las líneas de SSE empiezan con "data: "
                if line.startswith('data: '):
                    data_str = line[6:]  # Quitar "data: "
                    
                    try:
                        data = json.loads(data_str)
                        event_type = data.get('type', 'unknown')
                        
                        if event_type == 'start':
                            print(f"🚀 {data.get('message', 'Starting...')}")
                            print()
                        
                        elif event_type == 'info':
                            print(f"ℹ️  {data.get('message', '')}")
                            print()
                        
                        elif event_type == 'checking':
                            channel = data.get('channel', {})
                            index = data.get('index', 0)
                            total = data.get('total', 0)
                            print(f"⏳ [{index}/{total}] Verificando: {channel.get('name', 'N/A')} (ID: {channel.get('id', 'N/A')})")
                        
                        elif event_type == 'progress':
                            channel = data.get('channel', {})
                            index = data.get('index', 0)
                            total = data.get('total', 0)
                            status = channel.get('status', 'unknown')
                            
                            # Actualizar estadísticas
                            if 'stats' in data:
                                stats = data['stats']
                            
                            # Icono según estado
                            status_icon = {
                                'online': '✅',
                                'offline': '❌',
                                'skipped': '⏭️',
                                'error': '⚠️'
                            }.get(status, '❓')
                            
                            # Mostrar resultado
                            msg = f"{status_icon} [{index}/{total}] {channel.get('name', 'N/A')}"
                            
                            if status == 'online' or status == 'offline':
                                check_time = channel.get('check_time', 0)
                                msg += f" - {status.upper()} ({check_time:.2f}s)"
                            elif status == 'skipped':
                                msg += f" - OMITIDO ({channel.get('reason', 'N/A')})"
                            elif status == 'error':
                                msg += f" - ERROR: {channel.get('error', 'N/A')}"
                            
                            print(msg)
                            
                            # Mostrar estadísticas cada 10 canales
                            if index % 10 == 0:
                                print(f"   📊 Progreso: {stats['checked']} verificados | {stats['online']} online | {stats['offline']} offline | {stats['skipped']} omitidos")
                                print()
                        
                        elif event_type == 'complete':
                            print()
                            print("=" * 80)
                            print("✅ VERIFICACIÓN COMPLETADA")
                            print("=" * 80)
                            print(f"Mensaje: {data.get('message', '')}")
                            
                            if 'details' in data:
                                details = data['details']
                                print(f"\n📊 RESUMEN FINAL:")
                                print(f"   Total canales: {details.get('total_channels', 0)}")
                                print(f"   Verificados: {details.get('checked', 0)}")
                                print(f"   Online: {details.get('online', 0)} ✅")
                                print(f"   Offline: {details.get('offline', 0)} ❌")
                                print(f"   Omitidos: {details.get('skipped', 0)} ⏭️")
                                print(f"   Tiempo total: {details.get('elapsed_seconds', 0):.2f}s")
                                
                                total = details.get('checked', 0)
                                if total > 0:
                                    online_pct = (details.get('online', 0) / total) * 100
                                    offline_pct = (details.get('offline', 0) / total) * 100
                                    print(f"\n   Porcentaje Online: {online_pct:.1f}%")
                                    print(f"   Porcentaje Offline: {offline_pct:.1f}%")
                            
                            print("=" * 80)
                        
                        elif event_type == 'error':
                            print(f"\n❌ ERROR: {data.get('message', 'Unknown error')}")
                    
                    except json.JSONDecodeError as e:
                        print(f"⚠️  Error parsing JSON: {e}")
                        print(f"   Data: {data_str}")
        
        return True
        
    except requests.exceptions.Timeout:
        print(f"\n❌ TIMEOUT: La petición tardó más de 15 minutos")
        return False
        
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ ERROR DE CONEXIÓN: No se pudo conectar al servidor")
        print(f"   Error: {e}")
        return False
        
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {type(e).__name__}")
        print(f"   Mensaje: {e}")
        return False

if __name__ == "__main__":
    test_channel_check_sse()
