"""
CyberShield AI - Passive Live Flow Monitor

Captures IPv4 traffic passively, computes live flow statistics, and runs
XGBoost only when the validated 40-feature vector is complete.

Safety: this module does not block packets or execute automated defense.
"""

import os
from pathlib import Path
from threading import Lock
from time import time
from collections import deque

from scapy.all import IP, TCP, UDP, IFACES, AsyncSniffer

from .live_feature_extractor import extract_live_features
from .xgboost_service import xgboost_service

VIRTUAL_KEYWORDS = [
    "virtual", "vmware", "virtualbox", "hyper-v", "vethernet",
    "wan miniport", "loopback", "bluetooth", "wi-fi direct", "wifi direct", "teredo"
]

WIFI_KEYWORDS = ["wi-fi", "wifi", "wireless", "802.11", "wlan"]


def _load_env_file():
    """Load CYBERSHIELD_INTERFACE from the project‑root .env file.
    This function loads **only** the `CYBERSHIELD_INTERFACE` key and reports any I/O errors to stderr.
    """
    # Look only at the project‑root .env file (three levels up from this file)
    base = Path(__file__).resolve().parents[3]
    candidate = base / ".env"
    if candidate.exists():
        try:
            with open(candidate, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    k, v = k.strip(), v.strip().strip('"').strip("'")
                    if k == "CYBERSHIELD_INTERFACE" and k not in os.environ:
                        os.environ[k] = v
        except Exception as e:
            import sys
            sys.stderr.write(f"[live_flow_monitor] Failed to read .env file: {e}\n")


def is_virtual_or_loopback(name: str, desc: str) -> bool:
    target = f"{name} {desc}".lower()
    return any(keyword in target for keyword in VIRTUAL_KEYWORDS)


def is_wifi_adapter(name: str, desc: str) -> bool:
    target = f"{name} {desc}".lower()
    return any(keyword in target for keyword in WIFI_KEYWORDS)


def get_available_interfaces() -> list[dict]:
    result = []
    for dev_name, iface in IFACES.items():
        name = getattr(iface, "name", "")
        desc = getattr(iface, "description", "")
        guid = getattr(iface, "guid", "")
        ip = getattr(iface, "ip", "")
        net_name = getattr(iface, "network_name", dev_name)
        result.append({
            "name": name,
            "description": desc,
            "guid": guid,
            "network_name": net_name,
            "ip": ip,
            "is_virtual": is_virtual_or_loopback(name, desc),
            "is_wifi": is_wifi_adapter(name, desc),
        })
    return result


def resolve_capture_interface(explicit_target: str | None = None) -> tuple[str, str]:
    """Resolve the network interface for live flow capture.

    Order of precedence:
    1. explicit_target parameter (if provided)
    2. CYBERSHIELD_INTERFACE environment variable (or from .env)
    3. Automatic discovery of a single physical Wi‑Fi adapter via Scapy/Npcap
    """
    _load_env_file()
    interfaces = get_available_interfaces()
    if not interfaces:
        raise RuntimeError("No network interfaces found by Scapy/Npcap. Verify that Npcap is installed and running.")

    target = explicit_target or os.environ.get("CYBERSHIELD_INTERFACE", "").strip()
    if target:
        cleaned_target = target.lower()
        matched = []
        for iface in interfaces:
            net_name = iface["network_name"].lower()
            name = iface["name"].lower()
            guid = iface["guid"].lower()
            desc = iface["description"].lower()
            if cleaned_target in (net_name, name, guid, guid.strip("{}")):
                matched.append(iface)
        if not matched:
            avail = "\n".join(f"  - Name: {i['name']} | Desc: {i['description']} | Device: {i['network_name']}" for i in interfaces)
            raise ValueError(f"Configured interface '{target}' was not found among available interfaces.\nAvailable interfaces:\n{avail}")
        if len(matched) > 1:
            exact = [m for m in matched if cleaned_target in (m["network_name"].lower(), m["name"].lower(), m["guid"].lower())]
            if len(exact) == 1:
                selected = exact[0]
            else:
                summary = "\n".join(f"  - {m['name']} ({m['description']}): {m['network_name']}" for m in matched)
                raise ValueError(f"Configured interface '{target}' is ambiguous, matched multiple interfaces:\n{summary}")
        else:
            selected = matched[0]
        return selected["network_name"], selected["name"] or selected["description"] or "Wi‑Fi"

    # Automatic discovery
    wifi_candidates = [i for i in interfaces if i["is_wifi"] and not i["is_virtual"]]
    if len(wifi_candidates) == 1:
        sel = wifi_candidates[0]
        return sel["network_name"], sel["name"] or "Wi‑Fi"
    if len(wifi_candidates) > 1:
        active = [i for i in wifi_candidates if i["ip"] and not i["ip"].startswith("169.254.") and i["ip"] != "0.0.0.0"]
        if len(active) == 1:
            sel = active[0]
            return sel["network_name"], sel["name"] or "Wi-Fi"
        candidates_str = "\n".join(f"  - {c['name']} ({c['description']}) [IP: {c['ip']}]: {c['network_name']}" for c in wifi_candidates)
        raise RuntimeError(
            "Multiple Wi-Fi interfaces detected. Please set the CYBERSHIELD_INTERFACE environment variable to specify which one to use.\nDetected Wi-Fi interfaces:\n" + candidates_str)
    # Fallback error
    avail = "\n".join(f"  - Name: {i['name']} | Desc: {i['description']} [IP: {i['ip']}]" for i in interfaces if not i["is_virtual"])
    raise RuntimeError(
        "No physical Wi-Fi interface automatically detected. If using Ethernet or another adapter, set the CYBERSHIELD_INTERFACE environment variable with the adapter name or GUID.\n" +
        f"Available non-virtual interfaces:\n{avail}")

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
        self._started_at = None
        self._last_error = None
        self._active_interface_device = None
        self._active_interface_name = "Wi-Fi"
        # Legacy thread placeholder (kept for backward compatibility)
        self._thread = None
        # AsyncSniffer instance when capture is active
        self._sniffer = None

    def _sniffer_active(self) -> bool:
        """Return True if the AsyncSniffer is running or its thread is alive."""
        if not self._sniffer:
            return False
        if getattr(self._sniffer, "running", False):
            return True
        thread = getattr(self._sniffer, "_thread", None)
        return bool(thread and thread.is_alive())

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
                    oldest = min(self._flows, key=lambda k: self._flows[k]["last_seen"])
                    del self._flows[oldest]
                if TCP in packet and (tcp_flags & 0x02) and (tcp_flags & 0x10):
                    # Observed a TCP SYN-ACK as the first packet for this flow:
                    # Orient flow so destination is the client/initiator (forward endpoint)
                    # and source is the server.
                    self._flows[key] = self._new_flow(destination, source, protocol, now)
                else:
                    self._flows[key] = self._new_flow(source, destination, protocol, now)
            flow = self._flows[key]
            is_forward = source == flow["forward_endpoint"]
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

    def _sniffer_terminated(self, sniffer) -> bool:
        """Return True if the given sniffer is definitely not running."""
        if not sniffer:
            return True
        if getattr(sniffer, "running", False):
            return False
        thread = getattr(sniffer, "_thread", None)
        return not (thread and thread.is_alive())

    def start(self, interface: str | None = None):
        """Start live flow capture on the resolved interface.
        Returns a dict indicating the start status.
        """
        # Pre‑check for existing capture under lock
        with self._lock:
            if self._sniffer_active():
                return {"status": "error", "error": "previous capture still running", "capture_mode": "passive"}
            if self._thread and getattr(self._thread, "is_alive", lambda: False)():
                return {"status": "error", "error": "previous legacy capture thread still running", "capture_mode": "passive"}
            if self._running:
                return {"status": "already_running", "interface": self._active_interface_name, "capture_mode": "passive"}
            try:
                device, display_name = resolve_capture_interface(interface)
            except Exception as err:
                self._last_error = f"{type(err).__name__}: {err}"
                return {"status": "error", "error": str(err), "capture_mode": "passive"}
            self._active_interface_device = device
            self._active_interface_name = display_name
            self._running = True
            self._last_error = None
            self._started_at = time()
            candidate_sniffer = AsyncSniffer(iface=device, filter="ip", prn=self._handle_packet, store=False)
            self._sniffer = candidate_sniffer
        # Start outside the lock
        try:
            candidate_sniffer.start()
        except Exception as sn_err:
            orig_error = f"SnifferError: {type(sn_err).__name__}: {sn_err}"
            # Attempt safe cleanup without hiding the original startup error
            try:
                if hasattr(candidate_sniffer, "stop"):
                    candidate_sniffer.stop()
                if hasattr(candidate_sniffer, "join"):
                    candidate_sniffer.join(timeout=2)
            except Exception as cleanup_err:
                orig_error += f" (cleanup error: {type(cleanup_err).__name__}: {cleanup_err})"
            with self._lock:
                self._running = False
                still_running = not self._sniffer_terminated(candidate_sniffer)
                if not still_running:
                    if self._sniffer is candidate_sniffer:
                        self._sniffer = None
                self._last_error = orig_error
            return {"status": "error", "error": str(sn_err), "capture_mode": "passive"}
        return {"status": "started", "interface": self._active_interface_name, "device": device, "capture_mode": "passive"}

    def stop(self):
        """Request capture stop and clean up resources.
        Returns a dict with status `stop_requested`.
        """
        with self._lock:
            self._running = False
            sniffer = self._sniffer
            legacy_thread = self._thread
        if sniffer:
            try:
                sniffer.stop()
                sniffer.join(timeout=5)
            except Exception as e:
                with self._lock:
                    self._last_error = f"SnifferStopError: {type(e).__name__}: {e}"
            finally:
                if self._sniffer_terminated(sniffer):
                    with self._lock:
                        if self._sniffer is sniffer:
                            self._sniffer = None
        if legacy_thread:
            if getattr(legacy_thread, "is_alive", lambda: False)():
                try:
                    legacy_thread.join(timeout=5)
                except Exception:
                    pass
            if not getattr(legacy_thread, "is_alive", lambda: False)():
                with self._lock:
                    if self._thread is legacy_thread:
                        self._thread = None
        return {"status": "stop_requested"}

    def status(self):
        with self._lock:
            return {
                "running": self._running,
                "interface": self._active_interface_name,
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
        return (sum((v - mean) ** 2 for v in values) / len(values)) ** 0.5

    @staticmethod
    def _activity_metrics(timestamps):
        """Approximate CICFlowMeter-style active periods in seconds.
        Uses a 2‑second idle gap and a 5‑second active‑period cap.
        When a flow has insufficient packet timestamps (< 2) to calculate an
        interval, active metrics are 0.0, matching the CICIDS2017 training convention.
        """
        if len(timestamps) < 2:
            return 0.0, 0.0
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
            expired = [k for k, f in self._flows.items() if now - f["last_seen"] > IDLE_TIMEOUT_SECONDS]
            for k in expired:
                del self._flows[k]
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
                    "packet_length_variance": (sum((x - mean_length) ** 2 for x in lengths) / len(lengths)) if lengths else 0.0,
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
                    "fwd_bwd_packet_ratio": (flow["forward_packets"] / flow["backward_packets"]) if flow["backward_packets"] else 0.0,
                    "fwd_bwd_byte_ratio": (flow["forward_bytes"] / flow["backward_bytes"]) if flow["backward_bytes"] else 0.0,
                    "fwd_bwd_avg_packet_length_ratio": (mean_fwd_length / mean_bwd_length) if mean_bwd_length else 0.0,
                    "forward_packet_percentage": (flow["forward_packets"] / total_packets) if total_packets else 0.0,
                    "forward_byte_percentage": (flow["forward_bytes"] / total_bytes) if total_bytes else 0.0,
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
                            "status": ("Monitoring" if predicted_class == 0 else "Potential Threat"),
                            "mode": "passive_live_flow",
                        }
                    except Exception as err:
                        result["feature_extraction_reason"] = f"Model prediction failed: {type(err).__name__}: {err}"
                results.append(result)
            return results

# Global monitor instance
live_flow_monitor = LiveFlowMonitor()
