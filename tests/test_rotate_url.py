import sys
import subprocess
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.utils.logger import logger

def call_curl_command():
    url = "https://proxyxoay.shop/api/get.php?key=GSKgklgGCMQXVOVseRSnEF&&nhamang=random&&tinhthanh=0"
    
    try:
        # Chạy lệnh curl và lấy kết quả trả về
        result = subprocess.run(
            ["curl", "-s", url], 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        logger.info(f"Curl Output: {result.stdout}")
        return result.stdout
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Curl command failed: {e}")
        return None

if __name__ == "__main__":
    call_curl_command()

"""
curl -s https://proxyxoay.shop/api/get.php?key=GSKgklgGCMQXVOVseRSnEF&&nhamang=random&&tinhthanh=0
=> {
    "status": 100,
    "message": "proxy nay se die sau 1113s",
    "proxyhttp": "160.250.166.36:10715::",
    "proxysocks5": "160.250.166.36:11715::",
    "Nha Mang": "viettel",
    "Vi Tri": "NamDinh1",
    "Token expiration date": "13:20 22-03-2026",
    "ip": "116.97.131.165"
}

curl -s http://192.168.2.21:5000/rotate/8082
=> {
    "status": "success",
    "port": 8082,
    "new_ip": "192.168.0.143"
}
"""