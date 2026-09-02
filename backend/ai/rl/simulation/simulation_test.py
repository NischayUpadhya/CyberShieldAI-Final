"""
CyberShield AI - Simulation Testing

1. Exhaustive evaluation:
   Tests all 10 scenarios against all 5 defense actions = 50 tests.

2. Recommended policy evaluation:
   Tests the selected defense action for each scenario = 10 tests.
"""

import csv
from pathlib import Path

from ai.rl.simulation.threat_scenarios import (
    ThreatScenarioLibrary,
)

from ai.rl.simulation.defense_executor import (
    DefenseExecutor,
)


# =============================================================================
# Output
# =============================================================================

OUTPUT_DIR = Path("backend/ai/evaluation")

OUTPUT_FILE = (
    OUTPUT_DIR / "Simulation_Test_Results.csv"
)

POLICY_OUTPUT_FILE = (
    OUTPUT_DIR / "Recommended_Policy_Results.csv"
)


# =============================================================================
# Recommended Defense Policy
# =============================================================================

RECOMMENDED_ACTIONS = {

    "Benign Traffic": 0,          # MONITOR

    "DDoS - High": 3,              # BLOCK

    "DDoS - Critical": 4,          # ISOLATE

    "DoS - High": 3,               # BLOCK

    "Port Scan - Medium": 1,       # ALERT

    "Bot Attack - High": 2,        # RATE_LIMIT

    "Brute Force - High": 2,       # RATE_LIMIT

    "SQL Injection - Critical": 3, # BLOCK

    "Infiltration - Critical": 4,  # ISOLATE

    "Heartbleed - Critical": 3,    # BLOCK
}


# =============================================================================
# Main Simulation
# =============================================================================

def run_simulation_tests():

    library = ThreatScenarioLibrary()

    executor = DefenseExecutor()

    scenarios = library.get_all()

    results = []

    print()
    print("=" * 90)
    print("CYBERSHIELD AI - SIMULATION TESTING")
    print("=" * 90)

    print()
    print(f"Scenarios : {len(scenarios)}")
    print("Actions   : 5")
    print(
        f"Total Tests: {len(scenarios) * 5}"
    )

    # =========================================================================
    # 1. EXHAUSTIVE 50-TEST EVALUATION
    # =========================================================================

    print()
    print("=" * 90)
    print("EXHAUSTIVE DEFENSE ACTION EVALUATION")
    print("=" * 90)

    for scenario in scenarios:

        is_benign = (
            scenario.attack_type == 0
        )

        print()
        print("-" * 90)

        print(
            f"Scenario: {scenario.name}"
        )

        print(
            f"Severity: {scenario.severity.value}"
        )

        for action in range(5):

            result = executor.execute(

                action=action,

                threat_severity=(
                    scenario.attack_frequency
                ),

                packet_rate=(
                    scenario.packet_rate
                ),

                byte_rate=(
                    scenario.byte_rate
                ),

                is_benign=is_benign,
            )

            results.append({

                "scenario": (
                    scenario.name
                ),

                "attack_type": (
                    scenario.attack_type
                ),

                "severity": (
                    scenario.severity.value
                ),

                "action": (
                    result.action_name
                ),

                "successful": (
                    result.successful
                ),

                "threat_reduction": (
                    result.threat_reduction
                ),

                "traffic_reduction": (
                    result.traffic_reduction
                ),

                "legitimate_traffic_impact": (
                    result.legitimate_traffic_impact
                ),

                "resource_cost": (
                    result.resource_cost
                ),

                "response_effectiveness": (
                    result.response_effectiveness
                ),
            })

            print(

                f"{result.action_name:12} | "

                f"Threat Reduction: "
                f"{result.threat_reduction:.3f} | "

                f"Traffic Reduction: "
                f"{result.traffic_reduction:.3f} | "

                f"Legitimate Impact: "
                f"{result.legitimate_traffic_impact:.3f} | "

                f"Cost: "
                f"{result.resource_cost:.3f} | "

                f"Success: "
                f"{result.successful}"
            )

    # =========================================================================
    # Save Exhaustive Results
    # =========================================================================

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [

        "scenario",
        "attack_type",
        "severity",
        "action",
        "successful",
        "threat_reduction",
        "traffic_reduction",
        "legitimate_traffic_impact",
        "resource_cost",
        "response_effectiveness",
    ]

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(results)

    # =========================================================================
    # Exhaustive Metrics
    # =========================================================================

    attack_results = [

        result

        for result in results

        if result["attack_type"] != 0
    ]

    benign_results = [

        result

        for result in results

        if result["attack_type"] == 0
    ]

    successful_attack_responses = sum(

        1

        for result in attack_results

        if result["successful"]
    )

    attack_success_rate = (

        successful_attack_responses
        / len(attack_results)

        if attack_results

        else 0.0
    )

    avg_threat_reduction = (

        sum(
            result["threat_reduction"]
            for result in attack_results
        )

        / len(attack_results)

        if attack_results

        else 0.0
    )

    avg_traffic_reduction = (

        sum(
            result["traffic_reduction"]
            for result in attack_results
        )

        / len(attack_results)

        if attack_results

        else 0.0
    )

    avg_legitimate_impact = (

        sum(
            result["legitimate_traffic_impact"]
            for result in benign_results
        )

        / len(benign_results)

        if benign_results

        else 0.0
    )

    avg_resource_cost = (

        sum(
            result["resource_cost"]
            for result in results
        )

        / len(results)

        if results

        else 0.0
    )

    # =========================================================================
    # Exhaustive Summary
    # =========================================================================

    print()
    print("=" * 90)
    print("EXHAUSTIVE SIMULATION SUMMARY")
    print("=" * 90)

    print(
        f"Total tests                 : "
        f"{len(results)}"
    )

    print(
        f"Attack response success rate: "
        f"{attack_success_rate:.3f}"
    )

    print(
        f"Average threat reduction    : "
        f"{avg_threat_reduction:.3f}"
    )

    print(
        f"Average traffic reduction   : "
        f"{avg_traffic_reduction:.3f}"
    )

    print(
        f"Average benign traffic impact: "
        f"{avg_legitimate_impact:.3f}"
    )

    print(
        f"Average resource cost       : "
        f"{avg_resource_cost:.3f}"
    )

    print()
    print(
        f"Results saved to: "
        f"{OUTPUT_FILE}"
    )

    # =========================================================================
    # 2. RECOMMENDED POLICY EVALUATION
    # =========================================================================

    print()
    print("=" * 90)
    print("RECOMMENDED DEFENSE POLICY EVALUATION")
    print("=" * 90)

    policy_results = []

    for scenario in scenarios:

        is_benign = (
            scenario.attack_type == 0
        )

        action = RECOMMENDED_ACTIONS.get(

            scenario.name,

            0
        )

        result = executor.execute(

            action=action,

            threat_severity=(
                scenario.attack_frequency
            ),

            packet_rate=(
                scenario.packet_rate
            ),

            byte_rate=(
                scenario.byte_rate
            ),

            is_benign=is_benign,
        )

        policy_results.append({

            "scenario": (
                scenario.name
            ),

            "attack_type": (
                scenario.attack_type
            ),

            "severity": (
                scenario.severity.value
            ),

            "action": (
                result.action_name
            ),

            "successful": (
                result.successful
            ),

            "threat_reduction": (
                result.threat_reduction
            ),

            "traffic_reduction": (
                result.traffic_reduction
            ),

            "legitimate_traffic_impact": (
                result.legitimate_traffic_impact
            ),

            "resource_cost": (
                result.resource_cost
            ),

            "response_effectiveness": (
                result.response_effectiveness
            ),
        })

        print()

        print(
            f"{scenario.name:30} | "
            f"{result.action_name:12} | "
            f"Threat Reduction: "
            f"{result.threat_reduction:.3f} | "
            f"Traffic Reduction: "
            f"{result.traffic_reduction:.3f} | "
            f"Legitimate Impact: "
            f"{result.legitimate_traffic_impact:.3f} | "
            f"Cost: "
            f"{result.resource_cost:.3f} | "
            f"Success: "
            f"{result.successful}"
        )

    # =========================================================================
    # Save Policy Results
    # =========================================================================

    with open(
        POLICY_OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(policy_results)

    # =========================================================================
    # Policy Metrics
    # =========================================================================

    policy_attack_results = [

        result

        for result in policy_results

        if result["attack_type"] != 0
    ]

    policy_benign_results = [

        result

        for result in policy_results

        if result["attack_type"] == 0
    ]

    policy_success_rate = (

        sum(
            1
            for result in policy_attack_results
            if result["successful"]
        )

        / len(policy_attack_results)

        if policy_attack_results

        else 0.0
    )

    policy_threat_reduction = (

        sum(
            result["threat_reduction"]
            for result in policy_attack_results
        )

        / len(policy_attack_results)

        if policy_attack_results

        else 0.0
    )

    policy_traffic_reduction = (

        sum(
            result["traffic_reduction"]
            for result in policy_attack_results
        )

        / len(policy_attack_results)

        if policy_attack_results

        else 0.0
    )

    policy_benign_impact = (

        sum(
            result["legitimate_traffic_impact"]
            for result in policy_benign_results
        )

        / len(policy_benign_results)

        if policy_benign_results

        else 0.0
    )

    policy_resource_cost = (

        sum(
            result["resource_cost"]
            for result in policy_results
        )

        / len(policy_results)

        if policy_results

        else 0.0
    )

    # =========================================================================
    # Policy Summary
    # =========================================================================

    print()
    print("=" * 90)
    print("RECOMMENDED POLICY SUMMARY")
    print("=" * 90)

    print(
        f"Policy tests                 : "
        f"{len(policy_results)}"
    )

    print(
        f"Attack response success rate: "
        f"{policy_success_rate:.3f}"
    )

    print(
        f"Average threat reduction    : "
        f"{policy_threat_reduction:.3f}"
    )

    print(
        f"Average traffic reduction   : "
        f"{policy_traffic_reduction:.3f}"
    )

    print(
        f"Average benign traffic impact: "
        f"{policy_benign_impact:.3f}"
    )

    print(
        f"Average resource cost       : "
        f"{policy_resource_cost:.3f}"
    )

    print()
    print(
        f"Policy results saved to: "
        f"{POLICY_OUTPUT_FILE}"
    )

    print("=" * 90)


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":

    run_simulation_tests()