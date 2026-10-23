import sys, pathlib, importlib, traceback

# Ensure project root is on sys.path for package imports
project_root = pathlib.Path(r'C:/final year/CyberShieldAI-Final')
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    mod = importlib.import_module('backend.app.services.live_flow_monitor')
except Exception as e:
    print('Failed to import live_flow_monitor package:', e)
    traceback.print_exc()
    sys.exit(1)

# Mock IFACES for testing (scapy already installed)
class MockIface:
    def __init__(self, name='', description='', guid='', ip=''):
        self.name = name
        self.description = description
        self.guid = guid
        self.ip = ip
        self.network_name = name

mod.IFACES.clear()
mod.IFACES.update({
    'eth0': MockIface(name='Ethernet 0', description='Intel Ethernet', guid='GUID1', ip='192.168.1.10'),
    'wifi0': MockIface(name='Wi-Fi', description='Intel Wi-Fi', guid='GUID2', ip='192.168.1.20'),
    'wifi1': MockIface(name='Wi-Fi 2', description='Realtek Wi-Fi', guid='GUID3', ip='192.168.1.30'),
})

def run_tests():
    # Explicit name match
    try:
        dev, disp = mod.resolve_capture_interface('Wi-Fi')
        print('Explicit name matched:', dev, disp)
    except Exception as e:
        print('Explicit name error:', e)
    # Explicit GUID match
    try:
        dev, disp = mod.resolve_capture_interface('GUID2')
        print('Explicit GUID matched:', dev, disp)
    except Exception as e:
        print('Explicit GUID error:', e)
    # Ambiguous partial match should raise ValueError
    try:
        dev, disp = mod.resolve_capture_interface('wifi')
        print('Ambiguous result:', dev, disp)
    except Exception as e:
        print('Ambiguous error (expected):', e)
    # Auto discovery with single Wi-Fi
    mod.IFACES.pop('wifi1')
    try:
        dev, disp = mod.resolve_capture_interface()
        print('Auto discovery single Wi-Fi:', dev, disp)
    except Exception as e:
        print('Auto discovery error:', e)

if __name__ == '__main__':
    run_tests()
