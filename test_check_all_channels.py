"""
Test completo de verificación de canales usando SSE
"""
import requests
import json
import time

def test_check_all_channels():
    url = "http://localhost:6880/api/channels/check/stream"
    
    print("Iniciando test de verificación de canales...")
    print("=" * 80)
    
    start_time = time.time()
    
    try:
        response = requests.get(url, stream=True, timeout=600)
        
        if response.status_code != 200:
            print(f"ERROR: HTTP {response.status_code}")
            return
        
        checked = 0
        online = 0
        offline = 0
        errors = 0
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                
                if line.startswith('data: '):
                    data_str = line[6:]  # Remove 'data: ' prefix
                    
                    try:
                        data = json.loads(data_str)
                        msg_type = data.get('type')
                        
                        if msg_type == 'info':
                            print(f"\n[INFO] {data.get('message')}")
                        
                        elif msg_type == 'progress':
                            channel = data.get('channel', {})
                            stats = data.get('stats', {})
                            index = data.get('index')
                            total = data.get('total')
                            
                            checked = stats.get('checked', 0)
                            online = stats.get('online', 0)
                            offline = stats.get('offline', 0)
                            
                            status = channel.get('status', 'unknown')
                            name = channel.get('name', 'Unknown')
                            check_time = channel.get('check_time', 0)
                            
                            status_icon = "✅" if status == "online" else "❌" if status == "offline" else "⚠️"
                            
                            print(f"[{index}/{total}] {status_icon} {name[:40]:40} | {status:8} | {check_time:.2f}s | Online: {online} | Offline: {offline}")
                            
                            if status == "error":
                                errors += 1
                                error_msg = channel.get('error', 'Unknown error')
                                print(f"         ERROR: {error_msg}")
                        
                        elif msg_type == 'complete':
                            print("\n" + "=" * 80)
                            print("[COMPLETE] Test finalizado")
                            final_stats = data.get('stats', {})
                            print(f"Total verificados: {final_stats.get('checked', 0)}")
                            print(f"Online: {final_stats.get('online', 0)}")
                            print(f"Offline: {final_stats.get('offline', 0)}")
                            print(f"Skipped: {final_stats.get('skipped', 0)}")
                            break
                    
                    except json.JSONDecodeError as e:
                        print(f"Error parsing JSON: {e}")
                        print(f"Data: {data_str}")
        
        elapsed = time.time() - start_time
        print(f"\nTiempo total: {elapsed:.2f}s")
        print(f"Promedio por canal: {elapsed/checked:.2f}s" if checked > 0 else "")
        
    except requests.exceptions.Timeout:
        print("\nERROR: Timeout esperando respuesta")
    except Exception as e:
        print(f"\nERROR: {e}")

if __name__ == "__main__":
    test_check_all_channels()
