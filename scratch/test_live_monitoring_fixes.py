"""
Unit tests for CyberShieldAI live-monitoring fixes:
1. Normal TCP SYN -> SYN-ACK -> ACK handshake.
2. SYN-ACK-first capture, correct forward endpoint and backward window.
3. UDP/non-TCP feature extraction with -1.0 for window fields (and TCP omission preservation).
4. Single-packet flow with Active Min and Active Mean as 0.0 (without hiding multi-packet errors).
5. 40-feature order preservation and XGBoost input contract.
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_path = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(backend_path))

import unittest
from scapy.all import IP, TCP, UDP

from app.services.live_flow_monitor import LiveFlowMonitor
from app.services.live_feature_extractor import extract_live_features, FEATURE_NAMES
from app.services.xgboost_service import xgboost_service


class TestLiveMonitoringFixes(unittest.TestCase):

    def test_01_normal_tcp_handshake(self):
        """1. A normal TCP SYN -> SYN-ACK -> ACK handshake captures forward and backward windows."""
        monitor = LiveFlowMonitor()

        # 1. Client SYN (window=64240)
        syn_pkt = IP(src="192.168.1.50", dst="192.168.1.100") / TCP(sport=54321, dport=443, flags="S", window=64240)
        monitor._handle_packet(syn_pkt)

        # 2. Server SYN-ACK (window=65535)
        syn_ack_pkt = IP(src="192.168.1.100", dst="192.168.1.50") / TCP(sport=443, dport=54321, flags="SA", window=65535)
        monitor._handle_packet(syn_ack_pkt)

        # 3. Client ACK
        ack_pkt = IP(src="192.168.1.50", dst="192.168.1.100") / TCP(sport=54321, dport=443, flags="A", window=64240)
        monitor._handle_packet(ack_pkt)

        flows = monitor.get_flows()
        self.assertEqual(len(flows), 1)
        flow = flows[0]

        # Orientation: client is forward
        self.assertEqual(flow["source_ip"], "192.168.1.50")
        self.assertEqual(flow["destination_ip"], "192.168.1.100")
        self.assertEqual(flow["destination_port"], 443)

        # Windows
        self.assertEqual(flow["initial_window_forward"], 64240)
        self.assertEqual(flow["initial_window_backward"], 65535)
        self.assertEqual(flow["forward_packets"], 2)
        self.assertEqual(flow["backward_packets"], 1)

        # Feature readiness & predictions
        self.assertTrue(flow["feature_extraction_ready"])
        self.assertIsNotNone(flow["prediction"])

    def test_02_syn_ack_first_capture(self):
        """2. A SYN-ACK-first capture orients forward endpoint to the client and sets backward window."""
        monitor = LiveFlowMonitor()

        # Packet 1: Server SYN-ACK seen first (window=65535)
        syn_ack_pkt = IP(src="192.168.1.100", dst="192.168.1.50") / TCP(sport=443, dport=54321, flags="SA", window=65535)
        monitor._handle_packet(syn_ack_pkt)

        flows = monitor.get_flows()
        self.assertEqual(len(flows), 1)
        flow = flows[0]

        # Orientation: client (destination of SYN-ACK) must be forward endpoint
        self.assertEqual(flow["source_ip"], "192.168.1.50")
        self.assertEqual(flow["destination_ip"], "192.168.1.100")
        self.assertEqual(flow["source_port"], 54321)
        self.assertEqual(flow["destination_port"], 443)

        # Windows: backward window captured from SYN-ACK, forward window unobserved
        self.assertEqual(flow["initial_window_backward"], 65535)
        self.assertIsNone(flow["initial_window_forward"])
        self.assertEqual(flow["backward_packets"], 1)
        self.assertEqual(flow["forward_packets"], 0)

        # Packet 2: Client subsequent packet (ACK)
        client_ack = IP(src="192.168.1.50", dst="192.168.1.100") / TCP(sport=54321, dport=443, flags="A", window=64240)
        monitor._handle_packet(client_ack)

        flows2 = monitor.get_flows()
        flow2 = flows2[0]
        self.assertEqual(flow2["forward_packets"], 1)
        self.assertEqual(flow2["backward_packets"], 1)
        self.assertEqual(flow2["initial_window_backward"], 65535)

    def test_03_non_tcp_window_feature_extraction(self):
        """3. UDP/non-TCP feature extraction uses -1.0 for window fields; TCP omission is preserved."""
        monitor = LiveFlowMonitor()

        # Send a UDP packet
        udp_pkt = IP(src="10.0.0.1", dst="10.0.0.2") / UDP(sport=5000, dport=53)
        monitor._handle_packet(udp_pkt)

        flows = monitor.get_flows()
        self.assertEqual(len(flows), 1)
        udp_flow = flows[0]
        self.assertEqual(udp_flow["protocol"], "UDP")

        extracted = extract_live_features(udp_flow)
        self.assertTrue(extracted["ready"], f"UDP flow should be ready: {extracted.get('reason')}")

        features = extracted["features"]
        fwd_win_idx = FEATURE_NAMES.index("Init_Win_bytes_forward")
        bwd_win_idx = FEATURE_NAMES.index("Init_Win_bytes_backward")
        self.assertEqual(features[fwd_win_idx], -1.0)
        self.assertEqual(features[bwd_win_idx], -1.0)

        # Verify TCP with missing window is NOT defaulted to -1.0 and remains unready
        tcp_flow = udp_flow.copy()
        tcp_flow["protocol"] = "TCP"
        tcp_flow["initial_window_forward"] = None
        tcp_flow["initial_window_backward"] = None
        tcp_extracted = extract_live_features(tcp_flow)
        self.assertFalse(tcp_extracted["ready"])
        self.assertIn("Init_Win_bytes_forward", tcp_extracted["missing_features"])
        self.assertIn("Init_Win_bytes_backward", tcp_extracted["missing_features"])

    def test_04_other_protocol_flow(self):
        """4. OTHER protocol (e.g. ICMP) converts missing windows to -1.0 and runs XGBoost."""
        from scapy.all import ICMP
        monitor = LiveFlowMonitor()

        icmp_pkt = IP(src="10.0.0.1", dst="10.0.0.2") / ICMP()
        monitor._handle_packet(icmp_pkt)

        flows = monitor.get_flows()
        self.assertEqual(len(flows), 1)
        icmp_flow = flows[0]
        self.assertEqual(icmp_flow["protocol"], "OTHER")
        self.assertEqual(icmp_flow["destination_port"], 0)

        extracted = extract_live_features(icmp_flow)
        self.assertTrue(extracted["ready"], f"OTHER flow should be ready: {extracted.get('reason')}")
        self.assertEqual(extracted.get("missing_features", []), [])

        features = extracted["features"]
        fwd_win_idx = FEATURE_NAMES.index("Init_Win_bytes_forward")
        bwd_win_idx = FEATURE_NAMES.index("Init_Win_bytes_backward")
        self.assertEqual(features[fwd_win_idx], -1.0)
        self.assertEqual(features[bwd_win_idx], -1.0)

        # Confirm XGBoost prediction succeeds
        self.assertTrue(icmp_flow["feature_extraction_ready"])
        self.assertIsNotNone(icmp_flow["prediction"])

    def test_05_tcp_without_handshake_not_fabricated(self):
        """5. TCP flow without a captured handshake does NOT fabricate windows and stays unready."""
        monitor = LiveFlowMonitor()

        # Mid-stream TCP packet (flags='PA' or 'A') with no prior SYN / SYN-ACK
        mid_pkt = IP(src="192.168.1.10", dst="93.184.216.34") / TCP(sport=49152, dport=443, flags="PA", window=8192)
        monitor._handle_packet(mid_pkt)

        flows = monitor.get_flows()
        self.assertEqual(len(flows), 1)
        flow = flows[0]
        self.assertEqual(flow["protocol"], "TCP")
        self.assertIsNone(flow["initial_window_forward"])
        self.assertIsNone(flow["initial_window_backward"])

        extracted = extract_live_features(flow)
        self.assertFalse(extracted["ready"])
        self.assertIn("Init_Win_bytes_forward", extracted["missing_features"])
        self.assertIn("Init_Win_bytes_backward", extracted["missing_features"])
        self.assertFalse(flow["feature_extraction_ready"])
        self.assertIsNone(flow["prediction"])

    def test_06_single_packet_flow_activity_metrics(self):
        """6. Single-packet flow represents Active Min and Active Mean as 0.0 without masking multi-packet errors."""
        monitor = LiveFlowMonitor()

        # Send a single UDP packet
        pkt = IP(src="172.16.0.5", dst="172.16.0.1") / UDP(sport=1234, dport=8080)
        monitor._handle_packet(pkt)

        flows = monitor.get_flows()
        flow = flows[0]
        self.assertEqual(flow["packets"], 1)
        self.assertEqual(flow["active_min_seconds"], 0.0)
        self.assertEqual(flow["active_mean_seconds"], 0.0)

        extracted = extract_live_features(flow)
        self.assertTrue(extracted["ready"])
        active_min_idx = FEATURE_NAMES.index("Active Min")
        active_mean_idx = FEATURE_NAMES.index("Active Mean")
        self.assertEqual(extracted["features"][active_min_idx], 0.0)
        self.assertEqual(extracted["features"][active_mean_idx], 0.0)

        # Single-packet flow with active_min_seconds=None should still default to 0.0
        single_none_flow = flow.copy()
        single_none_flow["packets"] = 1
        single_none_flow["active_min_seconds"] = None
        single_none_flow["active_mean_seconds"] = None
        single_none_extracted = extract_live_features(single_none_flow)
        self.assertTrue(single_none_extracted["ready"])
        self.assertEqual(single_none_extracted["features"][active_min_idx], 0.0)
        self.assertEqual(single_none_extracted["features"][active_mean_idx], 0.0)

        # Flow with packets=None should safely handle without TypeError and default to 0.0
        none_packets_flow = flow.copy()
        none_packets_flow["packets"] = None
        none_packets_flow["active_min_seconds"] = None
        none_packets_flow["active_mean_seconds"] = None
        none_packets_extracted = extract_live_features(none_packets_flow)
        self.assertTrue(none_packets_extracted["ready"])
        self.assertEqual(none_packets_extracted["features"][active_min_idx], 0.0)
        self.assertEqual(none_packets_extracted["features"][active_mean_idx], 0.0)

        # Multi-packet flow with genuinely missing/None activity metrics should fail validation
        broken_flow = flow.copy()
        broken_flow["packets"] = 5
        broken_flow["active_min_seconds"] = None
        broken_flow["active_mean_seconds"] = None
        broken_extracted = extract_live_features(broken_flow)
        self.assertFalse(broken_extracted["ready"])
        self.assertIn("Active Min", broken_extracted["missing_features"])
        self.assertIn("Active Mean", broken_extracted["missing_features"])

    def test_07_feature_order_and_xgboost_contract(self):
        """7. 40-feature order matches Selected_Features.txt and XGBoost inference contract."""
        self.assertEqual(len(FEATURE_NAMES), 40)

        # Destination Port is index 0
        self.assertEqual(FEATURE_NAMES[0], "Destination Port")
        self.assertEqual(FEATURE_NAMES[1], "Init_Win_bytes_backward")
        self.assertEqual(FEATURE_NAMES[19], "Init_Win_bytes_forward")
        self.assertEqual(FEATURE_NAMES[31], "Active Min")
        self.assertEqual(FEATURE_NAMES[35], "Active Mean")
        self.assertEqual(FEATURE_NAMES[39], "ACK Flag Count")

        monitor = LiveFlowMonitor()
        pkt = IP(src="192.168.1.10", dst="192.168.1.1") / UDP(sport=4321, dport=53)
        monitor._handle_packet(pkt)
        flow = monitor.get_flows()[0]

        extracted = extract_live_features(flow)
        self.assertTrue(extracted["ready"])
        features = extracted["features"]
        self.assertEqual(len(features), 40)

        # XGBoost inference should accept the 40-feature vector
        pred = xgboost_service.predict(features)
        self.assertIn("predicted_class", pred)
        self.assertIn("attack_name", pred)
        self.assertIn("confidence", pred)
        self.assertIsInstance(pred["predicted_class"], int)
        self.assertIsInstance(pred["confidence"], float)


if __name__ == "__main__":
    unittest.main()
