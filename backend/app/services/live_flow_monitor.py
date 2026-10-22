"""
CyberShield AI - Passive Live Flow Monitor

Captures IPv4 traffic passively, computes live flow statistics, and runs
XGBoost only when the validated 40-feature vector is complete.

Safety: this module does not block packets or execute automated defense.
"""

from threading import Lock, Thread
from time import time
from collections import deque

from scapy.all import IP, TCP, UDP, sniff

from .live_feature_extractor import extract_live_features
from .xgboost_service import xgboost_service


WIFI_INTERFACE = r"\Device\NPF_{FFA90319-D30D-4021-B985-FA40FFE03DED}"
MAX_FLOWS = 2000
IDLE_TIMEOUT_SECONDS = 60.0
ACTIVE_TIMEOUT_SECONDS = 5.0
ACTIVITY_IDLE_THRESHOLD_SECONDS = 2.0
MAX_STORED_SAMPLES_PER_FLOW = 10000


class LiveFlowMonitor:
    def __init__(self):
        self._lock = Lock()
        self._flows = {}
        self._running = False
        self._thread = None
        self._started_at = None
        self._last_error = None

    @staticmethod
    def _packet_details(packet):
        ip = packet[IP]
        if TCP in packet:
            protocol = "TCP"
            src_port = int(packet[TCP].sport)
            dst_port = int(packet[TCP].dport)
        elif UDP in packet:
            protocol = "UDP"
            src_port = int(packet[UDP].sport)
            dst_port = int(packet[UDP].dport)
        else:
            protocol = "OTHER"
            src_port = 0
            dst_port = 0

        source = (ip.src, src_port)
        destination = (ip.dst, dst_port)
        endpoints = tuple(sorted((source, destination)))
        return (endpoints[0], endpoints[1], protocol), source, destination, protocol

    @staticmethod
    def _new_flow(source, destination, protocol, now):
        return {
            "source_ip": source[0],
            "destination_ip": destination[0],
            "source_port": source[1],
            "destination_port": destination[1],
            "protocol": protocol,
            "forward_endpoint": source,
            "first_seen": now,
            "last_seen": now,
            "last_packet_time": None,
            "packet_timestamps": deque(maxlen=MAX_STORED_SAMPLES_PER_FLOW),
            "packets": 0,
            "bytes": 0,
            "forward_packets": 0,
            "backward_packets": 0,
            "forward_bytes": 0,
            "backward_bytes": 0,
            "packet_lengths": deque(maxlen=MAX_STORED_SAMPLES_PER_FLOW),
            "forward_packet_lengths": deque(maxlen=MAX_STORED_SAMPLES_PER_FLOW),
            "backward_packet_lengths": deque(maxlen=MAX_STORED_SAMPLES_PER_FLOW),
            "inter_arrival_seconds": deque(maxlen=MAX_STORED_SAMPLES_PER_FLOW),
            "forward_iats": deque(maxlen=MAX_STORED_SAMPLES_PER_FLOW),
            "backward_iats": deque(maxlen=MAX_STORED_SAMPLES_PER_FLOW),
            "last_forward_time": None,
            "last_backward_time": None,
            "forward_header_lengths": deque(maxlen=MAX_STORED_SAMPLES_PER_FLOW),
            "backward_header_lengths": deque(maxlen=MAX_STORED_SAMPLES_PER_FLOW),
            "forward_initial_window": None,
            "backward_initial_window": None,
            "forward_data_packets": 0,
            "psh_flag_count": 0,
            "ack_flag_count": 0,
            "syn_flag_count": 0,
            "fin_flag_count": 0,
            "rst_flag_count": 0,
        }

    def _handle_packet(self, packet):
        if IP not in packet:
            return

        now = time()
        key, source, destination, protocol = self._packet_details(packet)
        ip = packet[IP]
        packet_length = int(ip.len or len(ip))
        ip_header_length = int(ip.ihl or 5) * 4

        tcp_header_length = 0
        tcp_flags = 0
        tcp_window = None
        payload_length = 0

        if TCP in packet:
            tcp = packet[TCP]
            tcp_header_length = int(tcp.dataofs or 5) * 4
            tcp_flags = int(tcp.flags)
            tcp_window = int(tcp.window)
            payload_length = len(bytes(tcp.payload))
        elif UDP in packet:
            payload_length = len(bytes(packet[UDP].payload))

        with self._lock:
            if key not in self._flows:
                if len(self._flows) >= MAX_FLOWS:
                    oldest = min(self._flows, key=lambda item: self._flows[item]["last_seen"])
                    del self._flows[oldest]
                self._flows[key] = self._new_flow(source, destination, protocol, now)

            flow = self._flows[key]
            is_forward = source == flow["forward_endpoint"]

            # Initial windows are only taken from actual handshake packets.
            # Midstream TCP window values are not substituted for initial windows.
            if TCP in packet:
                syn = bool(tcp_flags & 0x02)
                ack = bool(tcp_flags & 0x10)
                if syn and not ack and is_forward and flow["forward_initial_window"] is None:
                    flow["forward_initial_window"] = tcp_window
                elif syn and ack and not is_forward and flow["backward_initial_window"] is None:
                    flow["backward_initial_window"] = tcp_window

            flow["packets"] += 1
            flow["bytes"] += packet_length
            flow["last_seen"] = now
            flow["packet_lengths"].append(packet_length)
            flow["packet_timestamps"].append(now)

            if flow["last_packet_time"] is not None:
                flow["inter_arrival_seconds"].append(max(0.0, now - flow["last_packet_time"]))
            flow["last_packet_time"] = now

            if is_forward:
                flow["forward_packets"] += 1
                flow["forward_bytes"] += packet_length
                flow["forward_packet_lengths"].append(packet_length)
                if tcp_header_length:
                    flow["forward_header_lengths"].append(tcp_header_length)
                if payload_length > 0:
                    flow["forward_data_packets"] += 1
                if flow["last_forward_time"] is not None:
                    flow["forward_iats"].append(max(0.0, now - flow["last_forward_time"]))
                flow["last_forward_time"] = now
            else:
                flow["backward_packets"] += 1
                flow["backward_bytes"] += packet_length
                flow["backward_packet_lengths"].append(packet_length)
                if tcp_header_length:
                    flow["backward_header_lengths"].append(tcp_header_length)
                if flow["last_backward_time"] is not None:
                    flow["backward_iats"].append(max(0.0, now - flow["last_backward_time"]))
                flow["last_backward_time"] = now

            flow["fin_flag_count"] += int(bool(tcp_flags & 0x01))
            flow["syn_flag_count"] += int(bool(tcp_flags & 0x02))
            flow["rst_flag_count"] += int(bool(tcp_flags & 0x04))
            flow["psh_flag_count"] += int(bool(tcp_flags & 0x08))
            flow["ack_flag_count"] += int(bool(tcp_flags & 0x10))

    def _capture(self):
        try:
            sniff(
                iface=WIFI_INTERFACE,
                filter="ip",
                prn=self._handle_packet,
                store=False,
                stop_filter=lambda _: not self._running,
            )
        except Exception as error:
            with self._lock:
                self._last_error = f"{type(error).__name__}: {error}"
                self._running = False

    def start(self):
        with self._lock:
            if self._running:
                return {"status": "already_running", "capture_mode": "passive"}
            self._running = True
            self._last_error = None
            self._started_at = time()

        self._thread = Thread(target=self._capture, daemon=True)
        self._thread.start()
        return {"status": "started", "interface": "Wi-Fi", "capture_mode": "passive"}

    def stop(self):
        with self._lock:
            self._running = False
        return {"status": "stop_requested"}

    def status(self):
        with self._lock:
            return {
                "running": self._running,
                "interface": "Wi-Fi",
                "capture_mode": "passive",
                "flow_count": len(self._flows),
                "last_error": self._last_error,
                "model_predictions_enabled": True,
                "prediction_pipeline": "xgboost",
                "defense_execution": "disabled",
            }

    @staticmethod
    def _mean(values):
        return sum(values) / len(values) if values else 0.0

    @staticmethod
    def _minimum(values):
        return min(values) if values else 0.0

    @staticmethod
    def _maximum(values):
        return max(values) if values else 0.0

    @staticmethod
    def _std(values):
        if not values:
            return 0.0
        mean = sum(values) / len(values)
        return (sum((value - mean) ** 2 for value in values) / len(values)) ** 0.5

    @staticmethod
    def _activity_metrics(timestamps):
        """Approximate CICFlowMeter-style active periods in seconds.

        Uses a 2-second idle gap and a 5-second active-period cap. This is a
        live approximation and should not be assumed identical to training.
        """
        if len(timestamps) < 2:
            return None, None
        periods = []
        period_start = previous = timestamps[0]
        for current in list(timestamps)[1:]:
            if current - previous > ACTIVITY_IDLE_THRESHOLD_SECONDS:
                periods.append(min(max(previous - period_start, 0.0), ACTIVE_TIMEOUT_SECONDS))
                period_start = current
            elif current - period_start > ACTIVE_TIMEOUT_SECONDS:
                periods.append(ACTIVE_TIMEOUT_SECONDS)
                period_start = current
            previous = current
        periods.append(min(max(previous - period_start, 0.0), ACTIVE_TIMEOUT_SECONDS))
        return min(periods), sum(periods) / len(periods)

    def get_flows(self):
        now = time()
        with self._lock:
            expired = [
                key for key, flow in self._flows.items()
                if now - flow["last_seen"] > IDLE_TIMEOUT_SECONDS
            ]
            for key in expired:
                del self._flows[key]

            results = []
            for flow in self._flows.values():
                actual_duration = max(flow["last_seen"] - flow["first_seen"], 0.0)
                if actual_duration > 0:
                    packet_rate = flow["packets"] / actual_duration
                    byte_rate = flow["bytes"] / actual_duration
                    backward_rate = flow["backward_packets"] / actual_duration
                else:
                    packet_rate = byte_rate = backward_rate = 0.0

                lengths = list(flow["packet_lengths"])
                fwd_lengths = list(flow["forward_packet_lengths"])
                bwd_lengths = list(flow["backward_packet_lengths"])
                iats = list(flow["inter_arrival_seconds"])
                fwd_iats = list(flow["forward_iats"])
                bwd_iats = list(flow["backward_iats"])
                total_packets = flow["forward_packets"] + flow["backward_packets"]
                total_bytes = flow["forward_bytes"] + flow["backward_bytes"]
                active_min, active_mean = self._activity_metrics(flow["packet_timestamps"])

                mean_length = self._mean(lengths)
                mean_bwd_length = self._mean(bwd_lengths)
                mean_fwd_length = self._mean(fwd_lengths)
                result = {
                    "source_ip": flow["source_ip"],
                    "destination_ip": flow["destination_ip"],
                    "protocol": flow["protocol"],
                    "source_port": flow["source_port"],
                    "destination_port": flow["destination_port"],
                    "packets": flow["packets"],
                    "bytes": flow["bytes"],
                    "forward_packets": flow["forward_packets"],
                    "backward_packets": flow["backward_packets"],
                    "forward_bytes": flow["forward_bytes"],
                    "backward_bytes": flow["backward_bytes"],
                    "duration_seconds": actual_duration,
                    "packets_per_second": packet_rate,
                    "bytes_per_second": byte_rate,
                    "backward_packets_per_second": backward_rate,
                    "mean_packet_length": mean_length,
                    "min_packet_length": self._minimum(lengths),
                    "max_packet_length": self._maximum(lengths),
                    "packet_length_variance": (
                        sum((x - mean_length) ** 2 for x in lengths) / len(lengths)
                        if lengths else 0.0
                    ),
                    "flow_iat_mean_seconds": self._mean(iats),
                    "flow_iat_std_seconds": self._std(iats),
                    "flow_iat_min_seconds": self._minimum(iats),
                    "flow_iat_max_seconds": self._maximum(iats),
                    "forward_iat_mean_seconds": self._mean(fwd_iats),
                    "forward_iat_std_seconds": self._std(fwd_iats),
                    "forward_iat_min_seconds": self._minimum(fwd_iats),
                    "forward_iat_max_seconds": self._maximum(fwd_iats),
                    "backward_iat_mean_seconds": self._mean(bwd_iats),
                    "backward_iat_min_seconds": self._minimum(bwd_iats),
                    "backward_iat_max_seconds": self._maximum(bwd_iats),
                    "backward_iat_total_seconds": sum(bwd_iats),
                    "forward_mean_packet_length": mean_fwd_length,
                    "backward_mean_packet_length": mean_bwd_length,
                    "forward_min_packet_length": self._minimum(fwd_lengths),
                    "forward_max_packet_length": self._maximum(fwd_lengths),
                    "backward_min_packet_length": self._minimum(bwd_lengths),
                    "backward_max_packet_length": self._maximum(bwd_lengths),
                    "forward_header_length_total": sum(flow["forward_header_lengths"]),
                    "backward_header_length_total": sum(flow["backward_header_lengths"]),
                    "forward_data_packet_count": flow["forward_data_packets"],
                    "psh_flag_count": flow["psh_flag_count"],
                    "ack_flag_count": flow["ack_flag_count"],
                    "syn_flag_count": flow["syn_flag_count"],
                    "fin_flag_count": flow["fin_flag_count"],
                    "rst_flag_count": flow["rst_flag_count"],
                    "fwd_bwd_packet_ratio": (
                        flow["forward_packets"] / flow["backward_packets"]
                        if flow["backward_packets"] else 0.0
                    ),
                    "fwd_bwd_byte_ratio": (
                        flow["forward_bytes"] / flow["backward_bytes"]
                        if flow["backward_bytes"] else 0.0
                    ),
                    "fwd_bwd_avg_packet_length_ratio": (
                        mean_fwd_length / mean_bwd_length if mean_bwd_length else 0.0
                    ),
                    "forward_packet_percentage": (
                        flow["forward_packets"] / total_packets if total_packets else 0.0
                    ),
                    "forward_byte_percentage": (
                        flow["forward_bytes"] / total_bytes if total_bytes else 0.0
                    ),
                    # Only true handshake observations qualify as initial windows.
                    "initial_window_forward": flow["forward_initial_window"],
                    "initial_window_backward": flow["backward_initial_window"],
                    "active_min_seconds": active_min,
                    "active_mean_seconds": active_mean,
                    "feature_extraction_ready": False,
                    "feature_extraction_reason": None,
                    "missing_features": [],
                    "prediction": None,
                }

                extracted = extract_live_features(result)
                result["feature_extraction_ready"] = bool(extracted.get("ready"))
                if not extracted.get("ready"):
                    result["feature_extraction_reason"] = extracted.get("reason")
                    result["missing_features"] = extracted.get("missing_features", [])
                else:
                    try:
                        prediction = xgboost_service.predict(extracted["features"])
                        predicted_class = prediction.get("predicted_class")
                        result["prediction"] = {
                            **prediction,
                            "source_ip": result["source_ip"],
                            "status": (
                                "Monitoring" if predicted_class == 0 else "Potential Threat"
                            ),
                            "mode": "passive_live_flow",
                        }
                    except Exception as error:
                        result["feature_extraction_reason"] = (
                            f"Model prediction failed: {type(error).__name__}: {error}"
                        )
                results.append(result)

            return results


live_flow_monitor = LiveFlowMonitor()
