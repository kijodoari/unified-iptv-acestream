"""
Análisis de calidad de todos los IDs de AceStream usando /ace/getstream + ffprobe
Genera JSON con información técnica de cada stream
"""

import requests
import json
import uuid
import subprocess
import time
from datetime import datetime

# Configuración
ACESTREAM_HOST = "127.0.0.1"
ACESTREAM_PORT = 6878
BASE_URL = f"http://{ACESTREAM_HOST}:{ACESTREAM_PORT}"

# JSON de IPFS con los IDs
IPFS_JSON_URL = "https://ipfs.io/ipns/k51qzi5uqu5di462t7j4vu4akwfhvtjhy88qbupktvoacqfqe9uforjvhyi4wr/hashes.json"


def get_stream_url(acestream_id: str, timeout: int = 15) -> dict:
    """Obtiene playback_url usando /ace/getstream"""
    temp_pid = str(uuid.uuid4())
    
    url = f"{BASE_URL}/ace/getstream"
    params = {
        'id': acestream_id,
        'format': 'json',
        'pid': temp_pid
    }
    
    try:
        response = requests.get(url, params=params, timeout=timeout)
        
        if response.status_code != 200:
            return {'error': f"HTTP {response.status_code}"}
        
        data = response.json()
        
        if 'error' in data and data['error']:
            return {'error': data['error']}
        
        if 'response' in data and 'playback_url' in data['response']:
            return {
                'playback_url': data['response']['playback_url'],
                'command_url': data['response']['command_url'],
                'stat_url': data['response'].get('stat_url', '')
            }
        
        return {'error': 'Invalid response'}
        
    except Exception as e:
        return {'error': str(e)}


def get_stream_info_ffprobe(playback_url: str, timeout: int = 60) -> dict:
    """Usa ffprobe para obtener información del stream"""
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        playback_url
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode != 0:
            return {'error': f"ffprobe failed: {result.stderr[:200]}"}
        
        return json.loads(result.stdout)
        
    except subprocess.TimeoutExpired:
        return {'error': 'ffprobe timeout'}
    except FileNotFoundError:
        return {'error': 'ffprobe not found'}
    except Exception as e:
        return {'error': str(e)}


def stop_stream(command_url: str):
    """Detiene el stream"""
    try:
        stop_url = f"{command_url}?method=stop"
        requests.get(stop_url, timeout=5)
    except:
        pass


def extract_stream_info(probe_data: dict) -> dict:
    """Extrae información relevante del output de ffprobe"""
    info = {
        'format': {},
        'video': {},
        'audio': {}
    }
    
    # Formato
    if 'format' in probe_data:
        fmt = probe_data['format']
        info['format'] = {
            'format_name': fmt.get('format_name', 'N/A'),
            'duration': fmt.get('duration', 'N/A'),
            'bit_rate': fmt.get('bit_rate', 'N/A')
        }
    
    # Streams
    if 'streams' in probe_data:
        video_streams = [s for s in probe_data['streams'] if s['codec_type'] == 'video']
        audio_streams = [s for s in probe_data['streams'] if s['codec_type'] == 'audio']
        
        # Video (primer stream)
        if video_streams:
            v = video_streams[0]
            info['video'] = {
                'codec': v.get('codec_name', 'N/A'),
                'resolution': f"{v.get('width', 'N/A')}x{v.get('height', 'N/A')}",
                'width': v.get('width', 'N/A'),
                'height': v.get('height', 'N/A'),
                'fps': v.get('r_frame_rate', 'N/A'),
                'bit_rate': v.get('bit_rate', 'N/A'),
                'profile': v.get('profile', 'N/A'),
                'level': v.get('level', 'N/A')
            }
        
        # Audio (primer stream)
        if audio_streams:
            a = audio_streams[0]
            info['audio'] = {
                'codec': a.get('codec_name', 'N/A'),
                'channels': a.get('channels', 'N/A'),
                'sample_rate': a.get('sample_rate', 'N/A'),
                'bit_rate': a.get('bit_rate', 'N/A'),
                'language': a.get('tags', {}).get('language', 'N/A')
            }
    
    return info


def main():
    print("=" * 80)
    print("ANÁLISIS DE CALIDAD DE TODOS LOS STREAMS")
    print("Método: /ace/getstream + ffprobe")
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
    
    # Extraer IDs
    ids_to_check = []
    if 'hashes' in data and isinstance(data['hashes'], list):
        for item in data['hashes']:
            if isinstance(item, dict) and 'hash' in item:
                acestream_id = item['hash']
                if acestream_id and len(acestream_id) == 40:
                    ids_to_check.append({
                        'id': acestream_id,
                        'name': item.get('title', 'Unknown'),
                        'category': item.get('group', 'Unknown')
                    })
    
    total_ids = len(ids_to_check)
    print(f"📊 Total de IDs a analizar: {total_ids}")
    print()
    
    # Verificar ffprobe
    try:
        subprocess.run(['ffprobe', '-version'], capture_output=True, timeout=5)
        print("✅ ffprobe disponible")
    except FileNotFoundError:
        print("❌ ffprobe no encontrado - instala ffmpeg")
        return
    except Exception as e:
        print(f"❌ Error verificando ffprobe: {e}")
        return
    
    print()
    print("=" * 80)
    print("INICIANDO ANÁLISIS")
    print("=" * 80)
    print()
    
    results = []
    success_count = 0
    error_count = 0
    start_time = time.time()
    
    for index, item in enumerate(ids_to_check, 1):
        acestream_id = item['id']
        name = item['name']
        category = item['category']
        
        print(f"[{index}/{total_ids}] {name} ({category})")
        
        result = {
            'id': acestream_id,
            'name': name,
            'category': category,
            'status': 'error',
            'error': None,
            'quality': None
        }
        
        # Paso 1: Obtener playback_url
        stream_data = get_stream_url(acestream_id)
        
        if 'error' in stream_data:
            print(f"    ❌ Error obteniendo stream: {stream_data['error']}")
            result['error'] = stream_data['error']
            error_count += 1
            results.append(result)
            print()
            continue
        
        playback_url = stream_data['playback_url']
        command_url = stream_data['command_url']
        
        print(f"    ✅ Stream iniciado")
        
        # Esperar a que el stream esté listo
        time.sleep(5)
        
        # Paso 2: Analizar con ffprobe
        print(f"    🔍 Analizando con ffprobe...")
        probe_data = get_stream_info_ffprobe(playback_url)
        
        if 'error' in probe_data:
            print(f"    ❌ Error en ffprobe: {probe_data['error']}")
            result['error'] = probe_data['error']
            error_count += 1
        else:
            # Extraer información
            quality_info = extract_stream_info(probe_data)
            result['status'] = 'success'
            result['quality'] = quality_info
            success_count += 1
            
            # Mostrar resumen
            if quality_info['video'].get('resolution'):
                print(f"    ✅ {quality_info['video']['resolution']} | {quality_info['video']['codec']} | {quality_info['audio']['codec']}")
        
        # Detener stream
        stop_stream(command_url)
        
        results.append(result)
        print()
        
        # Pausa entre requests
        time.sleep(1)
    
    # Calcular tiempo total
    elapsed_time = time.time() - start_time
    
    # Mostrar resumen
    print("=" * 80)
    print("RESUMEN")
    print("=" * 80)
    print(f"Total analizado: {total_ids}")
    print(f"✅ Exitosos: {success_count} ({success_count/total_ids*100:.1f}%)")
    print(f"❌ Errores: {error_count} ({error_count/total_ids*100:.1f}%)")
    print(f"⏱️  Tiempo total: {elapsed_time:.1f} segundos")
    print(f"⚡ Promedio por ID: {elapsed_time/total_ids:.1f} segundos")
    print()
    
    # Guardar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"streams_quality_analysis_{timestamp}.json"
    
    output_data = {
        'generated': datetime.now().isoformat(),
        'total': total_ids,
        'success': success_count,
        'errors': error_count,
        'elapsed_time': elapsed_time,
        'streams': results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Resultados guardados en: {output_file}")
    print()
    
    # Estadísticas de calidad
    if success_count > 0:
        print("=" * 80)
        print("ESTADÍSTICAS DE CALIDAD")
        print("=" * 80)
        print()
        
        resolutions = {}
        codecs = {}
        
        for r in results:
            if r['status'] == 'success' and r['quality']:
                res = r['quality']['video'].get('resolution', 'N/A')
                codec = r['quality']['video'].get('codec', 'N/A')
                
                resolutions[res] = resolutions.get(res, 0) + 1
                codecs[codec] = codecs.get(codec, 0) + 1
        
        print("📺 Resoluciones:")
        for res, count in sorted(resolutions.items(), key=lambda x: x[1], reverse=True):
            print(f"   {res}: {count} streams ({count/success_count*100:.1f}%)")
        
        print()
        print("🎬 Codecs de video:")
        for codec, count in sorted(codecs.items(), key=lambda x: x[1], reverse=True):
            print(f"   {codec}: {count} streams ({count/success_count*100:.1f}%)")
        print()


if __name__ == "__main__":
    main()
