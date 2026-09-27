"""Build a deterministic offline asset plan. Does not import or connect to Unreal."""
import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate(config):
    m = config["movement"]
    for name in ("max_speed", "acceleration", "gravity", "jump_velocity", "capsule_radius", "capsule_half_height"):
        if m[name] <= 0:
            raise ValueError(f"movement.{name} must be positive")
    if m["fall_gravity_multiplier"] < 1:
        raise ValueError("Falling gravity must be at least rising gravity")
    for name in ("coyote_seconds", "jump_buffer_seconds"):
        if not 0.10 <= m[name] <= 0.15:
            raise ValueError(f"{name} must be between 0.10 and 0.15")
    if not 0 < m["jump_release_velocity_multiplier"] < 1:
        raise ValueError("Jump release multiplier must be between 0 and 1")
    platforms = config["level"]["platforms"]
    if len({p["id"] for p in platforms}) != len(platforms):
        raise ValueError("Duplicate platform identifiers")
    if any(p["width"] <= 2 * m["capsule_radius"] for p in platforms):
        raise ValueError("Platform narrower than player")
    if not config["content_root"].startswith("/Game/Platformer"):
        raise ValueError("Assets must remain in the Platformer namespace")


def jump_range(m, height):
    apex = m["jump_velocity"] ** 2 / (2 * m["gravity"])
    if height > apex:
        return 0
    time = m["jump_velocity"] / m["gravity"] + math.sqrt(
        2 * (apex - height) / (m["gravity"] * m["fall_gravity_multiplier"]))
    return time * m["max_speed"]


def routes(config):
    level, m = config["level"], config["movement"]
    nodes = list(level["platforms"])
    bridge = level["moving_platform"]
    for name in ("start", "end"):
        x, _, z = bridge[name]
        nodes.append({"id": f"bridge_{name}", "x": x - bridge["width"] / 2,
                      "width": bridge["width"], "top": z})
    nodes.sort(key=lambda p: p["x"])
    result = []
    for a, b in zip(nodes, nodes[1:]):
        if a["id"] == "bridge_start" and b["id"] == "bridge_end":
            result.append({"from": a["id"], "to": b["id"], "method": "ride_platform"})
            continue
        gap = max(0, b["x"] - a["x"] - a["width"])
        # Conservative margin for takeoff/landing; not a collision simulation.
        required = gap + 2 * m["capsule_radius"]
        budget = 0.8 * jump_range(m, b["top"] - a["top"])
        result.append({"from": a["id"], "to": b["id"], "method": "jump",
                       "gap_cm": gap, "required_cm": required,
                       "safe_budget_cm": round(budget, 2), "passes": required <= budget})
    return result


def assets(config):
    groups = [
        ("01_foundation", "Components", ["BPC_Health", "BPI_Damageable", "BPC_Feedback"]),
        ("01_foundation", "Input", ["IA_Move", "IA_Jump", "IA_Attack", "IA_Interact", "IA_Pause", "IMC_Platformer"]),
        ("02_player", "Characters", ["BP_Player"]),
        ("02_player", "Blueprints", ["BP_SideCamera"]),
        ("02_player", "GameModes", ["BP_PlatformerGameMode", "BP_PlatformerController", "BP_PlatformerGameState"]),
        ("03_world", "Environment", ["BP_Platform", "BP_MovingPlatform", "BP_Hazard", "BP_KillZone", "BP_Checkpoint", "BP_Goal"]),
        ("03_world", "Pickups", ["BP_Coin"]),
        ("04_combat", "Enemies", ["BP_PatrolEnemy"]),
        ("05_ui", "UI", ["WBP_HUD", "WBP_Pause", "WBP_Death", "WBP_LevelComplete"]),
        ("06_level", "Levels", [config["level"]["name"]])
    ]
    return [{"phase": phase, "path": f"{config['content_root']}/{folder}/{name}",
             "on_existing": "inspect_before_change"}
            for phase, folder, names in groups for name in names]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "Config/platformer.json")
    parser.add_argument("--output", type=Path, default=ROOT / "Build/Preparation")
    parser.add_argument("--check", action="store_true", help="Validate without writing files")
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    validate(config)
    route = routes(config)
    failures = [r for r in route if r.get("passes") is False]
    if failures:
        raise ValueError(f"Unreachable planned transitions: {failures}")
    report = {"status": "offline_plan_not_engine_validated", "config": config,
              "assets": assets(config), "route_checks": route,
              "limitations": ["Assumes full horizontal speed and full held jump.",
                              "Moving platform timing, collisions and input require PIE testing.",
                              "Input labels are design data, not serialized Enhanced Input assets."]}
    if not args.check:
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / "platformer_plan.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"OK: {len(report['assets'])} planned assets; {len(route)} route transitions. Unreal not contacted.")


if __name__ == "__main__":
    main()
