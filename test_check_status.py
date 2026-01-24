#!/usr/bin/env python3
"""
Test script para verificar el estado de todos los canales
"""
import requests
import json
import time
from datetime import datetime

def test_check_status():
    """Ejecuta el test de verificación de canales"""
    url = "http://localhost:6880/api/channels/check/stream"
    
    print("="*80)
    print("TEST: Verificación de Estado de Canales (Secuencial)")
    print("="*80)
    print(f"Inicio: {datetime.now().strftime('%H:%M:%S')}")
    print(f"URL: {url}")
    print("-"*80)
    
    start_time = time.time()
    
    try:
        # Hacer request con streaming
        response = requests.get(url, stream=True, timeout=600)
        
        if response.status_code != 200:
            print(f"❌ Error HTTP {response.status_code}")
            return
        
        # Procesar eventos SSE
        stats = {
            'total': 0,
            'checked': 0,
            'online': 0,
            'offline': 0,
            'skipped': 0,
            'errors': 0
        }
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                
                # Parsear eventos SSE
                if line.startswith('data: '):
                    data_str = line[6:]  # Remover "data: "
                    try:
                        data = json.loads(data_str)
                        event_type = data.get('type')
                        
                        if event_type == 'start':
                            print(f"🚀 {data.get('message')}")
                        
                        elif event_type == 'info':
                            print(f"ℹ️  {data.get('message')}")
                        
                        elif event_type == 'progress':
                            channel = data.get('channel', {})
                            stats_data = data.get('stats', {})
                            index = data.get('index')
                            total = data.get('total')
                            
                            # Actualizar stats
                            stats['checked'] = stats_data.get('checked', 0)
                            stats['online'] = stats_data.get('online', 0)
                            stats['offline'] = stats_data.get('offline', 0)
                            stats['skipped'] = stats_data.get('skipped', 0)
                            
                            status = channel.get('status')
                            name = channel.get('name', 'Unknown')
                            check_time = channel.get('check_time', 0)
                            
                            # Emoji según estado
                            if status == 'online':
                                emoji = "✅"
                            elif status == 'offline':
                                emoji = "❌"
                            else:
                                emoji = "⚠️"
                                stats['errors'] += 1
                            
                            # Mostrar progreso cada 10 canales o si es error
                            if index % 10 == 0 or status == 'error':
                                elapsed = time.time() - start_time
                                print(f"[{index}/{total}] {emoji} {name[:40]:40} | {check_time}s | Online: {stats['online']} Offline: {stats['offline']} | {elapsed:.1f}s")
                        
                        elif event_type == 'complete':
                            details = data.get('details', {})
                            stats['total'] = details.get('total_channels', 0)
                            stats['checked'] = details.get('checked', 0)
                            stats['online'] = details.get('online', 0)
                            stats['offline'] = details.get('offline', 0)
                            stats['skipped'] = details.get('skipped', 0)
                            elapsed = details.get('elapsed_seconds', 0)
                            
                            print("-"*80)
                            print(f"✅ {data.get('message')}")
                            print("-"*80)
                            print(f"📊 RESUMEN FINAL:")
                            print(f"   Total canales: {stats['total']}")
                            print(f"   Verificados: {stats['checked']}")
                            print(f"   ✅ Online: {stats['online']} ({stats['online']/stats['checked']*100:.1f}%)")
                            print(f"   ❌ Offline: {stats['offline']} ({stats['offline']/stats['checked']*100:.1f}%)")
                            print(f"   ⏭️  Skipped: {stats['skipped']}")
                            print(f"   ⚠️  Errors: {stats['errors']}")
                            print(f"   ⏱️  Tiempo total: {elapsed:.2f}s ({elapsed/60:.1f} min)")
                            print(f"   ⚡ Promedio: {elapsed/stats['checked']:.2f}s por canal")
                        
                        elif event_type == 'error':
                            print(f"❌ ERROR: {data.get('message')}")
                    
                    except json.JSONDecodeError as e:
                        print(f"⚠️  Error parseando JSON: {e}")
        
        total_elapsed = time.time() - start_time
        print("="*80)
        print(f"Fin: {datetime.now().strftime('%H:%M:%S')}")
        print(f"Duración total: {total_elapsed:.2f}s ({total_elapsed/60:.1f} min)")
        print("="*80)
        
        return stats
    
    except requests.exceptions.Timeout:
        print("❌ Timeout esperando respuesta del servidor")
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión con el servidor")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_check_status()
