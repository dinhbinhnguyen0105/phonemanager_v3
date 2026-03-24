import sys
import ipaddress
from urllib.parse import urlparse
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from src.entities import ProxyType # Giả định file chứa Enum của bạn

def classify_proxy_type(rotate_url: str) -> ProxyType:
    if not rotate_url or not rotate_url.strip():
        return ProxyType.STATIC

    url = rotate_url.strip()
    
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url

    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            return ProxyType.API
        if hostname.lower() == 'localhost':
            return ProxyType.LOCAL
        try:
            ip = ipaddress.ip_address(hostname)
            if ip.is_private or ip.is_loopback:
                return ProxyType.LOCAL
            else:
                return ProxyType.API
                
        except ValueError:
            return ProxyType.API

    except Exception:
        return ProxyType.API


# ==========================================
# TEST THỬ VỚI 2 LINK CỦA BẠN:
# ==========================================
if __name__ == "__main__":
    url_1 = 'https://proxyxoay.shop/api/get.php?key=123'
    url_2 = 'http://192.168.2.21:5000/rotate/8081'
    url_3 = '' # Không nhập link

    print(f"URL 1 -> {classify_proxy_type(url_1).value}") 
    # Kết quả: api (Vì proxyxoay.shop là tên miền)
    
    print(f"URL 2 -> {classify_proxy_type(url_2).value}") 
    # Kết quả: local (Vì 192.168.2.21 là IP Private)
    
    print(f"URL 3 -> {classify_proxy_type(url_3).value}") 
    # Kết quả: static (Vì bỏ trống)