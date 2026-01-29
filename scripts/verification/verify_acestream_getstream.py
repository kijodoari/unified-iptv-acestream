"""
Verificación de IDs de AceStream usando el método /ace/getstream
Este es el método que usa el proyecto padre wafy80/unified-iptv-acestream

Método: /ace/getstream
- Inicia el stream en AceStream Engine
- Devuelve playback_url si el ID es válido
- Más pesado que get_media_files porque inicia el stream
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Configuración
ACESTREAM_HOST = "127.0.0.1"
ACESTREAM_PORT = 6878
BASE_URL = f"http://{ACESTREAM_HOST}:{ACESTREAM_PORT}"

# JSON de IPFS con los IDs
IPFS_JSON_URL = "https://ipfs.io/ipns/k51qzi5uqu5di462t7j4vu4akwfhvtjhy88qbupktvoacqfqe9uforjvhyi4wr/hashes.json"


def check_id_with_getstream(acestream_id: str, timeout: int = 10) -> dict:
    """
    Verifica un ID de AceStream usando /ace/getstream
    Este método INICIA el stream en el engine
    
    Args:
        acestream_id: ID de AceStream a verificar
        timeout: Timeout en segundos
        
    Returns:
        dict con status, playback_url (si está disponible), y mensaje
    """
    # Generar PID único (como hace el proyecto padre)
    temp_pid = str(uuid.uuid4())
    
    # Endpoint y parámetros
    url = f"{BASE_URL}/ace/getstream"
    params = {
        'id': acestream_id,
        'format': 'json',
        'pid': temp_pid
    }
    
    try:
        # Hacer request
        response = requests.get(url, params=params, timeout=timeout)
        
        if response.status_code != 200:
            return {
                'status': 'offline',
                'available': False,
                'error': f"HTTP {response.status_code}",
                'response': response.text[:200]
            }
        
        # Parsear respuesta JSON
        data = response.json()
        
        # Verificar si hay error en la respuesta
        if 'error' in data and data['error']:
            return {
                'status': 'offline',
                'available': False,
                'error': data['error'],
                'response': data
            }
        
        # Verificar si tiene playback_url (señal de éxito)
        if 'response' in data and 'playback_url' in data['response']:
            playback_url = data['response']['playback_url']
            stat_url = data['response'].get('stat_url', '')
            command_url = data['response']['command_url']
            
            # IMPORTANTE: Detener el stream que acabamos de iniciar
            # El proyecto padre hace esto en _close_stream()
            try:
                stop_url = f"{command_url}?method=stop"
                requests.get(stop_url, timeout=5)
            except:
                pass  # Ignorar errores al detener
            
            return {
                'status': 'online',
                'available': True,
                'playback_url': playback_url,
                'stat_url': stat_url,
                'command_url': command_url,
                'response': data
            }
        
        # Respuesta inesperada
        return {
            'status': 'offline',
            'available': False,
            'error': 'Invalid response format',
            'response': data
        }
        
    except requests.Timeout:
        return {
            'status': 'offline',
            'available': False,
            'error': 'Timeout'
        }
    except requests.ConnectionError:
        return {
            'status': 'offline',
            'available': False,
            'error': 'Connection error - AceStream Engine no está corriendo'
        }
    except Exception as e:
        return {
            'status': 'offline',
            'available': False,
            'error': str(e)
        }


def main():
    """Función principal"""
    print("=" * 80)
    print("VERIFICACIÓN DE IDs DE ACESTREAM - MÉTODO /ace/getstream")
    print("(Método usado por wafy80/unified-iptv-acestream)")
    print("=" * 80)
    print()
    
    # Descargar JSON de IPFS
    print(f"📥 Descargando JSON desde IPFS...")
    try:
        response = requests.get(IPFS_JSON_URL, timeout=30)
        response.raise_for_status()
        data = response.json()
        print(f"✅ JSON descargado correctamente")
    except Exception as e:
        print(f"❌ Error descargando JSON: {e}")
        return
    
    # Extraer IDs - El JSON tiene estructura: {hashes: [{title, hash, group, logo}]}
    ids_to_check = []
    
    # Verificar estructura del JSON
    print(f"📋 Estructura del JSON:")
    if 'hashes' in data and isinstance(data['hashes'], list):
        print(f"   Formato: Array de hashes")
        print(f"   Total en JSON: {data.get('count', len(data['hashes']))}")
        
        for item in data['hashes']:
            if isinstance(item, dict) and 'hash' in item:
                acestream_id = item['hash']
                if acestream_id and len(acestream_id) == 40:  # IDs de acestream son 40 caracteres
                    ids_to_check.append({
                        'id': acestream_id,
                        'name': item.get('title', 'Unknown'),
                        'category': item.get('group', 'Unknown')
                    })
    else:
        print(f"   Claves principales: {list(data.keys())}")
    
    print()
    
    total_ids = len(ids_to_check)
    print(f"📊 Total de IDs a verificar: {total_ids}")
    
    if total_ids == 0:
        print("❌ No se encontraron IDs de AceStream en el JSON")
        print("   Verifica la estructura del JSON manualmente")
        return
    
    print()
    
    # Verificar conexión con AceStream Engine
    print(f"🔌 Verificando conexión con AceStream Engine en {BASE_URL}...")
    try:
        test_response = requests.get(f"{BASE_URL}/webui/api/service?method=get_version", timeout=5)
        if test_response.status_code == 200:
            version_data = test_response.json()
            if version_data.get('error') is None:
                version = version_data.get('result', {}).get('version', 'unknown')
                print(f"✅ AceStream Engine conectado - Versión: {version}")
            else:
                print(f"⚠️  AceStream Engine respondió con error: {version_data.get('error')}")
        else:
            print(f"⚠️  AceStream Engine respondió con HTTP {test_response.status_code}")
    except Exception as e:
        print(f"❌ No se puede conectar con AceStream Engine: {e}")
        print("   Asegúrate de que AceStream Engine está corriendo en el puerto 6878")
        return
    
    print()
    print("=" * 80)
    print("INICIANDO VERIFICACIÓN")
    print("=" * 80)
    print()
    
    # Contadores
    online_ids = []
    offline_ids = []
    start_time = time.time()
    
    # Verificar cada ID
    for index, item in enumerate(ids_to_check, 1):
        acestream_id = item['id']
        name = item['name']
        category = item['category']
        
        print(f"[{index}/{total_ids}] Verificando: {name} ({category})")
        print(f"    ID: {acestream_id}")
        
        result = check_id_with_getstream(acestream_id)
        
        if result['available']:
            print(f"    ✅ ONLINE")
            print(f"    Playback URL: {result['playback_url'][:60]}...")
            online_ids.append({
                'id': acestream_id,
                'name': name,
                'category': category,
                'playback_url': result['playback_url'],
                'command_url': result['command_url']
            })
        else:
            print(f"    ❌ OFFLINE - {result.get('error', 'Unknown error')}")
            offline_ids.append({
                'id': acestream_id,
                'name': name,
                'category': category,
                'error': result.get('error', 'Unknown')
            })
        
        print()
        
        # Pequeña pausa entre requests para no saturar el engine
        time.sleep(0.5)
    
    # Calcular tiempo total
    elapsed_time = time.time() - start_time
    
    # Mostrar resumen
    print("=" * 80)
    print("RESUMEN DE VERIFICACIÓN")
    print("=" * 80)
    print(f"Total de IDs verificados: {total_ids}")
    
    if total_ids > 0:
        print(f"✅ IDs ONLINE: {len(online_ids)} ({len(online_ids)/total_ids*100:.1f}%)")
        print(f"❌ IDs OFFLINE: {len(offline_ids)} ({len(offline_ids)/total_ids*100:.1f}%)")
        print(f"⏱️  Tiempo total: {elapsed_time:.1f} segundos")
        print(f"⚡ Promedio por ID: {elapsed_time/total_ids:.2f} segundos")
    else:
        print("⚠️  No se verificaron IDs")
    
    print()
    
    # Guardar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Guardar IDs activos
    active_file = f"acestream_active_getstream_{timestamp}.json"
    with open(active_file, 'w', encoding='utf-8') as f:
        json.dump(online_ids, f, indent=2, ensure_ascii=False)
    print(f"💾 IDs activos guardados en: {active_file}")
    
    # Guardar IDs inactivos
    inactive_file = f"acestream_inactive_getstream_{timestamp}.json"
    with open(inactive_file, 'w', encoding='utf-8') as f:
        json.dump(offline_ids, f, indent=2, ensure_ascii=False)
    print(f"💾 IDs inactivos guardados en: {inactive_file}")
    print()


if __name__ == "__main__":
    main()
