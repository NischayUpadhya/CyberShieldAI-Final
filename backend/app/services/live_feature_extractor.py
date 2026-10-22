"""Validated live-flow feature extraction for CyberShield AI.

Maps only measurements currently exposed by the passive monitor.
Time-based CICFlowMeter-style fields are converted from seconds to
microseconds. Unsupported fields remain missing; predictions must not
run unless all 40 fields are present and semantically validated.
"""

from pathlib import Path
import math

import numpy as np


FEATURE_LIST_PATH = (
    Path(__file__).resolve().parents[2]
    / "ai"
    / "evaluation"
    / "Selected_Features.txt"
)


def load_feature_names():
    """Load the exact feature order used during model training."""
    if not FEATURE_LIST_PATH.exists():
        raise FileNotFoundError(f"Feature list not found: {FEATURE_LIST_PATH}")

    with open(FEATURE_LIST_PATH, "r", encoding="utf-8") as file:
        names = [line.strip() for line in file if line.strip()]

    if len(names) != 40:
        raise ValueError(f"Expected 40 selected features; found {len(names)}")
    if len(set(names)) != len(names):
        raise ValueError("Feature list contains duplicate names")
    return names


FEATURE_NAMES = load_feature_names()


def validate_feature_values(values):
    """Validate completeness, numeric type, finiteness, and training order."""
    missing = [name for name in FEATURE_NAMES if name not in values]
    if missing:
        return {
            "ready": False,
            "reason": "Missing required feature measurements",
            "missing_features": missing,
        }

    ordered = [values[name] for name in FEATURE_NAMES]
    for name, value in zip(FEATURE_NAMES, ordered):
        if isinstance(value, bool) or not isinstance(
            value, (int, float, np.integer, np.floating)
        ):
            return {
                "ready": False,
                "reason": f"Non-numeric feature: {name}",
                "missing_features": [],
            }
        if not math.isfinite(float(value)):
            return {
                "ready": False,
                "reason": f"Non-finite feature: {name}",
                "missing_features": [],
            }

    return {
        "ready": True,
        "feature_names": FEATURE_NAMES.copy(),
        "features": [float(value) for value in ordered],
        "feature_count": len(ordered),
    }


def extract_live_features(flow):
    """Build candidate features without fabricating unavailable measurements.

    Duration and IAT fields are converted from seconds to microseconds.
    TCP window values are deliberately not mapped to Init_Win_bytes_*:
    the first observed packet may be from the middle of an existing flow.
    Active/idle metrics are not available from the current monitor.
    """
    values = {}

    def copy_feature(feature_name, flow_key):
        value = flow.get(flow_key)
        if value is not None:
            values[feature_name] = value

    def seconds_to_microseconds(feature_name, flow_key):
        value = flow.get(flow_key)
        if value is not None:
            values[feature_name] = float(value) * 1_000_000.0

    # Measurements whose current definitions/units can be mapped.
    copy_feature("Destination Port", "destination_port")
    copy_feature("Bwd Header Length", "backward_header_length_total")
    copy_feature("Bwd Packets/s", "backward_packets_per_second")
    copy_feature("Fwd Packet Length Max", "forward_max_packet_length")
    copy_feature("Bwd Packet Length Max", "backward_max_packet_length")
    copy_feature("Packet Length Mean", "mean_packet_length")
    copy_feature("Total Length of Fwd Packets", "forward_bytes")
    copy_feature("Fwd Header Length", "forward_header_length_total")
    copy_feature("Flow Packets/s", "packets_per_second")
    copy_feature("Max Packet Length", "max_packet_length")
    copy_feature("act_data_pkt_fwd", "forward_data_packet_count")
    copy_feature("Total Fwd Packets", "forward_packets")
    copy_feature("Packet Length Variance", "packet_length_variance")
    copy_feature("Fwd_Byte_Percentage", "forward_byte_percentage")
    copy_feature("Fwd Packet Length Mean", "forward_mean_packet_length")
    copy_feature("Fwd_Bwd_Avg_Packet_Length_Ratio", "fwd_bwd_avg_packet_length_ratio")
    copy_feature("Fwd_Bwd_Packet_Ratio", "fwd_bwd_packet_ratio")
    copy_feature("Flow Bytes/s", "bytes_per_second")
    copy_feature("Fwd_Bwd_Byte_Ratio", "fwd_bwd_byte_ratio")
    copy_feature("PSH Flag Count", "psh_flag_count")
    copy_feature("Bwd Packet Length Min", "backward_min_packet_length")
    copy_feature("Fwd_Packet_Percentage", "forward_packet_percentage")
    copy_feature("Min Packet Length", "min_packet_length")
    copy_feature("ACK Flag Count", "ack_flag_count")

    # CICFlowMeter-style duration and IAT fields are conventionally in
    # microseconds, while this monitor reports elapsed time in seconds.
    seconds_to_microseconds("Flow Duration", "duration_seconds")
    seconds_to_microseconds("Flow IAT Std", "flow_iat_std_seconds")
    seconds_to_microseconds("Fwd IAT Mean", "forward_iat_mean_seconds")
    seconds_to_microseconds("Flow IAT Mean", "flow_iat_mean_seconds")
    seconds_to_microseconds("Flow IAT Max", "flow_iat_max_seconds")
    seconds_to_microseconds("Flow IAT Min", "flow_iat_min_seconds")
    seconds_to_microseconds("Fwd IAT Std", "forward_iat_std_seconds")
    seconds_to_microseconds("Fwd IAT Min", "forward_iat_min_seconds")
    seconds_to_microseconds("Bwd IAT Total", "backward_iat_total_seconds")
    seconds_to_microseconds("Bwd IAT Mean", "backward_iat_mean_seconds")
    seconds_to_microseconds("Bwd IAT Max", "backward_iat_max_seconds")
    seconds_to_microseconds("Bwd IAT Min", "backward_iat_min_seconds")

    # Window features are only populated by the monitor when the SYN / SYN-ACK
    # handshake packets were actually observed. Otherwise validation keeps them missing.
    copy_feature("Init_Win_bytes_forward", "initial_window_forward")
    copy_feature("Init_Win_bytes_backward", "initial_window_backward")
    seconds_to_microseconds("Active Min", "active_min_seconds")
    seconds_to_microseconds("Active Mean", "active_mean_seconds")

    return validate_feature_values(values)
