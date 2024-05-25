import requests
import json
import subprocess

OUTPUT_FILE = "ovpn-e.conf"
API_CERT_URL = "https://api.black.riseup.net/3/cert"
API_GATEWAYS_URL = "https://api.black.riseup.net/3/config/eip-service.json"
VERBOSE = True

def verbose_log(message):
    if VERBOSE:
        print(f"> {message}")

def get_latency(ip_address):
    try:
        result = subprocess.run(
            ["ping", "-c", "1", ip_address],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            output = result.stdout
            time_line = output.split('\n')[1]
            time_ms = time_line.split('time=')[-1].split(' ')[0]
            return float(time_ms)
    except Exception as e:
        verbose_log(f"Error pinging {ip_address}: {e}")
    return float('inf')

verbose_log("Starting E-VPN setup...")

verbose_log(f"Fetching VPN client certs from: {API_CERT_URL}")
response = requests.get(API_CERT_URL, timeout=5)
response.raise_for_status()
key_cert = response.text

verbose_log(f"Creating/Open output file: {OUTPUT_FILE}")
with open(".e-vpn-base.conf", 'r') as sample_conf:
    with open(OUTPUT_FILE, 'w') as output_conf:
        output_conf.write(sample_conf.read())

verbose_log(f"Appending key_cert to {OUTPUT_FILE}")
with open(OUTPUT_FILE, 'a') as output_conf:
    output_conf.write(f"\n<key>\n{key_cert}\n</key>")
    output_conf.write(f"\n<cert>\n{key_cert}\n</cert>")

verbose_log(f"Fetching VPN gateways from: {API_GATEWAYS_URL}")
response = requests.get(API_GATEWAYS_URL, timeout=5)
response.raise_for_status()
gateways = response.json()['gateways']

fastest_gateway = None
fastest_latency = float('inf')

verbose_log(f"Measuring latency to VPN gateways")
for gateway in gateways:
    ip_address = gateway['ip_address']
    host = gateway['host']
    location = gateway['location']
    ports = [port['ports'] for port in gateway['capabilities']['transport'] if 'openvpn' in port['type']]

    latency = get_latency(ip_address)
    verbose_log(f"Latency to {host} ({ip_address}): {latency} ms")
    
    if latency < fastest_latency:
        fastest_latency = latency
        fastest_gateway = gateway

if fastest_gateway:
    ip_address = fastest_gateway['ip_address']
    host = fastest_gateway['host']
    location = fastest_gateway['location']
    ports = [port['ports'] for port in fastest_gateway['capabilities']['transport'] if 'openvpn' in port['type']]
    
    port = ports[0][0]

    verbose_log(f"Fastest gateway: {host} ({ip_address}) with latency {fastest_latency} ms")

    with open(OUTPUT_FILE, 'r') as file:
        lines = file.readlines()
    with open(OUTPUT_FILE, 'w') as file:
        for line in lines:
            if "remote-random" in line:
                file.write(f"remote {ip_address} {port} # {host} ({location})\n")
            file.write(line)
    print(f"\033[92mE-VPN setup completed successfully. You can now run: sudo openvpn --config {OUTPUT_FILE}\033[0m")
else:
    print("\033[91mNo valid gateways found.\033[0m")
