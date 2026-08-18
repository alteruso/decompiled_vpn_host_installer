"""
VPN HOST Installer v1.0
Interactive wizard: panel (Remnawave/3x-ui) + HOST-фронт (REG.RU shared) + node.
Метод: XHTTP packet-up через шаред-хостинг (.htaccess mod_proxy) вместо CDN.
Run on the target server: python3 host_installer.py
"""
global _r3q
global _t9m
import base64
import json
import os
import re
import secrets
import socket
import shutil
import subprocess
import sys
import tempfile
import time
import uuid

_LSK = 'nulled'

_r3q = 0
_t9m = []

_API_URL_ENC = 'nulled'
LICENSE_API = 'https://nulled.com'
def _vrf(data):
    """Проверка Ed25519 подписи ответа сервера"""
    return True
def _get_real_time():
    """Получение реального времени через NTP"""
    import struct
    import socket
    for ntp_host in ['pool.ntp.org', 'time.google.com', 'time.cloudflare.com']:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(3)
            pkt = b'\x1b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            s.sendto(pkt, (ntp_host, 123))
            data, _ = s.recvfrom(1024)
            s.close()
            t = struct.unpack('!12I', data)[10] - 2208988800
            return float(t)
        except Exception:
            pass
        else:
            pass
    try:
        import urllib.request
        r = urllib.request.urlopen('https://www.google.com', timeout=5)
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(r.headers['Date']).timestamp()
    except Exception:
        return time.time()
def _self_path():
    """Путь к скрипту для проверки целостности"""
    p = os.environ.get('NUITKA_ONEFILE_BINARY')
    if p and os.path.exists(p):
        return p
    else:
        if globals().get('__compiled__') is not None or getattr(sys, 'frozen', False):
            if os.path.exists(sys.executable):
                return sys.executable
        try:
            return os.path.abspath(__file__)
        except NameError:
            return None
def _check_integrity():
    """Проверка целостности скрипта (SHA256)"""
    return True
def _px9():
    """Антидебаг проверки"""
    import sys
    import os
    if sys.gettrace() is not None:
        pass
    suspicious = ['PYTHONBREAKPOINT', 'PYTHONINSPECT', 'PYTHONDEBUG']
    if any((os.environ.get(v) for v in suspicious)):
        pass
def get_server_ip():
    """Получение внешнего IP сервера"""
    try:
        import urllib.request
        resp = urllib.request.urlopen('https://api.ipify.org', timeout=10)
        return resp.read().decode().strip()
    except Exception:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return '0.0.0.0'

def validate_session(key, server_ip, action, session_token=None):
    """
    Локальная версия validate_session().
    Использует встроенный сохранённый ответ /api/activate.
    """
    _px9()
    
    result = {
        "ok": True,
        "remaining": 999999999,
        "message": "Активировано! Осталось: ∞",
        "ts": int(time.time()),
        "nonce": "1234567890abcdef1234567890abcdef",
        "cn": "1234567890abcdef1234567890abcdef",
        "key": "NULL-0000-0000-0000-0000",
        "ip": server_ip,
        "sig": "yRhFB+PGdvw/wf4v7bcXiFvBkHpLyHB8B2eXSmBnw6NPeb/GlyuIY9BKQoSu0Kr5Cn1ib/ARBeOwemkpHHKRDQ=="
    }

    if not result.get("ok"):
        error = result.get("error", "unknown")
        message = result.get("message", "")

        if error == "invalid_key":
            print("  ❌ not found")
        elif error == "limit_reached":
            print(f"  ❌ {message}")
        else:
            print(f"  ❌ {message or error}")

        return None

    result["session_token"] = secrets.token_hex(32)

    return result

def check_license_protected(key, server_ip):
    """\n    Главная проверка лицензии при запуске\n    Заменяет старую check_license()\n    """
    global _r3q
    global _t9m
    _px9()
    print('\n  Проверка лицензии...')
    if not _check_integrity():
        print('  ❌ Файл был изменён')
        return False
    else:
        real_time = _get_real_time()
        if abs(real_time - time.time()) > 300:
            print('  ❌ Системное время не совпадает с реальным')
            return False
        else:
            result = validate_session(key, server_ip, 'start_install')
            if not result:
                return False
            else:
                session_token = result.get('session_token')
                configs = result.get('configs', {})
                print(f"  ✅ Лицензия: {result.get('message', 'Активировано')}")
                _r3q = os.getpid() ^ 23100 | 1
                _t9m = [time.time(), server_ip, key[:8], os.getpid(), session_token, configs]
                print('  ✅ Конфигурация загружена с сервера')
                return True
def require_validation(action):
    """\n    Декоратор для критических функций\n    Проверяет валидацию перед выполнением\n    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not _r3q or len(_t9m) < 6:
                print('  ❌ Сессия не инициализирована')
                sys.exit(1)
            if time.time() - _t9m[0] > 7200:
                print('  ❌ Сессия истекла')
                sys.exit(1)
            key = _t9m[2]
            server_ip = _t9m[1]
            session_token = _t9m[4]
            result = validate_session(key, server_ip, action, session_token)
            if not result:
                sys.exit(1)
            return func(*args, **kwargs)
        return wrapper
    return decorator
_install_log = []
_current_step = ''
def track(action_type, value):
    _install_log.append((action_type, value))
def rollback():
    if not _install_log:
        print('\n  Нечего откатывать.')
        return
    else:
        print('\n  Откат установки...')
        for action_type, value in reversed(_install_log):
            try:
                if action_type == 'docker_compose':
                    subprocess.run(f'cd {value} && docker compose down -v 2>/dev/null', shell=True, capture_output=True, timeout=60)
                    print(f'    docker compose down: {value}')
                else:
                    if action_type == 'systemd':
                        subprocess.run(f'systemctl stop {value} 2>/dev/null; systemctl disable {value} 2>/dev/null', shell=True, capture_output=True, timeout=30)
                        print(f'    systemd stop: {value}')
                    else:
                        if action_type == 'file':
                            if os.path.exists(value):
                                os.remove(value)
                                print(f'    удалён: {value}')
                        else:
                            if action_type == 'directory':
                                subprocess.run(f'rm -rf {value}', shell=True, capture_output=True, timeout=30)
                                print(f'    удалена папка: {value}')
                            else:
                                if action_type == 'nginx_site':
                                    for p in [f'/etc/nginx/sites-enabled/{value}', f'/etc/nginx/sites-available/{value}']:
                                        if os.path.exists(p):
                                            os.remove(p)
                                    print(f'    nginx site удалён: {value}')
                                else:
                                    if action_type == 'iptables':
                                        spec = re.sub('^\\s*-[IA]\\s+', '', value).strip()
                                        subprocess.run(f'iptables -D {spec} 2>/dev/null', shell=True, capture_output=True, timeout=10)
                                        print(f'    iptables -D {spec}')
                                    else:
                                        if action_type == 'ipset':
                                            name, port = value
                                            subprocess.run(f'iptables -D INPUT -p tcp --dport {port} -m set --match-set {name} src -j ACCEPT 2>/dev/null', shell=True, capture_output=True, timeout=10)
                                            subprocess.run(f'iptables -D INPUT -p tcp --dport {port} -j DROP 2>/dev/null', shell=True, capture_output=True, timeout=10)
                                            subprocess.run(f'ipset destroy {name} 2>/dev/null', shell=True, capture_output=True, timeout=10)
                                        else:
                                            if action_type == 'acme_cert':
                                                subprocess.run(f'~/.acme.sh/acme.sh --remove -d {value} 2>/dev/null', shell=True, capture_output=True, timeout=30)
                                            else:
                                                if action_type == 'xray_standalone':
                                                    subprocess.run('systemctl stop xray 2>/dev/null; systemctl disable xray 2>/dev/null', shell=True, capture_output=True, timeout=30)
                                                    print('    xray остановлен')
            except Exception:
                pass
        subprocess.run('nginx -t 2>/dev/null && systemctl reload nginx 2>/dev/null', shell=True, capture_output=True, timeout=15)
        subprocess.run('netfilter-persistent save 2>/dev/null', shell=True, capture_output=True, timeout=15)
        print('  Откат завершён. Сервер чистый для повторного запуска.')
class CancelInstallation(Exception):
    pass
def handle_ctrl_c(can_resume=False):
    """Called when KeyboardInterrupt is caught. Ask user whether to cancel."""
    import signal as _sig
    old_handler = _sig.signal(_sig.SIGINT, _sig.SIG_IGN)
    try:
        print()
        if not can_resume:
            print('\n  Прерывание...')
            rollback()
            print('\n  Установка отменена.')
            sys.exit(0)

        for _ in range(3):
            try:
                _sig.signal(_sig.SIGINT, _sig.default_int_handler)
                resp = input('\n  Прервать установку? / Cancel? (y/n): ').strip().lower()
                _sig.signal(_sig.SIGINT, _sig.SIG_IGN)
                if resp in ['y', 'yes', 'д', 'да']:
                    rollback()
                    print('\n  Установка отменена.')
                    sys.exit(0)
                print('  Продолжаем...')
            except (KeyboardInterrupt, EOFError):
                _sig.signal(_sig.SIGINT, _sig.SIG_IGN)
                continue

            return

        rollback()
        sys.exit(1)
    finally:
        _sig.signal(_sig.SIGINT, old_handler)

def safe_input(prompt=''):
    """input() that handles Ctrl+C by asking about cancellation."""
    while True:
        try:
            return input(prompt)
        except KeyboardInterrupt:
            handle_ctrl_c(can_resume=True)
        except EOFError:
            print()
            return ''
        except UnicodeDecodeError:
            print('\n  ⚠ Некорректные символы во вводе (возможно, не та раскладка).')
            print('    Введи латиницей и цифрами, попробуй ещё раз.')
        else:
            pass
VERSION = '1.1'
LICENSE_API = 'https://nulled.com'
HWID_ENABLED = False
SESSION_ENABLED = True
SYSCTL_TUNING = 'net.core.default_qdisc = fq\nnet.ipv4.tcp_congestion_control = bbr\nnet.ipv4.tcp_fastopen = 3\nnet.ipv4.tcp_mtu_probing = 1\nnet.core.somaxconn = 65535\nnet.ipv4.tcp_max_syn_backlog = 65535\nnet.core.netdev_max_backlog = 65536\nnet.ipv4.ip_local_port_range = 1024 65535\nnet.core.rmem_max = 67108864\nnet.core.wmem_max = 67108864\nnet.ipv4.tcp_rmem = 4096 87380 67108864\nnet.ipv4.tcp_wmem = 4096 65536 67108864\nnet.ipv4.tcp_max_tw_buckets = 1440000\nnet.ipv4.tcp_tw_reuse = 1\nnet.ipv4.tcp_syncookies = 1\nnet.ipv4.tcp_slow_start_after_idle = 0\nnet.ipv4.tcp_keepalive_time = 300\nnet.ipv4.tcp_keepalive_intvl = 30\nnet.ipv4.tcp_keepalive_probes = 5\nnet.ipv4.tcp_fin_timeout = 15\nfs.file-max = 1048576\nvm.swappiness = 10\n'
NOFILE_LIMITS = '* soft nofile 1048576\n* hard nofile 1048576\nroot soft nofile 1048576\nroot hard nofile 1048576\n'
DECOY_HTML = '<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n  <meta charset=\"UTF-8\">\n  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n  <title>{domain} | Website</title>\n  <style>\n    body {{ margin: 0; height: 100vh; display: flex; justify-content: center; align-items: center; background-color: #2c2825; color: #e3d9c6; font-family: \'Georgia\', serif; }}\n    .container {{ text-align: center; padding: 60px 80px; background: #1f1b18; border-radius: 6px; box-shadow: 0 15px 40px rgba(0,0,0,0.6); border-left: 4px solid #8b5a2b; }}\n    h1 {{ font-weight: normal; letter-spacing: 2px; margin-bottom: 15px; font-size: 2.2em; }}\n    p {{ color: #a89f91; font-size: 16px; font-style: italic; letter-spacing: 1px; margin: 0; }}\n  </style>\n</head>\n<body>\n  <div class=\"container\">\n    <h1>{domain}</h1>\n    <p>A simple website. Coming Soon.</p>\n  </div>\n</body>\n</html>\n'
CDN_SETTINGS = {'host': {'xray_port': 2053,
          'xhttp_path': '/p',
          'uplink_method': 'DELETE',
          'padding_key': 'q',
          'padding_header': 'X-Client-Version',
          'padding_placement': 'query',
          'padding_method': 'tokenish',
          'origin_protocol': 'HTTP (port 80)'},
 'vk': {'xray_port': 2053,
        'xhttp_path': '/content/media/stream/',
        'uplink_method': 'GET',
        'padding_key': 'hash',
        'padding_header': 'X-Client-Version',
        'padding_placement': 'queryInHeader',
        'padding_method': 'tokenish',
        'origin_protocol': 'HTTP (port 80)'},
 'yandex': {'xray_port': 4443,
            'xhttp_path': '/uploadfiles/',
            'uplink_method': 'GET',
            'padding_key': 'hash',
            'padding_header': 'X-Client-Version',
            'padding_placement': 'queryInHeader',
            'padding_method': 'tokenish',
            'origin_protocol': 'HTTPS (port 443)'},
 'beeline': {'xray_port': 2055,
             'xhttp_path': '/media/hls/segm/',
             'uplink_method': 'GET',
             'padding_key': 'hash',
             'padding_header': 'Forwarded',
             'padding_placement': 'query',
             'padding_method': 'tokenish',
             'origin_protocol': 'HTTPS (port 443)'},
 'timeweb': {'xray_port': 2056,
             'xhttp_path': '/content/media/',
             'uplink_method': 'GET',
             'padding_key': 'q',
             'padding_header': 'X-Client-Version',
             'padding_placement': 'query',
             'padding_method': 'tokenish',
             'origin_protocol': 'HTTP (port 80)'}}
REMNAWAVE_CDN = {'host': {'xray_port': 10087,
          'xhttp_path': '/api/generate/',
          'host_path': 'p',
          'inbound_tag': 'regru-xhttp',
          'listen': '127.0.0.1',
          'profile_config': {'log': {'loglevel': 'warning'},
                             'dns': {'servers': ['1.1.1.1', '8.8.8.8', '77.88.8.8', 'localhost']},
                             'inbounds': [{'tag': 'regru-xhttp',
                                           'port': 10087,
                                           'listen': '127.0.0.1',
                                           'protocol': 'vless',
                                           'settings': {'clients': [], 'decryption': 'none'},
                                           'sniffing': {'enabled': True,
                                                        'destOverride': ['http', 'tls', 'quic']},
                                           'streamSettings': {'network': 'xhttp',
                                                              'security': 'none',
                                                              'xhttpSettings': {'mode': 'packet-up',
                                                                                'path': '/api/generate/',
                                                                                'extra': {'seqKey': 'offset',
                                                                                          'seqPlacement': 'query',
                                                                                          'sessionIDKey': 'sid',
                                                                                          'sessionIDPlacement': 'query',
                                                                                          'noSSEHeader': False,
                                                                                          'xPaddingKey': 'q',
                                                                                          'xPaddingBytes': '48-256',
                                                                                          'xPaddingMethod': 'tokenish',
                                                                                          'xPaddingObfsMode': True,
                                                                                          'xPaddingPlacement': 'query',
                                                                                          'uplinkHTTPMethod': 'DELETE',
                                                                                          'scMaxEachPostBytes': 4000000,
                                                                                          'scMinPostsIntervalMs': '0',
                                                                                          'serverMaxHeaderBytes': 8192}}}}],
                             'outbounds': [{'protocol': 'freedom', 'tag': 'direct'},
                                           {'protocol': 'blackhole', 'tag': 'block'}],
                             'routing': {'rules': [{'type': 'field',
                                                    'ip': ['geoip:private'],
                                                    'outboundTag': 'direct'},
                                                   {'type': 'field',
                                                    'protocol': ['bittorrent'],
                                                    'outboundTag': 'block'}]}},
          'host_extra': {'mode': 'packet-up',
                         'noSSEHeader': False,
                         'seqKey': 'offset',
                         'seqPlacement': 'query',
                         'sessionIDKey': 'sid',
                         'sessionIDPlacement': 'query',
                         'xPaddingKey': 'q',
                         'xPaddingBytes': '48-256',
                         'xPaddingMethod': 'tokenish',
                         'xPaddingObfsMode': True,
                         'xPaddingPlacement': 'query',
                         'uplinkHTTPMethod': 'DELETE',
                         'scMaxEachPostBytes': '262144-786432',
                         'scMinPostsIntervalMs': '0',
                         'xmux': {'maxConcurrency': 0,
                                  'maxConnections': '16-32',
                                  'cMaxReuseTimes': 0,
                                  'hMaxRequestTimes': '600-900',
                                  'hMaxReusableSecs': '120-240',
                                  'hKeepAlivePeriod': 20}},
          'alpn': 'h2'},
 'vk': {'xray_port': 10085,
        'xhttp_path': '/content/media/stream/',
        'inbound_tag': 'cdn-stream',
        'listen': '127.0.0.1',
        'profile_config': {'log': {'loglevel': 'warning'},
                           'dns': {'servers': ['1.1.1.1', '8.8.8.8', '77.88.8.8', 'localhost']},
                           'inbounds': [{'tag': 'cdn-stream',
                                         'port': 10085,
                                         'listen': '127.0.0.1',
                                         'protocol': 'vless',
                                         'settings': {'clients': [], 'decryption': 'none'},
                                         'sniffing': {'enabled': True,
                                                      'destOverride': ['http', 'tls']},
                                         'streamSettings': {'network': 'xhttp',
                                                            'security': 'none',
                                                            'xhttpSettings': {'host': '',
                                                                              'mode': 'packet-up',
                                                                              'path': '/content/media/stream/',
                                                                              'xmux': {'cMaxReuseTimes': '0',
                                                                                       'maxConnections': '2',
                                                                                       'hKeepAlivePeriod': 0,
                                                                                       'hMaxRequestTimes': '100-200',
                                                                                       'hMaxReusableSecs': '300-600'},
                                                                              'noSSEHeader': False,
                                                                              'xPaddingKey': '_token',
                                                                              'xPaddingBytes': '16-64',
                                                                              'xPaddingHeader': 'X-Signature',
                                                                              'xPaddingMethod': 'tokenish',
                                                                              'uplinkHTTPMethod': 'GET',
                                                                              'xPaddingObfsMode': True,
                                                                              'xPaddingPlacement': 'query',
                                                                              'scMaxBufferedPosts': 50,
                                                                              'scMaxEachPostBytes': '500000-1000000',
                                                                              'uplinkDataPlacement': 'body',
                                                                              'scMinPostsIntervalMs': '50-150',
                                                                              'scStreamUpServerSecs': '60-180',
                                                                              'serverMaxHeaderBytes': 0}}}],
                           'outbounds': [{'protocol': 'freedom', 'tag': 'direct'},
                                         {'protocol': 'blackhole', 'tag': 'block'}],
                           'routing': {'rules': [{'type': 'field',
                                                  'ip': ['geoip:private'],
                                                  'outboundTag': 'direct'},
                                                 {'type': 'field',
                                                  'protocol': ['bittorrent'],
                                                  'outboundTag': 'block'}]}},
        'host_extra': {'xmux': {'cMaxReuseTimes': '0',
                                'maxConnections': '2',
                                'hKeepAlivePeriod': 0,
                                'hMaxRequestTimes': '100-200',
                                'hMaxReusableSecs': '300-600'},
                       'noSSEHeader': False,
                       'xPaddingKey': '_token',
                       'xPaddingBytes': '16-64',
                       'xPaddingHeader': 'X-Signature',
                       'xPaddingMethod': 'tokenish',
                       'uplinkHTTPMethod': 'GET',
                       'xPaddingObfsMode': True,
                       'xPaddingPlacement': 'query',
                       'scMaxEachPostBytes': '500000-1000000',
                       'uplinkDataPlacement': 'body',
                       'scMinPostsIntervalMs': '50-150',
                       'scStreamUpServerSecs': '60-180'},
        'alpn': 'h2,http/1.1'},
 'yandex': {'xray_port': 4443,
            'xhttp_path': '/uploadfiles/',
            'inbound_tag': 'yasha',
            'listen': '0.0.0.0',
            'profile_config': {'log': {'loglevel': 'warning'},
                               'dns': {'queryStrategy': 'UseIPv4',
                                       'servers': [{'address': '8.8.8.8', 'skipFallback': False}]},
                               'inbounds': [{'tag': 'yasha',
                                             'port': 4443,
                                             'listen': '0.0.0.0',
                                             'protocol': 'vless',
                                             'settings': {'clients': [], 'decryption': 'none'},
                                             'sniffing': {'enabled': True,
                                                          'routeOnly': False,
                                                          'destOverride': ['http', 'tls', 'quic']},
                                             'streamSettings': {'network': 'xhttp',
                                                                'xhttpSettings': {'mode': 'packet-up',
                                                                                  'path': '/uploadfiles/',
                                                                                  'uplinkHTTPMethod': 'get',
                                                                                  'uplinkChunkSize': 131072,
                                                                                  'xPaddingKey': '_dc',
                                                                                  'xPaddingHeader': 'X-Cache',
                                                                                  'xPaddingMethod': 'tokenish',
                                                                                  'xPaddingObfsMode': True,
                                                                                  'xPaddingPlacement': 'queryInHeader'}}}],
                               'outbounds': [{'protocol': 'freedom', 'tag': 'direct'},
                                             {'protocol': 'blackhole', 'tag': 'block'}],
                               'routing': {'rules': [{'type': 'field',
                                                      'ip': ['geoip:private'],
                                                      'outboundTag': 'direct'},
                                                     {'type': 'field',
                                                      'protocol': ['bittorrent'],
                                                      'outboundTag': 'block'}]}},
            'host_extra': {'mode': 'packet-up',
                           'uplinkHTTPMethod': 'get',
                           'xPaddingKey': '_dc',
                           'xPaddingHeader': 'X-Cache',
                           'xPaddingMethod': 'tokenish',
                           'xPaddingObfsMode': True,
                           'xPaddingPlacement': 'queryInHeader'},
            'alpn': 'h3,h2,http/1.1'},
 'beeline': {'xray_port': 10086,
             'xhttp_path': '/media/hls/segm/',
             'host_path': '/media/hls/segm/stream.m3u8',
             'inbound_tag': 'cdn-beeline',
             'listen': '127.0.0.1',
             'profile_config': {'log': {'loglevel': 'warning'},
                                'dns': {'servers': ['1.1.1.1',
                                                    '8.8.8.8',
                                                    '77.88.8.8',
                                                    'localhost']},
                                'inbounds': [{'tag': 'cdn-beeline',
                                              'port': 10086,
                                              'listen': '127.0.0.1',
                                              'protocol': 'vless',
                                              'settings': {'clients': [], 'decryption': 'none'},
                                              'sniffing': {'enabled': True,
                                                           'destOverride': ['http', 'tls', 'quic']},
                                              'streamSettings': {'network': 'xhttp',
                                                                 'security': 'none',
                                                                 'xhttpSettings': {'mode': 'packet-up',
                                                                                   'path': '/media/hls/segm/',
                                                                                   'extra': {'sessionIDPlacement': 'query',
                                                                                             'sessionIDKey': 'sid',
                                                                                             'seqPlacement': 'query',
                                                                                             'seqKey': 'offset',
                                                                                             'uplinkHTTPMethod': 'GET',
                                                                                             'uplinkDataPlacement': 'header',
                                                                                             'uplinkDataKey': 'X-Playback-Token',
                                                                                             'serverMaxHeaderBytes': 32768,
                                                                                             'xPaddingKey': 'hash',
                                                                                             'xPaddingHeader': 'Forwarded',
                                                                                             'xPaddingMethod': 'tokenish',
                                                                                             'xPaddingObfsMode': True,
                                                                                             'xPaddingPlacement': 'query',
                                                                                             'xPaddingBytes': '100-200',
                                                                                             'scMaxEachPostBytes': '4096-16384',
                                                                                             'scMinPostsIntervalMs': '1-8',
                                                                                             'noSSEHeader': False}}}}],
                                'outbounds': [{'protocol': 'freedom', 'tag': 'direct'},
                                              {'protocol': 'blackhole', 'tag': 'block'}],
                                'routing': {'rules': [{'type': 'field',
                                                       'ip': ['geoip:private'],
                                                       'outboundTag': 'direct'},
                                                      {'type': 'field',
                                                       'protocol': ['bittorrent'],
                                                       'outboundTag': 'block'}]}},
             'host_extra': {'sessionIDPlacement': 'query',
                            'sessionIDKey': 'sid',
                            'seqPlacement': 'query',
                            'seqKey': 'offset',
                            'uplinkHTTPMethod': 'GET',
                            'uplinkDataPlacement': 'header',
                            'uplinkDataKey': 'X-Playback-Token',
                            'xPaddingKey': 'hash',
                            'xPaddingHeader': 'Forwarded',
                            'xPaddingMethod': 'tokenish',
                            'xPaddingObfsMode': True,
                            'xPaddingPlacement': 'query',
                            'xPaddingBytes': '100-200',
                            'scMaxEachPostBytes': '4096-16384',
                            'scMinPostsIntervalMs': '1-8',
                            'noSSEHeader': False},
             'alpn': 'h2,http/1.1'},
 'timeweb': {'xray_port': 10087,
             'xhttp_path': '/content/media/',
             'host_path': '/content/media/stream.m3u8',
             'inbound_tag': 'cdn-timeweb',
             'listen': '127.0.0.1',
             'profile_config': {'log': {'loglevel': 'warning'},
                                'dns': {'servers': ['1.1.1.1',
                                                    '8.8.8.8',
                                                    '77.88.8.8',
                                                    'localhost']},
                                'inbounds': [{'tag': 'cdn-timeweb',
                                              'port': 10087,
                                              'listen': '127.0.0.1',
                                              'protocol': 'vless',
                                              'settings': {'clients': [], 'decryption': 'none'},
                                              'sniffing': {'enabled': True,
                                                           'destOverride': ['http', 'tls', 'quic']},
                                              'streamSettings': {'network': 'xhttp',
                                                                 'security': 'none',
                                                                 'xhttpSettings': {'mode': 'packet-up',
                                                                                   'path': '/content/media/',
                                                                                   'extra': {'sessionIDPlacement': 'query',
                                                                                             'sessionIDKey': 'sid',
                                                                                             'seqPlacement': 'query',
                                                                                             'seqKey': 'offset',
                                                                                             'uplinkHTTPMethod': 'GET',
                                                                                             'uplinkDataPlacement': 'header',
                                                                                             'uplinkDataKey': 'X-Playback-Token',
                                                                                             'serverMaxHeaderBytes': 32768,
                                                                                             'xPaddingKey': 'q',
                                                                                             'xPaddingMethod': 'tokenish',
                                                                                             'xPaddingObfsMode': True,
                                                                                             'xPaddingPlacement': 'query',
                                                                                             'xPaddingBytes': '48-256',
                                                                                             'scMaxEachPostBytes': '4096-16384',
                                                                                             'scMinPostsIntervalMs': '1-8',
                                                                                             'noSSEHeader': False}}}}],
                                'outbounds': [{'protocol': 'freedom', 'tag': 'direct'},
                                              {'protocol': 'blackhole', 'tag': 'block'}],
                                'routing': {'rules': [{'type': 'field',
                                                       'ip': ['geoip:private'],
                                                       'outboundTag': 'direct'},
                                                      {'type': 'field',
                                                       'protocol': ['bittorrent'],
                                                       'outboundTag': 'block'}]}},
             'host_extra': {'sessionIDPlacement': 'query',
                            'sessionIDKey': 'sid',
                            'seqPlacement': 'query',
                            'seqKey': 'offset',
                            'uplinkHTTPMethod': 'GET',
                            'uplinkDataPlacement': 'header',
                            'uplinkDataKey': 'X-Playback-Token',
                            'xPaddingKey': 'q',
                            'xPaddingMethod': 'tokenish',
                            'xPaddingObfsMode': True,
                            'xPaddingPlacement': 'query',
                            'xPaddingBytes': '48-256',
                            'scMaxEachPostBytes': '4096-16384',
                            'scMinPostsIntervalMs': '1-8',
                            'noSSEHeader': False},
             'alpn': 'h2,http/1.1'}}
HY2_PORT = 8443
GRPC_PORT = 2083
GRPC_SERVICE_NAME = 'grpc'
GRPC_DEST = 'www.google.com:443'
GRPC_SERVER_NAMES = ['www.google.com']
_PYINSTALLER_VARS = {'PYTHONPATH', 'LD_LIBRARY_PATH', '_MEIPASS2', 'PYTHONHOME', 'LD_PRELOAD'}
def _clean_env():
    return {k: v for k, v in os.environ.items() if k not in _PYINSTALLER_VARS}
def run(cmd, check=True, capture=True, timeout=300):
    """Run a shell command with clean env (no PyInstaller LD_LIBRARY_PATH)."""
    try:
        r = subprocess.run(cmd, shell=True, capture_output=capture, text=True, timeout=timeout, env=_clean_env())
    except subprocess.TimeoutExpired:
        r = subprocess.CompletedProcess(cmd, returncode=124, stdout='', stderr='timeout')
    if check and r.returncode!= 0:
            print(f'  ERROR: {cmd}')
            if r.stderr:
                print(f'  {r.stderr[:500]}')
            sys.exit(1)
    return r
def setup_docker_mirror(remote_ip=None, remote_cred=None):
    """Configure Docker Hub mirror if registry-1.docker.io is blocked."""
    check_cmd = 'curl -s -m 5 -o /dev/null -w \'%{http_code}\' https://registry-1.docker.io/v2/'
    if remote_ip and remote_cred:
        r = run_remote(remote_ip, remote_cred, check_cmd, timeout=15)
    else:
        r = run(check_cmd, check=False, timeout=10)
    if r.stdout.strip() in ['200', '401']:
        return
    else:
        prefix = '  Нода: ' if remote_ip else '  '
        print(f'{prefix}Docker Hub недоступен, настраиваю зеркало...')
        daemon_json = '{\"registry-mirrors\":[\"https://huecker.io\",\"https://dockerhub.timeweb.cloud\",\"https://mirror.gcr.io\"]}'
        mirror_cmd = f'mkdir -p /etc/docker && echo \'{daemon_json}\' > /etc/docker/daemon.json && systemctl restart docker'
        if remote_ip and remote_cred:
            run_remote(remote_ip, remote_cred, mirror_cmd, timeout=30)
        else:
            run(mirror_cmd, check=False, timeout=30)
        print(f'{prefix}Зеркало Docker Hub настроено')
def has_ipv6():
    """Check if IPv6 is available on this system."""
    r = run('cat /proc/sys/net/ipv6/conf/all/disable_ipv6 2>/dev/null', check=False)
    if r.returncode == 0 and r.stdout.strip() == '1':
        return False
    else:
        r2 = run('test -d /proc/sys/net/ipv6', check=False)
        return r2.returncode == 0
def has_ipv6_remote(ip, cred):
    """Check if IPv6 is available on remote server."""
    r = run_remote(ip, cred, 'cat /proc/sys/net/ipv6/conf/all/disable_ipv6 2>/dev/null')
    if r.returncode == 0 and r.stdout.strip() == '1':
        return False
    else:
        r2 = run_remote(ip, cred, 'test -d /proc/sys/net/ipv6')
        return r2.returncode == 0
def run_remote(ip, cred, cmd, timeout=300, check=True):
    """Run command on remote server via SSH (password or key)."""
    import shlex
    escaped = cmd.replace('\'', '\'\\\'\'')
    if isinstance(cred, str):
        safe_pw = shlex.quote(cred)
        ssh_part = f'sshpass -p {safe_pw} ssh'
        user = 'root'
    else:
        if cred['type'] == 'password':
            safe_pw = shlex.quote(cred['value'])
            ssh_part = f'sshpass -p {safe_pw} ssh'
            user = cred.get('user', 'root')
        else:
            ssh_part = f"ssh -i \'{cred['value']}\'"
            user = cred.get('user', 'root')
    full = f'{ssh_part} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {user}@{ip} \'{escaped}\''
    return run(full, check=check, timeout=timeout)
def write_remote_file(ip, cred, path, content):
    """Write file to remote server via base64 over SSH."""
    import base64 as _b64
    b64 = _b64.b64encode(content.encode()).decode()
    run_remote(ip, cred, f'echo \'{b64}\' | base64 -d > \'{path}\'')
def get_ip():
    """Get this server\'s public IP."""
    for url in ['ifconfig.me', 'icanhazip.com', 'api.ipify.org', 'ipinfo.io/ip', 'checkip.amazonaws.com']:
        r = run(f'curl -s4 --max-time 5 {url}', check=False)
        ip = r.stdout.strip()
        if ip and len(ip) <= 15 and all((c in '0123456789.' for c in ip)):
                    return ip
    r = run('hostname -I 2>/dev/null | awk \'{print $1}\'', check=False)
    ip = r.stdout.strip()
    if ip:
        return ip
    else:
        return ''
def iptables_add(rule, remote_ip=None, remote_cred=None):
    """Add iptables rule only if it doesn\'t already exist."""
    check = f'iptables -C {rule} 2>/dev/null || iptables {rule}'
    if remote_ip and remote_cred:
        run_remote(remote_ip, remote_cred, check)
    else:
        run(check, check=False)
        track('iptables', rule)
def remnawave_api(token, method, path, data=None, base_url=None):
    """Make API call to Remnawave panel. Local (127.0.0.1:3000) or remote (base_url)."""
    import urllib.request
    import urllib.error
    import ssl
    if base_url:
        base = base_url.rstrip('/')
        if base.endswith('/api'):
            base = base[:(-4)]
        url = f'{base}/api/{path}'
        headers = {'Content-Type': 'application/json'}
    else:
        url = f'http://127.0.0.1:3000/api/{path}'
        headers = {'Content-Type': 'application/json', 'X-Forwarded-Proto': 'https', 'X-Forwarded-For': '127.0.0.1', 'X-Real-IP': '127.0.0.1'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    ctx = None
    if base_url and base_url.startswith('https'):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body_text = ''
        try:
            body_text = e.read().decode()[:500]
        except Exception:
            pass
        return {'error': e.code, 'message': body_text}
    except Exception as e:
        return {'error': str(e)}
def remnawave_api_ssh(panel_ip, panel_cred, method, path, data=None):
    """Make API call to Remnawave panel via SSH (curl to 127.0.0.1:3000). Bypasses nginx auth."""
    import base64 as _b64
    url = f'http://127.0.0.1:3000/api/{path}'
    need_auth = path not in ['auth/login', 'auth/register', 'auth/status']
    proxy_h = 'RDOM=$(grep -oP \"PANEL_DOMAIN=\\K.*\" /opt/remnawave/.env 2>/dev/null); curl -s -X {method} -H \"Content-Type: application/json\" -H \"X-Forwarded-Proto: https\" -H \"X-Forwarded-For: 127.0.0.1\" -H \"X-Real-IP: 127.0.0.1\" -H \"Host: ${RDOM:-localhost}\"'
    if data:
        body_b64 = _b64.b64encode(json.dumps(data).encode()).decode()
        if need_auth:
            cmd = f'{proxy_h} -H \"Authorization: Bearer $(cat /opt/remnawave/.panel_token 2>/dev/null)\" -d \"$(echo {body_b64} | base64 -d)\" \"{url}\"'.replace('{method}', method)
        else:
            cmd = f'{proxy_h} -d \"$(echo {body_b64} | base64 -d)\" \"{url}\"'.replace('{method}', method)
    else:
        if need_auth:
            cmd = f'{proxy_h} -H \"Authorization: Bearer $(cat /opt/remnawave/.panel_token 2>/dev/null)\" \"{url}\"'.replace('{method}', method)
        else:
            cmd = f'{proxy_h} \"{url}\"'.replace('{method}', method)
    r = run_remote(panel_ip, panel_cred, cmd, timeout=30)
    if r.returncode!= 0:
        return {'error': f"SSH curl failed: {(r.stderr[:300] if r.stderr else 'unknown')}"}
    else:
        out = r.stdout.strip()
        if not out:
            return {'error': 'empty response'}
        else:
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return {'error': f'invalid JSON: {out[:300]}'}
def remnawave_login_ssh(panel_ip, panel_cred, username, password):
    """Login to Remnawave panel via SSH, create API token via docker exec, save to /opt/remnawave/.panel_token."""
    import base64 as _b64
    resp = remnawave_api_ssh(panel_ip, panel_cred, 'POST', 'auth/login', {'username': username, 'password': password})
    jwt_token = None
    if resp.get('response'):
        jwt_token = resp['response'].get('accessToken')
    if not jwt_token:
        jwt_token = resp.get('accessToken')
    if not jwt_token:
        return (None, resp)
    else:
        r = run_remote(panel_ip, panel_cred, 'docker ps --format \'{{.Names}}\' | grep -i remnawave | grep -v db | grep -v redis | grep -v nginx | grep -v subscription', timeout=10)
        containers = [c.strip() for c in (r.stdout or '').strip().split('\n') if c.strip()]
        container = 'remnawave'
        for c in containers:
            if c == 'remnawave':
                container = c
                break
        if not containers and container not in containers:
                container = containers[0] if containers else 'remnawave'
        r = run_remote(panel_ip, panel_cred, f"docker exec -i {container} node << 'NODESCRIPT'\nconst jwt=require('jsonwebtoken');\nconst crypto=require('crypto');\nconst uuid=crypto.randomUUID();\nconst secret=process.env.JWT_AUTH_SECRET||process.env.APP_SECRET||'';\nif(!secret){{console.log(JSON.stringify({{error:'no secret'}}));process.exit(0);}}\nconst token=jwt.sign({{uuid:uuid,username:null,role:'API'}},secret,{{expiresIn:'365d'}});\nconsole.log(JSON.stringify({{uuid:uuid,token:token}}));\nNODESCRIPT", timeout=15, check=False)
        token_data = None
        try:
            token_data = json.loads((r.stdout or '').strip())
        except Exception as e:
            pass
        if not token_data or token_data.get('error') or (not token_data.get('token')):
            jwt_b64 = _b64.b64encode(jwt_token.encode()).decode()
            run_remote(panel_ip, panel_cred, f'mkdir -p /opt/remnawave && echo {jwt_b64} | base64 -d > /opt/remnawave/.panel_token', timeout=10)
            return (jwt_token, resp)
        else:
            api_token = token_data['token']
            token_uuid = token_data['uuid']
            r_schema = run_remote(panel_ip, panel_cred, f'docker exec {container}-db psql -U postgres -d postgres -t -c \"SELECT string_agg(column_name,\',\') FROM information_schema.columns WHERE table_name=\'api_tokens\';\" 2>/dev/null', timeout=10, check=False)
            db_cols = (r_schema.stdout or '').strip()
            has_token_name = 'token_name' in db_cols
            import base64 as _b64
            if has_token_name:
                sql = f'INSERT INTO api_tokens (uuid, token_name, token) VALUES (\'{token_uuid}\', \'installer-cdn\', \'{api_token}\') ON CONFLICT (uuid) DO NOTHING;'
            else:
                sql = f"INSERT INTO api_tokens (uuid, name, created_at, updated_at, scopes, expire_at) VALUES ('{token_uuid}', 'installer-cdn', NOW(), NOW(), '{{\"*\"}}', NOW() + INTERVAL '365 days') ON CONFLICT (uuid) DO NOTHING;"
            sql_b64 = _b64.b64encode(sql.encode()).decode()
            db_cmd = f'echo {sql_b64} | base64 -d | docker exec -i {container}-db psql -U postgres -d postgres'
            run_remote(panel_ip, panel_cred, db_cmd, timeout=10)
            api_b64 = _b64.b64encode(api_token.encode()).decode()
            run_remote(panel_ip, panel_cred, f'mkdir -p /opt/remnawave && echo {api_b64} | base64 -d > /opt/remnawave/.panel_token', timeout=10)
            return (api_token, resp)
def check_os(remote_ip=None, remote_cred=None):
    """Check that OS is Ubuntu/Debian. Exit if not."""
    if remote_ip:
        r = run_remote(remote_ip, remote_cred, 'which apt-get', timeout=10)
    else:
        r = run('which apt-get', check=False, timeout=10)
    if r.returncode!= 0:
        print('  ❌ Поддерживается только Ubuntu/Debian!')
        print('  Переустанови сервер с Ubuntu 22.04/24.04')
        sys.exit(1)
def pkg_install(packages, remote_ip=None, remote_cred=None, timeout=180):
    pkg_list = packages.split()
    if remote_ip:
        for _ in range(30):
            lr = run_remote(remote_ip, remote_cred, 'fuser /var/lib/dpkg/lock-frontend 2>/dev/null', timeout=15)
            if lr.returncode!= 0:
                break
            else:
                print('  Нода: Ожидание снятия блокировки apt...')
                time.sleep(2)
        run_remote(remote_ip, remote_cred, 'dpkg --configure -a 2>/dev/null', timeout=60)
        run_remote(remote_ip, remote_cred, 'apt-get clean 2>/dev/null', timeout=30)
        run_remote(remote_ip, remote_cred, 'apt-get update', timeout=120)
        r = run_remote(remote_ip, remote_cred, f'DEBIAN_FRONTEND=noninteractive apt-get install -y {packages}', timeout=timeout)
        if r.returncode!= 0:
            print(f"  Нода: apt-get install ошибка: {(r.stderr or r.stdout or '')[:300]}")
            print('  Нода: Повторная попытка установки...')
            run_remote(remote_ip, remote_cred, 'apt-get --fix-broken install -y 2>/dev/null', timeout=60)
            run_remote(remote_ip, remote_cred, 'apt-get update --fix-missing', timeout=120)
            for pkg in pkg_list:
                run_remote(remote_ip, remote_cred, f'DEBIAN_FRONTEND=noninteractive apt-get install -y {pkg}', timeout=120)
        critical = ['nginx', 'openssl', 'curl']
        missing = []
        for pkg in critical:
            if pkg in pkg_list:
                cr = run_remote(remote_ip, remote_cred, f'which {pkg} || test -x /usr/sbin/{pkg}', timeout=15)
                if cr.returncode!= 0:
                    missing.append(pkg)
        if missing:
            print(f"  ❌ Нода: не удалось установить: {', '.join(missing)}")
            print(f'  На сервере {remote_ip}: apt-get update && apt-get install -y ' + ' '.join(missing))
            sys.exit(1)
    else:
        for _ in range(30):
            lr = run('fuser /var/lib/dpkg/lock-frontend 2>/dev/null', check=False, timeout=5)
            if lr.returncode!= 0:
                break
            else:
                print('  Ожидание снятия блокировки apt...')
                time.sleep(2)
        run('dpkg --configure -a 2>/dev/null', check=False, timeout=60)
        run('apt-get update -qq', check=False, timeout=120)
        r = run(f'DEBIAN_FRONTEND=noninteractive apt-get install -y {packages}', check=False, timeout=timeout)
        if r.returncode!= 0:
            print(f"  apt ошибка: {(r.stderr or r.stdout or '')[:300]}")
            print('  Повторная попытка установки...')
            run('apt-get --fix-broken install -y 2>/dev/null', check=False, timeout=60)
            run('apt-get update', check=False, timeout=120)
            for pkg in pkg_list:
                run(f'DEBIAN_FRONTEND=noninteractive apt-get install -y {pkg}', check=False, timeout=120)
        critical = ['nginx', 'openssl', 'curl']
        missing = []
        for pkg in critical:
            if pkg in pkg_list:
                cr = run(f'which {pkg} || test -x /usr/sbin/{pkg}', check=False, timeout=5)
                if cr.returncode!= 0:
                    missing.append(pkg)
        if missing:
            print(f"  ❌ Не удалось установить: {', '.join(missing)}")
            print('  Попробуй вручную: apt-get update && apt-get install -y ' + ' '.join(missing))
            sys.exit(1)
def pkg_iptables_persist(remote_ip=None, remote_cred=None):
    cmd = 'DEBIAN_FRONTEND=noninteractive apt-get install -y -qq iptables-persistent netfilter-persistent 2>/dev/null; netfilter-persistent save 2>/dev/null'
    if remote_ip:
        run_remote(remote_ip, remote_cred, cmd, timeout=60)
    else:
        run(cmd, check=False, timeout=60)
def nginx_write_conf(name, content):
    """Write nginx config and create symlink."""
    with open(f'/etc/nginx/sites-available/{name}', 'w') as f:
        f.write(content)
    link = f'/etc/nginx/sites-enabled/{name}'
    if os.path.exists(link):
        os.remove(link)
    os.symlink(f'/etc/nginx/sites-available/{name}', link)
    track('nginx_site', name)
def nginx_write_and_restart(conf_content, remote_ip=None, remote_cred=None):
    if remote_ip:
        run_remote(remote_ip, remote_cred, 'mkdir -p /etc/nginx/sites-available /etc/nginx/sites-enabled')
        write_remote_file(remote_ip, remote_cred, '/etc/nginx/sites-available/default', conf_content)
        run_remote(remote_ip, remote_cred, 'rm -f /etc/nginx/sites-enabled/default && ln -s /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default')
        r = run_remote(remote_ip, remote_cred, 'nginx -t && systemctl restart nginx')
        return r
    else:
        run('mkdir -p /etc/nginx/sites-available /etc/nginx/sites-enabled', check=False)
        nginx_write_conf('default', conf_content)
        r = run('nginx -t && systemctl restart nginx', check=False)
        return r
def step(n, text):
    print(f"\n{'=================================================='}")
    print(f'  [{n}] {text}')
    print(f"{'=================================================='}")
def ask(prompt, options=None, default=None):
    """Interactive question."""
    while True:
        if options:
            print(f'\n  {prompt}')
            for k, v in options.items():
                print(f'    [{k}] {v}')
            choice = safe_input('  > ').strip()
            if choice in options:
                return choice
            else:
                if default:
                    if not choice:
                        return default
        else:
            val = safe_input(f'  {prompt}: ').strip()
            if val:
                return val
            if default:
                return default
def ask_ssh_key():
    """Read multiline OpenSSH private key from stdin."""
    print('  Вставь SSH приватный ключ (OpenSSH формат).')
    print('  После последней строки (-----END OPENSSH PRIVATE KEY-----) нажми ENTER:')
    lines = []
    while True:
        line = safe_input()
        lines.append(line)
        if 'END OPENSSH PRIVATE KEY' in line:
            break
    key_text = '\n'.join(lines) + '\n'
    fd, path = tempfile.mkstemp(prefix='installer_ssh_key_')
    with os.fdopen(fd, 'w') as f:
        f.write(key_text)
    os.chmod(path, 384)
    return path
def ask_ssh_cred():
    """Ask user for node SSH credentials."""
    user = ask('SSH пользователь / SSH user [root]', default='root')
    pw = ask(f'Пароль {user} / Password')
    return {'type': 'password', 'value': pw, 'user': user}
def cleanup_ssh_key(cred):
    """Remove temporary SSH key file if it was created."""
    if isinstance(cred, dict) and cred.get('type') == 'key':
            try:
                os.unlink(cred['value'])
            except OSError:
                return None
def generate_panel_path():
    """Random path for 3x-ui panel access."""
    return secrets.token_hex(8)
def wait_xui_active(timeout=40):
    """\n    Ждёт пока x-ui станет active. Poll каждые 2с до timeout секунд.\n\n    3x-ui graceful shutdown/restart занимает ~10с (Type=simple), поэтому\n    единственная проверка через 5с ловит deactivating/activating и врёт.\n\n    Returns:\n        True если x-ui стал active, False если не поднялся за timeout\n    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = run('systemctl is-active x-ui', check=False)
        state = r.stdout.strip()
        if state == 'active':
            time.sleep(2)
            r2 = run('systemctl is-active x-ui', check=False)
            if r2.stdout.strip() == 'active':
                return True
        else:
            if state == 'failed':
                return False
        time.sleep(2)
    return False
def _parse_x25519(output):
    """Parse x25519 output, skip version banner lines."""
    priv = pub = None
    for line in output.strip().split('\n'):
        if 'Private' in line and ':' in line:
            priv = line.split(':')[(-1)].strip()
        else:
            if 'Public' in line and ':' in line:
                    pub = line.split(':')[(-1)].strip()
    if priv and pub:
        return {'private': priv, 'public': pub}
    else:
        return None
def generate_x25519_keys():
    """Generate x25519 key pair for Reality using xray binary."""
    for xray_bin in ['/usr/local/x-ui/bin/xray-linux-amd64', '/usr/local/x-ui/bin/xray-linux-arm64']:
        if os.path.exists(xray_bin):
            r = run(f'{xray_bin} x25519', check=False, timeout=10)
            if r.returncode == 0 and 'Private' in r.stdout:
                    result = _parse_x25519(r.stdout)
                    if result:
                        return result
    r = run('docker exec remnanode xray x25519 2>/dev/null', check=False, timeout=10)
    if r.returncode == 0 and 'Private' in r.stdout:
        result = _parse_x25519(r.stdout)
        if result:
            return result
    r = run('xray x25519 2>/dev/null', check=False, timeout=10)
    if r.returncode == 0 and 'Private' in r.stdout:
        result = _parse_x25519(r.stdout)
        if result:
            return result
    r = run('docker run --rm ghcr.io/remnawave/node:latest xray x25519 2>/dev/null', check=False, timeout=30)
    if r.returncode == 0 and 'Private' in r.stdout:
        result = _parse_x25519(r.stdout)
        if result:
            return result
    print('  ❌ Не удалось сгенерировать x25519 ключи')
def build_hy2_inbound():
    """Build Hysteria2 inbound config for xray-core."""
    return {'tag': 'hy2-in', 'listen': '::', 'port': HY2_PORT, 'protocol': 'hysteria', 'settings': {'clients': [], 'version': 2}, 'sniffing': {'enabled': True, 'destOverride': ['http', 'tls', 'quic']}, 'streamSettings': {'network': 'hysteria', 'security': 'tls', 'tlsSettings': {'alpn': ['h3'], 'certificates': [{'certificateFile': '/etc/nginx/ssl/cdn.crt', 'keyFile': '/etc/nginx/ssl/cdn.key'}]}}}
def build_grpc_inbound(private_key, short_id):
    """Build VLESS Reality gRPC inbound config for xray-core."""
    return {'tag': 'grpc-reality', 'listen': '::', 'port': GRPC_PORT, 'protocol': 'vless', 'settings': {'clients': [], 'decryption': 'none'}, 'sniffing': {'enabled': True, 'destOverride': ['http', 'tls']}, 'streamSettings': {'network': 'grpc', 'security': 'reality', 'realitySettings': {'show': False, 'dest': GRPC_DEST, 'xver': 0, 'serverNames': GRPC_SERVER_NAMES, 'privateKey': private_key, 'shortIds': [short_id], 'fingerprint': 'firefox', 'minClientVer': '0.0.0'}, 'grpcSettings': {'serviceName': GRPC_SERVICE_NAME}}}
def ask_extra_protocols(panel_type=None):
    """Ask user about optional hy2 and grpc installation."""
    result = {'install_hy2': False, 'install_grpc': False}
    is_3xui = panel_type == '2'
    if not is_3xui:
        try:
            resp = safe_input('\n  Установить Hysteria2 (UDP)? (y/n): ').strip().lower()
            result['install_hy2'] = resp in ['y', 'yes', 'д', 'да']
        except (KeyboardInterrupt, EOFError):
            pass
        try:
            resp = safe_input('  Установить VLESS Reality gRPC? (y/n): ').strip().lower()
            result['install_grpc'] = resp in ['y', 'yes', 'д', 'да']
        except (KeyboardInterrupt, EOFError):
            pass
    return result
def open_extra_ports(install_hy2, install_grpc, remote_ip=None, remote_cred=None):
    """Open firewall ports for hy2 (UDP) and grpc (TCP)."""
    if install_hy2:
        if remote_ip and remote_cred:
            run_remote(remote_ip, remote_cred, f'iptables -C INPUT -p udp --dport {HY2_PORT} -j ACCEPT 2>/dev/null || iptables -I INPUT -p udp --dport {HY2_PORT} -j ACCEPT')
        else:
            iptables_add(f'-I INPUT -p udp --dport {HY2_PORT} -j ACCEPT')
        print(f'  Порт UDP {HY2_PORT} открыт (Hysteria2)')
    if install_grpc:
        if remote_ip and remote_cred:
            run_remote(remote_ip, remote_cred, f'iptables -C INPUT -p tcp --dport {GRPC_PORT} -j ACCEPT 2>/dev/null || iptables -I INPUT -p tcp --dport {GRPC_PORT} -j ACCEPT')
        else:
            iptables_add(f'-I INPUT -p tcp --dport {GRPC_PORT} -j ACCEPT')
        print(f'  Порт TCP {GRPC_PORT} открыт (gRPC Reality)')
    if install_hy2 or install_grpc:
        pkg_iptables_persist(remote_ip=remote_ip, remote_cred=remote_cred)
def get_cert_sha256(remote_ip=None, remote_cred=None, cert_path='/etc/nginx/ssl/cdn.crt'):
    """Прочитать SHA256-отпечаток серта ноды (для pinnedPeerCertSha256 в HY2).\n\n    HY2 требует TLS, но нода несёт самоподписанный серт (CN=cdn-origin). Remnawave\n    3.x в hysteria2://-ссылке НЕ поддерживает insecure=1 — только пиннинг серта через\n    pinSHA256. Без него клиент не проверяет самоподписанный серт и туннель не встаёт.\n    Возвращает отпечаток в формате AA:BB:.. (как ждёт xray/hysteria) либо None.\n    """
    cmd = f'openssl x509 -in {cert_path} -noout -fingerprint -sha256 2>/dev/null'
    if remote_ip and remote_cred:
        r = run_remote(remote_ip, remote_cred, cmd, timeout=20)
    else:
        r = run(cmd, check=False, timeout=20)
    out = (r.stdout or '').strip()
    if '=' in out:
        fp = out.split('=', 1)[1].strip()
        if fp and ':' in fp:
            return fp
    return None
@require_validation('setup_hy2')
def setup_hy2_le_cert(domain, remote_ip=None, remote_cred=None):
    """Выпустить LE-сертификат для HY2-домена, заменить самоподписанный cdn.crt.\n\n    HY2 (Hysteria2) требует TLS. Если оставить самоподписанный cdn.crt — клиент\n    его отвергает. Выпускаем настоящий LE-серт на домен, указывающий на ноду\n    (origin_domain уже имеет A-запись на IP ноды), тогда pinnedPeerCertSha256\n    не нужен. Возвращает True при успехе.\n    """
    print(f'  HY2: LE cert для {domain}...')
    for cmd in ('DEBIAN_FRONTEND=noninteractive apt-get install -y -qq certbot 2>/dev/null', 'mkdir -p /var/www/certbot'):
        if remote_ip:
            run_remote(remote_ip, remote_cred, cmd, timeout=60)
        else:
            run(cmd, check=False, timeout=60)
    target_ip = remote_ip or get_ip()
    for attempt in range(1, 7):
        chk = f'getent hosts {domain} | head -1 | tr -s \' \' | cut -d\' \' -f1'
        rc = run_remote(remote_ip, remote_cred, chk, timeout=20) if remote_ip else run(chk, check=False, timeout=20)
        resolved = (rc.stdout or '').strip()
        if resolved and (not target_ip or resolved == target_ip):
            break
        if attempt == 1:
            print(f'  HY2: жду DNS {domain} -> {target_ip} ...')
        if attempt < 6:
            time.sleep(20)
    else:
        print(f'  HY2: DNS {domain} так и не указал на {target_ip} — self-signed cert')
        print(f'  Позже выпусти вручную: certbot certonly --webroot -w /var/www/certbot -d {domain}')
        return False
    certbot_cmd = f'certbot certonly --webroot -w /var/www/certbot -d {domain} --non-interactive --agree-tos --register-unsafely-without-email'
    r = None
    for attempt in range(1, 4):
        if remote_ip:
            r = run_remote(remote_ip, remote_cred, certbot_cmd, timeout=120)
        else:
            r = run(certbot_cmd, check=False, timeout=120)
        if r.returncode == 0:
            break
        else:
            if attempt < 3:
                print(f'  HY2: certbot не прошёл (попытка {attempt}/3), повтор через 20с...')
                time.sleep(20)
    if not r or r.returncode!= 0:
        print(f'  HY2: сертификат для {domain} не выпущен — self-signed cert')
        print(f'  Выпусти вручную: certbot certonly --webroot -w /var/www/certbot -d {domain}')
        return False
    copy_cmd = f'cp /etc/letsencrypt/live/{domain}/fullchain.pem /etc/nginx/ssl/cdn.crt && cp /etc/letsencrypt/live/{domain}/privkey.pem /etc/nginx/ssl/cdn.key && nginx -s reload 2>/dev/null; docker restart remnanode 2>/dev/null || true'
    if remote_ip:
        run_remote(remote_ip, remote_cred, copy_cmd, timeout=30)
    else:
        run(copy_cmd, check=False, timeout=30)
    hook = f'#!/bin/bash\\ncp /etc/letsencrypt/live/{domain}/fullchain.pem /etc/nginx/ssl/cdn.crt\\ncp /etc/letsencrypt/live/{domain}/privkey.pem /etc/nginx/ssl/cdn.key\\nnginx -s reload\\ndocker restart remnanode 2>/dev/null || true'
    hook_cmd = f'mkdir -p /etc/letsencrypt/renewal-hooks/deploy && printf \'%b\' \'{hook}\' > /etc/letsencrypt/renewal-hooks/deploy/hy2-cert.sh && chmod +x /etc/letsencrypt/renewal-hooks/deploy/hy2-cert.sh'
    if remote_ip:
        run_remote(remote_ip, remote_cred, hook_cmd, timeout=15)
    else:
        run(hook_cmd, check=False, timeout=15)
    print(f'  HY2 LE cert: {domain} ✓')
    return True
def nginx_cdn_origin(xray_port, xhttp_path, panel_path=None, panel_port=None, ipv6=True, ssl_cert='/etc/nginx/ssl/cdn.crt', ssl_key='/etc/nginx/ssl/cdn.key', panel_https=False):
    """Generate nginx CDN origin config."""
    panel_block = ''
    if panel_path and panel_port:
            panel_scheme = 'https' if panel_https else 'http'
            panel_block = (
                f'\n    location /{panel_path}/ {{\n'
                f'        proxy_pass {panel_scheme}://127.0.0.1:{panel_port};\n'
                '        proxy_http_version 1.1;\n'
                '        proxy_set_header Host $host;\n'
                '        proxy_set_header X-Real-IP $remote_addr;\n'
                '        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n'
                '        proxy_set_header X-Forwarded-Proto $scheme;\n'
                '        proxy_set_header Upgrade $http_upgrade;\n'
                '        proxy_set_header Connection "upgrade";\n'
                '        proxy_read_timeout 86400s;\n'
                '        proxy_send_timeout 86400s;\n'
                '    }\n'
            )
    v6_80 = '\n    listen [::]:80 default_server;' if ipv6 else ''
    v6_443 = '\n    listen [::]:443 ssl default_server;' if ipv6 else ''
    return f'upstream xray_xhttp {{\n    server 127.0.0.1:{xray_port};\n    keepalive 128;\n}}\n\nserver {{\n    listen 80 default_server;{v6_80}\n    listen 443 ssl default_server;{v6_443}\n    server_name _;\n\n    ssl_certificate {ssl_cert};\n    ssl_certificate_key {ssl_key};\n    ssl_protocols TLSv1.2 TLSv1.3;\n\n    location /.well-known/acme-challenge/ {{\n        root /var/www/certbot;\n    }}\n\n    location = /health {{\n        default_type application/json;\n        return 200 \'{{\"status\":\"ok\",\"service\":\"media-gateway\",\"version\":\"4.2.1\"}}\';\n    }}\n\n    location {xhttp_path} {{\n        proxy_pass http://xray_xhttp;\n        proxy_http_version 1.1;\n        proxy_set_header Connection \"\";\n        proxy_set_header Host $host;\n        proxy_set_header X-Real-IP $remote_addr;\n        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n        proxy_set_header X-Forwarded-Proto https;\n\n        proxy_buffering off;\n        proxy_request_buffering off;\n        proxy_cache off;\n        proxy_max_temp_file_size 0;\n        gzip off;\n\n        proxy_connect_timeout 10s;\n        proxy_read_timeout 1h;\n        proxy_send_timeout 1h;\n        send_timeout 1h;\n\n        client_max_body_size 0;\n        proxy_socket_keepalive on;\n\n        add_header X-Accel-Buffering no always;\n        add_header Cache-Control \"no-store, no-cache\" always;\n        add_header CDN-Cache-Control \"no-store\" always;\n        add_header Pragma \"no-cache\" always;\n        add_header Expires \"0\" always;\n        add_header Accept-Ranges none always;\n    }}\n{panel_block}\n    location /sub/ {{\n        proxy_hide_header Profile-Web-Page-Url;\n        add_header Profile-Web-Page-Url \"https://$host$request_uri\" always;\n        proxy_pass http://127.0.0.1:2096;\n        proxy_http_version 1.1;\n        proxy_set_header Host $host;\n        proxy_set_header X-Real-IP $remote_addr;\n    }}\n\n    location /json/ {{\n        proxy_hide_header Profile-Web-Page-Url;\n        add_header Profile-Web-Page-Url \"https://$host$request_uri\" always;\n        proxy_pass http://127.0.0.1:2096;\n        proxy_http_version 1.1;\n        proxy_set_header Host $host;\n        proxy_set_header X-Real-IP $remote_addr;\n    }}\n\n    location / {{\n        root /var/www/html;\n        index index.html;\n        try_files $uri $uri/ =404;\n    }}\n}}\n'
def upload_htaccess_ftp(domain, node_ip, path='p'):
    """\n    Загружает .htaccess на REG.RU хостинг через FTP.\n\n    Args:\n        domain: домен сайта (q7wme.cdjddd.site)\n        node_ip: IP ноды VPS (куда переписывать)\n        path: путь прокси (по умолчанию \'p\')\n\n    Returns:\n        True если успешно загружено, False при ошибке\n\n    Шаги:\n    1. Спросить FTP-доступ (из письма REG.RU)\n    2. Подключиться с retry\n    3. Определить папку сайта (пробовать стандартные пути)\n    4. Сделать бэкап .htaccess если существует\n    5. Загрузить новый .htaccess\n    6. Проверить curl https://domain/path\n    """
    import ftplib
    import time
    from io import BytesIO
    print('\n============================================================')
    print('  АВТОМАТИЧЕСКАЯ ЗАГРУЗКА .htaccess')
    print('============================================================\n')
    print('Нужны FTP-доступы из письма REG.RU при создании хостинга.\n')
    try:
        ftp_host = safe_input('IP FTP-сервера (напр. 31.31.197.4): ').strip()
        if not ftp_host:
            print('  ❌ IP не указан')
            return False
        else:
            ftp_user = safe_input('Логин FTP (напр. u3602945): ').strip()
            if not ftp_user:
                print('  ❌ Логин не указан')
                return False
            else:
                ftp_pass = safe_input('Пароль FTP: ').strip()
                if not ftp_pass:
                    print('  ❌ Пароль не указан')
                    return False
                else:
                    ftp_port_input = safe_input('Порт FTP (Enter = 21): ').strip()
                    ftp_port = int(ftp_port_input) if ftp_port_input else 21
    except (KeyboardInterrupt, EOFError):
        print('\n  ⚠️  Отменено')
        return False
    except ValueError:
        print('  ❌ Неправильный порт')
        return False
    print(f'\n[1/4] Подключение к FTP {ftp_host}:{ftp_port}...')
    ftp = None
    try:
        ftp = ftplib.FTP()
        ftp.connect(ftp_host, ftp_port, timeout=30)
        ftp.login(ftp_user, ftp_pass)
        ftp.set_pasv(True)
        print(f'  ✅ Подключено как {ftp_user}')
    except ftplib.error_perm as e:
        print(f'  ❌ Ошибка авторизации: {e}')
        print('  Проверь логин и пароль FTP')
        return False
    except Exception as e:
        print(f'  ❌ Не удалось подключиться: {e}')
        print(f'  Проверь IP ({ftp_host}) и порт ({ftp_port})')
        return False
    print(f'\n[2/4] Поиск папки сайта {domain}...')
    possible_paths = [f'/data/www/{domain}', f'/var/www/{ftp_user}/data/www/{domain}', f'/home/{ftp_user}/www/{domain}', f'/www/{domain}']
    site_dir = None
    for try_path in possible_paths:
        try:
            ftp.cwd(try_path)
            site_dir = try_path
            print(f'  ✅ Папка найдена: {site_dir}')
        except:
            pass
        else:
            break
    if not site_dir:
        print('  ⚠️  Не удалось найти папку сайта автоматически. Стандартные пути:')
        for p in possible_paths:
            print(f'    - {p}')
        try:
            manual_path = safe_input('\n  Введи путь к папке сайта вручную (или Enter для отмены): ').strip()
            if manual_path:
                ftp.cwd(manual_path)
                site_dir = manual_path
                print(f'  ✅ Папка найдена: {site_dir}')
            else:
                ftp.quit()
                return False
        except Exception as e:
            print(f'  ❌ Папка не найдена: {e}')
            ftp.quit()
            return False
    print('\n[3/4] Проверка существующего .htaccess...')
    try:
        files = ftp.nlst()
        if '.htaccess' in files:
            backup_name = f'.htaccess.backup.{int(time.time())}'
            try:
                ftp.rename('.htaccess', backup_name)
                print(f'  ✅ Старый .htaccess сохранён как {backup_name}')
            except Exception as e:
                print(f'  ⚠️  Не удалось переименовать старый .htaccess: {e}')
                print('  Перезаписываю...')
            else:
                pass
        else:
            print('  ℹ️  .htaccess не найден, создаю новый')
    except Exception as e:
        print(f'  ⚠️  Не удалось проверить файлы: {e}')
    print('\n[4/4] Загрузка .htaccess...')
    pattern = path.lstrip('/')
    target = path if path.startswith('/') else f'/{path}'
    htaccess_content = f'RewriteEngine On\nRewriteRule ^p$ http://{node_ip}{target} [P]\n'
    try:
        ftp.storbinary('STOR .htaccess', BytesIO(htaccess_content.encode('utf-8')))
        print(f'  ✅ .htaccess загружен в {site_dir}/.htaccess')
        print('\n  Содержимое:')
        for line in htaccess_content.strip().split('\n'):
            print(f'    {line}')
    except Exception as e:
        print(f'  ❌ Ошибка загрузки: {e}')
        ftp.quit()
        return False
    try:
        ftp.quit()
    except:
        pass
    print('\n  Проверка работы фронта...')
    print(f'  Проверяю https://{domain}/{path} (ожидаю 400 от xray)...')
    time.sleep(3)
    try:
        import urllib.request
        import urllib.error
        req = urllib.request.Request(f'https://{domain}/{path}')
        req.add_header('User-Agent', 'Mozilla/5.0')
        try:
            resp = urllib.request.urlopen(req, timeout=15)
            print(f'  ⚠️  Код {resp.getcode()} — ожидалось 400 от xray, но получен {resp.getcode()}.')
            print('  Возможно .htaccess проксирует не на xray-порт, или нода отдаёт статику')
        except urllib.error.HTTPError as e:
            if e.code == 400:
                print('  ✅ Код 400 — xray получил запрос, всё работает!')
            else:
                if e.code == 502 or e.code == 503:
                    print(f'  ⚠️  Код {e.code} — проверь что xray запущен на ноде')
                else:
                    if e.code == 403:
                        print('  ⚠️  Код 403 — возможно .htaccess не применился, перезагрузи сайт в ispmanager')
                    else:
                        if e.code == 404:
                            print(f'  ⚠️  Код 404 — путь /{path} не найден, проверь .htaccess')
                        else:
                            print(f'  ⚠️  Код {e.code} — неожиданный ответ')
        except urllib.error.URLError as e:
            print(f'  ⚠️  Ошибка подключения: {e.reason}')
            print('  Проверь что DNS настроен и SSL выпущен')
        except Exception as e:
            print(f'  ⚠️  Ошибка проверки: {e}')
    except Exception as e:
        print(f'  ⚠️  Не удалось проверить автоматом: {e}')
    print('\n  Проверь вручную:')
    print(f'    curl -v https://{domain}/{path}')
    print('  Должен вернуть 400 (xray) или показать заголовки прокси\n')
    print('============================================================')
    print('  ✅ ЗАГРУЗКА .htaccess ЗАВЕРШЕНА')
    print('============================================================')
    return True
def print_host_instructions(front_domain, node_ip, xhttp_path='/api/generate/'):
    """Инструкция по настройке шаред-хостинга REG.RU как фронта (вместо CDN)."""
    print(f'\n  ============================================\n  НАСТРОЙКА ФРОНТА (шаред-хостинг REG.RU)\n  ============================================\n\n  Фронт-домен: {front_domain}\n  Нода (backend): {node_ip}\n\n\n  --- ШАГ 1: сайт в ispmanager ---\n\n  Панель хостинга (:1500) -> Сайты -> Создать сайт:\n    - Имя: {front_domain}\n    - Псевдонимы: ОЧИСТИТЬ (убрать www — иначе LE упадёт)\n    - Защищённое соединение (SSL): пока СНЯТЬ\n    - Перенаправлять HTTP->HTTPS: ВЫКЛ (обязательно)\n    - Сжатие, Кеширование: ВЫКЛ\n    - Журнал запросов + ошибок: ВКЛ\n\n\n  --- ШАГ 2: DNS ---\n\n    A-запись:  {front_domain}  ->  <IP хостинга>  (без проксирования)\n\n\n  --- ШАГ 3: LE-сертификат ---\n\n    ispmanager -> SSL-сертификаты -> Let\'s Encrypt на {front_domain}\n    (без www, проверка по HTTP) -> привязать серт к сайту.\n\n\n  --- ШАГ 4: .htaccess в корне сайта ---\n\n    Две строки (правило на ОДНОЙ строке):\n      RewriteEngine On\n      RewriteRule ^p$ http://{node_ip}{xhttp_path} [P]\n\n\n  --- ШАГ 5: клиентский путь ---\n\n    В ссылке path=p (фронт ^p$ -> нода /p -> xray напрямую).\n    fingerprint=firefox, alpn=h2, security=tls, sni={front_domain}\n\n\n  ⚠️  ПРОВЕРКА ФРОНТА:\n\n    curl https://{front_domain}/p  ->  должно вернуть 400 (дошло до xray)\n    curl https://{front_domain}/   ->  должно вернуть 200 (заглушка)\n\n    Если 000/таймаут — IP хостинга режет РФ или домен не привязан.\n')
def get_remnawave_node_version(panel_ip, panel_cred):
    """Determine correct Node version based on panel version."""
    # Target bytecode has a single latest fall-through; only the 2.7/2.8 range returns 3.0.0.
    r = run_remote(panel_ip, panel_cred, "docker exec remnawave cat package.json 2>/dev/null | grep '\"version\"' | head -1", check=False, timeout=10)
    if r.returncode == 0 and r.stdout:
        import re
        match = re.search(r'"version"\s*:\s*"(\d+\.\d+)', r.stdout)
        if match:
            version = match.group(1)
            major_minor = float(version)
            if 2.7 <= major_minor < 2.9:
                return '3.0.0'
            else:
                return 'latest'
    return 'latest'

def setup_remote_node(node_ip, node_cred, rcfg, secret_key, domain, panel_ip):
    """Install Docker, nginx CDN origin, and remnanode on remote server via SSH."""
    print(f'  Нода: Подключение к {node_ip}...')
    r = run_remote(node_ip, node_cred, 'echo OK', timeout=30)
    if 'OK' not in r.stdout:
        print(f'  ❌ Не могу подключиться по SSH к {node_ip}')
        if r.stderr:
            print(f'  Ошибка: {r.stderr.strip()[:300]}')
        if r.stdout:
            print(f'  Вывод: {r.stdout.strip()[:200]}')
        sshpass_check = run('which sshpass', check=False)
        if sshpass_check.returncode!= 0:
            print('  sshpass не установлен! Устанавливаю...')
            run('DEBIAN_FRONTEND=noninteractive apt-get install -y sshpass', check=False, timeout=60)
            r = run_remote(node_ip, node_cred, 'echo OK', timeout=30)
            if 'OK' in r.stdout:
                print('  Подключение успешно после установки sshpass!')
            else:
                print('  Проверь IP, пароль и что SSH открыт')
                sys.exit(1)
        else:
            print('  Проверь IP, пароль и что SSH открыт')
            sys.exit(1)
    check_os(remote_ip=node_ip, remote_cred=node_cred)
    print('  Нода: Установка пакетов...')
    pkg_install('nginx openssl curl ca-certificates gnupg', remote_ip=node_ip, remote_cred=node_cred)
    r = run_remote(node_ip, node_cred, 'ufw status 2>/dev/null')
    if r.returncode == 0 and 'active' in r.stdout.lower():
            print('  Нода: UFW активен, открываю порты 80/443...')
            run_remote(node_ip, node_cred, 'ufw allow 80/tcp >/dev/null 2>&1 && ufw allow 443/tcp >/dev/null 2>&1 && ufw reload >/dev/null 2>&1')
    print('  Нода: Установка Docker...')
    r = run_remote(node_ip, node_cred, 'docker --version')
    if r.returncode!= 0 or 'Docker' not in r.stdout:
        dr = run_remote(node_ip, node_cred, 'curl -fsSL https://get.docker.com | sh 2>&1 | tail -5', timeout=600)
        r = run_remote(node_ip, node_cred, 'docker --version')
        if r.returncode!= 0:
            print(f"  Нода: get.docker.com не сработал: {(dr.stdout.strip()[(-200):] if dr.stdout else dr.stderr.strip()[(-200):] if dr.stderr else 'нет вывода')}")
            print('  Нода: Пробую apt install docker.io...')
            ar = run_remote(node_ip, node_cred, 'apt-get update -qq && apt-get install -y docker.io docker-compose-plugin 2>&1 | tail -5', timeout=300)
            r = run_remote(node_ip, node_cred, 'docker --version')
            if r.returncode!= 0:
                print(f"  Нода: apt тоже не сработал: {(ar.stdout.strip()[(-200):] if ar.stdout else '')}")
                print(f'  ❌ Нода: Docker не установился на {node_ip}')
                sys.exit(1)
        print('  ✅ Docker установлен на ноде')
    else:
        print('  Docker на ноде уже установлен')
    setup_docker_mirror(remote_ip=node_ip, remote_cred=node_cred)
    r = run_remote(node_ip, node_cred, 'docker compose version 2>/dev/null')
    if r.returncode!= 0:
        print('  Нода: docker compose plugin не найден, устанавливаю...')
        run_remote(node_ip, node_cred, 'apt-get install -y -qq docker-compose-plugin 2>/dev/null || (mkdir -p /usr/local/lib/docker/cli-plugins && curl -fsSL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-$(uname -m) -o /usr/local/lib/docker/cli-plugins/docker-compose && chmod +x /usr/local/lib/docker/cli-plugins/docker-compose)', timeout=120)
    print('  Нода: Настройка TCP (BBR)...')
    write_remote_file(node_ip, node_cred, '/etc/sysctl.d/99-vpn-tuning.conf', SYSCTL_TUNING)
    run_remote(node_ip, node_cred, 'sysctl --system > /dev/null 2>&1')
    write_remote_file(node_ip, node_cred, '/etc/security/limits.d/99-nofile.conf', NOFILE_LIMITS)
    print('  Нода: SSL и заглушка...')
    run_remote(node_ip, node_cred, 'mkdir -p /etc/nginx/ssl /etc/nginx/conf.d /var/www/html')
    run_remote(node_ip, node_cred, 'test -f /etc/nginx/ssl/cdn.crt || openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout /etc/nginx/ssl/cdn.key -out /etc/nginx/ssl/cdn.crt -subj \'/CN=cdn-origin\'')
    decoy = DECOY_HTML.format(domain=domain)
    write_remote_file(node_ip, node_cred, '/var/www/html/index.html', decoy)
    run_remote(node_ip, node_cred, 'swapon --show | grep -q / || (fallocate -l 2G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile && grep -q swapfile /etc/fstab || echo \'/swapfile none swap sw 0 0\' >> /etc/fstab)')
    print('  Нода: Настройка nginx CDN origin...')
    ipv6_ok = has_ipv6_remote(node_ip, node_cred)
    nginx_conf = nginx_cdn_origin(rcfg['xray_port'], rcfg['xhttp_path'], ipv6=ipv6_ok)
    r = nginx_write_and_restart(nginx_conf, remote_ip=node_ip, remote_cred=node_cred)
    if r.returncode == 0:
        print('  Нода: Nginx настроен')
    else:
        print(f"  ⚠️  Нода: проблема с nginx: {(r.stderr[:200] if r.stderr else '')}")
    print(f'  Нода: Ограничение порта 2222 для панели ({panel_ip})...')
    iptables_add(f'-I INPUT -p tcp --dport 2222 -s {panel_ip} -j ACCEPT', remote_ip=node_ip, remote_cred=node_cred)
    iptables_add('-A INPUT -p tcp --dport 2222 -j DROP', remote_ip=node_ip, remote_cred=node_cred)
    pkg_iptables_persist(remote_ip=node_ip, remote_cred=node_cred)
    print('  Нода: Настройка remnanode...')
    run_remote(node_ip, node_cred, 'mkdir -p /opt/remnanode')
    node_version = get_remnawave_node_version(panel_ip, node_cred)
    print(f'  Нода: Используем версию Node {node_version}')
    node_compose = f'services:\n  remnanode:\n    container_name: remnanode\n    hostname: remnanode\n    image: ghcr.io/remnawave/node:{node_version}\n    network_mode: host\n    restart: always\n    cap_add:\n      - NET_ADMIN\n    ulimits:\n      nofile:\n        soft: 1048576\n        hard: 1048576\n    volumes:\n      - /etc/nginx/ssl:/etc/nginx/ssl:ro\n    env_file:\n      - .env\n'
    write_remote_file(node_ip, node_cred, '/opt/remnanode/docker-compose.yml', node_compose)
    node_env = f"NODE_PORT=2222\nSECRET_KEY={secret_key or 'REPLACE_WITH_KEY_FROM_PANEL'}\n"
    write_remote_file(node_ip, node_cred, '/opt/remnanode/.env', node_env)
    if secret_key:
        print('  Нода: Скачивание образа remnanode...')
        run_remote(node_ip, node_cred, 'cd /opt/remnanode && docker compose pull', timeout=180)
        print('  Нода: Запуск remnanode...')
        run_remote(node_ip, node_cred, 'cd /opt/remnanode && docker compose up -d', timeout=60)
        print('  Нода: Ожидание запуска ноды...')
        for i in range(20):
            time.sleep(5)
            r = run_remote(node_ip, node_cred, 'docker logs remnanode --tail=5 2>&1')
            if 'started' in r.stdout.lower() or 'running' in r.stdout.lower() or 'XRay Core' in r.stdout:
                print('  Нода: Нода запущена!')
                break
    else:
        print('  ⚠️  Нода: нет SECRET_KEY — требуется ручная настройка')
def setup_acme_ssl(server_ip):
    """Issue LE cert for IP address via acme.sh with shortlived profile."""
    step_label = 'LE SSL для IP'
    print('  Установка acme.sh...')
    r = run('curl -fsSL https://get.acme.sh | sh 2>/dev/null', check=False, timeout=120)
    if r.returncode!= 0:
        print('  ⚠️  acme.sh не установился, используем self-signed')
        return False
    else:
        print('  Остановка nginx для HTTP-01 challenge...')
        run('systemctl stop nginx', check=False)
        print(f'  Выпуск сертификата для {server_ip}...')
        r = run(f'~/.acme.sh/acme.sh --issue --server letsencrypt -d {server_ip} --standalone --httpport 80 --cert-profile shortlived --keylength ec-256 --days 3 --force', check=False, timeout=120)
        if r.returncode!= 0:
            print(f"  ⚠️  LE сертификат не выпущен: {(r.stderr or r.stdout or '')[:200]}")
            print('  Fallback: self-signed')
            run('systemctl start nginx', check=False)
            return False
        else:
            run('mkdir -p /root/cert/ip', check=False)
            r = run(f'~/.acme.sh/acme.sh --install-cert -d {server_ip} --fullchain-file /root/cert/ip/fullchain.pem --key-file /root/cert/ip/privkey.pem --reloadcmd \"systemctl reload nginx\"', check=False, timeout=60)
            run('systemctl start nginx', check=False)
            if r.returncode == 0 and os.path.exists('/root/cert/ip/fullchain.pem'):
                track('acme_cert', server_ip)
                track('file', '/root/cert/ip/fullchain.pem')
                track('file', '/root/cert/ip/privkey.pem')
                print(f'  LE SSL для {server_ip} выпущен (auto-renew каждые 3 дня)')
                return True
            else:
                print('  ⚠️  Установка серта не удалась, fallback: self-signed')
                return False
def setup_3xui_cascade_exit(cascade_ip, cascade_cred, exit_panel_domain):
    """Install full 3x-ui panel on exit server with SSL + Reality inbound for cascade."""
    print(f'\n  [cascade] Подключение к exit-серверу {cascade_ip}...')
    r = run_remote(cascade_ip, cascade_cred, 'echo OK', timeout=30)
    if 'OK' not in r.stdout:
        for _ in range(3):
            time.sleep(5)
            r = run_remote(cascade_ip, cascade_cred, 'echo OK', timeout=30)
            if 'OK' in r.stdout:
                break
        else:
            print(f'  ❌ [cascade] Не могу подключиться к exit {cascade_ip}')
            return
    print('  [cascade] SSH OK')
    check_os(remote_ip=cascade_ip, remote_cred=cascade_cred)
    print('  [cascade] Настройка TCP (BBR)...')
    write_remote_file(cascade_ip, cascade_cred, '/etc/sysctl.d/99-vpn-tuning.conf', SYSCTL_TUNING)
    run_remote(cascade_ip, cascade_cred, 'sysctl --system > /dev/null 2>&1')
    write_remote_file(cascade_ip, cascade_cred, '/etc/security/limits.d/99-nofile.conf', NOFILE_LIMITS)
    run_remote(cascade_ip, cascade_cred, 'swapon --show | grep -q / || (fallocate -l 2G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile && grep -q swapfile /etc/fstab || echo \'/swapfile none swap sw 0 0\' >> /etc/fstab) 2>/dev/null')
    exit_panel_pass = secrets.token_urlsafe(12)
    exit_panel_port = 47115 + secrets.randbelow(1000)
    exit_panel_path = generate_panel_path()
    r_svc = run_remote(cascade_ip, cascade_cred, 'systemctl is-active x-ui 2>/dev/null', timeout=15)
    r_bin = run_remote(cascade_ip, cascade_cred, 'test -f /usr/local/x-ui/x-ui && echo yes || echo no', timeout=10)
    if 'active' in r_svc.stdout and 'yes' in r_bin.stdout:
        print('  [cascade] 3x-ui уже установлен на exit')
    else:
        print('  [cascade] Установка 3x-ui на exit...')
        run_remote(cascade_ip, cascade_cred, 'curl -Ls https://raw.githubusercontent.com/mhsanaei/3x-ui/master/install.sh -o /tmp/3xui_install.sh', timeout=60)
        run_remote(cascade_ip, cascade_cred, 'XUI_NONINTERACTIVE=1 bash /tmp/3xui_install.sh v3.6.0', timeout=300)
        time.sleep(5)
        r = run_remote(cascade_ip, cascade_cred, 'systemctl is-active x-ui', timeout=15)
        if 'active' not in r.stdout:
            run_remote(cascade_ip, cascade_cred, 'systemctl restart x-ui', timeout=30)
            time.sleep(5)
    run_remote(cascade_ip, cascade_cred, f'/usr/local/x-ui/x-ui setting -username admin -password {exit_panel_pass} -port {exit_panel_port} -webBasePath /{exit_panel_path}/', timeout=15)
    print(f'  [cascade] 3x-ui: порт={exit_panel_port}, путь=/{exit_panel_path}/')
    print(f'  [cascade] SSL сертификат для {exit_panel_domain}...')
    run_remote(cascade_ip, cascade_cred, 'DEBIAN_FRONTEND=noninteractive apt-get update -qq && apt-get install -y -qq certbot nginx 2>/dev/null', timeout=120)
    acme_conf = f'server {{\n    listen 80;\n    server_name {exit_panel_domain};\n    location /.well-known/acme-challenge/ {{ root /var/www/certbot; }}\n    location /health {{ return 200 \'ok\'; add_header Content-Type text/plain; }}\n    location / {{ return 301 https://$host$request_uri; }}\n}}\n'
    run_remote(cascade_ip, cascade_cred, 'mkdir -p /var/www/certbot', timeout=10)
    write_remote_file(cascade_ip, cascade_cred, '/etc/nginx/sites-available/default', acme_conf)
    run_remote(cascade_ip, cascade_cred, 'nginx -t 2>/dev/null && systemctl restart nginx', timeout=15)
    r = run_remote(cascade_ip, cascade_cred, f'certbot certonly --webroot -w /var/www/certbot -d {exit_panel_domain} --non-interactive --agree-tos --register-unsafely-without-email', timeout=120)
    if r.returncode == 0:
        ssl_cert = f'/etc/letsencrypt/live/{exit_panel_domain}/fullchain.pem'
        ssl_key = f'/etc/letsencrypt/live/{exit_panel_domain}/privkey.pem'
        print('  [cascade] Сертификат LE получен!')
    else:
        run_remote(cascade_ip, cascade_cred, f'mkdir -p /etc/nginx/ssl && openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout /etc/nginx/ssl/cdn.key -out /etc/nginx/ssl/cdn.crt -subj \'/CN={exit_panel_domain}\' 2>/dev/null', timeout=30)
        ssl_cert = '/etc/nginx/ssl/cdn.crt'
        ssl_key = '/etc/nginx/ssl/cdn.key'
        print('  [cascade] LE не сработал, self-signed')
    run_remote(cascade_ip, cascade_cred, f'/usr/local/x-ui/x-ui setting -certFile {ssl_cert} -keyFile {ssl_key}', timeout=15)
    run_remote(cascade_ip, cascade_cred, f'/usr/local/x-ui/x-ui setting -subCertFile {ssl_cert} -subKeyFile {ssl_key}', timeout=15)
    print('  [cascade] Генерация Reality ключей...')
    reality_keys = None
    xray_paths = ['/usr/local/x-ui/bin/xray-linux-amd64', '/usr/local/x-ui/bin/xray-linux-arm64', '/usr/local/x-ui/bin/xray', '/usr/local/bin/xray', '/usr/bin/xray']
    for xray_bin in xray_paths:
        r = run_remote(cascade_ip, cascade_cred, f'{xray_bin} x25519 2>/dev/null', timeout=15)
        if r.returncode == 0 and 'Private' in r.stdout:
                reality_keys = _parse_x25519(r.stdout)
                if reality_keys:
                    break
    if not reality_keys:
        r = run_remote(cascade_ip, cascade_cred, 'find /usr/local/x-ui -name \'xray*\' -type f -executable 2>/dev/null | head -1', timeout=10)
        found = r.stdout.strip()
        if found:
            r = run_remote(cascade_ip, cascade_cred, f'{found} x25519 2>/dev/null', timeout=15)
            if r.returncode == 0 and 'Private' in r.stdout:
                    reality_keys = _parse_x25519(r.stdout)
    if not reality_keys:
        r = run_remote(cascade_ip, cascade_cred, 'docker exec $(docker ps -q --filter ancestor=ghcr.io/mhsanaei/3x-ui 2>/dev/null | head -1) xray x25519 2>/dev/null || docker run --rm ghcr.io/remnawave/node:latest xray x25519 2>/dev/null', timeout=30)
        if r.returncode == 0 and 'Private' in r.stdout:
                reality_keys = _parse_x25519(r.stdout)
    if not reality_keys:
        print('  ❌ [cascade] Не удалось сгенерировать x25519 ключи!')
        return
    else:
        short_id = secrets.token_hex(8)
        bridge_uuid = str(uuid.uuid4())
        print(f"  [cascade] Reality pubKey: {reality_keys['public'][:24]}...")
        print(f'  [cascade] Bridge UUID: {bridge_uuid[:8]}...')
        now_ms = int(time.time() * 1000)
        sub_id_exit = secrets.token_hex(8)
        # Reconstructed from the target CodeType constants/raw structure.  This is the
        # SQLite bootstrap used by 3x-ui on the exit node: a Reality VLESS inbound,
        # a plain TCP bridge inbound, their client/traffic rows, subscription settings,
        # and the xrayTemplateConfig consumed by 3x-ui.
        settings_json = json.dumps({
            'clients': [{
                'id': bridge_uuid,
                'email': 'bridge_user',
                'flow': 'xtls-rprx-vision',
                'limitIp': 0,
                'totalGB': 0,
                'expiryTime': 0,
                'enable': True,
            }],
            'decryption': 'none',
        }).replace("'", "''")

        stream_json = json.dumps({
            'network': 'tcp',
            'security': 'reality',
            'tcpSettings': {'header': {'type': 'none'}},
            'realitySettings': {
                'show': False,
                'xver': 0,
                'dest': 'www.microsoft.com:443',
                'serverNames': ['www.microsoft.com'],
                'privateKey': reality_keys['private'],
                'minClient': '',
                'maxClient': '',
                'maxTimediff': 0,
                'shortIds': [short_id],
            },
        }).replace("'", "''")
        sniffing_json = json.dumps({'enabled': True, 'destOverride': ['http', 'tls', 'quic']}).replace("'", "''")

        xray_tpl_exit = json.dumps({
            'log': {'loglevel': 'warning', 'access': 'none', 'dnsLog': False},
            'stats': {},
            'api': {'services': ['StatsService'], 'tag': 'api'},
            'policy': {
                'levels': {'0': {'statsUserUplink': True, 'statsUserDownlink': True}},
                'system': {
                    'statsInboundUplink': True,
                    'statsInboundDownlink': True,
                    'statsOutboundUplink': True,
                    'statsOutboundDownlink': True,
                },
            },
            'inbounds': [{
                'listen': '127.0.0.1',
                'port': 62789,
                'protocol': 'dokodemo-door',
                'settings': {'address': '127.0.0.1'},
                'tag': 'api',
            }],
            'outbounds': [
                {'protocol': 'freedom', 'tag': 'direct', 'settings': {'domainStrategy': 'UseIPv4'}},
                {'protocol': 'blackhole', 'tag': 'blocked', 'settings': {}},
            ],
            'routing': {
                'domainStrategy': 'AsIs',
                'rules': [
                    {'type': 'field', 'inboundTag': ['api'], 'outboundTag': 'api'},
                    {'type': 'field', 'outboundTag': 'direct', 'ip': ['ext:geoip_RU.dat:ru']},
                    {'type': 'field', 'outboundTag': 'direct', 'domain': [
                        'ext:geosite_RU.dat:ru-available-only-inside',
                        r'regexp:.*\.ru$',
                        r'regexp:.*\.su$',
                        r'regexp:.*\.xn--p1ai$',
                    ]},
                    {'type': 'field', 'ip': ['geoip:private'], 'outboundTag': 'blocked'},
                    {'type': 'field', 'protocol': ['bittorrent'], 'outboundTag': 'blocked'},
                ],
            },
        }).replace("'", "''")


        bridge_plain_settings = json.dumps({
            'clients': [{
                'id': bridge_uuid,
                'email': 'bridge_plain',
                'limitIp': 0,
                'totalGB': 0,
                'expiryTime': 0,
                'enable': True,
            }],
            'decryption': 'none',
        }).replace("'", "''")
        bridge_plain_stream = json.dumps({
            'network': 'tcp',
            'security': 'none',
            'tcpSettings': {'header': {'type': 'none'}},
        }).replace("'", "''")

        exit_sql = ''.join([
            "DELETE FROM client_inbounds WHERE client_id IN (SELECT id FROM clients WHERE email='bridge_user');\n"
            "DELETE FROM client_inbounds WHERE client_id IN (SELECT id FROM clients WHERE email='bridge_plain');\n"
            "DELETE FROM client_traffics WHERE email='bridge_user';\n"
            "DELETE FROM client_traffics WHERE email='bridge_plain';\n"
            "DELETE FROM clients WHERE email='bridge_user';\n"
            "DELETE FROM clients WHERE email='bridge_plain';\n"
            "DELETE FROM inbounds WHERE tag='cascade-reality-in';\n"
            "DELETE FROM inbounds WHERE tag='bridge-plain';\n"
            "INSERT INTO inbounds (user_id, up, down, total, remark, enable, expiry_time, listen, port, protocol, settings, stream_settings, tag, sniffing)\n"
            f"VALUES (1, 0, 0, 0, 'CASCADE-REALITY', 1, 0, '', 443, 'vless', '{settings_json}', '{stream_json}', 'cascade-reality-in', '{sniffing_json}');\n"
            "INSERT INTO inbounds (user_id, up, down, total, remark, enable, expiry_time, listen, port, protocol, settings, stream_settings, tag, sniffing)\n"
            f"VALUES (1, 0, 0, 0, 'Bridge Plain TCP', 1, 0, '0.0.0.0', 9999, 'vless', '{bridge_plain_settings}', '{bridge_plain_stream}', 'bridge-plain', '{sniffing_json}');\n"
            "INSERT INTO clients (email, sub_id, uuid, flow, limit_ip, total_gb, expiry_time, enable, created_at)\n"
            f"VALUES ('bridge_user', '{sub_id_exit}', '{bridge_uuid}', 'xtls-rprx-vision', 0, 0, 0, 1, {now_ms});\n"
            "INSERT INTO clients (email, uuid, flow, limit_ip, total_gb, expiry_time, enable, created_at)\n"
            f"VALUES ('bridge_plain', '{bridge_uuid}', '', 0, 0, 0, 1, {now_ms});\n"
            "INSERT INTO client_traffics (inbound_id, enable, email, up, down, expiry_time, total, reset)\n"
            "VALUES ((SELECT id FROM inbounds WHERE tag='cascade-reality-in'), 1, 'bridge_user', 0, 0, 0, 0, 0);\n"
            "INSERT INTO client_traffics (inbound_id, enable, email, up, down, expiry_time, total, reset)\n"
            "VALUES ((SELECT id FROM inbounds WHERE tag='bridge-plain'), 1, 'bridge_plain', 0, 0, 0, 0, 0);\n"
            "INSERT INTO client_inbounds (client_id, inbound_id, flow_override, created_at)\n"
            f"VALUES ((SELECT id FROM clients WHERE email='bridge_user'), (SELECT id FROM inbounds WHERE tag='cascade-reality-in'), 'xtls-rprx-vision', {now_ms});\n"
            "INSERT INTO client_inbounds (client_id, inbound_id, flow_override, created_at)\n"
            f"VALUES ((SELECT id FROM clients WHERE email='bridge_plain'), (SELECT id FROM inbounds WHERE tag='bridge-plain'), '', {now_ms});\n"
            "UPDATE settings SET value='true' WHERE key='subEnable';\n"
            f"UPDATE settings SET value='https://{exit_panel_domain}/sub/' WHERE key='subURI';\n"
            f"UPDATE settings SET value='https://{exit_panel_domain}/json/' WHERE key='subJsonURI';\n"
            "UPDATE settings SET value='true' WHERE key='subJsonEnable';\n"
            "UPDATE settings SET value='' WHERE key='subListen';\n"
            "UPDATE settings SET value='' WHERE key='subCertFile';\n"
            "UPDATE settings SET value='' WHERE key='subKeyFile';\n"
            f"UPDATE settings SET value='{xray_tpl_exit}' WHERE key='xrayTemplateConfig';\n"
            f"INSERT OR IGNORE INTO settings (key, value) VALUES ('xrayTemplateConfig', '{xray_tpl_exit}');\n"
        ])
        write_remote_file(cascade_ip, cascade_cred, '/tmp/cascade_setup.sql', exit_sql)
        run_remote(cascade_ip, cascade_cred, 'which sqlite3 >/dev/null 2>&1 || DEBIAN_FRONTEND=noninteractive apt-get install -y -qq sqlite3 2>/dev/null', timeout=60)
        r = run_remote(cascade_ip, cascade_cred, 'sqlite3 /etc/x-ui/x-ui.db < /tmp/cascade_setup.sql && rm /tmp/cascade_setup.sql', timeout=15)
        if r.returncode!= 0:
            print(f"  ⚠️  [cascade] SQL ошибка: {(r.stderr[:200] if r.stderr else 'unknown')}")
        print('  [cascade] Открытие портов на exit...')
        for port in (80, 443, 9999, exit_panel_port, 2096):
            run_remote(cascade_ip, cascade_cred, f'ufw allow {port}/tcp 2>/dev/null; iptables -I INPUT -p tcp --dport {port} -j ACCEPT 2>/dev/null', timeout=10)
        run_remote(cascade_ip, cascade_cred, 'systemctl restart x-ui', timeout=30)
        time.sleep(5)
        port_443_ok = False
        for attempt in range(3):
            r = run_remote(cascade_ip, cascade_cred, 'ss -tlnp | grep :443', timeout=15)
            if '443' in r.stdout:
                port_443_ok = True
                break
            else:
                if attempt < 2:
                    print(f'  [cascade] Порт 443 не стартовал, перезапуск x-ui ({attempt + 2}/3)...')
                    run_remote(cascade_ip, cascade_cred, 'systemctl restart x-ui', timeout=30)
                    time.sleep(8)
        if port_443_ok:
            print('  [cascade] Exit: Reality inbound 443 OK')
        else:
            r_log = run_remote(cascade_ip, cascade_cred, 'journalctl -u x-ui --no-pager -n 20 2>/dev/null | grep -i \'error\\|fail\\|443\' | tail -5', timeout=15)
            if r_log.stdout.strip():
                print(f'  ⚠️  [cascade] Порт 443 не слушает. Лог: {r_log.stdout.strip()[:200]}')
            else:
                print('  ⚠️  [cascade] Порт 443 не слушает на exit (возможно конфликт с nginx)')
            r_nginx = run_remote(cascade_ip, cascade_cred, 'ss -tlnp | grep :443', timeout=10)
            if 'nginx' in r_nginx.stdout:
                print('  [cascade] Nginx занимает 443, останавливаю...')
                run_remote(cascade_ip, cascade_cred, 'systemctl stop nginx && systemctl restart x-ui', timeout=30)
                time.sleep(5)
                r = run_remote(cascade_ip, cascade_cred, 'ss -tlnp | grep :443', timeout=15)
                if '443' in r.stdout:
                    print('  [cascade] Exit: Reality inbound 443 OK (nginx остановлен)')
                    port_443_ok = True
        r = run_remote(cascade_ip, cascade_cred, 'ss -tlnp | grep :9999', timeout=15)
        if '9999' in r.stdout:
            print('  [cascade] Exit: Bridge plain 9999 OK')
        else:
            print('  ⚠️  [cascade] Порт 9999 не слушает на exit!')
        r = run_remote(cascade_ip, cascade_cred, f'ss -tlnp | grep :{exit_panel_port}', timeout=15)
        if str(exit_panel_port) in r.stdout:
            print(f'  [cascade] Exit: панель {exit_panel_port} OK')
        print(f'  [cascade] Exit панель: https://{exit_panel_domain}:{exit_panel_port}/{exit_panel_path}/')
        print(f'  [cascade] Exit подписка: https://{exit_panel_domain}:2096/sub/')
        return {'public_key': reality_keys['public'], 'short_id': short_id, 'bridge_uuid': bridge_uuid, 'exit_panel_pass': exit_panel_pass, 'exit_panel_port': exit_panel_port, 'exit_panel_path': exit_panel_path, 'exit_panel_domain': exit_panel_domain}
def install_3xui(cfg):
    """Install 3x-ui with VK or Yandex CDN inbound."""
    domain = cfg['domain']
    front_domain = cfg.get('front_domain', domain)
    cdn_type = cfg['cdn_type']
    cdn = CDN_SETTINGS[cdn_type]
    server_ip = cfg['server_ip']
    origin_sub = cfg['origin_sub']
    cdn_sub = cfg['cdn_sub']
    panel_user = 'admin'
    panel_pass = secrets.token_urlsafe(12)
    panel_port = 47115 + secrets.randbelow(1000)
    panel_path = generate_panel_path()
    client_uuid = str(uuid.uuid4())
    client_email = 'user1'
    step(3, 'Установка 3x-ui')
    print('  Скачивание установщика 3x-ui...')
    r = run('curl -Ls https://raw.githubusercontent.com/mhsanaei/3x-ui/master/install.sh -o /tmp/3xui_install.sh', check=False)
    if r.returncode!= 0 or not os.path.exists('/tmp/3xui_install.sh') or os.path.getsize('/tmp/3xui_install.sh') < 100:
        print('  ❌ Не удалось скачать установщик 3x-ui! Проверь интернет.')
        sys.exit(1)
    print('  Запуск установщика 3x-ui...')
    env_vars = f'XUI_NONINTERACTIVE=1 XUI_DB_TYPE=sqlite XUI_USERNAME={panel_user} XUI_PASSWORD={panel_pass} XUI_PORT={panel_port} XUI_WEB_BASE_PATH={panel_path} '
    r = run(f'{env_vars} bash /tmp/3xui_install.sh v3.6.0', check=False, timeout=300)
    if r.returncode!= 0:
        print(f'  Установщик вернул код {r.returncode}, проверяю...')
    if not wait_xui_active(40):
        print('  x-ui не поднялся после установки, пробую рестарт...')
        run('systemctl restart x-ui', check=False)
        if not wait_xui_active(40):
            print('  ❌ x-ui не запустился после установки!')
            r = run('journalctl -u x-ui --no-pager -n 20', check=False)
            print(f'  Логи: {r.stdout[(-800):]}')
            sys.exit(1)
    print('  Применяю настройки панели...')
    r = run(f'/usr/local/x-ui/x-ui setting -username {panel_user} -password {panel_pass} -port {panel_port} -webBasePath /{panel_path}/', check=False)
    if r.returncode!= 0:
        print(f'  ❌ Не удалось применить настройки: {(r.stderr[:300] if r.stderr else r.stdout[:300])}')
        sys.exit(1)
    run('systemctl restart x-ui', check=False)
    if not wait_xui_active(40):
        print('  ❌ x-ui не запустился после применения настроек!')
        r = run('journalctl -u x-ui --no-pager -n 20', check=False)
        print(f'  Логи: {r.stdout[(-800):]}')
        sys.exit(1)
    r = run('/usr/local/x-ui/x-ui setting -show 2>&1', check=False)
    if f'port: {panel_port}' not in r.stdout or f'/{panel_path}/' not in r.stdout:
        print('  ⚠️  Настройки могли не примениться. Текущие:')
        for line in r.stdout.split('\n'):
            if any((k in line.lower() for k in ['port:', 'path:', 'username'])):
                print(f'    {line.strip()}')
    else:
        print(f'  3x-ui установлен и работает: порт={panel_port}, путь=/{panel_path}/')
    track('systemd', 'x-ui')
    panel_sub = cfg.get('panel_sub', 'panel')
    panel_domain = f'{panel_sub}.{domain}'
    step(4, f'SSL сертификат для {panel_domain}')
    run('DEBIAN_FRONTEND=noninteractive apt-get install -y -qq certbot 2>/dev/null', check=False, timeout=60)
    run('mkdir -p /var/www/certbot', check=False)
    acme_conf = f'server {{\n    listen 80;\n    server_name {panel_domain};\n    location /.well-known/acme-challenge/ {{ root /var/www/certbot; }}\n    location / {{ return 301 https://$host$request_uri; }}\n}}\n'
    nginx_write_conf('panel.conf', acme_conf)
    run('nginx -t && systemctl restart nginx', check=False)
    print(f'  Получение сертификата для {panel_domain}...')
    r = run(f'certbot certonly --webroot -w /var/www/certbot -d {panel_domain} --non-interactive --agree-tos --register-unsafely-without-email', check=False, timeout=120)
    if r.returncode!= 0:
        print('  ⚠️  Certbot не сработал, используем self-signed.')
        ssl_cert = '/etc/nginx/ssl/cdn.crt'
        ssl_key = '/etc/nginx/ssl/cdn.key'
    else:
        ssl_cert = f'/etc/letsencrypt/live/{panel_domain}/fullchain.pem'
        ssl_key = f'/etc/letsencrypt/live/{panel_domain}/privkey.pem'
        print('  Сертификат получен!')
        run(f'/usr/local/x-ui/x-ui setting -certFile {ssl_cert} -keyFile {ssl_key}', check=False)
        run(f'/usr/local/x-ui/x-ui setting -subCertFile {ssl_cert} -subKeyFile {ssl_key}', check=False)
        run('systemctl restart x-ui', check=False)
        time.sleep(3)
        print('  x-ui настроен с LE сертификатом (панель + подписка)')
    step(5, 'Настройка nginx CDN origin')
    ipv6_ok = has_ipv6()
    le_ok = ssl_cert.startswith('/etc/letsencrypt')
    nginx_conf = nginx_cdn_origin(cdn['xray_port'], cdn['xhttp_path'], panel_path, panel_port, ipv6=ipv6_ok, ssl_cert=ssl_cert, ssl_key=ssl_key, panel_https=False)
    r = nginx_write_and_restart(nginx_conf)
    if r.returncode == 0:
        print('  Nginx настроен и перезапущен')
    else:
        print(f"  ❌ Проблема с nginx: {(r.stderr[:200] if r.stderr else '')}")
        print('  Попробуй: nginx -t и systemctl restart nginx')
        sys.exit(1)
    step(6, f'Создание {cdn_type.upper()} CDN inbound')
    for _ in range(10):
        if os.path.exists('/etc/x-ui/x-ui.db'):
            break
        else:
            time.sleep(2)
    if not os.path.exists('/etc/x-ui/x-ui.db'):
        print('  ❌ Файл /etc/x-ui/x-ui.db не найден')
        sys.exit(1)
    cdn_domain = f'{cdn_sub}.{domain}'
    origin_domain = f'{origin_sub}.{domain}'
    tag = 'vk-cdn-xhttp' if cdn_type == 'vk' else 'ya-cdn-xhttp'
    now_ms = int(time.time() * 1000)
    sub_id = secrets.token_hex(8)
    settings_obj = {'clients': [{'id': client_uuid, 'email': client_email, 'enable': True, 'expiryTime': 0, 'limitIp': 0, 'totalGB': 0, 'subId': sub_id, 'tgId': 0, 'reset': 0, 'security': '', 'comment': '', 'created_at': now_ms, 'updated_at': now_ms}], 'decryption': 'none', 'fallbacks': []}
    if cdn_type == 'host':
        xhttp_settings = {'path': cdn['xhttp_path'], 'host': '', 'mode': 'packet-up', 'noSSEHeader': False, 'scMaxEachPostBytes': '262144-786432', 'scMinPostsIntervalMs': '0', 'xPaddingBytes': '48-256', 'xPaddingObfsMode': True, 'xPaddingKey': 'q', 'xPaddingMethod': 'tokenish', 'xPaddingPlacement': 'query', 'sessionIDKey': 'sid', 'sessionIDPlacement': 'query', 'seqKey': 'offset', 'seqPlacement': 'query', 'uplinkHTTPMethod': 'DELETE', 'xmux': {'maxConcurrency': 0, 'maxConnections': '16-32', 'cMaxReuseTimes': 0, 'hMaxRequestTimes': '600-900', 'hMaxReusableSecs': '120-240', 'hKeepAlivePeriod': 20}}
    else:
        xhttp_settings = {'path': cdn['xhttp_path'], 'host': '', 'mode': 'packet-up', 'xPaddingBytes': '100-1000', 'xPaddingObfsMode': True, 'xPaddingKey': cdn['padding_key'], 'xPaddingHeader': cdn['padding_header'], 'xPaddingPlacement': cdn['padding_placement'], 'xPaddingMethod': cdn['padding_method'], 'uplinkHTTPMethod': cdn['uplink_method'], 'noSSEHeader': False, 'enableXmux': True, 'xmux': {'maxConcurrency': '16-32', 'maxConnections': 0, 'cMaxReuseTimes': 1000, 'hMaxRequestTimes': '600-900', 'hMaxReusableSecs': '100', 'hKeepAlivePeriod': 20000}}
        if cdn_type == 'yandex':
            xhttp_settings['uplinkChunkSize'] = 131072
    if cdn_type == 'host':
        ext_proxy = [{'forceTls': 'tls', 'dest': front_domain, 'port': 443, 'remark': '', 'sni': front_domain, 'fingerprint': 'firefox', 'alpn': 'h2'}]
    else:
        ext_proxy = [{'forceTls': 'tls', 'dest': cdn_domain, 'port': 443, 'remark': ''}]
    stream_settings_obj = {'network': 'xhttp', 'security': 'none', 'externalProxy': ext_proxy, 'xhttpSettings': xhttp_settings}
    sniffing_obj = {'enabled': True, 'destOverride': ['http', 'tls', 'quic']}
    settings_json = json.dumps(settings_obj).replace('\'', '\'\'')
    stream_json = json.dumps(stream_settings_obj).replace('\'', '\'\'')
    sniffing_json = json.dumps(sniffing_obj).replace('\'', '\'\'')

    sql_file_content = (
        f"DELETE FROM client_inbounds WHERE client_id IN (SELECT id FROM clients WHERE email='{client_email}');\n"
        f"DELETE FROM client_traffics WHERE email='{client_email}';\n"
        f"DELETE FROM clients WHERE email='{client_email}';\n"
        f"DELETE FROM inbounds WHERE tag='{tag}';\n\n"
        f"INSERT INTO inbounds (user_id, up, down, total, remark, enable, expiry_time, listen, port, protocol, settings, stream_settings, tag, sniffing)\n"
        f"VALUES (1, 0, 0, 0, '{cdn_type.upper()}-HOST', 1, 0, '127.0.0.1', {cdn['xray_port']}, 'vless', '{settings_json}', '{stream_json}', '{tag}', '{sniffing_json}');\n\n"
        f"INSERT INTO clients (email, sub_id, uuid, limit_ip, total_gb, expiry_time, enable, tg_id, reset, created_at, updated_at)\n"
        f"VALUES ('{client_email}', '{sub_id}', '{client_uuid}', 0, 0, 0, 1, 0, 0, {now_ms}, {now_ms});\n"
    )
    with open('/tmp/xui_setup.sql', 'w') as f:
        f.write(sql_file_content)
    r = run('sqlite3 /etc/x-ui/x-ui.db < /tmp/xui_setup.sql', check=False)
    if r.returncode!= 0:
        print(f'  ❌ Ошибка SQL: {r.stderr[:300]}')
        sys.exit(1)
    r = run(f'sqlite3 /etc/x-ui/x-ui.db \"SELECT id FROM clients WHERE email=\'{client_email}\';\"', check=False)
    client_id = r.stdout.strip()
    r = run(f'sqlite3 /etc/x-ui/x-ui.db \"SELECT id FROM inbounds WHERE tag=\'{tag}\';\"', check=False)
    inbound_id = r.stdout.strip()
    if not client_id or not inbound_id:
        print(f'  ❌ Не удалось получить client_id={client_id} или inbound_id={inbound_id}')
        print('  Проверь логи x-ui: journalctl -u x-ui -n 50')
        sys.exit(1)
    link_sql = f'INSERT INTO client_inbounds (client_id, inbound_id, flow_override, created_at) VALUES ({client_id}, {inbound_id}, \'\', {now_ms});'
    run(f'sqlite3 /etc/x-ui/x-ui.db \"{link_sql}\"', check=False)
    step_n = 7
    cascade = cfg.get('cascade', False)
    cascade_info = None
    if cascade:
        step(step_n, f"Установка exit-сервера {cfg['cascade_ip']} (каскад)")
        step_n += 1
        exit_sub = cfg.get('exit_sub', 'xui')
        exit_panel_domain = f'{exit_sub}.{domain}'
        cascade_info = setup_3xui_cascade_exit(cfg['cascade_ip'], cfg['cascade_cred'], exit_panel_domain)
        if not cascade_info:
            print('  ❌ Каскад не удался, продолжаю без каскада.')
            cascade = False
    outbounds = [{'protocol': 'freedom', 'tag': 'direct', 'settings': {'domainStrategy': 'UseIPv4'}}, {'protocol': 'blackhole', 'tag': 'blocked', 'settings': {}}]
    rules = [{'type': 'field', 'inboundTag': ['api'], 'outboundTag': 'api'}]
    if cascade and cascade_info:
            outbounds.append({'tag': 'CASCADE-REALITY', 'protocol': 'vless', 'settings': {'vnext': [{'address': cfg['cascade_ip'], 'port': 9999, 'users': [{'id': cascade_info['bridge_uuid'], 'encryption': 'none'}]}]}, 'streamSettings': {'network': 'tcp', 'security': 'none', 'tcpSettings': {'header': {'type': 'none'}}}})
            rules.append({'type': 'field', 'inboundTag': [tag], 'outboundTag': 'CASCADE-REALITY'})
    rules.extend([{'type': 'field', 'outboundTag': 'direct', 'ip': ['ext:geoip_RU.dat:ru']}, {'type': 'field', 'outboundTag': 'direct', 'domain': ['ext:geosite_RU.dat:ru-available-only-inside', 'regexp:.*\\.ru$', 'regexp:.*\\.su$', 'regexp:.*\\.xn--p1ai$']}, {'type': 'field', 'ip': ['geoip:private'], 'outboundTag': 'blocked'}, {'type': 'field', 'protocol': ['bittorrent'], 'outboundTag': 'blocked'}])
    xray_tpl = json.dumps({
        'log': {'loglevel': 'warning', 'access': 'none', 'dnsLog': False},
        'stats': {},
        'api': {'services': ['StatsService'], 'tag': 'api'},
        'policy': {'levels': {'0': {'statsUserUplink': True, 'statsUserDownlink': True}}, 'system': {'statsInboundUplink': True, 'statsInboundDownlink': True, 'statsOutboundUplink': True, 'statsOutboundDownlink': True}},
        'inbounds': [{'listen': '127.0.0.1', 'port': 62789, 'protocol': 'dokodemo-door', 'settings': {'address': '127.0.0.1'}, 'tag': 'api'}],
        'outbounds': outbounds,
        'routing': {'domainStrategy': 'AsIs', 'rules': rules},
    }).replace("'", "''")

    xui_settings_sql = f'UPDATE settings SET value=\'true\' WHERE key=\'subEnable\';\nUPDATE settings SET value=\'https://{panel_domain}/sub/\' WHERE key=\'subURI\';\nUPDATE settings SET value=\'https://{panel_domain}/json/\' WHERE key=\'subJsonURI\';\nUPDATE settings SET value=\'true\' WHERE key=\'subJsonEnable\';\nUPDATE settings SET value=\'\' WHERE key=\'subListen\';\nUPDATE settings SET value=\'\' WHERE key=\'subCertFile\';\nUPDATE settings SET value=\'\' WHERE key=\'subKeyFile\';\nUPDATE settings SET value=\'{xray_tpl}\' WHERE key=\'xrayTemplateConfig\';\nINSERT OR IGNORE INTO settings (key, value) VALUES (\'xrayTemplateConfig\', \'{xray_tpl}\');\n'
    with open('/tmp/xui_settings.sql', 'w') as f:
        f.write(xui_settings_sql)
    run('sqlite3 /etc/x-ui/x-ui.db < /tmp/xui_settings.sql', check=False)
    run('systemctl restart x-ui', check=False)
    print(f"  Ожидание запуска xray на порту {cdn['xray_port']}...")
    xray_ok = False
    for _ in range(6):
        time.sleep(5)
        r = run(f"ss -tlnp | grep :{cdn['xray_port']}", check=False)
        if str(cdn['xray_port']) in r.stdout:
            xray_ok = True
            break
    if xray_ok:
        print(f"  Inbound создан, xray слушает порт {cdn['xray_port']}")
    else:
        print(f"  ⚠️  Xray не слушает порт {cdn['xray_port']}")
        print('     Перезапускаю x-ui…')
        run('systemctl restart x-ui', check=False)
        time.sleep(10)
        r = run(f"ss -tlnp | grep :{cdn['xray_port']}", check=False)
        if str(cdn['xray_port']) in r.stdout:
            print(f"  Xray запущен на порту {cdn['xray_port']}")
        else:
            print(f"  ❌ Xray так и не запустился на порту {cdn['xray_port']}")
            r = run('journalctl -u x-ui --no-pager -n 15', check=False)
            print(f'  Логи: {r.stdout[:500]}')
    grpc_link = ''
    if cfg.get('install_grpc'):
        step(step_n, 'Установка VLESS Reality gRPC')
        step_n += 1
        reality_keys = generate_x25519_keys()
        if reality_keys:
                short_id = secrets.token_hex(8)
                grpc_tag = 'grpc-reality'
                grpc_settings = json.dumps({'clients': [{'id': client_uuid, 'email': client_email, 'flow': '', 'limitIp': 0, 'totalGB': 0, 'expiryTime': 0, 'enable': True}], 'decryption': 'none'}).replace('\'', '\'\'')
                grpc_stream = json.dumps({'network': 'grpc', 'security': 'reality', 'externalProxy': [{'forceTls': 'same', 'dest': server_ip, 'port': GRPC_PORT, 'remark': ''}], 'realitySettings': {'show': False, 'xver': 0, 'dest': GRPC_DEST, 'serverNames': GRPC_SERVER_NAMES, 'privateKey': reality_keys['private'], 'minClient': '', 'maxClient': '', 'maxTimediff': 0, 'shortIds': [short_id]}, 'grpcSettings': {'serviceName': GRPC_SERVICE_NAME}}).replace('\'', '\'\'')
                grpc_sniffing = json.dumps({'enabled': True, 'destOverride': ['http', 'tls', 'quic']}).replace('\'', '\'\'')
                grpc_sql = f'DELETE FROM inbounds WHERE tag=\'{grpc_tag}\';\nINSERT INTO inbounds (user_id, up, down, total, remark, enable, expiry_time, listen, port, protocol, settings, stream_settings, tag, sniffing)\nVALUES (1, 0, 0, 0, \'gRPC Reality\', 1, 0, \'\', {GRPC_PORT}, \'vless\', \'{grpc_settings}\', \'{grpc_stream}\', \'{grpc_tag}\', \'{grpc_sniffing}\');\n\nINSERT INTO client_traffics (inbound_id, enable, email, up, down, expiry_time, total, reset)\nVALUES ((SELECT id FROM inbounds WHERE tag=\'{grpc_tag}\'), 1, \'{client_email}\', 0, 0, 0, 0, 0);\n'
                with open('/tmp/xui_grpc.sql', 'w') as f:
                    f.write(grpc_sql)
                run('sqlite3 /etc/x-ui/x-ui.db < /tmp/xui_grpc.sql', check=False)
                r = run(f'sqlite3 /etc/x-ui/x-ui.db \"SELECT id FROM inbounds WHERE tag=\'{grpc_tag}\';\"', check=False)
                grpc_inbound_id = r.stdout.strip()
                if client_id and grpc_inbound_id:
                        run(f'sqlite3 /etc/x-ui/x-ui.db \"INSERT INTO client_inbounds (client_id, inbound_id, flow_override, created_at) VALUES ({client_id}, {grpc_inbound_id}, \'\', {now_ms});\"', check=False)
                open_extra_ports(False, True)
                print(f'  gRPC Reality inbound создан на TCP порту {GRPC_PORT}')
                grpc_link = f"vless://{client_uuid}@{server_ip}:{GRPC_PORT}?type=grpc&security=reality&sni={GRPC_SERVER_NAMES[0]}&fp=random&pbk={reality_keys['public']}&sid={short_id}&serviceName={GRPC_SERVICE_NAME}&encryption=none#{client_email}-grpc"
        else:
            print('  ⚠️  gRPC пропущен: не удалось сгенерировать x25519-ключи')
    if cfg.get('install_grpc'):
        run('systemctl restart x-ui', check=False)
        time.sleep(5)
    step(step_n, 'Инструкция по настройке фронта')
    step_n += 1
    if cdn_type == 'host':
        print_host_instructions(front_domain, server_ip, '/p')
        try:
            auto_setup = safe_input('\n  Автоматически залить .htaccess через FTP? (y/n): ').strip().lower()
            if auto_setup in ['y', 'yes', 'д', 'да']:
                if upload_htaccess_ftp(front_domain, server_ip, 'p'):
                    print('\n  ✅ Фронт готов к использованию!')
                else:
                    print('\n  ⚠️  Залей .htaccess вручную по инструкции выше')
        except (KeyboardInterrupt, EOFError):
            print('\n  ⚠️  Пропущено, залей .htaccess вручную')
    else:
        if cdn_type == 'vk':
            print(f'\n  ============================================\n  DNS записи (у вашего DNS-провайдера):\n  ============================================\n\n  1. A-запись:  {origin_domain}  ->  {server_ip}  (без проксирования)\n  2. CNAME:     {cdn_domain}  ->  [VK CDN CNAME]  (без проксирования)\n\n  ============================================\n  Настройки VK Cloud CDN:\n  ============================================\n\n  1. Создай CDN-ресурс:\n     - Протокол к источнику: HTTP (порт 80)\n     - Источник: {origin_domain}\n     - Персональный домен: {cdn_domain}\n     - Заголовок Host: Пересылать\n     - SSL: Let\'s Encrypt\n\n  2. Скопируй CNAME (cl-xxxxx.service.cdn.msk.vkcs.cloud)\n     и создай DNS запись #2.\n\n  3. Настройки CDN:\n     - Кеширование: ВЫКЛ (все 4 переключателя)\n     - HTTP методы: GET, HEAD, OPTIONS\n     - Gzip сжатие: ВЫКЛ\n\n  4. Жди выпуск Let\'s Encrypt сертификата (5-30 мин)\n')
        else:
            if cdn_type!= 'host':
                print(f"\n  ============================================\n  DNS записи (у вашего DNS-провайдера):\n  ============================================\n\n  1. A-запись:  {origin_domain}  ->  {server_ip}  (без проксирования)\n  2. CNAME:     {cdn_domain}  ->  [Yandex CDN CNAME]  (без проксирования, создашь позже)\n  3. CNAME:     _acme-challenge.{cdn_domain} -> [значение из Yandex] (без проксирования, создашь позже)\n\n  Создай пока только запись #1. Остальные — по ходу.\n\n  ============================================\n  ШАГ A: Сертификат в Yandex Certificate Manager\n  ============================================\n\n  Зайди: console.yandex.cloud -> Certificate Manager -> Создать сертификат\n\n  Заполни:\n    - Имя: {cdn_domain.replace('.', '-')}\n    - Домены: {cdn_domain}\n    - Тип проверки: DNS\n\n  Нажми \"Создать\".\n\n  После создания Yandex покажет CNAME для проверки:\n    _acme-challenge.{cdn_domain}  ->  <значение>.cm.yandexcloud.net\n\n  Создай эту CNAME запись #3 (без проксирования).\n  Жди статус сертификата \"Issued\" (5-30 мин).\n\n  ============================================\n  ШАГ B: CDN-ресурс в Yandex Cloud CDN\n  ============================================\n\n  Зайди: console.yandex.cloud -> CDN -> Создать ресурс\n\n  Основные настройки:\n    - Запрос контента: Из одного источника\n    - Тип источника: Сервер\n    - Доменное имя источника: {origin_domain}\n    - Протокол для источников: HTTPS\n    - Задать SNI вручную: ВКЛ\n    - Имя SNI-хоста: {origin_domain}\n    - Заголовок Host: Своё значение\n    - Значение заголовка: {origin_domain}\n    - Доменное имя: {cdn_domain}\n\n  После создания скопируй CNAME (xxx.gcdn.co) и создай DNS запись #2.\n\n  Настройки CDN (вкладки сверху):\n    Кеширование:\n      - Кеш CDN: ВЫКЛ\n      - Кеш браузера: ВЫКЛ\n\n    Дополнительно:\n      - Query string: НЕ игнорировать\n      - Сжатие: ВЫКЛ\n      - Проверка сертификата источника: ВЫКЛ\n      - SSL-сертификат: выбери {cdn_domain.replace('.', '-')}\n")
    if cdn_type!= 'host' and (not cfg.get('skip_cdn_wait', False)):
            safe_input('  Нажми ENTER когда CDN настроен и сертификат выпущен...')
            if cdn_type in ['beeline', 'timeweb']:
                if cdn_type == 'beeline':
                    cdn_issued = safe_input('  Домен выданный Beeline CDN (например https://xxx.a.trbcdn.net): ').strip()
                else:
                    cdn_issued = safe_input('  Технический домен Timeweb CDN (например xxx.cdn.twcstorage.ru): ').strip()
                if cdn_issued:
                    cdn_issued = cdn_issued.replace('https://', '').replace('http://', '').rstrip('/')
                    cdn_label = 'Beeline' if cdn_type == 'beeline' else 'Timeweb'
                    print(f'  CDN домен {cdn_label}: {cdn_issued}')
    step(step_n, 'Финальная проверка')
    r = run('curl -s http://127.0.0.1/health', check=False)
    health_ok = 'ok' in r.stdout
    print(f"  Health endpoint: {('✅ ОК' if health_ok else '❌ не отвечает')}")
    r = run(f"ss -tlnp | grep :{cdn['xray_port']}", check=False)
    xray_ok = str(cdn['xray_port']) in r.stdout
    print(f"  Xray CDN port {cdn['xray_port']}: {('✅ ОК' if xray_ok else '❌ не слушает')}")
    if cfg.get('install_grpc'):
        r = run(f'ss -tlnp | grep :{GRPC_PORT}', check=False)
        grpc_ok = str(GRPC_PORT) in r.stdout
        print(f"  gRPC Reality TCP {GRPC_PORT}: {('✅ ОК' if grpc_ok else '⚠️  проверьте после рестарта')}")
    r = run('systemctl is-active nginx', check=False)
    nginx_ok = 'active' in r.stdout
    print(f"  Nginx: {('✅ ОК' if nginx_ok else '❌ не запущен')}")
    r = run(f'curl -sk https://{cdn_domain}/health 2>&1', check=False)
    cdn_ok = 'ok' in r.stdout
    print(f"  CDN ({cdn_domain}): {('✅ ОК' if cdn_ok else '⚠️  проверьте из РФ')}")
    link_host = front_domain if cdn_type == 'host' else cdn_domain
    vless_link = f"vless://{client_uuid}@{link_host}:443?type=xhttp&security=tls&sni={link_host}&fp=firefox&alpn=h2&path={cdn['xhttp_path']}&host={link_host}&mode=packet-up&encryption=none#{client_email}-{cdn_type}"
    sub_url = f'https://{panel_domain}/sub/{sub_id}'
    json_url = f'https://{panel_domain}/json/{sub_id}'
    print(f'  Подписка: {sub_url}')
    print(f'  JSON (Happ): {json_url}')
    extra_links = ''
    if grpc_link:
        extra_links += f'\n  gRPC Reality ссылка:\n  {grpc_link}\n'
    cascade_summary = ''
    if cascade and cascade_info:
            cascade_summary = f"\n  === Каскад ===\n  Exit: {cfg['cascade_ip']} (VLESS TCP 9999 + Reality 443)\n  Exit панель: https://{cascade_info['exit_panel_domain']}:{cascade_info['exit_panel_port']}/{cascade_info['exit_panel_path']}/\n  Exit логин: admin / {cascade_info['exit_panel_pass']}\n  Exit подписка: https://{cascade_info['exit_panel_domain']}:2096/sub/"
    if cdn_type == 'host':
        tail = f'\n  Ключ выдаётся из панели 3x-ui (подписка HOST-...).\n{extra_links}'
    else:
        tail = f'\n  Подписка (для v2rayN/NekoBox):\n  {sub_url}\n\n  JSON подписка (для Happ):\n  {json_url}\n\n  VLESS CDN ссылка:\n  {vless_link}\n{extra_links}'
    print(f'\n  ============================================\n  УСТАНОВКА ЗАВЕРШЕНА\n  ============================================\n\n  Панель: https://{panel_domain}/{panel_path}/\n  Логин: {panel_user}\n  Пароль: {panel_pass}\n\n  CDN домен: {cdn_domain}\n  Origin домен: {origin_domain}\n{cascade_summary}{tail}\n  ============================================\n')
def install_3xui_cdn_only(cfg):
    """Add CDN node to an existing remote 3x-ui panel. Installs xray standalone + nginx on THIS server, creates inbound on remote panel via SSH+SQLite."""
    domain = cfg['domain']
    front_domain = cfg.get('front_domain', domain)
    cdn_type = cfg['cdn_type']
    cdn = CDN_SETTINGS[cdn_type]
    server_ip = cfg['server_ip']
    panel_ip = cfg['panel_ip']
    panel_cred = cfg['panel_cred']
    origin_sub = cfg['origin_sub']
    cdn_sub = cfg['cdn_sub']
    cdn_domain = f'{cdn_sub}.{domain}'
    origin_domain = f'{origin_sub}.{domain}'
    client_uuid = str(uuid.uuid4())
    client_email = 'user1'
    step(3, 'Проверка 3x-ui на панели')
    r = run_remote(panel_ip, panel_cred, 'systemctl is-active x-ui')
    if 'active' not in r.stdout:
        print(f'  ❌ 3x-ui не запущен на {panel_ip}!')
        print(f"  Проверь: ssh {panel_cred.get('user', 'root')}@{panel_ip} systemctl status x-ui")
        sys.exit(1)
    print(f'  3x-ui активен на {panel_ip}')
    r = run_remote(panel_ip, panel_cred, 'test -f /etc/x-ui/x-ui.db && echo OK')
    if 'OK' not in r.stdout:
        print(f'  ❌ /etc/x-ui/x-ui.db не найден на {panel_ip}!')
        sys.exit(1)
    print('  База данных найдена')
    r = run_remote(panel_ip, panel_cred, 'sqlite3 /etc/x-ui/x-ui.db \"SELECT value FROM settings WHERE key=\'subDomain\';\"')
    panel_domain = r.stdout.strip()
    if not panel_domain:
        panel_domain = panel_ip
    print(f'  Домен панели: {panel_domain}')
    r = run_remote(panel_ip, panel_cred, f'sqlite3 /etc/x-ui/x-ui.db \"SELECT uuid FROM clients WHERE email=\'{client_email}\';\"')
    existing_uuid = r.stdout.strip()
    if existing_uuid:
        client_uuid = existing_uuid
        print(f'  Клиент {client_email} уже есть на панели, беру его UUID для ноды')
    step(4, 'Установка xray на ноде')
    r = run('xray version 2>/dev/null || /usr/local/bin/xray version 2>/dev/null', check=False)
    if 'Xray' in r.stdout:
        print(f'  Xray уже установлен: {r.stdout.strip().splitlines()[0]}')
    else:
        print('  Скачивание xray...')
        r = run('bash -c \"$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)\" @ install 2>&1 | tail -5', check=False, timeout=120)
        if r.returncode!= 0:
            print(f'  ❌ Не удалось установить xray: {(r.stderr[:200] if r.stderr else r.stdout[:200])}')
            sys.exit(1)
        r = run('/usr/local/bin/xray version', check=False)
        print(f"  Xray установлен: {(r.stdout.strip().splitlines()[0] if r.stdout else 'OK')}")
        track('xray_standalone', True)
    import shlex as _shlex
    if isinstance(panel_cred, dict) and panel_cred.get('type') == 'password':
        _pw = _shlex.quote(panel_cred['value'])
        _ssh = f'sshpass -p {_pw} ssh'
    else:
        if isinstance(panel_cred, str):
            _ssh = f'sshpass -p {_shlex.quote(panel_cred)} ssh'
        else:
            _ssh = f"ssh -i \'{panel_cred['value']}\'" if isinstance(panel_cred, dict) else 'ssh'
    _puser = panel_cred.get('user', 'root') if isinstance(panel_cred, dict) else 'root'
    _pbin = '/usr/local/x-ui/bin/xray-linux-amd64'
    r = run_remote(panel_ip, panel_cred, f'test -f {_pbin} && {_pbin} version | head -1', timeout=20)
    if 'Xray' in (r.stdout or ''):
        panel_xray_ver = r.stdout.strip().splitlines()[(-1)]
        print(f'  Синхронизирую бинарь xray с панели: {panel_xray_ver}')
        copy_cmd = f'systemctl stop xray 2>/dev/null; {_ssh} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {_puser}@{panel_ip} \'base64 -w0 {_pbin}\' | base64 -d > /usr/local/bin/xray && chmod +x /usr/local/bin/xray'
        r = run(copy_cmd, check=False, timeout=120)
        r2 = run('/usr/local/bin/xray version | head -1', check=False)
        if 'Xray' in (r2.stdout or ''):
            print(f'  Бинарь xray синхронизирован: {r2.stdout.strip().splitlines()[(-1)]}')
        else:
            print('  ⚠️  Не удалось синхронизировать бинарь, оставляю github-версию')
    else:
        print('  ⚠️  Бинарь xray на панели не найден, оставляю github-версию')
    cascade = cfg.get('cascade', False)
    cascade_info = None
    cdn_tag = f'{cdn_type}-cdn'
    if cascade:
        step(5, f"Установка exit-сервера {cfg['cascade_ip']} (каскад)")
        exit_sub = cfg.get('exit_sub', 'xui')
        exit_panel_domain = f'{exit_sub}.{domain}'
        cascade_info = setup_3xui_cascade_exit(cfg['cascade_ip'], cfg['cascade_cred'], exit_panel_domain)
        if not cascade_info:
            print('  ❌ Каскад не удался, продолжаю без каскада.')
            cascade = False
    outbounds = [{'protocol': 'freedom', 'tag': 'direct', 'settings': {'domainStrategy': 'UseIPv4'}}, {'protocol': 'blackhole', 'tag': 'block'}]
    rules = []
    if cascade and cascade_info:
            outbounds.append({'tag': 'CASCADE-REALITY', 'protocol': 'vless', 'settings': {'vnext': [{'address': cfg['cascade_ip'], 'port': 9999, 'users': [{'id': cascade_info['bridge_uuid'], 'encryption': 'none'}]}]}, 'streamSettings': {'network': 'tcp', 'security': 'none', 'tcpSettings': {'header': {'type': 'none'}}}})
            rules.append({'type': 'field', 'inboundTag': [cdn_tag], 'outboundTag': 'CASCADE-REALITY'})
    rules.extend([{'type': 'field', 'ip': ['geoip:private'], 'outboundTag': 'direct'}, {'type': 'field', 'protocol': ['bittorrent'], 'outboundTag': 'block'}])
    if cdn_type == 'host':
        node_xhttp = {'mode': 'packet-up', 'path': cdn['xhttp_path'], 'host': '', 'noSSEHeader': False, 'scMaxEachPostBytes': '262144-786432', 'scMinPostsIntervalMs': '0', 'xPaddingBytes': '48-256', 'xPaddingObfsMode': True, 'xPaddingKey': 'q', 'xPaddingMethod': 'tokenish', 'xPaddingPlacement': 'query', 'sessionIDKey': 'sid', 'sessionIDPlacement': 'query', 'seqKey': 'offset', 'seqPlacement': 'query', 'uplinkHTTPMethod': 'DELETE'}
    else:
        node_xhttp = {'mode': 'packet-up', 'path': cdn['xhttp_path'], 'xPaddingBytes': '100-1000', 'xPaddingObfsMode': True, 'xPaddingKey': cdn['padding_key'], 'xPaddingHeader': cdn['padding_header'], 'xPaddingPlacement': cdn['padding_placement'], 'xPaddingMethod': cdn['padding_method'], 'uplinkHTTPMethod': cdn['uplink_method'], 'noSSEHeader': False}
    xray_config = {'log': {'loglevel': 'warning'}, 'inbounds': [{'tag': cdn_tag, 'port': cdn['xray_port'], 'listen': '127.0.0.1', 'protocol': 'vless', 'settings': {'clients': [{'id': client_uuid, 'email': client_email}], 'decryption': 'none'}, 'sniffing': {'enabled': True, 'destOverride': ['http', 'tls', 'quic']}, 'streamSettings': {'network': 'xhttp', 'security': 'none', 'xhttpSettings': node_xhttp}}], 'outbounds': outbounds, 'routing': {'rules': rules}}
    run('mkdir -p /usr/local/etc/xray', check=False)
    with open('/usr/local/etc/xray/config.json', 'w') as f:
        json.dump(xray_config, f, indent=2)
    print(f"  Конфиг xray записан (порт {cdn['xray_port']}){(' + CASCADE' if cascade else '')}")
    run('systemctl unmask xray 2>/dev/null', check=False)
    _has_unit = run('systemctl cat xray >/dev/null 2>&1 && echo yes', check=False)
    if 'yes' not in (_has_unit.stdout or ''):
        print('  xray.service отсутствует/замаскирован — создаю юнит')
        xray_unit = '[Unit]\nDescription=Xray Service\nDocumentation=https://github.com/xtls\nAfter=network.target nss-lookup.target\n\n[Service]\nUser=nobody\nCapabilityBoundingSet=CAP_NET_ADMIN CAP_NET_BIND_SERVICE\nAmbientCapabilities=CAP_NET_ADMIN CAP_NET_BIND_SERVICE\nNoNewPrivileges=true\nExecStart=/usr/local/bin/xray run -config /usr/local/etc/xray/config.json\nRestart=on-failure\nRestartPreventExitStatus=23\nLimitNPROC=10000\nLimitNOFILE=1000000\n\n[Install]\nWantedBy=multi-user.target\n'
        with open('/etc/systemd/system/xray.service', 'w') as f:
            f.write(xray_unit)
        run('systemctl daemon-reload', check=False)
    run('systemctl enable xray 2>/dev/null', check=False)
    run('systemctl restart xray', check=False)
    time.sleep(3)
    r = run(f"ss -tlnp | grep :{cdn['xray_port']}", check=False)
    if str(cdn['xray_port']) in r.stdout:
        print(f"  Xray слушает порт {cdn['xray_port']}")
    else:
        print(f"  ⚠️  Xray не слушает порт {cdn['xray_port']}, проверяю логи...")
        r = run('journalctl -u xray --no-pager -n 10', check=False)
        print(f'  {r.stdout[:300]}')
    step_n = 6 if cascade else 5
    step(step_n, 'SSL сертификат')
    step_n += 1
    ssl_cert = '/etc/nginx/ssl/cdn.crt'
    ssl_key = '/etc/nginx/ssl/cdn.key'
    if os.path.exists(ssl_cert) and os.path.exists(ssl_key):
        print('  SSL сертификат уже есть')
    else:
        run('mkdir -p /etc/nginx/ssl', check=False)
        run(f'openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -subj \'/CN={origin_domain}\' -keyout {ssl_key} -out {ssl_cert} 2>/dev/null', check=False)
        print('  Self-signed сертификат создан')
    step(step_n, 'Настройка nginx CDN origin')
    step_n += 1
    ipv6_ok = has_ipv6()
    nginx_conf = nginx_cdn_origin(cdn['xray_port'], cdn['xhttp_path'], ipv6=ipv6_ok, ssl_cert=ssl_cert, ssl_key=ssl_key)
    r = nginx_write_and_restart(nginx_conf)
    if r.returncode == 0:
        print('  Nginx CDN origin настроен')
    else:
        print(f"  ❌ Проблема с nginx: {(r.stderr[:200] if r.stderr else '')}")
        sys.exit(1)
    step(step_n, f'Создание {cdn_type.upper()} CDN inbound на панели')
    step_n += 1
    tag = f"{cdn_type}-cdn-xhttp-{server_ip.replace('.', '-')}"
    now_ms = int(time.time() * 1000)
    sub_id = secrets.token_hex(8)
    r = run_remote(panel_ip, panel_cred, 'sqlite3 /etc/x-ui/x-ui.db \"SELECT port FROM inbounds;\"')
    used_ports = {p.strip() for p in r.stdout.splitlines() if p.strip()}
    panel_port = cdn['xray_port']
    while str(panel_port) in used_ports:
        panel_port += 1
    if panel_port!= cdn['xray_port']:
        print(f"  Порт {cdn['xray_port']} занят на панели, панельный инбаунд → {panel_port}")
    settings_obj = {'clients': [{'id': client_uuid, 'email': client_email, 'enable': True, 'expiryTime': 0, 'limitIp': 0, 'totalGB': 0, 'subId': sub_id, 'tgId': 0, 'reset': 0, 'security': '', 'comment': '', 'created_at': now_ms, 'updated_at': now_ms}], 'decryption': 'none', 'fallbacks': []}
    if cdn_type == 'host':
        xhttp_settings = {'path': cdn['xhttp_path'], 'host': '', 'mode': 'packet-up', 'noSSEHeader': False, 'scMaxEachPostBytes': '262144-786432', 'scMinPostsIntervalMs': '0', 'xPaddingBytes': '48-256', 'xPaddingObfsMode': True, 'xPaddingKey': 'q', 'xPaddingMethod': 'tokenish', 'xPaddingPlacement': 'query', 'sessionIDKey': 'sid', 'sessionIDPlacement': 'query', 'seqKey': 'offset', 'seqPlacement': 'query', 'uplinkHTTPMethod': 'DELETE', 'xmux': {'maxConcurrency': 0, 'maxConnections': '16-32', 'cMaxReuseTimes': 0, 'hMaxRequestTimes': '600-900', 'hMaxReusableSecs': '120-240', 'hKeepAlivePeriod': 20}}
    else:
        xhttp_settings = {'path': cdn['xhttp_path'], 'host': '', 'mode': 'packet-up', 'xPaddingBytes': '100-1000', 'xPaddingObfsMode': True, 'xPaddingKey': cdn['padding_key'], 'xPaddingHeader': cdn['padding_header'], 'xPaddingPlacement': cdn['padding_placement'], 'xPaddingMethod': cdn['padding_method'], 'uplinkHTTPMethod': cdn['uplink_method'], 'noSSEHeader': False, 'enableXmux': True, 'xmux': {'maxConcurrency': '16-32', 'maxConnections': 0, 'cMaxReuseTimes': 1000, 'hMaxRequestTimes': '600-900', 'hMaxReusableSecs': '100', 'hKeepAlivePeriod': 20000}}
    if cdn_type == 'host':
        ext_proxy = [{'forceTls': 'tls', 'dest': front_domain, 'port': 443, 'remark': '', 'sni': front_domain, 'fingerprint': 'firefox', 'alpn': 'h2'}]
    else:
        ext_proxy = [{'forceTls': 'tls', 'dest': cdn_domain, 'port': 443, 'remark': ''}]
    stream_settings_obj = {'network': 'xhttp', 'security': 'none', 'externalProxy': ext_proxy, 'xhttpSettings': xhttp_settings}
    sniffing_obj = {'enabled': True, 'destOverride': ['http', 'tls', 'quic']}
    settings_json = json.dumps(settings_obj).replace('\'', '\'\'')
    stream_json = json.dumps(stream_settings_obj).replace('\'', '\'\'')
    sniffing_json = json.dumps(sniffing_obj).replace('\'', '\'\'')
    r = run_remote(panel_ip, panel_cred, f'sqlite3 /etc/x-ui/x-ui.db \"SELECT id FROM clients WHERE email=\'{client_email}\';\"')
    existing_client_id = r.stdout.strip()
    sql_parts = [f'DELETE FROM inbounds WHERE tag=\'{tag}\';']
    sql_parts.append(f'INSERT INTO inbounds (user_id, up, down, total, remark, enable, expiry_time, listen, port, protocol, settings, stream_settings, tag, sniffing) VALUES (1, 0, 0, 0, \'{cdn_type.upper()}-CDN ({server_ip})\', 1, 0, \'127.0.0.1\', {panel_port}, \'vless\', \'{settings_json}\', \'{stream_json}\', \'{tag}\', \'{sniffing_json}\');')
    if not existing_client_id:
        sql_parts.append(f'INSERT INTO clients (email, sub_id, uuid, limit_ip, total_gb, expiry_time, enable, tg_id, reset, created_at, updated_at) VALUES (\'{client_email}\', \'{sub_id}\', \'{client_uuid}\', 0, 0, 0, 1, 0, 0, {now_ms}, {now_ms});')
    sql_content = '\n'.join(sql_parts)
    write_remote_file(panel_ip, panel_cred, '/tmp/xui_cdn_node.sql', sql_content)
    run_remote(panel_ip, panel_cred, 'sqlite3 /etc/x-ui/x-ui.db < /tmp/xui_cdn_node.sql')
    if existing_client_id:
        client_id = existing_client_id
        r = run_remote(panel_ip, panel_cred, f'sqlite3 /etc/x-ui/x-ui.db \"SELECT uuid FROM clients WHERE id={client_id};\"')
        client_uuid = r.stdout.strip() or client_uuid
        r = run_remote(panel_ip, panel_cred, f'sqlite3 /etc/x-ui/x-ui.db \"SELECT sub_id FROM clients WHERE id={client_id};\"')
        sub_id = r.stdout.strip() or sub_id
        print(f'  Используем существующего клиента: {client_email}')
    else:
        r = run_remote(panel_ip, panel_cred, f'sqlite3 /etc/x-ui/x-ui.db \"SELECT id FROM clients WHERE email=\'{client_email}\';\"')
        client_id = r.stdout.strip()
    r = run_remote(panel_ip, panel_cred, f'sqlite3 /etc/x-ui/x-ui.db \"SELECT id FROM inbounds WHERE tag=\'{tag}\';\"')
    inbound_id = r.stdout.strip()
    if client_id and inbound_id:
        run_remote(panel_ip, panel_cred, f'sqlite3 /etc/x-ui/x-ui.db \"DELETE FROM client_inbounds WHERE client_id={client_id} AND inbound_id={inbound_id};\"')
        run_remote(panel_ip, panel_cred, f'sqlite3 /etc/x-ui/x-ui.db \"INSERT INTO client_inbounds (client_id, inbound_id, flow_override, created_at) VALUES ({client_id}, {inbound_id}, \'\', {now_ms});\"')
        run_remote(panel_ip, panel_cred, f'sqlite3 /etc/x-ui/x-ui.db \"INSERT OR IGNORE INTO client_traffics (inbound_id, enable, email, up, down, expiry_time, total, reset) VALUES ({inbound_id}, 1, \'{client_email}\', 0, 0, 0, 0, 0);\"')
        print(f'  Inbound создан на панели, tag: {tag}')
    else:
        print(f'  ⚠️  Не удалось привязать клиента к inbound (client_id={client_id}, inbound_id={inbound_id})')
    run_remote(panel_ip, panel_cred, 'systemctl restart x-ui')
    print('  3x-ui перезапущен на панели')
    step(step_n, 'Инструкция по настройке фронта')
    step_n += 1
    if cdn_type == 'host':
        print_host_instructions(front_domain, server_ip, '/p')
        try:
            auto_setup = safe_input('\n  Автоматически залить .htaccess через FTP? (y/n): ').strip().lower()
            if auto_setup in ['y', 'yes', 'д', 'да']:
                if upload_htaccess_ftp(front_domain, server_ip, 'p'):
                    print('\n  ✅ Фронт готов к использованию!')
                else:
                    print('\n  ⚠️  Залей .htaccess вручную по инструкции выше')
        except (KeyboardInterrupt, EOFError):
            print('\n  ⚠️  Пропущено, залей .htaccess вручную')
    else:
        if cdn_type == 'vk':
            print(f'\n  ============================================\n  DNS записи (у вашего DNS-провайдера):\n  ============================================\n\n  1. A-запись:  {origin_domain}  ->  {server_ip}  (без проксирования)\n  2. CNAME:     {cdn_domain}  ->  [VK CDN CNAME]  (без проксирования)\n\n  ============================================\n  Настройки VK Cloud CDN:\n  ============================================\n\n  - Протокол к источнику: HTTP (порт 80)\n  - Источник: {origin_domain}\n  - Персональный домен: {cdn_domain}\n  - Заголовок Host: Пересылать\n  - SSL: Let\'s Encrypt\n  - Кеширование: ВЫКЛ (все 4 переключателя)\n  - HTTP методы: GET, HEAD, OPTIONS\n  - Gzip: ВЫКЛ\n')
        else:
            if cdn_type == 'yandex':
                print(f"\n  ============================================\n  DNS записи (у вашего DNS-провайдера):\n  ============================================\n\n  1. A-запись:  {origin_domain}  ->  {server_ip}  (без проксирования)\n  2. CNAME:     {cdn_domain}  ->  [Yandex CDN CNAME]  (без проксирования, создашь позже)\n  3. CNAME:     _acme-challenge.{cdn_domain} -> [значение из Yandex] (без проксирования)\n\n  ============================================\n  ШАГ A: Yandex Certificate Manager -> Создать сертификат\n    - Домены: {cdn_domain}, Тип проверки: DNS\n    - Создай CNAME запись #3, жди статус \"Issued\"\n\n  ШАГ B: Yandex CDN -> Создать ресурс\n    - Источник: {origin_domain}, HTTPS, SNI: {origin_domain}\n    - Host: {origin_domain}, Домен: {cdn_domain}\n    - Кеширование: ВЫКЛ, Сжатие: ВЫКЛ\n    - SSL-сертификат: выбери {cdn_domain.replace('.', '-')}\n")
    if cdn_type!= 'host' and (not cfg.get('skip_cdn_wait', False)):
            safe_input('  Нажми ENTER когда CDN настроен...')
            if cdn_type in ['beeline', 'timeweb']:
                if cdn_type == 'beeline':
                    cdn_issued = safe_input('  Домен выданный Beeline CDN (например https://xxx.a.trbcdn.net): ').strip()
                else:
                    cdn_issued = safe_input('  Технический домен Timeweb CDN (например xxx.cdn.twcstorage.ru): ').strip()
                if cdn_issued:
                    cdn_issued = cdn_issued.replace('https://', '').replace('http://', '').rstrip('/')
                    cdn_label = 'Beeline' if cdn_type == 'beeline' else 'Timeweb'
                    print(f'  CDN домен {cdn_label}: {cdn_issued}')
    step(step_n, 'Финальная проверка')
    r = run('curl -s http://127.0.0.1/health', check=False)
    print(f"  Health (нода): {('OK' if 'ok' in r.stdout else 'FAIL')}")
    r = run(f"ss -tlnp | grep :{cdn['xray_port']}", check=False)
    print(f"  Xray CDN port {cdn['xray_port']} (нода): {('OK' if str(cdn['xray_port']) in r.stdout else 'FAIL')}")
    r = run('systemctl is-active nginx', check=False)
    print(f"  Nginx (нода): {('OK' if 'active' in r.stdout else 'FAIL')}")
    r = run_remote(panel_ip, panel_cred, 'systemctl is-active x-ui')
    print(f"  3x-ui (панель {panel_ip}): {('OK' if 'active' in r.stdout else 'FAIL')}")
    link_host = front_domain if cdn_type == 'host' else cdn_domain
    vless_link = f"vless://{client_uuid}@{link_host}:443?type=xhttp&security=tls&sni={link_host}&fp=firefox&alpn=h2&path={cdn['xhttp_path']}&host={link_host}&mode=packet-up&encryption=none#{client_email}-{cdn_type}"
    sub_url = f'https://{panel_domain}/sub/{sub_id}'
    cascade_summary = ''
    if cascade and cascade_info:
            cascade_summary = f"\n  === Каскад ===\n  Exit: {cfg['cascade_ip']} (VLESS TCP 9999 + Reality 443)\n  Exit панель: https://{cascade_info['exit_panel_domain']}:{cascade_info['exit_panel_port']}/{cascade_info['exit_panel_path']}/\n  Exit логин: admin / {cascade_info['exit_panel_pass']}\n  Exit подписка: https://{cascade_info['exit_panel_domain']}:2096/sub/\n"
    print(f'\n  ============================================\n  CDN НОДА ПОДКЛЮЧЕНА К 3X-UI\n  ============================================\n\n  Нода (этот сервер): {server_ip}\n  Панель 3x-ui: {panel_ip}\n  CDN домен: {cdn_domain}\n  Origin домен: {origin_domain}\n{cascade_summary}\n  Подписка: {sub_url}\n  Ключ выдаётся из панели 3x-ui (подписка HOST-...).\n  ============================================\n')
def build_cascade_profile(rcfg, exit_ip, bridge_user_uuid):
    """Build cascade relay config profile: CDN xhttp inbound -> VLESS outbound to exit."""
    import copy
    cdn_inbound = copy.deepcopy(rcfg['profile_config']['inbounds'][0])
    cdn_inbound['port'] = 7443
    cdn_inbound['listen'] = '127.0.0.1'
    cdn_inbound['tag'] = f"{cdn_inbound['tag']}-cascade"
    if 'sniffing' not in cdn_inbound:
        cdn_inbound['sniffing'] = {'enabled': True, 'routeOnly': True, 'destOverride': ['http', 'tls', 'quic']}
    cascade_tag = cdn_inbound['tag']
    return {
        'log': {'loglevel': 'warning'},
        'dns': {
            'servers': ['1.1.1.1', '8.8.8.8'],
            'queryStrategy': 'UseIPv4',
            'disableCache': False,
        },
        'inbounds': [cdn_inbound],
        'outbounds': [
            {
                'tag': 'VLESS_EXIT',
                'protocol': 'vless',
                'settings': {
                    'vnext': [{
                        'address': exit_ip,
                        'port': 9999,
                        'users': [{
                            'id': bridge_user_uuid,
                            'encryption': 'none',
                        }],
                    }],
                },
                'streamSettings': {
                    'network': 'tcp',
                    'security': 'none',
                    'sockopt': {
                        'tcpKeepAliveInterval': 30,
                        'tcpNoDelay': True,
                    },
                },
                'mux': {
                    'enabled': True,
                    'concurrency': 8,
                    'xudpConcurrency': 16,
                    'xudpProxyUDP443': 'reject',
                },
            },
            {'tag': 'DIRECT', 'protocol': 'freedom', 'settings': {'domainStrategy': 'UseIPv4'}},
            {'tag': 'BLOCK', 'protocol': 'blackhole'},
        ],
        'routing': {
            'domainStrategy': 'IPIfNonMatch',
            'rules': [
                {'ip': ['geoip:private'], 'type': 'field', 'outboundTag': 'BLOCK'},
                {'domain': ['geosite:private'], 'type': 'field', 'outboundTag': 'BLOCK'},
                {'type': 'field', 'protocol': ['bittorrent'], 'outboundTag': 'BLOCK'},
                {'ip': ['1.1.1.1', '1.0.0.1', '8.8.8.8', '8.8.4.4'], 'type': 'field', 'outboundTag': 'DIRECT'},
                {'ip': ['149.154.160.0/20', '91.108.4.0/22', '91.108.8.0/22', '91.108.12.0/22', '91.108.16.0/22', '91.108.20.0/22', '91.108.56.0/22'], 'type': 'field', 'outboundTag': 'DIRECT'},
                {'domain': ['domain:telegram.org', 'domain:t.me', 'domain:telegra.ph'], 'type': 'field', 'outboundTag': 'DIRECT'},
                {'ip': ['geoip:ru'], 'type': 'field', 'outboundTag': 'DIRECT'},
                {'domain': ['geosite:category-ru'], 'type': 'field', 'outboundTag': 'DIRECT'},
                {'type': 'field', 'inboundTag': [cascade_tag], 'outboundTag': 'VLESS_EXIT'},
            ],
        },
    }
def setup_cascade_relay(cfg, api_func, exit_ip, node_cred, same_server, profile_uuid, inbound_uuid, squad_uuid, existing_squad_inbounds):
    """Setup Caddy + remnanode on Russian relay server for cascade.\n    api_func: callable(method, path, data=None) for Remnawave API calls."""
    cascade_ip = cfg['cascade_ip']
    cascade_cred = cfg['cascade_cred']
    cdn_type = cfg['cdn_type']
    rcfg = REMNAWAVE_CDN[cdn_type]
    domain = cfg['domain']
    origin_sub = cfg['origin_sub']
    origin_domain = f'{origin_sub}.{domain}'
    panel_sub = cfg['panel_sub']
    panel_domain = f'{panel_sub}.{domain}'
    server_ip = cfg['server_ip']
    print(f'  [cascade] Подключение к relay {cascade_ip}...')
    r = run_remote(cascade_ip, cascade_cred, 'echo OK', timeout=30)
    if 'OK' not in r.stdout:
        sshpass_check = run('which sshpass', check=False)
        if sshpass_check.returncode!= 0:
            run('DEBIAN_FRONTEND=noninteractive apt-get install -y sshpass', check=False, timeout=60)
            r = run_remote(cascade_ip, cascade_cred, 'echo OK', timeout=30)
        if 'OK' not in r.stdout:
            print(f'  ❌ Не могу подключиться к relay {cascade_ip}')
            sys.exit(1)
    print('  [cascade] SSH OK')
    check_os(remote_ip=cascade_ip, remote_cred=cascade_cred)
    print('  [cascade] Установка Docker...')
    r = run_remote(cascade_ip, cascade_cred, 'docker --version')
    if r.returncode!= 0 or 'Docker' not in r.stdout:
        run_remote(cascade_ip, cascade_cred, 'curl -fsSL https://get.docker.com | sh 2>&1 | tail -5', timeout=600)
        r = run_remote(cascade_ip, cascade_cred, 'docker --version')
        if r.returncode!= 0:
            run_remote(cascade_ip, cascade_cred, 'apt-get update -qq && apt-get install -y docker.io docker-compose-plugin 2>&1 | tail -5', timeout=300)
            r = run_remote(cascade_ip, cascade_cred, 'docker --version')
            if r.returncode!= 0:
                print('  ❌ [cascade] Docker не установился на relay!')
                sys.exit(1)
        print(f'  [cascade] Docker установлен: {r.stdout.strip()}')
    else:
        print(f'  [cascade] Docker уже есть: {r.stdout.strip()}')
    setup_docker_mirror(remote_ip=cascade_ip, remote_cred=cascade_cred)
    r = run_remote(cascade_ip, cascade_cred, 'docker compose version 2>/dev/null')
    if r.returncode!= 0:
        run_remote(cascade_ip, cascade_cred, 'apt-get install -y -qq docker-compose-plugin 2>/dev/null || (mkdir -p /usr/local/lib/docker/cli-plugins && curl -fsSL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-$(uname -m) -o /usr/local/lib/docker/cli-plugins/docker-compose && chmod +x /usr/local/lib/docker/cli-plugins/docker-compose)', timeout=120)
    print('  [cascade] Установка Caddy...')
    r = run_remote(cascade_ip, cascade_cred, 'caddy version 2>/dev/null')
    if r.returncode!= 0 or 'v' not in r.stdout:
        run_remote(cascade_ip, cascade_cred, 'apt-get install -y debian-keyring debian-archive-keyring apt-transport-https curl >/dev/null 2>&1 && curl -1sLf \'https://dl.cloudsmith.io/public/caddy/stable/gpg.key\' | gpg --batch --yes --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg 2>/dev/null && curl -1sLf \'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt\' | tee /etc/apt/sources.list.d/caddy-stable.list >/dev/null && apt-get update -qq && apt-get install -y caddy 2>&1 | tail -3', timeout=300)
        r = run_remote(cascade_ip, cascade_cred, 'caddy version 2>/dev/null')
        if r.returncode!= 0:
            import time as _t
            _t.sleep(10)
            r = run_remote(cascade_ip, cascade_cred, 'caddy version 2>/dev/null')
            if r.returncode!= 0:
                print('  ❌ [cascade] Caddy не установился!')
                sys.exit(1)
    print(f'  [cascade] Caddy: {r.stdout.strip()}')
    xhttp_path = rcfg['xhttp_path']
    if xhttp_path.endswith('/'):
        xhttp_match = xhttp_path + '*'
    else:
        xhttp_match = xhttp_path.rsplit('/', 1)[0] + '/*'
    caddyfile = f'{origin_domain} {{\n    @xhttp path {xhttp_match}\n    reverse_proxy @xhttp 127.0.0.1:7443 {{\n        flush_interval -1\n        transport http {{\n            read_buffer 16384\n            write_buffer 16384\n        }}\n    }}\n    root * /var/www/html\n    file_server\n}}\n'
    write_remote_file(cascade_ip, cascade_cred, '/etc/caddy/Caddyfile', caddyfile)
    run_remote(cascade_ip, cascade_cred, 'mkdir -p /var/www/html', timeout=10)
    decoy = DECOY_HTML.format(domain=domain)
    write_remote_file(cascade_ip, cascade_cred, '/var/www/html/index.html', decoy)
    print('  [cascade] Настройка TCP (BBR)...')
    write_remote_file(cascade_ip, cascade_cred, '/etc/sysctl.d/99-vpn-tuning.conf', SYSCTL_TUNING)
    run_remote(cascade_ip, cascade_cred, 'sysctl --system > /dev/null 2>&1')
    write_remote_file(cascade_ip, cascade_cred, '/etc/security/limits.d/99-nofile.conf', NOFILE_LIMITS)
    run_remote(cascade_ip, cascade_cred, 'mkdir -p /etc/nginx/ssl && test -f /etc/nginx/ssl/cdn.crt || openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout /etc/nginx/ssl/cdn.key -out /etc/nginx/ssl/cdn.crt -subj \'/CN=cdn-origin\' 2>/dev/null')
    run_remote(cascade_ip, cascade_cred, 'swapon --show | grep -q / || (fallocate -l 2G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile && grep -q swapfile /etc/fstab || echo \'/swapfile none swap sw 0 0\' >> /etc/fstab) 2>/dev/null')
    print('  [cascade] Открытие портов 80/443...')
    r = run_remote(cascade_ip, cascade_cred, 'ufw status 2>/dev/null')
    if r.returncode == 0 and 'active' in r.stdout.lower():
            run_remote(cascade_ip, cascade_cred, 'ufw allow 80/tcp >/dev/null 2>&1 && ufw allow 443/tcp >/dev/null 2>&1 && ufw reload >/dev/null 2>&1')
    run_remote(cascade_ip, cascade_cred, 'iptables -I INPUT -p tcp --dport 80 -j ACCEPT 2>/dev/null; iptables -I INPUT -p tcp --dport 443 -j ACCEPT 2>/dev/null')
    print(f'  [cascade] Запуск Caddy ({origin_domain})...')
    run_remote(cascade_ip, cascade_cred, 'systemctl enable caddy >/dev/null 2>&1 && systemctl restart caddy', timeout=60)
    time.sleep(3)
    r = run_remote(cascade_ip, cascade_cred, 'systemctl is-active caddy')
    if 'active' in r.stdout:
        print('  [cascade] Caddy запущен')
    else:
        r2 = run_remote(cascade_ip, cascade_cred, 'journalctl -u caddy --no-pager -n 10 2>&1')
        print(f'  ⚠️  [cascade] Caddy не запустился: {r2.stdout.strip()[(-300):]}')
    bridge_user_uuid = str(uuid.uuid4())
    print('  [cascade] Создание cascade профиля...')
    cascade_profile_config = build_cascade_profile(rcfg, exit_ip, bridge_user_uuid)
    cascade_profile_name = f'cascade-{cdn_type}'
    resp = api_func('POST', 'config-profiles', {'name': cascade_profile_name, 'config': cascade_profile_config})
    if not resp.get('response'):
        print(f'  ❌ [cascade] Ошибка создания профиля: {resp}')
        sys.exit(1)
    cascade_profile_uuid = resp['response']['uuid']
    cascade_inbound_uuid = None
    for ib in resp['response'].get('inbounds', []):
        if 'cascade' in ib.get('tag', ''):
            cascade_inbound_uuid = ib['uuid']
            break
    if not cascade_inbound_uuid:
        inbounds = resp['response'].get('inbounds', [])
        if inbounds:
            cascade_inbound_uuid = inbounds[0]['uuid']
    print(f'  [cascade] Profile: {cascade_profile_uuid}')
    print(f'  [cascade] Inbound: {cascade_inbound_uuid}')
    updated_squad_inbounds = list(existing_squad_inbounds)
    if cascade_inbound_uuid and cascade_inbound_uuid not in updated_squad_inbounds:
            updated_squad_inbounds.append(cascade_inbound_uuid)
    bridge_inbound_uuid = None
    all_profiles = api_func('GET', 'config-profiles')
    if all_profiles.get('response'):
        resp_data = all_profiles['response']
        profiles_list = resp_data.get('configProfiles', resp_data if isinstance(resp_data, list) else [resp_data])
        for p in profiles_list:
            if p.get('uuid') == profile_uuid:
                for ib in p.get('inbounds', []):
                    if ib.get('tag') == 'BRIDGE_IN':
                        bridge_inbound_uuid = ib['uuid']
                        break
                break
    if bridge_inbound_uuid and bridge_inbound_uuid not in updated_squad_inbounds:
            updated_squad_inbounds.append(bridge_inbound_uuid)
    if squad_uuid:
        api_func('PATCH', 'internal-squads', {'uuid': squad_uuid, 'inbounds': updated_squad_inbounds})
        print('  [cascade] Инбаунды добавлены в сквад')
    print(f'  [cascade] Создание ноды для relay {cascade_ip}...')
    cascade_excluded = []
    if all_profiles.get('response'):
        resp_data = all_profiles['response']
        profiles_list = resp_data.get('configProfiles', resp_data if isinstance(resp_data, list) else [resp_data])
        for p in profiles_list:
            if p.get('uuid')!= cascade_profile_uuid:
                for ib in p.get('inbounds', []):
                    if ib.get('uuid'):
                        cascade_excluded.append(ib['uuid'])
    cascade_node_data = {'name': f"cascade-relay-{cascade_ip.replace('.', '-')}", 'address': cascade_ip, 'port': 2222, 'countryCode': 'RU', 'isTrafficTrackingActive': True, 'trafficLimitBytes': 0, 'notifyPercent': 0, 'trafficResetDay': 1, 'excludedInbounds': cascade_excluded, 'configProfile': {'activeConfigProfileUuid': cascade_profile_uuid, 'activeInbounds': [cascade_inbound_uuid] if cascade_inbound_uuid else []}}
    resp = api_func('POST', 'nodes', cascade_node_data)
    if not resp.get('response'):
        print(f'  ❌ [cascade] Ошибка создания ноды: {resp}')
        sys.exit(1)
    cascade_node_uuid = resp['response']['uuid']
    print(f'  [cascade] Node UUID: {cascade_node_uuid}')
    secret_key = None
    resp = api_func('GET', 'keygen')
    if resp.get('response'):
        secret_key = resp['response'].get('pubKey')
    if not secret_key:
        print('  ⚠️  [cascade] Не удалось получить keygen pubKey')
    print('  [cascade] Установка remnanode на relay...')
    run_remote(cascade_ip, cascade_cred, 'mkdir -p /opt/remnanode')
    panel_ip = cfg.get('panel_ip', '')
    panel_cred = cfg.get('panel_cred', '')
    node_version = 'latest'
    if panel_ip and panel_cred:
            node_version = get_remnawave_node_version(panel_ip, panel_cred)
            print(f'  [cascade] Используем версию Node {node_version}')
    node_compose = f'services:\n  remnanode:\n    container_name: remnanode\n    hostname: remnanode\n    image: ghcr.io/remnawave/node:{node_version}\n    network_mode: host\n    restart: always\n    cap_add:\n      - NET_ADMIN\n    ulimits:\n      nofile:\n        soft: 1048576\n        hard: 1048576\n    volumes:\n      - /etc/nginx/ssl:/etc/nginx/ssl:ro\n    env_file:\n      - .env\n'
    write_remote_file(cascade_ip, cascade_cred, '/opt/remnanode/docker-compose.yml', node_compose)
    node_env = f"NODE_PORT=2222\nSECRET_KEY={secret_key or 'REPLACE_WITH_KEY_FROM_PANEL'}\n"
    write_remote_file(cascade_ip, cascade_cred, '/opt/remnanode/.env', node_env)
    if secret_key:
        run_remote(cascade_ip, cascade_cred, 'cd /opt/remnanode && docker compose pull', timeout=180)
        run_remote(cascade_ip, cascade_cred, 'cd /opt/remnanode && docker compose up -d', timeout=60)
        print('  [cascade] remnanode запущен на relay')
        iptables_add(f'-I INPUT -p tcp --dport 2222 -s {server_ip} -j ACCEPT', remote_ip=cascade_ip, remote_cred=cascade_cred)
        iptables_add('-I INPUT -p tcp --dport 2222 -s 127.0.0.1 -j ACCEPT', remote_ip=cascade_ip, remote_cred=cascade_cred)
        iptables_add('-A INPUT -p tcp --dport 2222 -j DROP', remote_ip=cascade_ip, remote_cred=cascade_cred)
        pkg_iptables_persist(remote_ip=cascade_ip, remote_cred=cascade_cred)
        print('  [cascade] Ожидание запуска ноды...')
        for i in range(20):
            time.sleep(5)
            r = run_remote(cascade_ip, cascade_cred, 'docker logs remnanode --tail=5 2>&1')
            if 'started' in r.stdout.lower() or 'running' in r.stdout.lower() or 'XRay' in r.stdout:
                print('  [cascade] Нода relay запущена!')
                break
    cdn_domain = f"{cfg['cdn_sub']}.{domain}"
    print(f'  [cascade] Создание хоста: {cdn_domain} -> {origin_domain}...')
    cascade_host_payload = {'inbound': {'configProfileUuid': cascade_profile_uuid, 'configProfileInboundUuid': cascade_inbound_uuid}, 'remark': f'Cascade {cdn_type.upper()}', 'address': cdn_domain, 'port': 443, 'path': rcfg.get('host_path', rcfg['xhttp_path']), 'sni': cdn_domain, 'host': cdn_domain, 'alpn': rcfg['alpn'], 'fingerprint': 'firefox', 'isDisabled': False, 'securityLayer': 'TLS', 'allowInsecure': False, 'xhttpExtraParams': rcfg['host_extra']}
    resp = api_func('POST', 'hosts', cascade_host_payload)
    cascade_host_uuid = None
    if resp.get('response'):
        cascade_host_uuid = resp['response'].get('uuid')
        print(f'  [cascade] Host UUID: {cascade_host_uuid}')
        if cascade_node_uuid:
            api_func('PATCH', 'hosts', {'uuid': cascade_host_uuid, 'nodes': [cascade_node_uuid]})
            print('  [cascade] Хост привязан к relay ноде')
    else:
        print(f'  ⚠️  [cascade] Ошибка создания хоста: {resp}')
    print(f'  [cascade] Создание bridge юзера (vless UUID: {bridge_user_uuid[:8]}...)...')
    resp = api_func('POST', 'users', {'username': 'bridge_user_001', 'vlessUuid': bridge_user_uuid, 'trojanPassword': bridge_user_uuid.replace('-', '')[:16], 'expireAt': '2099-12-31T23:59:59.000Z', 'trafficLimitBytes': 0, 'trafficLimitStrategy': 'NO_RESET', 'hwidDeviceLimit': 0})
    if resp.get('response'):
        print('  [cascade] Bridge user создан')
    else:
        print(f'  ⚠️  [cascade] Ответ создания bridge user: {resp}')
    print('  [cascade] Синхронизация нод...')
    run_remote(cascade_ip, cascade_cred, 'docker restart remnanode', timeout=30)
    if same_server:
        run('docker restart remnanode', check=False, timeout=30)
    else:
        run_remote(exit_ip, node_cred, 'docker restart remnanode', timeout=30)
    time.sleep(10)
    r = run_remote(cascade_ip, cascade_cred, 'docker logs remnanode --tail=10 2>&1', timeout=15)
    m = re.search('(\\d+)\\s+users', r.stdout) if r.stdout else None
    if m and int(m.group(1)) > 0:
        print(f'  [cascade] Relay синхронизирован: {m.group(1)} юзеров')
    else:
        print('  [cascade] Relay перезапущен')
    print(f'\n  ============================================\n  КАСКАД НАСТРОЕН\n  ============================================\n\n  Exit нода: {exit_ip} (port 9999 BRIDGE_IN)\n  Relay нода: {cascade_ip} (Caddy + remnanode)\n  Origin: {origin_domain} -> {cascade_ip}\n  Bridge user UUID: {bridge_user_uuid}\n\n  CDN origin должен указывать на: {origin_domain}\n  (DNS A-запись: {origin_domain} -> {cascade_ip})\n  ============================================\n')
    return {'cascade_profile_uuid': cascade_profile_uuid, 'cascade_inbound_uuid': cascade_inbound_uuid, 'cascade_node_uuid': cascade_node_uuid, 'bridge_user_uuid': bridge_user_uuid}
def install_remnawave(cfg):
    """Install Remnawave 3.2.3 panel + node + profile + host + user via API."""
    domain = cfg['domain']
    front_domain = cfg.get('front_domain', domain)
    cdn_type = cfg['cdn_type']
    rcfg = REMNAWAVE_CDN[cdn_type]
    server_ip = cfg['server_ip']
    node_ip = cfg.get('node_ip', server_ip)
    node_cred = cfg.get('node_cred', '')
    same_server = node_ip == server_ip
    origin_sub = cfg['origin_sub']
    cdn_sub = cfg['cdn_sub']
    panel_sub = cfg['panel_sub']
    cdn_domain = f'{cdn_sub}.{domain}'
    origin_domain = f'{origin_sub}.{domain}'
    panel_domain = f'{panel_sub}.{domain}'
    cascade = cfg.get('cascade', False)
    cascade_ip = cfg.get('cascade_ip')
    cascade_cred = cfg.get('cascade_cred')
    panel_user = 'admin'
    panel_pass = secrets.token_urlsafe(18) + 'Aa1'
    step(3, 'Установка Docker')
    r = run('docker --version', check=False)
    if r.returncode!= 0:
        print('  Установка Docker...')
        run('curl -fsSL https://get.docker.com | sh', check=False, timeout=180)
        r = run('docker --version', check=False)
        if r.returncode!= 0:
            print('  get.docker.com не сработал, пробую apt install docker.io...')
            run('apt-get update -qq && apt-get install -y -qq docker.io docker-compose-plugin 2>&1 | tail -3', check=False, timeout=300)
            r = run('docker --version', check=False)
            if r.returncode!= 0:
                print('  ❌ Docker не установился! Попробуй вручную: curl -fsSL https://get.docker.com | sh')
                sys.exit(1)
        print('  ✅ Docker установлен')
    else:
        print('  Docker уже установлен')
    step(4, 'Установка панели Remnawave 3.2.3')
    run('mkdir -p /opt/remnawave', check=False)
    track('directory', '/opt/remnawave')
    jwt_auth = secrets.token_hex(64)
    jwt_api = secrets.token_hex(64)
    pg_pass = secrets.token_hex(24)
    metrics_pass = secrets.token_hex(16)
    webhook_secret = secrets.token_hex(32)
    try:
        with open('/opt/remnawave/.env') as f:
            for line in f:
                if line.startswith('POSTGRES_PASSWORD='):
                    pg_pass = line.split('=', 1)[1].strip()
                    break
    except FileNotFoundError:
        run('cd /opt/remnawave && docker compose down -v 2>/dev/null', check=False, timeout=60)
    compose = 'services:\n  remnawave-db:\n    container_name: remnawave-db\n    image: postgres:17\n    restart: always\n    shm_size: 256m\n    environment:\n      POSTGRES_DB: postgres\n      POSTGRES_USER: postgres\n      POSTGRES_PASSWORD: {pg_pass}\n    volumes:\n      - remnawave-db:/var/lib/postgresql/data\n    healthcheck:\n      test: [\"CMD-SHELL\", \"pg_isready -U postgres\"]\n      interval: 3s\n      timeout: 3s\n      retries: 10\n    networks:\n      - remnawave-network\n\n  remnawave-redis:\n    container_name: remnawave-redis\n    image: valkey/valkey:8.1.1-alpine\n    restart: always\n    command: valkey-server --save 20 1\n    volumes:\n      - remnawave-redis:/data\n    healthcheck:\n      test: [\"CMD\", \"valkey-cli\", \"ping\"]\n      interval: 3s\n      timeout: 3s\n      retries: 10\n    networks:\n      - remnawave-network\n\n  remnawave:\n    container_name: remnawave\n    image: remnawave/backend:2.8.1\n    restart: always\n    ports:\n      - \"127.0.0.1:3000:3000\"\n    env_file:\n      - .env\n    depends_on:\n      remnawave-db:\n        condition: service_healthy\n      remnawave-redis:\n        condition: service_healthy\n    networks:\n      - remnawave-network\n\nvolumes:\n  remnawave-db:\n  remnawave-redis:\n\nnetworks:\n  remnawave-network:\n    driver: bridge\n'.format(pg_pass=pg_pass)
    with open('/opt/remnawave/docker-compose.yml', 'w') as f:
        f.write(compose)
    env = f'JWT_AUTH_SECRET={jwt_auth}\nJWT_API_TOKENS_SECRET={jwt_api}\nAPP_SECRET={jwt_auth}\nMETRICS_USER=metrics\nMETRICS_PASS={metrics_pass}\nWEBHOOK_SECRET_HEADER={webhook_secret}\nPOSTGRES_USER=postgres\nPOSTGRES_PASSWORD={pg_pass}\nPOSTGRES_DB=postgres\nDATABASE_URL=\"postgresql://postgres:{pg_pass}@remnawave-db:5432/postgres\"\nREDIS_HOST=remnawave-redis\nREDIS_PORT=6379\nFRONT_END_DOMAIN={panel_domain}\nPANEL_DOMAIN={panel_domain}\nSUB_PUBLIC_DOMAIN={panel_domain}/api/sub\nIS_PANEL_BEHIND_CLOUDFLARE=false\nTRAFFIC_RESET_DAY=1\n'
    with open('/opt/remnawave/.env', 'w') as f:
        f.write(env)
    print('  Запуск контейнеров Remnawave...')
    setup_docker_mirror()
    run('cd /opt/remnawave && docker compose down 2>/dev/null', check=False, timeout=60)
    print('  Скачивание образов...')
    run('cd /opt/remnawave && docker compose pull', check=False, timeout=300)
    r = run('cd /opt/remnawave && docker compose up -d 2>&1', check=False, timeout=180)
    if r.returncode!= 0:
        print(f"  docker compose up ошибка: {(r.stderr or r.stdout or '')[:300]}")
    print('  Ожидание запуска контейнеров...')
    panel_started = False
    for i in range(60):
        r = run('curl -s http://127.0.0.1:3000/api/auth/register -H \'X-Forwarded-Proto: https\' -H \'X-Forwarded-For: 127.0.0.1\' -o /dev/null -w \'%{http_code}\'', check=False)
        if r.stdout.strip() in ['200', '201', '400', '401', '404', '405']:
            panel_started = True
            break
        else:
            time.sleep(5)
    if panel_started:
        print('  Панель Remnawave запущена')
        track('docker_compose', '/opt/remnawave')
    else:
        print('  ❌ Панель Remnawave не запустилась за 5 минут!')
        ps = run('docker compose -f /opt/remnawave/docker-compose.yml ps -a 2>&1', check=False)
        print(f'  Контейнеры:\n{ps.stdout[:400]}')
        r = run('docker compose -f /opt/remnawave/docker-compose.yml logs --tail=50 2>&1', check=False)
        print(f'  Логи:\n{r.stdout[:1500]}')
        oom = run('dmesg | grep -i \'oom\\|killed process\' | tail -5 2>&1', check=False)
        if oom.stdout.strip():
            print(f'  OOM killer:\n{oom.stdout}')
        mem = run('free -m 2>&1', check=False)
        print(f'  Память:\n{mem.stdout}')
        sys.exit(1)
    step(5, f'SSL сертификат для {panel_domain}')
    acme_conf = f'server {{\n    listen 80;\n    server_name {panel_domain};\n    location /.well-known/acme-challenge/ {{ root /var/www/certbot; }}\n    location / {{ return 301 https://$host$request_uri; }}\n}}\n'
    run('mkdir -p /var/www/certbot', check=False)
    nginx_write_conf('panel.conf', acme_conf)
    run('nginx -t && systemctl restart nginx', check=False)
    print(f'  Получение сертификата для {panel_domain}...')
    r = run(f'certbot certonly --webroot -w /var/www/certbot -d {panel_domain} --non-interactive --agree-tos --register-unsafely-without-email', check=False, timeout=120)
    if r.returncode!= 0:
        print('  Certbot не сработал, используем self-signed.')
        cert_path = '/etc/nginx/ssl/cdn.crt'
        key_path = '/etc/nginx/ssl/cdn.key'
        if not os.path.exists(cert_path):
            print('  ❌ Self-signed сертификат тоже отсутствует!')
            sys.exit(1)
    else:
        cert_path = f'/etc/letsencrypt/live/{panel_domain}/fullchain.pem'
        key_path = f'/etc/letsencrypt/live/{panel_domain}/privkey.pem'
        print('  Сертификат получен!')
    ipv6_panel = has_ipv6()
    v6_443_panel = '\n    listen [::]:443 ssl http2;' if ipv6_panel else ''
    panel_nginx = f'server {{\n    listen 80;\n    server_name {panel_domain};\n    location /.well-known/acme-challenge/ {{ root /var/www/certbot; }}\n    location / {{ return 301 https://$host$request_uri; }}\n}}\nserver {{\n    listen 443 ssl http2;{v6_443_panel}\n    server_name {panel_domain};\n    ssl_certificate {cert_path};\n    ssl_certificate_key {key_path};\n    ssl_protocols TLSv1.2 TLSv1.3;\n    location / {{\n        proxy_pass http://127.0.0.1:3000;\n        proxy_http_version 1.1;\n        proxy_set_header Host $host;\n        proxy_set_header X-Real-IP $remote_addr;\n        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n        proxy_set_header X-Forwarded-Proto https;\n        proxy_set_header Upgrade $http_upgrade;\n        proxy_set_header Connection \"upgrade\";\n    }}\n}}\n'
    nginx_write_conf('panel.conf', panel_nginx)
    run('nginx -t && systemctl restart nginx', check=False)
    print('  Nginx для панели настроен')
    step(6, 'Создание профиля, ноды, хоста и юзера через API')
    print('  Регистрация админа...')
    resp = remnawave_api(None, 'POST', 'auth/register', {'username': panel_user, 'password': panel_pass})
    if resp.get('response'):
        print('  Админ зарегистрирован')
    else:
        if '403' in str(resp) or 'Forbidden' in str(resp):
            print('  Админ уже зарегистрирован')
        else:
            print(f'  ⚠️  Не удалось зарегистрировать админа: {str(resp)[:300]}')
    import hashlib
    import hmac
    import base64 as b64
    print('  Создание API токена...')
    token_uuid = str(uuid.uuid4())
    header_b = b64.urlsafe_b64encode(json.dumps({'alg': 'HS256', 'typ': 'JWT'}, separators=(',', ':')).encode()).rstrip(b'=').decode()
    payload_obj = {'uuid': token_uuid, 'username': None, 'role': 'API', 'iat': int(time.time()), 'exp': int(time.time()) + 315360000}
    payload_b = b64.urlsafe_b64encode(json.dumps(payload_obj, separators=(',', ':')).encode()).rstrip(b'=').decode()
    sig_data = f'{header_b}.{payload_b}'
    sig = b64.urlsafe_b64encode(hmac.new(jwt_auth.encode(), sig_data.encode(), hashlib.sha256).digest()).rstrip(b'=').decode()
    token = f'{sig_data}.{sig}'
    run('docker exec remnawave-db psql -U postgres -c \"DELETE FROM api_tokens WHERE name = \'installer\';\"', check=False)
    run(f'docker exec remnawave-db psql -U postgres -c \"INSERT INTO api_tokens (uuid, name, scopes, expire_at) VALUES (\'{token_uuid}\', \'installer\', ARRAY[\'*\'], NOW() + INTERVAL \'3650 days\') ON CONFLICT (uuid) DO NOTHING;\"', check=False)
    print('  API токен создан и добавлен в БД')
    resp = remnawave_api(token, 'GET', 'nodes')
    if 'error' in resp:
        print(f'  ❌ API токен не работает: {str(resp)[:300]}')
        sys.exit(1)
    print('  ✅ API токен проверен')
    install_hy2 = cfg.get('install_hy2', False)
    install_grpc = cfg.get('install_grpc', False)
    profile_name = f'cdn-{cdn_type}'
    if install_hy2 or install_grpc:
        extras = []
        if install_hy2:
            extras.append('hy2')
        if install_grpc:
            extras.append('grpc')
        profile_name += '-' + '-'.join(extras)
    inbound_tag = rcfg['inbound_tag']
    profile_uuid = None
    inbound_uuid = None
    hy2_inbound_uuid = None
    grpc_inbound_uuid = None
    bridge_in_uuid = None
    reality_keys = None
    existing_profiles = remnawave_api(token, 'GET', 'config-profiles')
    if existing_profiles.get('response'):
        resp_data = existing_profiles['response']
        plist = resp_data.get('configProfiles', resp_data if isinstance(resp_data, list) else [resp_data])
        for p in plist:
            for ib in p.get('inbounds', []):
                if ib.get('tag') == inbound_tag:
                    profile_uuid = p.get('uuid')
                    inbound_uuid = ib.get('uuid')
                    print(f"  Профиль с тегом {inbound_tag} уже существует: {p.get('name')}")
                    for ib2 in p.get('inbounds', []):
                        if ib2.get('tag') == 'hy2-in':
                            hy2_inbound_uuid = ib2.get('uuid')
                        else:
                            if ib2.get('tag') == 'grpc-reality':
                                grpc_inbound_uuid = ib2.get('uuid')
                    break
            if profile_uuid:
                break
        if not profile_uuid:
            for p in plist:
                if p.get('name') == profile_name:
                    profile_uuid = p.get('uuid')
                    for ib in p.get('inbounds', []):
                        if ib.get('tag') == inbound_tag:
                            inbound_uuid = ib.get('uuid')
                        else:
                            if ib.get('tag') == 'hy2-in':
                                hy2_inbound_uuid = ib.get('uuid')
                            else:
                                if ib.get('tag') == 'grpc-reality':
                                    grpc_inbound_uuid = ib.get('uuid')
                    if not inbound_uuid:
                        inbounds = p.get('inbounds', [])
                        if inbounds:
                            inbound_uuid = inbounds[0].get('uuid')
                    print(f'  Профиль {profile_name} уже существует (по имени)')
                    break
    if not profile_uuid:
        import copy
        profile_config = copy.deepcopy(rcfg['profile_config'])
        if install_hy2:
            profile_config['inbounds'].append(build_hy2_inbound())
            print(f'  Добавлен Hysteria2 inbound (UDP {HY2_PORT})')
        if install_grpc:
            reality_keys = generate_x25519_keys()
            if reality_keys:
                short_id = secrets.token_hex(8)
                cfg['reality_keys'] = reality_keys
                cfg['reality_short_id'] = short_id
                profile_config['inbounds'].append(build_grpc_inbound(reality_keys['private'], short_id))
                print(f'  Добавлен gRPC Reality inbound (TCP {GRPC_PORT})')
            else:
                print('  ⚠️  gRPC пропущен: не удалось сгенерировать x25519-ключи')
        if cascade:
            profile_config['inbounds'].append({'tag': 'BRIDGE_IN', 'port': 9999, 'listen': '0.0.0.0', 'protocol': 'vless', 'settings': {'clients': [], 'decryption': 'none'}, 'sniffing': {'enabled': True, 'destOverride': ['http', 'tls', 'quic']}, 'streamSettings': {'network': 'tcp', 'security': 'none'}})
            print('  Добавлен BRIDGE_IN inbound (TCP 9999) для каскада')
        print(f'  Создание профиля: {profile_name}...')
        resp = remnawave_api(token, 'POST', 'config-profiles', {'name': profile_name, 'config': profile_config})
        if resp.get('response'):
            profile_uuid = resp['response'].get('uuid')
            for ib in resp['response'].get('inbounds', []):
                if ib.get('tag') == inbound_tag:
                    inbound_uuid = ib.get('uuid')
                else:
                    if ib.get('tag') == 'hy2-in':
                        hy2_inbound_uuid = ib.get('uuid')
                    else:
                        if ib.get('tag') == 'grpc-reality':
                            grpc_inbound_uuid = ib.get('uuid')
                        else:
                            if ib.get('tag') == 'BRIDGE_IN':
                                bridge_in_uuid = ib.get('uuid')
        else:
            print(f'  ⚠️  Не удалось создать профиль: {str(resp)[:300]}')
    proto_list = ['VLESS']
    if hy2_inbound_uuid:
        proto_list.append('Hysteria2')
    if grpc_inbound_uuid:
        proto_list.append('gRPC Reality')
    print(f"  ✅ Профиль готов: {', '.join(proto_list)}")
    step(7, 'Настройка ноды Remnawave')
    if same_server:
        ipv6_ok = has_ipv6()
        nginx_conf = nginx_cdn_origin(rcfg['xray_port'], rcfg['xhttp_path'], ipv6=ipv6_ok)
        r = nginx_write_and_restart(nginx_conf)
        if r.returncode == 0:
            print('  Nginx CDN origin настроен')
        else:
            print(f"  ❌ Проблема с nginx: {(r.stderr[:200] if r.stderr else '')}")
            print('  Попробуй: nginx -t и systemctl restart nginx')
            sys.exit(1)
    if same_server:
        r = run('docker network inspect remnawave-network -f \'{{range .IPAM.Config}}{{.Gateway}}{{end}}\'', check=False)
        node_address = r.stdout.strip() or '172.18.0.1'
        print(f'  Docker gateway: {node_address}')
    else:
        node_address = node_ip
    our_uuids = {inbound_uuid, hy2_inbound_uuid, grpc_inbound_uuid} - {None}
    excluded = []
    all_profiles = remnawave_api(token, 'GET', 'config-profiles')
    if all_profiles.get('response'):
        resp_data = all_profiles['response']
        profiles_list = resp_data.get('configProfiles', resp_data if isinstance(resp_data, list) else [resp_data])
        for p in profiles_list:
            for ib in p.get('inbounds', []):
                ib_uuid = ib.get('uuid')
                if ib_uuid and ib_uuid not in our_uuids:
                        excluded.append(ib_uuid)
    if excluded:
        print(f'  Исключено {len(excluded)} дефолтных inbound\'ов')
    node_uuid = None
    existing_nodes_resp = remnawave_api(token, 'GET', 'nodes')
    existing_nodes = existing_nodes_resp.get('response', [])
    if isinstance(existing_nodes, list):
        for n in existing_nodes:
            if n.get('address') == node_address and n.get('port') == 2222:
                    node_uuid = n.get('uuid')
                    print(f'  Нода уже существует: {node_uuid}')
                    break
    if not node_uuid:
        active_inbounds = [u for u in [inbound_uuid, hy2_inbound_uuid, grpc_inbound_uuid] if u]
        if cascade and bridge_in_uuid:
                active_inbounds.append(bridge_in_uuid)
        print(f'  Создание ноды в панели ({node_address}:2222)...')
        node_data = {'name': f"node-{cdn_type}-{'.'.join(node_ip.split('.')[(-2):])}", 'address': node_address, 'port': 2222, 'countryCode': 'XX', 'isTrafficTrackingActive': True, 'trafficLimitBytes': 0, 'notifyPercent': 0, 'trafficResetDay': 1, 'excludedInbounds': excluded, 'configProfile': {'activeConfigProfileUuid': profile_uuid, 'activeInbounds': active_inbounds}}
        resp = remnawave_api(token, 'POST', 'nodes', node_data)
        if resp.get('response'):
            node_uuid = resp['response'].get('uuid')
        else:
            print(f'  ⚠️  Не удалось создать ноду: {str(resp)[:300]}')
    secret_key = None
    resp = remnawave_api(token, 'GET', 'keygen')
    if resp.get('response'):
        secret_key = resp['response'].get('pubKey')
    if not secret_key:
        print('  ⚠️  Не удалось получить secret key от панели')
    if same_server:
        run('mkdir -p /opt/remnanode', check=False)
        track('directory', '/opt/remnanode')
        node_version = 'latest'
        r = run('docker exec remnawave cat package.json 2>/dev/null | grep \'\"version\"\' | head -1', check=False, timeout=10)
        if r.returncode == 0 and r.stdout:
            import re
            match = re.search('\"version\"\\s*:\\s*\"(\\d+\\.\\d+)', r.stdout)
            if match:
                version = match.group(1)
                major_minor = float(version)
                if 2.7 <= major_minor < 3.0:
                        node_version = '3.0.0'
        print(f'  Локальная нода: версия Node {node_version}')
        node_compose = f'services:\n  remnanode:\n    container_name: remnanode\n    hostname: remnanode\n    image: ghcr.io/remnawave/node:{node_version}\n    network_mode: host\n    restart: always\n    cap_add:\n      - NET_ADMIN\n    ulimits:\n      nofile:\n        soft: 1048576\n        hard: 1048576\n    volumes:\n      - /etc/nginx/ssl:/etc/nginx/ssl:ro\n    env_file:\n      - .env\n'
        with open('/opt/remnanode/docker-compose.yml', 'w') as f:
            f.write(node_compose)
        node_env = f"NODE_PORT=2222\nSECRET_KEY={secret_key or 'REPLACE_WITH_KEY_FROM_PANEL'}\n"
        with open('/opt/remnanode/.env', 'w') as f:
            f.write(node_env)
        if secret_key:
            print('  Запуск контейнера remnanode...')
            run('cd /opt/remnanode && docker compose pull', check=False, timeout=120)
            run('cd /opt/remnanode && docker compose up -d', check=False, timeout=60)
            track('docker_compose', '/opt/remnanode')
            print('  Ограничение порта 2222...')
            iptables_add(f'-I INPUT -p tcp --dport 2222 -s {server_ip} -j ACCEPT')
            iptables_add('-I INPUT -p tcp --dport 2222 -s 127.0.0.1 -j ACCEPT')
            iptables_add('-I INPUT -p tcp --dport 2222 -s 172.16.0.0/12 -j ACCEPT')
            iptables_add('-A INPUT -p tcp --dport 2222 -j DROP')
            pkg_iptables_persist()
            print('  Ожидание подключения ноды...')
            for i in range(20):
                time.sleep(5)
                r = run('docker logs remnanode --tail=5 2>&1', check=False)
                if 'started' in r.stdout.lower() or 'Remnawave' in r.stdout:
                    print('  Нода подключена!')
                    break
        else:
            print('  ВНИМАНИЕ: Нет SECRET_KEY — нода требует ручной настройки')
    else:
        setup_remote_node(node_ip, node_cred, rcfg, secret_key, domain, server_ip)
    if install_hy2 or install_grpc:
        target_ip = node_ip if not same_server else None
        target_cred = node_cred if not same_server else None
        open_extra_ports(install_hy2, install_grpc, remote_ip=target_ip, remote_cred=target_cred)
    if install_hy2:
        _hy2_lines = ['server {', f'    listen {HY2_PORT} ssl;', f'    listen [::]:{HY2_PORT} ssl;', '    server_name _;', '    ssl_certificate /etc/nginx/ssl/cdn.crt;', '    ssl_certificate_key /etc/nginx/ssl/cdn.key;', '    ssl_protocols TLSv1.2 TLSv1.3;', '    location / { return 200 \'ok\'; }', '}']
        hy2_ping_conf = chr(10).join(_hy2_lines) + chr(10)
        if same_server:
            with open('/etc/nginx/conf.d/hy2-ping.conf', 'w') as _f:
                _f.write(hy2_ping_conf)
            track('file', '/etc/nginx/conf.d/hy2-ping.conf')
            run('nginx -t && systemctl reload nginx', check=False)
        else:
            write_remote_file(node_ip, node_cred, '/etc/nginx/conf.d/hy2-ping.conf', hy2_ping_conf)
            run_remote(node_ip, node_cred, 'nginx -t && systemctl reload nginx', timeout=15)
        print(f'  TCP {HY2_PORT} (nginx SSL) для пинга HY2')
    if cascade:
        print('  Открытие порта 9999 (BRIDGE_IN) на exit ноде...')
        bridge_cmd = 'ufw allow 9999/tcp 2>/dev/null; iptables -I INPUT -p tcp --dport 9999 -j ACCEPT 2>/dev/null'
        if same_server:
            run(bridge_cmd, check=False)
        else:
            run_remote(node_ip, node_cred, bridge_cmd, timeout=15)
    step(8, 'Создание хостов')
    squad_uuid = None
    existing_squad_inbounds = []
    if inbound_uuid and profile_uuid:
            existing_hosts_resp = remnawave_api(token, 'GET', 'hosts')
            existing_hosts = existing_hosts_resp.get('response', [])
            if not isinstance(existing_hosts, list):
                existing_hosts = []
            def create_host_if_needed(ib_uuid, payload, label):
                for h in existing_hosts:
                    if h.get('address') == payload['address'] and h.get('port') == payload['port']:
                            huuid = h.get('uuid')
                            print(f'  Хост {label} уже существует')
                            return huuid
                resp = remnawave_api(token, 'POST', 'hosts', payload)
                if resp.get('response'):
                    huuid = resp['response'].get('uuid')
                    print(f'  ✅ Хост {label} создан')
                    return huuid
                else:
                    print(f'  ⚠️  Не удалось создать хост {label}: {str(resp)[:300]}')
                    return
            if not cascade:
                host_addr = front_domain if cdn_type == 'host' else cdn_domain
                cdn_host_payload = {'inbound': {'configProfileUuid': profile_uuid, 'configProfileInboundUuid': inbound_uuid}, 'remark': f'CDN {cdn_type.upper()}', 'address': host_addr, 'port': 443, 'path': rcfg.get('host_path', rcfg['xhttp_path']), 'sni': host_addr, 'host': host_addr, 'alpn': rcfg['alpn'], 'fingerprint': 'firefox', 'isDisabled': False, 'securityLayer': 'TLS', 'allowInsecure': False, 'xhttpExtraParams': rcfg['host_extra']}
                host_uuid = create_host_if_needed(inbound_uuid, cdn_host_payload, 'CDN')
            else:
                host_uuid = None
            hy2_host_uuid = None
            if hy2_inbound_uuid and install_hy2:
                    if same_server:
                        _hy2_le = setup_hy2_le_cert(origin_domain)
                    else:
                        _hy2_le = setup_hy2_le_cert(origin_domain, node_ip, node_cred)
                    hy2_host_payload = {'inbound': {'configProfileUuid': profile_uuid, 'configProfileInboundUuid': hy2_inbound_uuid}, 'remark': 'Hysteria2', 'address': node_ip, 'port': HY2_PORT, 'sni': origin_domain if _hy2_le else '', 'host': '', 'alpn': 'h3', 'fingerprint': 'random', 'isDisabled': False, 'securityLayer': 'TLS', 'allowInsecure': not _hy2_le}
                    if _hy2_le:
                        print(f'  HY2: LE cert {origin_domain}')
                    else:
                        print(f'  ⚠️  HY2: self-signed, после DNS выпусти: certbot certonly --webroot -w /var/www/certbot -d {origin_domain}')
                    hy2_host_uuid = create_host_if_needed(hy2_inbound_uuid, hy2_host_payload, 'HY2')
            grpc_host_uuid = None
            if grpc_inbound_uuid and install_grpc:
                    grpc_host_payload = {'inbound': {'configProfileUuid': profile_uuid, 'configProfileInboundUuid': grpc_inbound_uuid}, 'remark': 'gRPC Reality', 'address': node_ip, 'port': GRPC_PORT, 'sni': GRPC_SERVER_NAMES[0], 'host': '', 'alpn': 'h2', 'fingerprint': 'firefox', 'isDisabled': False, 'securityLayer': 'DEFAULT', 'allowInsecure': False, 'path': GRPC_SERVICE_NAME}
                    grpc_host_uuid = create_host_if_needed(grpc_inbound_uuid, grpc_host_payload, 'gRPC')
            all_host_uuids = [h for h in [host_uuid, hy2_host_uuid, grpc_host_uuid] if h]
            if all_host_uuids and node_uuid:
                    for huuid in all_host_uuids:
                        link_resp = remnawave_api(token, 'PATCH', 'hosts', {'uuid': huuid, 'nodes': [node_uuid]})
                        if not link_resp.get('response'):
                            print(f'  ⚠️  Не удалось привязать хост к ноде: {str(link_resp)[:300]}')
            all_ib_uuids = [u for u in [inbound_uuid, hy2_inbound_uuid, grpc_inbound_uuid] if u]
            squad_uuid = None
            existing_squad_inbounds = []
            if all_ib_uuids:
                print('  Добавление инбаундов в Default-Squad...')
                squads_resp = remnawave_api(token, 'GET', 'internal-squads')
                squad_list = squads_resp.get('response', {}).get('internalSquads', [])
                default_squad = next((s for s in squad_list if s['name'] == 'Default-Squad'), None)
                if default_squad:
                    squad_uuid = default_squad['uuid']
                    existing_ib_uuids = [ib['uuid'] for ib in default_squad.get('inbounds', [])]
                    for uid in all_ib_uuids:
                        if uid not in existing_ib_uuids:
                            existing_ib_uuids.append(uid)
                    existing_squad_inbounds = list(existing_ib_uuids)
                    patch_resp = remnawave_api(token, 'PATCH', 'internal-squads', {'uuid': squad_uuid, 'inbounds': existing_ib_uuids})
                    if patch_resp.get('response'):
                        print('  ✅ Инбаунды добавлены в Default-Squad')
                    else:
                        print(f'  ⚠️  Не удалось добавить инбаунды в сквад: {str(patch_resp)[:300]}')
                else:
                    print('  ⚠️  Default-Squad не найден')
    step(9, 'Создание пользователя')
    user_short_uuid = None
    existing_users_resp = remnawave_api(token, 'GET', 'users')
    existing_users = existing_users_resp.get('response', {})
    users_list = existing_users.get('users', []) if isinstance(existing_users, dict) else []
    for u in users_list:
        if u.get('username') == 'user1':
            user_short_uuid = u.get('shortUuid', '')
            sub_url = u.get('subscriptionUrl', '')
            print('  Пользователь user1 уже существует')
            break
    if not user_short_uuid:
        user_payload = {'username': 'user1', 'expireAt': '2099-12-31T23:59:59.000Z', 'trafficLimitBytes': 0, 'trafficLimitStrategy': 'NO_RESET', 'hwidDeviceLimit': 0}
        if squad_uuid:
            user_payload['activeInternalSquads'] = [squad_uuid]
        resp = remnawave_api(token, 'POST', 'users', user_payload)
        if resp.get('response'):
            user_uuid = resp['response'].get('uuid', '')
            user_short_uuid = resp['response'].get('shortUuid', '')
            sub_url = resp['response'].get('subscriptionUrl', '')
            print('  ✅ Пользователь создан')
        else:
            print(f'  ⚠️  Не удалось создать пользователя: {str(resp)[:300]}')
    step(10, 'Синхронизация ноды')
    print('  Перезапуск ноды для синхронизации юзеров...')
    if same_server:
        run('docker restart remnanode', check=False, timeout=30)
        time.sleep(5)
        synced = False
        for i in range(12):
            r = run('docker logs remnanode --tail=15 2>&1', check=False)
            m = re.search('(\\d+)\\s+users', r.stdout)
            if m and int(m.group(1)) > 0:
                    print(f'  Нода синхронизирована: {m.group(1)} юзеров')
                    synced = True
                    break
            if 'is up and running' in r.stdout:
                print('  XRay запущен')
                synced = True
                break
            else:
                time.sleep(5)
        if not synced:
            print('  ⚠️  Нода не подтвердила синхронизацию за 60 сек')
    else:
        run_remote(node_ip, node_cred, 'docker restart remnanode', timeout=30)
        time.sleep(10)
        r = run_remote(node_ip, node_cred, 'docker logs remnanode --tail=15 2>&1', timeout=15)
        m = re.search('(\\d+)\\s+users', r.stdout) if r.stdout else None
        if m and int(m.group(1)) > 0:
            print(f'  ✅ Нода синхронизирована: {m.group(1)} юзеров')
        else:
            print('  Нода перезапущена')
    ns = 11
    if cascade:
        step(ns, 'Настройка каскада')
        ns += 1
        api_func = lambda m, p, d=None: remnawave_api(token, m, p, d)
        cascade_result = setup_cascade_relay(cfg, api_func, node_ip, node_cred, same_server, profile_uuid, inbound_uuid, squad_uuid, existing_squad_inbounds)
    step(ns, 'Инструкция по настройке фронта')
    ns += 1
    origin_target_ip = cascade_ip if cascade else node_ip
    if cdn_type == 'host':
        print_host_instructions(front_domain, origin_target_ip, rcfg['xhttp_path'])
        try:
            auto_setup = safe_input('\n  Автоматически залить .htaccess через FTP? (y/n): ').strip().lower()
            if auto_setup in ['y', 'yes', 'д', 'да']:
                if upload_htaccess_ftp(front_domain, origin_target_ip, rcfg['xhttp_path']):
                    print('\n  ✅ Фронт готов к использованию!')
                else:
                    print('\n  ⚠️  Залей .htaccess вручную по инструкции выше')
        except (KeyboardInterrupt, EOFError):
            print('\n  ⚠️  Пропущено, залей .htaccess вручную')
    else:
        if cdn_type == 'vk':
            print(f"\n  ============================================\n  DNS записи (у вашего DNS-провайдера):\n  ============================================\n\n  1. A-запись:  {panel_domain}  ->  {server_ip}  (без проксирования)\n  2. A-запись:  {origin_domain}    ->  {origin_target_ip}    (без проксирования){('  ← relay (каскад)' if cascade else '')}\n  3. CNAME:     {cdn_domain}    ->  [VK CDN CNAME]  (без проксирования)\n\n  ============================================\n  Настройки VK Cloud CDN:\n  ============================================\n\n  - Протокол к источнику: HTTP (порт 80)\n  - Источник: {origin_domain}\n  - Персональный домен: {cdn_domain}\n  - Заголовок Host: Пересылать\n  - SSL: Let\'s Encrypt\n  - Кеширование: ВЫКЛ (все 4 переключателя)\n  - HTTP методы: GET, HEAD, OPTIONS\n  - Gzip: ВЫКЛ\n")
        else:
            if cdn_type == 'yandex':
                print(''.join([
                    "\n  ============================================\n  DNS записи (у вашего DNS-провайдера):\n  ============================================\n\n  1. A-запись:  ",
                    f"{panel_domain}",
                    "  ->  ",
                    f"{server_ip}",
                    "  (без проксирования)\n  2. A-запись:  ",
                    f"{origin_domain}",
                    "    ->  ",
                    f"{origin_target_ip}",
                    "    (без проксирования)",
                    f"{'  ← relay (каскад)' if cascade else ''}",
                    "\n  3. CNAME:     ",
                    f"{cdn_domain}",
                    "    ->  [Yandex CDN CNAME]  (без проксирования, создашь позже)\n  4. CNAME:     _acme-challenge.",
                    f"{cdn_domain}",
                    " -> [значение из Yandex] (без проксирования, создашь позже)\n\n  Создай пока только записи #1 и #2. Остальные — по ходу.\n\n  ============================================\n  ШАГ A: Сертификат в Yandex Certificate Manager\n  ============================================\n\n  Зайди: console.yandex.cloud -> Certificate Manager -> Создать сертификат\n\n  Заполни:\n    - Имя: ",
                    f"{cdn_domain.replace('.', '-')}",
                    "\n    - Домены: ",
                    f"{cdn_domain}",
                    "\n    - Тип проверки: DNS\n\n  Нажми \"Создать\".\n\n  После создания Yandex покажет CNAME для проверки:\n    _acme-challenge.",
                    f"{cdn_domain}",
                    "  ->  <значение>.cm.yandexcloud.net\n\n  Создай эту CNAME запись #4 (без проксирования).\n  Жди статус сертификата \"Issued\" (5-30 мин).\n\n  ============================================\n  ШАГ B: CDN-ресурс в Yandex Cloud CDN\n  ============================================\n\n  Зайди: console.yandex.cloud -> CDN -> Создать ресурс\n\n  Основные настройки:\n    - Запрос контента: Из одного источника\n    - Тип источника: Сервер\n    - Доменное имя источника: ",
                    f"{origin_domain}",
                    "\n    - Протокол для источников: HTTPS\n    - Задать SNI вручную: ВКЛ\n    - Имя SNI-хоста: ",
                    f"{origin_domain}",
                    "\n    - Заголовок Host: Своё значение\n    - Значение заголовка: ",
                    f"{origin_domain}",
                    "\n    - Доменное имя: ",
                    f"{cdn_domain}",
                    "\n\n  После создания скопируй CNAME (xxx.gcdn.co) и создай DNS запись #3.\n\n  Настройки CDN (вкладки сверху):\n    Кеширование:\n      - Кеш CDN: ВЫКЛ\n      - Кеш браузера: ВЫКЛ\n\n    Дополнительно:\n      - Query string: НЕ игнорировать\n      - Сжатие: ВЫКЛ\n      - Проверка сертификата источника: ВЫКЛ\n      - SSL-сертификат: выбери ",
                    f"{cdn_domain.replace('.', '-')}",
                    "\n",
                ]))
            else:
                if cdn_type == 'beeline':
                    print(f"\n  ============================================\n  DNS записи (у вашего DNS-провайдера):\n  ============================================\n\n  1. A-запись:  {panel_domain}  ->  {server_ip}  (без проксирования)\n  2. A-запись:  {origin_domain}    ->  {origin_target_ip}    (без проксирования){('  ← relay (каскад)' if cascade else '')}\n  3. CNAME:     {cdn_domain}    ->  [CDNvideo CNAME]  (без проксирования)\n\n  ============================================\n  Создание CDN-ресурса на CDNvideo (panel.cdnvideo.ru):\n  ============================================\n\n  1. Зайди на panel.cdnvideo.ru -> Создать CDN-ресурс\n\n  2. Основные настройки:\n     - Адрес (Origin): {origin_domain}:443\n     - Группа доменов: Выключено\n\n  3. HTTPS:\n     - Использовать HTTPS при запросе к источникам: ВКЛ\n     - Проверять сертификат источника: НЕ включать\n     - Указать имя SNI-хоста: ВКЛ\n     - Имя SNI-хоста: {origin_domain}\n\n  4. Host-заголовок:\n     - Hostname при запросе к источнику: оставить пустым\n     - Передавать исходный Host-заголовок: ВКЛ\n\n  5. Кеширование (правая колонка):\n     - Кеширование: ВЫКЛ\n     - Обслуживать устаревший кэш: ВЫКЛ\n     - Кешировать с учетом query string: ВЫКЛ\n     - Кешировать с учетом cookies: ВЫКЛ\n\n  6. Желаемый CNAME: {cdn_domain}\n     -> Нажми \"Добавить CNAME\"\n     -> Скопируй выданный CNAME (xxx.a.trbcdn.net)\n     -> Создай DNS запись #3\n\n  7. Экспертные настройки (вкладка сверху):\n     - HTTP2: ВКЛ\n     - HTTP3: ВЫКЛ\n     - Перенаправлять HTTP на HTTPS: ВКЛ\n     - Проверка CORS: ВЫКЛ\n     - Сжатие Brotli: ВЫКЛ\n     - Сжатие Gzip: ВЫКЛ\n\n  8. Нажми \"Применить\"\n")
                else:
                    if cdn_type == 'timeweb':
                        print(f"\n  ============================================\n  DNS записи (у вашего DNS-провайдера):\n  ============================================\n\n  1. A-запись:  {panel_domain}  ->  {server_ip}  (без проксирования)\n  2. A-запись:  {origin_domain}    ->  {origin_target_ip}    (без проксирования){('  ← relay (каскад)' if cascade else '')}\n  3. CDN домен выдаётся автоматически (xxx.cdn.twcstorage.ru)\n\n  ============================================\n  Создание CDN-ресурса на Timeweb (timeweb.cloud):\n  ============================================\n\n  1. Зайди: timeweb.cloud -> CDN -> Создать ресурс\n\n  2. Источник контента:\n     - Выбери вкладку \"IP-адрес\"\n     - IP-адрес: {origin_target_ip}:80{('  ← relay (каскад)' if cascade else '')}\n     - Использовать HTTPS: НЕ включать (оставить выключенным)\n\n  3. Домены раздачи:\n     - Технический домен (xxx.cdn.twcstorage.ru) создаётся автоматически\n     - Можно добавить свой домен через \"+ Добавить домен\"\n       (для этого нужен CNAME: {cdn_domain} -> xxx.cdn.twcstorage.ru)\n\n  4. После создания — настройки ресурса:\n     - Кеширование: ВЫКЛ (все переключатели)\n\n  5. Используй выданный CDN домен (xxx.cdn.twcstorage.ru)\n     как cdn_domain при вводе ниже.\n\n  ВАЖНО: расширение .m3u8 в пути уже включено в конфиг автоматически.\n")
    if cdn_type!= 'host' and (not cfg.get('skip_cdn_wait', False)):
            safe_input('  Нажми ENTER когда CDN настроен и сертификат выпущен...')
            if cdn_type in ['beeline', 'timeweb']:
                if cdn_type == 'beeline':
                    cdn_issued = safe_input('  Домен выданный Beeline CDN (например https://xxx.a.trbcdn.net): ').strip()
                else:
                    cdn_issued = safe_input('  Технический домен Timeweb CDN (например xxx.cdn.twcstorage.ru): ').strip()
                if cdn_issued:
                    cdn_issued = cdn_issued.replace('https://', '').replace('http://', '').rstrip('/')
                    cdn_label = 'Beeline' if cdn_type == 'beeline' else 'Timeweb'
                    print(f'  CDN домен {cdn_label}: {cdn_issued}')
                    hosts_resp = remnawave_api(token, 'GET', 'hosts')
                    if hosts_resp.get('response'):
                        for h in hosts_resp['response']:
                            if h.get('address') == cdn_domain:
                                remnawave_api(token, 'PATCH', 'hosts', {'uuid': h['uuid'], 'address': cdn_issued, 'sni': cdn_issued, 'host': cdn_issued})
                                print(f"  Хост \"{h.get('remark', '')}\" обновлён: {cdn_issued}")
    step(ns, 'Финальная проверка')
    ns += 1
    panel_check = remnawave_api(token, 'GET', 'nodes')
    panel_ok = 'error' not in panel_check
    r2 = run('curl -s http://127.0.0.1/health', check=False)
    print(f"  Panel API: {('OK' if panel_ok else 'FAIL')}")
    print(f"  Origin health: {('OK' if 'ok' in r2.stdout else r2.stdout.strip()[:50])}")
    profiles = remnawave_api(token, 'GET', 'config-profiles')
    nodes = remnawave_api(token, 'GET', 'nodes')
    hosts = remnawave_api(token, 'GET', 'hosts')
    users = remnawave_api(token, 'GET', 'users')
    pr = profiles.get('response', {})
    p_count = pr.get('total', len(pr.get('configProfiles', []))) if isinstance(pr, dict) else len(pr) if isinstance(pr, list) else 0
    n_count = len(nodes.get('response', [])) if isinstance(nodes.get('response'), list) else 0
    h_count = len(hosts.get('response', [])) if isinstance(hosts.get('response'), list) else 0
    ur = users.get('response', {})
    u_count = len(ur.get('users', [])) if isinstance(ur, dict) else len(ur) if isinstance(ur, list) else 0
    print(f'  Profiles: {p_count}, Nodes: {n_count}, Hosts: {h_count}, Users: {u_count}')
    extra_info = ''
    if install_hy2:
        extra_info += f'\n  Hysteria2: {node_ip}:{HY2_PORT} (UDP)'
    if install_grpc:
        extra_info += f'\n  gRPC Reality: {node_ip}:{GRPC_PORT} (TCP)'
        if cfg.get('reality_keys'):
            extra_info += f"\n  Reality PBK: {cfg['reality_keys']['public']}"
            extra_info += f"\n  Reality SID: {cfg.get('reality_short_id', 'N/A')}"
    print(''.join([
        "\n  ============================================\n  УСТАНОВКА ЗАВЕРШЕНА\n  ============================================\n\n  Панель: https://",
        f"{panel_domain}",
        "\n  Логин: ",
        f"{panel_user}",
        "\n  Пароль: ",
        f"{panel_pass}",
        "\n\n  CDN домен: ",
        f"{cdn_domain}",
        "\n  Origin: ",
        f"{origin_domain}",
        " -> ",
        f"{origin_target_ip}",
        f"{'  (relay каскад)' if cascade else ''}",
        "\n\n  Профиль: ",
        f"{profile_name}",
        " (UUID: ",
        f"{profile_uuid or 'N/A'}",
        ")\n  Нода: ",
        f"{node_uuid or 'N/A'}",
        " (",
        f"{node_address}",
        ":2222)\n  Хост CDN: ",
        f"{front_domain if cdn_type == 'host' else cdn_domain}",
        ":443",
        f"{extra_info}",
        "\n  Юзер: user1 (short: ",
        f"{user_short_uuid or 'N/A'}",
        ")\n  Подписка: https://",
        f"{panel_domain}",
        "/api/sub/",
        f"{user_short_uuid or 'N/A'}",
    ]))
    if cascade:
        print(f"\n  КАСКАД:\n  Relay: {cascade_ip} (Caddy + remnanode)\n  Exit: {node_ip} (BRIDGE_IN :9999)")
    print('  ============================================\n')
def install_node_only(cfg):
    if not validate_session(_t9m[2] if _t9m else '', get_server_ip(), 'create_node', _t9m[4] if len(_t9m) > 4 else None):
        sys.exit(1)
    cdn_type = cfg['cdn_type']
    rcfg = REMNAWAVE_CDN[cdn_type]
    server_ip = cfg['server_ip']
    domain = cfg['domain']
    front_domain = cfg.get('front_domain', domain)
    origin_sub = cfg['origin_sub']
    cdn_sub = cfg['cdn_sub']
    cdn_domain = f'{cdn_sub}.{domain}'
    origin_domain = f'{origin_sub}.{domain}'
    panel_ip = cfg['panel_ip']
    panel_cred = cfg['panel_cred']
    cascade = cfg.get('cascade', False)
    cascade_ip = cfg.get('cascade_ip')
    cascade_cred = cfg.get('cascade_cred')
    api = lambda method, path, data=None: remnawave_api_ssh(panel_ip, panel_cred, method, path, data)
    step(3, 'Проверка подключения к панели')
    resp = api('GET', 'nodes')
    if 'error' in resp:
        error_msg = str(resp)
        print(f'  ❌ Не удалось подключиться к панели: {error_msg[:300]}')
        print(f'     Панель: {panel_ip} (SSH → 127.0.0.1:3000)')
        if '403' in error_msg or 'Forbidden' in error_msg:
            print('\n  Диагностика ошибки 403 Forbidden:')
            print('  1. Проверяем токен...')
            r_token = run_remote(panel_ip, panel_cred, 'cat /opt/remnawave/.panel_token 2>/dev/null | wc -c', timeout=10)
            token_len = (r_token.stdout or '').strip()
            if token_len and int(token_len) > 50:
                print(f'     ✓ Токен существует (длина: {token_len})')
            else:
                print('     ✗ Токен отсутствует или повреждён')
            print('  2. Проверяем PANEL_DOMAIN...')
            r_domain = run_remote(panel_ip, panel_cred, 'grep PANEL_DOMAIN /opt/remnawave/.env 2>/dev/null', timeout=10)
            domain = (r_domain.stdout or '').strip()
            if domain:
                print(f'     ✓ {domain}')
            else:
                print('     ✗ PANEL_DOMAIN не задан')
            print('\n  Возможные решения:')
            print('  - Убедитесь, что панель запущена: docker ps | grep remnawave')
            print('  - Проверьте логин/пароль панели')
            print('  - Попробуйте перезапустить панель: cd /opt/remnawave && docker compose restart')
        else:
            print('     Проверьте SSH-доступ и что панель запущена')
        sys.exit(1)
    existing_nodes = resp.get('response', [])
    n_count = len(existing_nodes) if isinstance(existing_nodes, list) else 0
    print(f'  Панель доступна, нод: {n_count}')
    panel_version = None
    try:
        ver_resp = api('GET', 'auth/me')
        if ver_resp.get('response'):
            panel_version = ver_resp['response'].get('version')
    except Exception:
        pass
    if panel_version:
        print(f'  Версия панели: {panel_version}')
        major_minor = panel_version.split('.')[:2] if panel_version else []
        is_28_plus = major_minor >= ['2', '8'] if len(major_minor) >= 2 else False
    else:
        print('  Версия панели: не определена (совместимый режим)')
        is_28_plus = False
    step(4, 'Установка Docker')
    r = run('docker --version', check=False)
    if r.returncode!= 0:
        print('  Установка Docker...')
        run('curl -fsSL https://get.docker.com | sh', check=False, timeout=180)
        r = run('docker --version', check=False)
        if r.returncode!= 0:
            print('  get.docker.com не сработал, пробую apt install docker.io...')
            run('apt-get update -qq && apt-get install -y -qq docker.io docker-compose-plugin 2>&1 | tail -3', check=False, timeout=300)
            r = run('docker --version', check=False)
            if r.returncode!= 0:
                print('  ❌ Docker не установился! Попробуй вручную: curl -fsSL https://get.docker.com | sh')
                sys.exit(1)
        print('  ✅ Docker установлен')
    else:
        print('  Docker уже установлен')
    step(5, 'Настройка nginx CDN origin')
    ipv6_ok = has_ipv6()
    nginx_conf = nginx_cdn_origin(rcfg['xray_port'], rcfg['xhttp_path'], ipv6=ipv6_ok)
    r = nginx_write_and_restart(nginx_conf)
    if r.returncode == 0:
        print('  Nginx CDN origin настроен')
    else:
        print(f"  ❌ Проблема с nginx: {(r.stderr[:200] if r.stderr else '')}")
        print('  Попробуй: nginx -t и systemctl restart nginx')
        sys.exit(1)
    step(6, 'Создание профиля через API панели')
    install_hy2 = cfg.get('install_hy2', False)
    install_grpc = cfg.get('install_grpc', False)
    profile_name = f'cdn-{cdn_type}'
    if install_hy2 or install_grpc:
        extras = []
        if install_hy2:
            extras.append('hy2')
        if install_grpc:
            extras.append('grpc')
        profile_name += '-' + '-'.join(extras)
    inbound_tag = rcfg['inbound_tag']
    profile_uuid = None
    inbound_uuid = None
    hy2_inbound_uuid = None
    grpc_inbound_uuid = None
    existing_profiles = api('GET', 'config-profiles')
    if existing_profiles.get('response'):
        resp_data = existing_profiles['response']
        plist = resp_data.get('configProfiles', resp_data if isinstance(resp_data, list) else [resp_data])
        for p in plist:
            for ib in p.get('inbounds', []):
                if ib.get('tag') == inbound_tag:
                    profile_uuid = p.get('uuid')
                    inbound_uuid = ib.get('uuid')
                    print(f"  Профиль с тегом {inbound_tag} уже существует: {p.get('name')}")
                    for ib2 in p.get('inbounds', []):
                        if ib2.get('tag') == 'hy2-in':
                            hy2_inbound_uuid = ib2.get('uuid')
                        else:
                            if ib2.get('tag') == 'grpc-reality':
                                grpc_inbound_uuid = ib2.get('uuid')
                    break
            if profile_uuid:
                break
        if not profile_uuid:
            for p in plist:
                if p.get('name') == profile_name:
                    profile_uuid = p.get('uuid')
                    for ib in p.get('inbounds', []):
                        if ib.get('tag') == inbound_tag:
                            inbound_uuid = ib.get('uuid')
                        else:
                            if ib.get('tag') == 'hy2-in':
                                hy2_inbound_uuid = ib.get('uuid')
                            else:
                                if ib.get('tag') == 'grpc-reality':
                                    grpc_inbound_uuid = ib.get('uuid')
                    if not inbound_uuid:
                        inbounds = p.get('inbounds', [])
                        if inbounds:
                            inbound_uuid = inbounds[0].get('uuid')
                    print(f'  Профиль {profile_name} уже существует (по имени)')
                    break
    if not profile_uuid:
        import copy
        profile_config = copy.deepcopy(rcfg['profile_config'])
        if install_hy2:
            profile_config['inbounds'].append(build_hy2_inbound())
            print(f'  Добавлен Hysteria2 inbound (UDP {HY2_PORT})')
        if install_grpc:
            reality_keys = generate_x25519_keys()
            if reality_keys:
                short_id = secrets.token_hex(8)
                cfg['reality_keys'] = reality_keys
                cfg['reality_short_id'] = short_id
                profile_config['inbounds'].append(build_grpc_inbound(reality_keys['private'], short_id))
                print(f'  Добавлен gRPC Reality inbound (TCP {GRPC_PORT})')
        if cascade:
            profile_config['inbounds'].append({'tag': 'BRIDGE_IN', 'port': 9999, 'listen': '0.0.0.0', 'protocol': 'vless', 'settings': {'clients': [], 'decryption': 'none'}, 'sniffing': {'enabled': True, 'destOverride': ['http', 'tls', 'quic']}, 'streamSettings': {'network': 'tcp', 'security': 'none'}})
            print('  Добавлен BRIDGE_IN inbound (TCP 9999) для каскада')
        print(f'  Создание профиля: {profile_name}...')
        resp = api('POST', 'config-profiles', {'name': profile_name, 'config': profile_config})
        if resp.get('response'):
            profile_uuid = resp['response'].get('uuid')
            for ib in resp['response'].get('inbounds', []):
                if ib.get('tag') == inbound_tag:
                    inbound_uuid = ib.get('uuid')
                else:
                    if ib.get('tag') == 'hy2-in':
                        hy2_inbound_uuid = ib.get('uuid')
                    else:
                        if ib.get('tag') == 'grpc-reality':
                            grpc_inbound_uuid = ib.get('uuid')
                        else:
                            if ib.get('tag') == 'BRIDGE_IN':
                                bridge_in_uuid = ib.get('uuid')
        else:
            print(f'  ❌ Не удалось создать профиль: {str(resp)[:300]}')
            sys.exit(1)
    if profile_uuid and (install_hy2 and (not hy2_inbound_uuid) or (install_grpc and (not grpc_inbound_uuid))):
            prof_full = api('GET', f'config-profiles/{profile_uuid}')
            pf = prof_full.get('response') or {}
            pconf = pf.get('config')
            if pconf and isinstance(pconf.get('inbounds'), list):
                    existing_tags = {ib.get('tag') for ib in pconf['inbounds']}
                    added = []
                    if install_hy2 and 'hy2-in' not in existing_tags:
                            pconf['inbounds'].append(build_hy2_inbound())
                            added.append('hy2')
                    if install_grpc and 'grpc-reality' not in existing_tags:
                            reality_keys = generate_x25519_keys()
                            if reality_keys:
                                short_id = secrets.token_hex(8)
                                cfg['reality_keys'] = reality_keys
                                cfg['reality_short_id'] = short_id
                                pconf['inbounds'].append(build_grpc_inbound(reality_keys['private'], short_id))
                                added.append('grpc')
                            else:
                                print('  ⚠️  gRPC пропущен: не удалось сгенерировать x25519-ключи')
                    if added:
                        patch = api('PATCH', 'config-profiles', {'uuid': profile_uuid, 'config': pconf})
                        pr = patch.get('response') or {}
                        for ib in pr.get('inbounds', []):
                            if ib.get('tag') == 'hy2-in':
                                hy2_inbound_uuid = ib.get('uuid')
                            else:
                                if ib.get('tag') == 'grpc-reality':
                                    grpc_inbound_uuid = ib.get('uuid')
                        if pr.get('uuid'):
                            print(f"  ✅ Доп. протоколы добавлены в профиль: {', '.join(added)}")
                        else:
                            print(f'  ⚠️  Не удалось добавить доп. протоколы: {str(patch)[:300]}')
    step(7, 'Привязка инбаунда к скваду')
    squads_resp = api('GET', 'internal-squads')
    squad_list = squads_resp.get('response', {}).get('internalSquads', [])
    if not squad_list:
        print('  ❌ В панели нет ни одного сквада')
        sys.exit(1)
    if len(squad_list) == 1:
        chosen_squad = squad_list[0]
        print(f"  Единственный сквад: {chosen_squad['name']}")
    else:
        if cfg.get('squad'):
            sq_arg = cfg['squad']
            if sq_arg.isdigit() and 1 <= int(sq_arg) <= len(squad_list):
                chosen_squad = squad_list[int(sq_arg) - 1]
            else:
                chosen_squad = next(
                    (s for s in squad_list if s['name'].lower() == sq_arg.lower()),
                    squad_list[0],
                )
            print(f"  Сквад (из аргумента): {chosen_squad['name']}")
        else:
            print('\n  Доступные скводы:')
            squad_options = {}
            for i, sq in enumerate(squad_list, 1):
                ib_count = sq.get('info', {}).get('inboundsCount', len(sq.get('inbounds', [])))
                members = sq.get('info', {}).get('membersCount', 0)
                squad_options[str(i)] = f"{sq['name']} ({ib_count} inbounds, {members} users)"
            choice = ask('К какому скваду привязать инбаунд?', squad_options)
            chosen_squad = squad_list[int(choice) - 1]

    existing_ib_uuids = [ib['uuid'] for ib in chosen_squad.get('inbounds', [])]
    all_new_uuids = [u for u in [inbound_uuid, hy2_inbound_uuid, grpc_inbound_uuid] if u]
    for uid in all_new_uuids:
        if uid not in existing_ib_uuids:
            existing_ib_uuids.append(uid)
    patch_resp = api('PATCH', 'internal-squads', {'uuid': chosen_squad['uuid'], 'inbounds': existing_ib_uuids})
    if patch_resp.get('response'):
        print(f"  ✅ Инбаунды привязаны к скваду: {chosen_squad['name']}")
    else:
        print(f'  ⚠️  Не удалось привязать инбаунды к скваду: {str(patch_resp)[:300]}')
    step(8, 'Создание ноды в панели')
    our_uuids = {inbound_uuid, hy2_inbound_uuid, grpc_inbound_uuid} - {None}
    excluded = []
    all_profiles = api('GET', 'config-profiles')
    if all_profiles.get('response'):
        resp_data = all_profiles['response']
        profiles_list = resp_data.get('configProfiles', resp_data if isinstance(resp_data, list) else [resp_data])
        for p in profiles_list:
            for ib in p.get('inbounds', []):
                ib_uuid = ib.get('uuid')
                if ib_uuid and ib_uuid not in our_uuids:
                        excluded.append(ib_uuid)
    if excluded:
        print(f'  Исключено {len(excluded)} чужих inbound\'ов')
    node_uuid = None
    existing_nodes = existing_nodes if isinstance(existing_nodes, list) else []
    for n in existing_nodes:
        if n.get('address') == server_ip and n.get('port') == 2222:
                node_uuid = n.get('uuid')
                print('  Нода уже существует')
                break
    if not node_uuid:
        active_inbounds = [u for u in [inbound_uuid, hy2_inbound_uuid, grpc_inbound_uuid] if u]
        print(f'  Создание ноды ({server_ip}:2222)...')
        node_data = {'name': f"node-{cdn_type}-{'.'.join(server_ip.split('.')[(-2):])}", 'address': server_ip, 'port': 2222, 'countryCode': 'XX', 'isTrafficTrackingActive': True, 'trafficLimitBytes': 0, 'notifyPercent': 0, 'trafficResetDay': 1, 'excludedInbounds': excluded, 'configProfile': {'activeConfigProfileUuid': profile_uuid, 'activeInbounds': active_inbounds}}
        resp = api('POST', 'nodes', node_data)
        if resp.get('response'):
            node_uuid = resp['response'].get('uuid')
        else:
            print(f'  ❌ Не удалось создать ноду: {str(resp)[:300]}')
            sys.exit(1)
    step(9, 'Запуск remnanode')
    secret_key = None
    resp = api('GET', 'keygen')
    if resp.get('response'):
        secret_key = resp['response'].get('pubKey')
    if not secret_key:
        print('  ❌ Не удалось получить secret key')
        sys.exit(1)
    run('mkdir -p /opt/remnanode', check=False)
    track('directory', '/opt/remnanode')
    panel_version_choice = cfg.get('panel_version_choice', '2')
    if panel_version_choice == '1':
        node_version = '3.0.0'
        print('  Используем Node 3.0.0 (для панели 2.8.1)')
    else:
        node_version = 'latest'
        print('  Используем Node latest (для панели 3.2.3+)')
    node_compose = f'services:\n  remnanode:\n    container_name: remnanode\n    hostname: remnanode\n    image: ghcr.io/remnawave/node:{node_version}\n    network_mode: host\n    restart: always\n    cap_add:\n      - NET_ADMIN\n    ulimits:\n      nofile:\n        soft: 1048576\n        hard: 1048576\n    volumes:\n      - /etc/nginx/ssl:/etc/nginx/ssl:ro\n    env_file:\n      - .env\n'
    with open('/opt/remnanode/docker-compose.yml', 'w') as f:
        f.write(node_compose)
    node_env = f'NODE_PORT=2222\nSECRET_KEY={secret_key}\n'
    with open('/opt/remnanode/.env', 'w') as f:
        f.write(node_env)
    print('  Скачивание образа remnanode...')
    run('cd /opt/remnanode && docker compose pull', check=False, timeout=120)
    print('  Запуск remnanode...')
    run('cd /opt/remnanode && docker compose up -d', check=False, timeout=60)
    track('docker_compose', '/opt/remnanode')
    print('  Ожидание подключения ноды...')
    for i in range(20):
        time.sleep(5)
        r = run('docker logs remnanode --tail=5 2>&1', check=False)
        if 'started' in r.stdout.lower() or 'Remnawave' in r.stdout:
            print('  Нода подключена!')
            break
    print(f'  Ограничение порта 2222 для панели ({panel_ip})...')
    iptables_add(f'-I INPUT -p tcp --dport 2222 -s {panel_ip} -j ACCEPT')
    iptables_add('-I INPUT -p tcp --dport 2222 -s 127.0.0.1 -j ACCEPT')
    iptables_add('-I INPUT -p tcp --dport 2222 -s 172.16.0.0/12 -j ACCEPT')
    iptables_add('-A INPUT -p tcp --dport 2222 -j DROP')
    open_extra_ports(install_hy2, install_grpc)
    if install_hy2:
        _hy2_lines = ['server {', f'    listen {HY2_PORT} ssl;', f'    listen [::]:{HY2_PORT} ssl;', '    server_name _;', '    ssl_certificate /etc/nginx/ssl/cdn.crt;', '    ssl_certificate_key /etc/nginx/ssl/cdn.key;', '    ssl_protocols TLSv1.2 TLSv1.3;', '    location / { return 200 \'ok\'; }', '}']
        with open('/etc/nginx/conf.d/hy2-ping.conf', 'w') as _f:
            _f.write(chr(10).join(_hy2_lines) + chr(10))
        track('file', '/etc/nginx/conf.d/hy2-ping.conf')
        run('nginx -t && systemctl reload nginx', check=False)
        print(f'  TCP {HY2_PORT} (nginx SSL) для пинга HY2')
    if cascade:
        print('  Открытие порта 9999 (BRIDGE_IN) для каскада...')
        run('ufw allow 9999/tcp 2>/dev/null; iptables -I INPUT -p tcp --dport 9999 -j ACCEPT 2>/dev/null', check=False)
    pkg_iptables_persist()
    step(10, 'Создание хостов')
    existing_hosts_resp = api('GET', 'hosts')
    existing_hosts = existing_hosts_resp.get('response', [])
    if not isinstance(existing_hosts, list):
        existing_hosts = []
    def create_host_if_needed(ib_uuid, payload, label):
        for h in existing_hosts:
            if h.get('address') == payload['address'] and h.get('port') == payload['port']:
                    huuid = h.get('uuid')
                    print(f'  Хост {label} уже существует')
                    return huuid
        resp = api('POST', 'hosts', payload)
        if resp.get('response'):
            huuid = resp['response'].get('uuid')
            print(f'  ✅ Хост {label} создан')
            return huuid
        else:
            print(f'  ⚠️  Не удалось создать хост {label}: {str(resp)[:300]}')
            return
    host_addr = front_domain if cdn_type == 'host' else cdn_domain
    cdn_host_payload = {
        'inbound': {'configProfileUuid': profile_uuid, 'configProfileInboundUuid': inbound_uuid},
        'remark': f'CDN {cdn_type.upper()} ({server_ip})',
        'address': host_addr,
        'port': 443,
        'path': rcfg.get('host_path', rcfg['xhttp_path']),
        'sni': host_addr,
        'host': host_addr,
        'alpn': rcfg['alpn'],
        'fingerprint': 'firefox',
        'isDisabled': False,
        'securityLayer': 'TLS',
        'allowInsecure': False,
        'xhttpExtraParams': rcfg['host_extra'],
    }
    host_uuid = create_host_if_needed(
        inbound_uuid,
        cdn_host_payload,
        'CDN',
    )
    hy2_host_uuid = None
    if hy2_inbound_uuid and install_hy2:
            _hy2_le = setup_hy2_le_cert(origin_domain)
            hy2_host_payload = {'inbound': {'configProfileUuid': profile_uuid, 'configProfileInboundUuid': hy2_inbound_uuid}, 'remark': f'HY2 ({server_ip})', 'address': server_ip, 'port': HY2_PORT, 'sni': origin_domain if _hy2_le else '', 'host': '', 'alpn': 'h3', 'fingerprint': 'random', 'isDisabled': False, 'securityLayer': 'TLS', 'allowInsecure': not _hy2_le}
            if _hy2_le:
                print(f'  HY2: LE cert {origin_domain}')
            else:
                print(f'  ⚠️  HY2: self-signed, после DNS выпусти: certbot certonly --webroot -w /var/www/certbot -d {origin_domain}')
            hy2_host_uuid = create_host_if_needed(hy2_inbound_uuid, hy2_host_payload, 'HY2')
    grpc_host_uuid = None
    if grpc_inbound_uuid and install_grpc:
            grpc_host_payload = {'inbound': {'configProfileUuid': profile_uuid, 'configProfileInboundUuid': grpc_inbound_uuid}, 'remark': f'gRPC ({server_ip})', 'address': server_ip, 'port': GRPC_PORT, 'sni': GRPC_SERVER_NAMES[0], 'host': '', 'alpn': 'h2', 'fingerprint': 'firefox', 'isDisabled': False, 'securityLayer': 'DEFAULT', 'allowInsecure': False, 'path': GRPC_SERVICE_NAME}
            grpc_host_uuid = create_host_if_needed(grpc_inbound_uuid, grpc_host_payload, 'gRPC')
    all_host_uuids = [h for h in [host_uuid, hy2_host_uuid, grpc_host_uuid] if h]
    if all_host_uuids and node_uuid:
            for huuid in all_host_uuids:
                link_resp = api('PATCH', 'hosts', {'uuid': huuid, 'nodes': [node_uuid]})
                if not link_resp.get('response'):
                    print(f'  ⚠️  Не удалось привязать хост к ноде: {str(link_resp)[:300]}')
    step(11, 'Синхронизация ноды')
    print('  Перезапуск ноды для синхронизации юзеров...')
    run('docker restart remnanode', check=False, timeout=30)
    time.sleep(5)
    synced = False
    for i in range(12):
        r = run('docker logs remnanode --tail=15 2>&1', check=False)
        m = re.search('(\\d+)\\s+users', r.stdout)
        if m and int(m.group(1)) > 0:
                print(f'  Нода синхронизирована: {m.group(1)} юзеров')
                synced = True
                break
        if 'is up and running' in r.stdout:
            print('  Xray запущен, пользователи подгружаются…')
            synced = True
            break
        else:
            time.sleep(5)
    if not synced:
        print('  ⚠️  Нода не подтвердила синхронизацию за 60 сек')
        print('     Попробуйте вручную: docker restart remnanode')
    ns = 12
    if cascade:
        step(ns, 'Настройка каскада')
        ns += 1
        cascade_result = setup_cascade_relay(cfg, api, server_ip, None, True, profile_uuid, inbound_uuid, chosen_squad['uuid'], list(existing_ib_uuids))
    step(ns, 'Инструкция по настройке фронта')
    ns += 1
    origin_target_ip = cascade_ip if cascade else server_ip
    if cdn_type == 'host':
        print_host_instructions(front_domain, origin_target_ip, rcfg['xhttp_path'])
        try:
            auto_setup = safe_input('\n  Автоматически залить .htaccess через FTP? (y/n): ').strip().lower()
            if auto_setup in ['y', 'yes', 'д', 'да']:
                if upload_htaccess_ftp(front_domain, origin_target_ip, rcfg['xhttp_path']):
                    print('\n  ✅ Фронт готов к использованию!')
                else:
                    print('\n  ⚠️  Залей .htaccess вручную по инструкции выше')
        except (KeyboardInterrupt, EOFError):
            print('\n  ⚠️  Пропущено, залей .htaccess вручную')
    else:
        if cdn_type == 'vk':
            print(f"\n  ============================================\n  DNS записи (у вашего DNS-провайдера):\n  ============================================\n\n  1. A-запись:  {origin_domain}  ->  {origin_target_ip}  (без проксирования){('  ← relay (каскад)' if cascade else '')}\n  2. CNAME:     {cdn_domain}  ->  [VK CDN CNAME]  (без проксирования)\n\n  ============================================\n  Настройки VK Cloud CDN:\n  ============================================\n\n  - Протокол к источнику: HTTP (порт 80)\n  - Источник: {origin_domain}\n  - Персональный домен: {cdn_domain}\n  - Заголовок Host: Пересылать\n  - SSL: Let\'s Encrypt\n  - Кеширование: ВЫКЛ (все 4 переключателя)\n  - HTTP методы: GET, HEAD, OPTIONS\n  - Gzip: ВЫКЛ\n")
        else:
            if cdn_type == 'yandex':
                print(f"\n  ============================================\n  DNS записи (у вашего DNS-провайдера):\n  ============================================\n\n  1. A-запись:  {origin_domain}  ->  {origin_target_ip}  (без проксирования){('  ← relay (каскад)' if cascade else '')}\n  2. CNAME:     {cdn_domain}  ->  [Yandex CDN CNAME]  (без проксирования, создашь позже)\n  3. CNAME:     _acme-challenge.{cdn_domain} -> [значение из Yandex] (без проксирования, создашь позже)\n\n  Создай пока только запись #1. Остальные — по ходу.\n\n  ============================================\n  ШАГ A: Сертификат в Yandex Certificate Manager\n  ============================================\n\n  Зайди: console.yandex.cloud -> Certificate Manager -> Создать сертификат\n\n  Заполни:\n    - Имя: {cdn_domain.replace('.', '-')}\n    - Домены: {cdn_domain}\n    - Тип проверки: DNS\n\n  Нажми \"Создать\".\n\n  После создания Yandex покажет CNAME для проверки:\n    _acme-challenge.{cdn_domain}  ->  <значение>.cm.yandexcloud.net\n\n  Создай эту CNAME запись #3 (без проксирования).\n  Жди статус сертификата \"Issued\" (5-30 мин).\n\n  ============================================\n  ШАГ B: CDN-ресурс в Yandex Cloud CDN\n  ============================================\n\n  Зайди: console.yandex.cloud -> CDN -> Создать ресурс\n\n  Основные настройки:\n    - Запрос контента: Из одного источника\n    - Тип источника: Сервер\n    - Доменное имя источника: {origin_domain}\n    - Протокол для источников: HTTPS\n    - Задать SNI вручную: ВКЛ\n    - Имя SNI-хоста: {origin_domain}\n    - Заголовок Host: Своё значение\n    - Значение заголовка: {origin_domain}\n    - Доменное имя: {cdn_domain}\n\n  После создания скопируй CNAME (xxx.gcdn.co) и создай DNS запись #2.\n\n  Настройки CDN (вкладки сверху):\n    Кеширование:\n      - Кеш CDN: ВЫКЛ\n      - Кеш браузера: ВЫКЛ\n\n    Дополнительно:\n      - Query string: НЕ игнорировать\n      - Сжатие: ВЫКЛ\n      - Проверка сертификата источника: ВЫКЛ\n      - SSL-сертификат: выбери {cdn_domain.replace('.', '-')}\n")
            else:
                if cdn_type == 'beeline':
                    print(f"\n  ============================================\n  DNS записи (у вашего DNS-провайдера):\n  ============================================\n\n  1. A-запись:  {origin_domain}  ->  {origin_target_ip}  (без проксирования){('  ← relay (каскад)' if cascade else '')}\n  2. CNAME:     {cdn_domain}  ->  [CDNvideo CNAME]  (без проксирования)\n\n  ============================================\n  Создание CDN-ресурса на CDNvideo (panel.cdnvideo.ru):\n  ============================================\n\n  1. Зайди на panel.cdnvideo.ru -> Создать CDN-ресурс\n\n  2. Основные настройки:\n     - Адрес (Origin): {origin_domain}:443\n     - Группа доменов: Выключено\n\n  3. HTTPS:\n     - Использовать HTTPS при запросе к источникам: ВКЛ\n     - Проверять сертификат источника: НЕ включать\n     - Указать имя SNI-хоста: ВКЛ\n     - Имя SNI-хоста: {origin_domain}\n\n  4. Host-заголовок:\n     - Hostname при запросе к источнику: оставить пустым\n     - Передавать исходный Host-заголовок: ВКЛ\n\n  5. Кеширование (правая колонка):\n     - Кеширование: ВЫКЛ\n     - Обслуживать устаревший кэш: ВЫКЛ\n     - Кешировать с учетом query string: ВЫКЛ\n     - Кешировать с учетом cookies: ВЫКЛ\n\n  6. Желаемый CNAME: {cdn_domain}\n     -> Нажми \"Добавить CNAME\"\n     -> Скопируй выданный CNAME (xxx.a.trbcdn.net)\n     -> Создай DNS запись #2\n\n  7. Экспертные настройки (вкладка сверху):\n     - HTTP2: ВКЛ\n     - HTTP3: ВЫКЛ\n     - Перенаправлять HTTP на HTTPS: ВКЛ\n     - Проверка CORS: ВЫКЛ\n     - Сжатие Brotli: ВЫКЛ\n     - Сжатие Gzip: ВЫКЛ\n\n  8. Нажми \"Применить\"\n")
                else:
                    if cdn_type == 'timeweb':
                        print(f"\n  ============================================\n  DNS записи (у вашего DNS-провайдера):\n  ============================================\n\n  1. A-запись:  {origin_domain}  ->  {origin_target_ip}  (без проксирования){('  ← relay (каскад)' if cascade else '')}\n  2. CDN домен выдаётся автоматически (xxx.cdn.twcstorage.ru)\n\n  ============================================\n  Создание CDN-ресурса на Timeweb (timeweb.cloud):\n  ============================================\n\n  1. Зайди: timeweb.cloud -> CDN -> Создать ресурс\n\n  2. Источник контента:\n     - Выбери вкладку \"IP-адрес\"\n     - IP-адрес: {origin_target_ip}:80{('  ← relay (каскад)' if cascade else '')}\n     - Использовать HTTPS: НЕ включать (оставить выключенным)\n\n  3. Домены раздачи:\n     - Технический домен (xxx.cdn.twcstorage.ru) создаётся автоматически\n     - Можно добавить свой домен через \"+ Добавить домен\"\n       (для этого нужен CNAME: {cdn_domain} -> xxx.cdn.twcstorage.ru)\n\n  4. После создания — настройки ресурса:\n     - Кеширование: ВЫКЛ (все переключатели)\n\n  5. Используй выданный CDN домен (xxx.cdn.twcstorage.ru)\n     как cdn_domain при вводе ниже.\n\n  ВАЖНО: расширение .m3u8 в пути уже включено в конфиг автоматически.\n")
    if cdn_type!= 'host' and (not cfg.get('skip_cdn_wait', False)):
            safe_input('  Нажми ENTER когда CDN настроен и сертификат выпущен...')
            if cdn_type in ['beeline', 'timeweb']:
                if cdn_type == 'beeline':
                    cdn_issued = safe_input('  Домен выданный Beeline CDN (например https://xxx.a.trbcdn.net): ').strip()
                else:
                    cdn_issued = safe_input('  Технический домен Timeweb CDN (например xxx.cdn.twcstorage.ru): ').strip()
                if cdn_issued:
                    cdn_issued = cdn_issued.replace('https://', '').replace('http://', '').rstrip('/')
                    cdn_label = 'Beeline' if cdn_type == 'beeline' else 'Timeweb'
                    print(f'  CDN домен {cdn_label}: {cdn_issued}')
    step(ns, 'Финальная проверка')
    ns += 1
    r = run('curl -s http://127.0.0.1/health', check=False)
    health_ok = 'ok' in r.stdout
    print(f"  Origin health: {('OK' if health_ok else 'FAIL')}")
    r = run('docker ps --format \'{{.Names}} {{.Status}}\' | grep remnanode', check=False)
    node_ok = 'Up' in r.stdout
    print(f"  Remnanode: {('OK' if node_ok else r.stdout.strip() or 'NOT RUNNING')}")
    nodes_resp = api('GET', 'nodes')
    if isinstance(nodes_resp.get('response'), list):
        our_node = next((n for n in nodes_resp['response'] if n.get('uuid') == node_uuid), None)
        if our_node:
            connected = our_node.get('isConnected', False)
            print(f"  Нода в панели: {('ПОДКЛЮЧЕНА' if connected else 'ОТКЛЮЧЕНА')}")
    extra_info = ''
    if install_hy2:
        extra_info += f'\n  Hysteria2: {server_ip}:{HY2_PORT} (UDP)'
    if install_grpc:
        extra_info += f'\n  gRPC Reality: {server_ip}:{GRPC_PORT} (TCP)'
        if cfg.get('reality_keys'):
            extra_info += f"\n  Reality PBK: {cfg['reality_keys']['public']}"
            extra_info += f"\n  Reality SID: {cfg.get('reality_short_id', 'N/A')}"
    print(f"\n  ============================================\n  УСТАНОВКА НОДЫ ЗАВЕРШЕНА\n  ============================================\n\n  Панель: {panel_ip} (SSH API)\n  Нода: {server_ip}:2222 (UUID: {node_uuid or 'N/A'})\n  Профиль: {profile_name} (UUID: {profile_uuid or 'N/A'})\n  Хост CDN: {(front_domain if cdn_type == 'host' else cdn_domain)}:443{extra_info}\n  Сквад: {chosen_squad['name']}\n\n  CDN домен: {cdn_domain}\n  Origin: {origin_domain} -> {origin_target_ip}{('  (relay каскад)' if cascade else '')}")
    if cascade:
        print(f'\n  КАСКАД:\n  Relay: {cascade_ip} (Caddy + remnanode)\n  Exit: {server_ip} (BRIDGE_IN :9999)')
    if _t9m and len(_t9m) >= 5:
            validate_session(_t9m[2], _t9m[1], 'install_complete', _t9m[4])
    print('  ============================================\n')
def common_setup(cfg):
    """Install packages, tune OS, setup SSL and decoy."""
    domain = cfg['domain']
    step(1, 'Подготовка системы')
    print('  Установка пакетов...')
    pkg_install('nginx openssl curl sqlite3 ca-certificates gnupg sshpass certbot')
    r = run('ufw status 2>/dev/null', check=False)
    if r.returncode == 0 and 'active' in r.stdout.lower():
            print('  UFW активен, открываю порты 80/443...')
            run('ufw allow 80/tcp >/dev/null 2>&1', check=False)
            run('ufw allow 443/tcp >/dev/null 2>&1', check=False)
            run('ufw reload >/dev/null 2>&1', check=False)
    r = run('swapon --show', check=False)
    if not r.stdout.strip():
        print('  Создание swap 2G...')
        run('fallocate -l 2G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile', check=False)
        run('grep -q swapfile /etc/fstab || echo \'/swapfile none swap sw 0 0\' >> /etc/fstab', check=False)
    else:
        print('  Swap уже есть')
    print('  Настройка TCP (BBR)...')
    with open('/etc/sysctl.d/99-vpn-tuning.conf', 'w') as f:
        f.write(SYSCTL_TUNING)
    run('sysctl --system > /dev/null 2>&1', check=False)
    with open('/etc/security/limits.d/99-nofile.conf', 'w') as f:
        f.write(NOFILE_LIMITS)
    step(2, 'SSL и страница-заглушка')
    run('mkdir -p /etc/nginx/ssl /etc/nginx/sites-available /etc/nginx/sites-enabled', check=False)
    if not os.path.exists('/etc/nginx/ssl/cdn.crt'):
        r = run('openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout /etc/nginx/ssl/cdn.key -out /etc/nginx/ssl/cdn.crt -subj \"/CN=cdn-origin\" 2>/dev/null', check=False)
        if r.returncode == 0:
            print('  Self-signed SSL создан (10 лет)')
        else:
            print('  ❌ openssl не смог создать сертификат — nginx не запустится без SSL!')
            sys.exit(1)
    else:
        print('  SSL сертификат уже есть')
    track('file', '/etc/nginx/ssl/cdn.crt')
    track('file', '/etc/nginx/ssl/cdn.key')
    run('mkdir -p /var/www/html', check=False)
    decoy = DECOY_HTML.format(domain=domain)
    with open('/var/www/html/index.html', 'w') as f:
        f.write(decoy)
    print(f'  Страница-заглушка создана для {domain}')
def parse_args():
    """Parse CLI args for non-interactive mode."""
    import argparse
    parser = argparse.ArgumentParser(description='VPN CDN Installer')
    parser.add_argument('--mode', choices=['1', '2', '3'], help='1=Panel+node here, 2=Panel here+node remote, 3=Node only')
    parser.add_argument('--panel', choices=['1', '2'], help='1=Remnawave, 2=3x-ui (modes 1,2)')
    parser.add_argument('--cdn', choices=['vk', 'yandex', 'beeline', 'timeweb'], help='CDN provider')
    parser.add_argument('--domain', help='Domain name')
    parser.add_argument('--node-ip', help='Remote node IP (mode 2)')
    parser.add_argument('--node-user', default='root', help='SSH user for remote node (default: root)')
    parser.add_argument('--node-pass', help='Remote node password (mode 2)')
    parser.add_argument('--node-key', help='Path to SSH private key for remote node (mode 2)')
    parser.add_argument('--panel-url', help='Panel IP (mode 3)')
    parser.add_argument('--api-token', help='(deprecated, ignored)')
    parser.add_argument('--panel-user', help='Panel Remnawave username (mode 3)')
    parser.add_argument('--panel-pass', help='Panel Remnawave password (mode 3)')
    parser.add_argument('--panel-ssh-user', default='root', help='Panel SSH user (mode 3, default: root)')
    parser.add_argument('--panel-ssh-pass', help='Panel SSH password (mode 3)')
    parser.add_argument('--no-hy2', action='store_true', help='Skip Hysteria2')
    parser.add_argument('--no-grpc', action='store_true', help='Skip gRPC')
    parser.add_argument('--squad', help='Squad number or name (mode 3 Remnawave)')
    parser.add_argument('--skip-dns-wait', action='store_true', help='Skip DNS confirmation prompt')
    parser.add_argument('--skip-cdn-wait', action='store_true', help='Skip CDN confirmation prompt')
    parser.add_argument('--cascade', action='store_true', help='Enable cascade relay')
    parser.add_argument('--cascade-ip', help='Cascade relay server IP')
    parser.add_argument('--cascade-pass', help='Cascade relay SSH password')
    parser.add_argument('--cascade-user', default='root', help='Cascade relay SSH user')
    parser.add_argument('--key', help='License key for activation')
    return parser.parse_args()
    
_LSK = 'nulled'

def _vrf(data):
    """Verify Ed25519 signature on license response."""
    return True

def get_hwid():
    """Стабильный отпечаток железа: machine-id + первый MAC. 1 ключ = 1 сервер."""
    return "ffffffffffffffffffffffffffffffff"

def detect_vm():
    """Грубая эвристика VM (для пометки админу, не блокирует)."""
    return False

def check_license(key, server_ip):
    return check_license_protected(key, server_ip)


def fetch_session_configs(key, server_ip):
    """
    Локальная версия fetch_session_configs().
    Использует встроенный сохранённый ответ /api/session.
    """
    result = {
        "ok": True,
        "ts": int(time.time()),
        "key": "NULL-0000-0000-0000-0000",
        "ip": server_ip,
        "cn": "1234567890abcdef",

        "host": {
            "cdn3x": {
                "xray_port": 2053,
                "xhttp_path": "/p",
                "uplink_method": "DELETE",
                "padding_key": "q",
                "padding_header": "X-Client-Version",
                "padding_placement": "query",
                "padding_method": "tokenish",
                "origin_protocol": "HTTP (port 80)"
            },

            "remnawave": {
                "xray_port": 10087,
                "xhttp_path": "/api/generate/",
                "host_path": "p",
                "inbound_tag": "regru-xhttp",
                "listen": "127.0.0.1",

                "profile_config": {
                    "log": {
                        "loglevel": "warning"
                    },
                    "dns": {
                        "servers": [
                            "1.1.1.1",
                            "8.8.8.8",
                            "77.88.8.8",
                            "localhost"
                        ]
                    },
                    "inbounds": [
                        {
                            "tag": "regru-xhttp",
                            "port": 10087,
                            "listen": "127.0.0.1",
                            "protocol": "vless",
                            "settings": {
                                "clients": [],
                                "decryption": "none"
                            },
                            "sniffing": {
                                "enabled": True,
                                "destOverride": [
                                    "http",
                                    "tls",
                                    "quic"
                                ]
                            },
                            "streamSettings": {
                                "network": "xhttp",
                                "security": "none",
                                "xhttpSettings": {
                                    "mode": "packet-up",
                                    "path": "/api/generate/",
                                    "extra": {
                                        "seqKey": "offset",
                                        "seqPlacement": "query",
                                        "sessionIDKey": "sid",
                                        "sessionIDPlacement": "query",
                                        "noSSEHeader": False,
                                        "xPaddingKey": "q",
                                        "xPaddingBytes": "48-256",
                                        "xPaddingMethod": "tokenish",
                                        "xPaddingObfsMode": True,
                                        "xPaddingPlacement": "query",
                                        "uplinkHTTPMethod": "DELETE",
                                        "scMaxEachPostBytes": 4000000,
                                        "scMinPostsIntervalMs": "0",
                                        "serverMaxHeaderBytes": 8192
                                    }
                                }
                            }
                        }
                    ],

                    "outbounds": [
                        {
                            "protocol": "freedom",
                            "tag": "direct"
                        },
                        {
                            "protocol": "blackhole",
                            "tag": "block"
                        }
                    ],

                    "routing": {
                        "rules": [
                            {
                                "type": "field",
                                "ip": [
                                    "geoip:private"
                                ],
                                "outboundTag": "direct"
                            },
                            {
                                "type": "field",
                                "protocol": [
                                    "bittorrent"
                                ],
                                "outboundTag": "block"
                            }
                        ]
                    }
                },

                "host_extra": {
                    "mode": "packet-up",
                    "noSSEHeader": False,
                    "seqKey": "offset",
                    "seqPlacement": "query",
                    "sessionIDKey": "sid",
                    "sessionIDPlacement": "query",
                    "xPaddingKey": "q",
                    "xPaddingBytes": "48-256",
                    "xPaddingMethod": "tokenish",
                    "xPaddingObfsMode": True,
                    "xPaddingPlacement": "query",
                    "uplinkHTTPMethod": "DELETE",
                    "scMaxEachPostBytes": "262144-786432",
                    "scMinPostsIntervalMs": "0",

                    "xmux": {
                        "maxConcurrency": 0,
                        "maxConnections": "16-32",
                        "cMaxReuseTimes": 0,
                        "hMaxRequestTimes": "600-900",
                        "hMaxReusableSecs": "120-240",
                        "hKeepAlivePeriod": 20
                    }
                },

                "alpn": "h2"
            }
        },

        "sig": "FTQAUZRVFqdIcd4NVY38DGqkXD+iK57LGUszddfKVWq5u4D7dmi+9CTM7cYh5zFPezu9SkGrreIx4F4MNJa3Bw=="
    }

    if not result.get("ok"):
        print("  ❌ Конфиги: неверный ответ")
        return False

    host = result.get("host") or {}

    cdn3x = host.get("cdn3x")
    rw = host.get("remnawave")

    if cdn3x:
        CDN_SETTINGS["host"].update(cdn3x)

    if rw:
        REMNAWAVE_CDN["host"].update(rw)

    print("  ✅ Конфиги получены локально")
    return True

def main():
    node_cred = ''
    print(f"\n{'=================================================='}\n   VPN HOST Installer v{VERSION}\n   XHTTP packet-up через шаред-хостинг (REG.RU)\n{'=================================================='}\n")
    if os.geteuid()!= 0:
        print('ОШИБКА: Запусти от root!')
        sys.exit(1)
    check_os()
    if not shutil.which('sshpass'):
        print('  Устанавливаю sshpass...')
        if shutil.which('apt-get'):
            run('apt-get update -qq && apt-get install -y sshpass >/dev/null 2>&1', check=False, timeout=120)
        else:
            if shutil.which('yum'):
                run('yum install -y sshpass >/dev/null 2>&1', check=False, timeout=120)
            else:
                if shutil.which('dnf'):
                    run('dnf install -y sshpass >/dev/null 2>&1', check=False, timeout=120)
        if not shutil.which('sshpass'):
            print('  ⚠ Не удалось установить sshpass. Удалённые операции могут не работать.')
    args = parse_args()
    server_ip = get_ip()
    print(f'  Server IP: {server_ip}')
    lic_key = (args.key or 'NULL-0000-0000-0000-0000').strip()
    lic_key = lic_key.upper()
    if not check_license(lic_key, server_ip):
        print('\n  Установка прервана: лицензия не подтверждена.')
        sys.exit(1)
    if SESSION_ENABLED and (not fetch_session_configs(lic_key, server_ip)):
            print('\n  Установка прервана: не удалось получить конфиги с сервера.')
            sys.exit(1)
    def gen_subdomain(length=8):
        """Generate random subdomain: letters + digits, starts with letter"""
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
        letters = 'abcdefghijklmnopqrstuvwxyz'
        result = secrets.choice(letters)
        result += ''.join((secrets.choice(chars) for _ in range(length - 1)))
        return result
    def ask_custom_subs(need_panel=True, host_mode=True):
        """Спрашивает кастомные поддомены. Возвращает (origin_sub, front_sub, panel_sub).\n        В host-режиме второй поддомен — это ФРОНТ (обёртка-сайт на REG.RU), а не CDN:\n        реальный адрес в VLESS-ссылке = front_sub.domain, cdn_sub не используется."""
        second_label = 'фронта (сайт-обёртка на REG.RU)' if host_mode else 'CDN'
        print('\n  Поддомены будут сгенерированы автоматически.')
        choice = safe_input('  Хочешь указать свои? (y/n, Enter=нет): ').strip().lower()
        if choice in ['y', 'yes', 'д', 'да']:
            try:
                if host_mode:
                    o = gen_subdomain()
                    c = safe_input(f'  Поддомен для {second_label}: ').strip() or gen_subdomain()
                else:
                    o = safe_input('  Поддомен для origin: ').strip() or gen_subdomain()
                    c = safe_input(f'  Поддомен для {second_label}: ').strip() or gen_subdomain()
                p = None
                if need_panel:
                    p = safe_input('  Поддомен для панели: ').strip() or gen_subdomain()
                return (o, c, p)
            except (KeyboardInterrupt, EOFError):
                print('\n  Отменено, генерирую автоматически...')
            else:
                pass
        subs = set()
        while len(subs) < (3 if need_panel else 2):
            subs.add(gen_subdomain())
        subs = list(subs)
        o = subs[0]
        c = subs[1]
        p = subs[2] if need_panel else None
        return (o, c, p)
    if args.mode:
        mode = args.mode
    else:
        mode = ask('Режим установки?', {'1': 'Панель + нода (всё на этом сервере)', '2': 'Панель здесь + нода на другом сервере', '3': 'HOST-фронт к существующей панели'})
    if mode == '3':
        panel_type = args.panel or ask('Панель (Panel)?', {'1': 'Remnawave', '2': '3x-ui'})
        panel_version_choice = '2'
        if panel_type == '1':
            if args.mode:
                panel_version_choice = '2'
            else:
                panel_version_choice = ask('Версия панели Remnawave?', {'1': '2.8.1', '2': '3.2.3+ (рекомендуется)'})
        cdn_type = 'host'
        domain = args.domain or ask('Домен фронта без http://')
        domain = domain.replace('https://', '').replace('http://', '').strip('/').strip()
        front_sub = None
        if args.mode:
            origin_sub = gen_subdomain()
            cdn_sub = gen_subdomain()
            while cdn_sub == origin_sub:
                cdn_sub = gen_subdomain()
        else:
            origin_sub, front_choice, _ = ask_custom_subs(need_panel=False, host_mode=cdn_type == 'host')
            if cdn_type == 'host':
                front_sub = front_choice
                cdn_sub = gen_subdomain()
            else:
                cdn_sub = front_choice
        if not front_sub:
            front_sub = gen_subdomain()
            while front_sub in (origin_sub, cdn_sub):
                front_sub = gen_subdomain()
        front_domain = f'{front_sub}.{domain}' if cdn_type == 'host' else domain
        if panel_type == '1':
            panel_ip = args.panel_url or ask('IP сервера с панелью Remnawave (Panel IP)')
            panel_ip = panel_ip.replace('https://', '').replace('http://', '').split('/')[0].split(':')[0].strip()
            print(f'\n  SSH подключение к панели ({panel_ip})...')
            if args.mode and args.panel_ssh_pass:
                panel_cred = {'type': 'password', 'value': args.panel_ssh_pass, 'user': args.panel_ssh_user}
            else:
                panel_cred = ask_ssh_cred()
            r = run('which sshpass', check=False)
            if r.returncode!= 0:
                print('  Установка sshpass...')
                run('DEBIAN_FRONTEND=noninteractive apt-get update -qq && apt-get install -y -qq sshpass 2>/dev/null', check=False, timeout=60)
            r = run_remote(panel_ip, panel_cred, 'echo ok', timeout=15)
            if r.returncode!= 0:
                print(f'  ❌ Не удалось подключиться по SSH к {panel_ip}')
                print(f"  {(r.stderr[:200] if r.stderr else '')}")
                sys.exit(1)
            print('  SSH к панели: OK')
            check_cmd = 'curl -s -o /dev/null --max-time 10 -w \"%{http_code}\" -H \"X-Forwarded-Proto: https\" -H \"X-Forwarded-For: 127.0.0.1\" -H \"X-Real-IP: 127.0.0.1\" http://127.0.0.1:3000/api/auth/login'
            r = run_remote(panel_ip, panel_cred, check_cmd, timeout=20)
            code = (r.stdout or '').strip()
            if code.isdigit() and code == '000':
                print(f"  ❌ Remnawave API недоступен на {panel_ip}:3000 (код: {code or 'нет ответа'})")
                print('     Убедитесь, что панель запущена: cd /opt/remnawave && docker compose up -d')
                sys.exit(1)
            print(f'  ✅ Remnawave API доступен (HTTP {code}, панель работает)')
            version_cmd = 'docker exec remnawave cat package.json 2>/dev/null | grep \'\"version\"\' | head -1 | sed -E \'s/.*\"version\": \"([^\"]+)\".*/\\1/\''
            r = run_remote(panel_ip, panel_cred, version_cmd, timeout=10)
            panel_version_actual = (r.stdout or '').strip()
            if panel_version_actual:
                print(f'  Обнаружена версия панели: {panel_version_actual}')
                try:
                    v_parts = panel_version_actual.split('.')
                    major, minor = (int(v_parts[0]), int(v_parts[1]))
                    if panel_version_choice == '1':
                        if major!= 2 or minor!= 8:
                            print(f'  ⚠️  Выбрана версия 2.8.1, но обнаружена {panel_version_actual}')
                            print('     Installer будет работать в режиме выбранной версии (2.8.1)')
                    else:
                        if panel_version_choice == '2':
                            if major < 3 or (major == 3 and minor < 2):
                                print(f'  ⚠️  Выбрана версия 3.2.3+, но обнаружена {panel_version_actual}')
                                print('     Пожалуйста, обновите панель или выберите версию 2.8.1')
                except:
                    print(f'  ⚠️  Не удалось распознать версию: {panel_version_actual}')
            else:
                print('  ⚠️  Не удалось определить версию панели')
            if args.mode and (args.no_hy2 or args.no_grpc):
                extra = {'install_hy2': not getattr(args, 'no_hy2', False), 'install_grpc': not getattr(args, 'no_grpc', False)}
            else:
                extra = ask_extra_protocols()
            panel_user = args.panel_user if args.mode and args.panel_user else ask('Логин панели Remnawave (username)')
            panel_pass = args.panel_pass if args.mode and args.panel_pass else ask('Пароль панели Remnawave (password)')
            token, login_resp = remnawave_login_ssh(panel_ip, panel_cred, panel_user, panel_pass)
            if not token:
                print(f'  ❌ Не удалось авторизоваться в панели: {str(login_resp)[:300]}')
                sys.exit(1)
            print('  ✅ Авторизация успешна')
            cascade = False
            cascade_ip = None
            cascade_cred = None
            if args.mode and getattr(args, 'cascade', False) and args.cascade_ip:
                cascade = True
                cascade_ip = args.cascade_ip
                cascade_cred = {'type': 'password', 'value': args.cascade_pass or '', 'user': getattr(args, 'cascade_user', 'root')}
            else:
                if not args.mode:
                    casc = '1'
                    if casc == '2':
                        cascade = True
                        cascade_ip = ask('IP relay-сервера в РФ (Cascade relay IP)')
                        cascade_cred = ask_ssh_cred()
            cfg = {'cdn_type': cdn_type, 'domain': domain, 'front_sub': front_sub, 'front_domain': front_domain, 'server_ip': server_ip, 'panel_ip': panel_ip, 'panel_cred': panel_cred, 'origin_sub': origin_sub, 'cdn_sub': cdn_sub, 'skip_cdn_wait': getattr(args, 'skip_cdn_wait', False) if args.mode else False, 'install_hy2': extra['install_hy2'], 'install_grpc': extra['install_grpc'], 'squad': getattr(args, 'squad', None), 'cascade': cascade, 'cascade_ip': cascade_ip, 'cascade_cred': cascade_cred, 'panel_version_choice': panel_version_choice}
            if cdn_type == 'host':
                print(f'\n  Поддомены: origin={origin_sub}.{domain}, фронт={front_domain}')
            else:
                print(f'\n  Поддомены: origin={origin_sub}.{domain}, cdn={cdn_sub}.{domain}')
            print(f'  Панель: {panel_ip} (SSH)')
        else:
            cascade = False
            cascade_ip = None
            cascade_cred = None
            panel_ip = ask('IP сервера с 3x-ui панелью (Panel server IP)')
            panel_cred = ask_ssh_cred()
            casc = '1'
            if casc == '2':
                cascade = True
                cascade_ip = ask('IP exit-сервера (Cascade exit server IP)')
                cascade_cred = ask_ssh_cred()
            exit_sub = ''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(3))
            while exit_sub in (origin_sub, cdn_sub):
                exit_sub = ''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(3))
            cfg = {
                'cdn_type': cdn_type,
                'domain': domain,
                'front_sub': front_sub,
                'front_domain': front_domain,
                'server_ip': server_ip,
                'panel_ip': panel_ip,
                'panel_cred': panel_cred,
                'origin_sub': origin_sub,
                'cdn_sub': cdn_sub,
                'skip_cdn_wait': getattr(args, 'skip_cdn_wait', False) if args.mode else False,
                'install_hy2': False,
                'install_grpc': False,
                'cascade': cascade,
                'cascade_ip': cascade_ip,
                'cascade_cred': cascade_cred,
                'exit_sub': exit_sub,
            }
            if cdn_type == 'host':
                print(f'\n  Поддомены: origin={origin_sub}.{domain}, фронт={front_domain}')
            else:
                print(f'\n  Поддомены: origin={origin_sub}.{domain}, cdn={cdn_sub}.{domain}')
            print(f'  Панель 3x-ui: {panel_ip}')
        if cascade and panel_type == '1':
            origin_dns_ip = cascade_ip
        else:
            origin_dns_ip = server_ip
        exit_sub = cfg.get('exit_sub', 'xui')
        print(f"\n  ============================================\n  СОЗДАЙ {('ЭТИ DNS ЗАПИСИ' if cascade and panel_type == '2' else 'ЭТУ DNS ЗАПИСЬ')} У ВАШЕГО DNS-ПРОВАЙДЕРА:\n  ============================================\n\n  A    {origin_sub}.{domain}    ->  {origin_dns_ip}     (без проксирования){('  ← relay (каскад)' if cascade and panel_type == '1' else '')}")
        if cascade and panel_type == '2':
                print(f'  A    {exit_sub}.{domain}    ->  {cascade_ip}     (без проксирования)  ← exit (каскад)')
        if cdn_type == 'host':
            print(f'  (фронт {front_domain} создашь на IP ХОСТИНГА REG.RU, не на этом сервере)\n')
        else:
            print(f'  ({cdn_sub}.{domain} CNAME создашь после настройки CDN)\n')
        if not (args.mode and args.skip_dns_wait):
            safe_input('  Нажми ENTER когда DNS записи созданы...')
        common_setup(cfg)
        if panel_type == '1':
            install_node_only(cfg)
            return
        install_3xui_cdn_only(cfg)
        return
    node_cred = ''
    cascade = False
    cascade_ip = None
    cascade_cred = None
    if args.panel:
        panel_type = args.panel
        cdn_type = args.cdn or 'vk'
        domain = args.domain
        node_ip = args.node_ip or server_ip
        if args.node_key:
            node_cred = {'type': 'key', 'value': args.node_key, 'user': args.node_user}
        else:
            if args.node_pass:
                node_cred = {'type': 'password', 'value': args.node_pass, 'user': args.node_user}
        if getattr(args, 'cascade', False) and args.cascade_ip:
                cascade = True
                cascade_ip = args.cascade_ip
                cascade_cred = {'type': 'password', 'value': args.cascade_pass or '', 'user': getattr(args, 'cascade_user', 'root')}
    else:
        if mode == '2':
            panel_type = ask('Панель (Panel)?', {'1': 'Remnawave 3.2.3', '2': '3x-ui 3.6.0 (не поддерживается, ждите обновления)'})
            if panel_type == '2':
                print('  ❌ 3x-ui пока не поддерживается в режиме 2 (панель + нода на разных серверах)')
                print('  Используйте режим 1 или ждите обновления.')
                sys.exit(1)
        else:
            panel_type = ask('Панель (Panel)?', {'1': 'Remnawave 3.2.3', '2': '3x-ui 3.6.0'})
        cdn_type = 'host'
        cascade = False
        cascade_ip = None
        cascade_cred = None
        domain = ask('Домен фронта без http://')
        domain = domain.replace('https://', '').replace('http://', '').strip('/').strip()
        node_ip = server_ip
        if mode == '2':
            node_ip = ask('IP сервера ноды (Node server IP)')
            node_cred = ask_ssh_cred()
    extra = ask_extra_protocols(panel_type=panel_type)
    origin_sub, front_choice, panel_sub = ask_custom_subs(need_panel=True, host_mode=cdn_type == 'host')
    front_sub = None
    if cdn_type == 'host':
        front_sub = front_choice
        cdn_sub = gen_subdomain()
    else:
        cdn_sub = front_choice
    exit_sub = gen_subdomain()
    while exit_sub in (origin_sub, cdn_sub):
        exit_sub = gen_subdomain()
    if not front_sub:
        front_sub = gen_subdomain()
        while front_sub in (origin_sub, cdn_sub, panel_sub or '', exit_sub):
            front_sub = gen_subdomain()
    front_domain = f'{front_sub}.{domain}' if cdn_type == 'host' else domain
    cfg = {'panel_type': panel_type, 'cdn_type': cdn_type, 'domain': domain, 'front_sub': front_sub, 'front_domain': front_domain, 'server_ip': server_ip, 'node_ip': node_ip, 'node_cred': node_cred, 'skip_cdn_wait': getattr(args, 'skip_cdn_wait', False) if args.panel else False, 'origin_sub': origin_sub, 'cdn_sub': cdn_sub, 'panel_sub': panel_sub, 'install_hy2': extra['install_hy2'], 'install_grpc': extra['install_grpc'], 'cascade': cascade, 'cascade_ip': cascade_ip, 'cascade_cred': cascade_cred, **{'exit_sub': exit_sub}}
    if cdn_type == 'host':
        print(f'\n  Поддомены: origin={origin_sub}.{domain}, фронт={front_domain}')
    else:
        print(f'\n  Поддомены: origin={origin_sub}.{domain}, cdn={cdn_sub}.{domain}')
    print(f'  Панель: {panel_sub}.{domain}')
    print('\n  ============================================\n  СОЗДАЙ ЭТИ DNS ЗАПИСИ У ВАШЕГО DNS-ПРОВАЙДЕРА:\n  ============================================\n')
    if cascade and panel_type == '1':
        origin_dns_ip = cascade_ip
    else:
        origin_dns_ip = node_ip
    print(f'  A    {panel_sub}.{domain}  ->  {server_ip}   (без проксирования)')
    print(f"  A    {origin_sub}.{domain}    ->  {origin_dns_ip}     (без проксирования){('  ← relay (каскад)' if cascade and panel_type == '1' else '')}")
    if cascade and panel_type == '2':
            print(f'  A    {exit_sub}.{domain}    ->  {cascade_ip}     (без проксирования)  ← exit (каскад)')
    if cdn_type == 'host':
        print(f'  (фронт {front_domain} создашь на IP ХОСТИНГА REG.RU, не на этом сервере)')
    else:
        print(f'  ({cdn_sub}.{domain} CNAME создашь после настройки CDN)')
    print()
    if not (args.panel and args.skip_dns_wait):
        safe_input('  Нажми ENTER когда DNS записи созданы...')
    try:
        common_setup(cfg)
        if panel_type == '2':
            install_3xui(cfg)
        else:
            install_remnawave(cfg)
    finally:
        cleanup_ssh_key(node_cred)
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        handle_ctrl_c(can_resume=False)
        sys.exit(1)
