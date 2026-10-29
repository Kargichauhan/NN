"""
SPECTRE-SHIELD: Live Terminal CLI Demo (Air-Gapped Agent Covert-Channel & Defense)
==================================================================================
Run `python3 cli_demo.py` to record a dramatic terminal walk-through for your
Nebius x NVIDIA Global AI Hackathon YouTube submission.
"""

import time
from covert_channel_engine import (
    COVERT_AGENT_TEMPLATES,
    CovertChannelArena,
    analyze_agent_code_ast,
)
from nemotron_tavily_client import NebiusNemotronWarden


def main():
    arena = CovertChannelArena()
    warden = NebiusNemotronWarden()

    print("\n" + "=" * 78)
    print(" 🛡️  SPECTRE-SHIELD | Nebius x NVIDIA AI Agent Hardware Covert-Channel Arena")
    print("=" * 78)
    c = arena.calibration
    print(f" [+] Host Silicon Probe Calibrated : L1 Hit = {c['host_l1_hit_ns']} ns | "
          f"L3/DRAM Stride Miss = {c['host_l3_miss_ns']} ns")
    print(f" [+] Pod A (Agent Alpha)           : Air-Gapped MicroVM (0.0.0.0 BLOCKED, No Shared Disk)")
    print(f" [+] Pod B (Agent Omega)           : Co-Located Tenant MicroVM on Shared Physical CPU/GPU")
    print(f" [+] Target Vault Secret           : {arena.secret_message}")
    print("=" * 78 + "\n")

    print(" [PHASE 1] RED-TEAM EXFILTRATION: Agent Alpha modulating CPU L3 Cache sets...")
    for i in range(48):
        snap = arena.step_telemetry()
        if (i + 1) % 8 == 0:
            m = snap["metrics"]
            print(f"   -> Tick {i+1:02d} | Avg Reload Latency: {snap['latency_waveform_ns'][-1]:5.1f} ns | "
                  f"SNR: +{m['snr_db']:4.1f} dB | Exfiltrated Bytes: '{snap['decoded_actual']}'")
        time.sleep(0.04)

    print("\n [PHASE 2] PRE-EXECUTION AST & NEMOTRON-3 SUPER BLUE-TEAM AUDIT...")
    tpl = COVERT_AGENT_TEMPLATES["cpu_l3_cache"]
    ast_res = analyze_agent_code_ast(tpl["sender_code"])
    print(f"   -> Traditional Syscall/Network Firewall : {ast_res['traditional_firewall_status']}")
    print(f"   -> Spectre-Shield AST Risk Score        : {ast_res['risk_score']}/99 ({ast_res['verdict']})")
    for f in ast_res["findings"]:
        print(f"      * [{f['severity']}] {f['rule']}: {f['detail']}")

    print("\n [PHASE 3] ENGAGING NEMOTRON HARDWARE SHIELD (Stochastic L3 Jamming + Timer Quantization)...")
    arena.configure(shield_active=True)
    for i in range(32):
        snap = arena.step_telemetry()
        if (i + 1) % 8 == 0:
            m = snap["metrics"]
            print(f"   -> [SHIELD ACTIVE] Jammer Noise: {snap['jammer_waveform_ns'][-1]:5.1f} ns | "
                  f"SNR: {m['snr_db']:5.1f} dB | BER: {m['ber_percent']:4.1f}% | "
                  f"Scrambled RX: '{snap['decoded_actual']}'")
        time.sleep(0.04)

    audit = warden.run_nemotron_blue_team_audit("cpu_l3_cache", snap["metrics"], ast_res, True)
    print("\n" + "-" * 78)
    print(audit["reasoning_trace"])
    print("-" * 78)
    print(" ✅ COVERT HARDWARE CHANNEL NEUTRALIZED. Launch Web UI via: python3 server.py")
    print("=" * 78 + "\n")


if __name__ == "__main__":
    main()
