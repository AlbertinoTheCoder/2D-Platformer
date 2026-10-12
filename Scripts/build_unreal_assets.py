"""Run with Unreal's Python plugin after the Scintilla native module is compiled.

Creates only /Game/Platformer assets. Existing production assets are reused.
Pass --execute through UnrealEditor-Cmd using -ExecutePythonScript=<this file>.
"""
import json
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "Config/platformer.json").read_text(encoding="utf-8"))
BASE = "/Game/Platformer"
LIB = unreal.EditorAssetLibrary
TOOLS = unreal.AssetToolsHelpers.get_asset_tools()


def asset(folder, name, cls, factory):
    path = f"{BASE}/{folder}/{name}"
    if LIB.does_asset_exist(path):
        result = LIB.load_asset(path)
        if not isinstance(result, cls):
            raise RuntimeError(f"Conflicting asset type at {path}")
        return result
    LIB.make_directory(f"{BASE}/{folder}")
    result = TOOLS.create_asset(name, f"{BASE}/{folder}", cls, factory)
    if result is None:
        raise RuntimeError(f"Failed to create {path}")
    return result


def blueprint(folder, name, parent):
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", parent)
    bp = asset(folder, name, unreal.Blueprint, factory)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    LIB.save_loaded_asset(bp)
    return bp.generated_class()


def spawn(cls, position, label):
    actor = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_class(cls, unreal.Vector(*position))
    if actor is None:
        raise RuntimeError(f"Cannot spawn {label}")
    actor.set_actor_label(label)
    actor.set_folder_path("Scintilla")
    return actor


def material():
    mat = asset("Materials", "M_Color", unreal.Material, unreal.MaterialFactoryNew())
    # This graph is owned by this bootstrap script and is deliberately simple.
    unreal.MaterialEditingLibrary.delete_all_material_expressions(mat)
    mat.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    tint = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, -240, 0)
    tint.set_editor_property("parameter_name", "Tint")
    tint.set_editor_property("default_value", unreal.LinearColor(.1, .3, .5, 1))
    unreal.MaterialEditingLibrary.connect_material_property(tint, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    unreal.MaterialEditingLibrary.recompile_material(mat)
    LIB.save_loaded_asset(mat)
    colors = {"Steel": (.08, .17, .23), "Player": (.8, .48, .13), "Eye": (.05, 1, .85),
              "Hazard": (1, .08, .1), "Enemy": (.7, .1, .2), "Checkpoint": (.1, .3, .5),
              "Goal": (.5, .32, .09), "Dark": (.015, .025, .055), "Sky": (.006, .01, .025), "Window": (.06, .12, .16)}
    instances = {}
    for name, color in colors.items():
        mi = asset("Materials", f"MI_{name}", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        unreal.MaterialEditingLibrary.set_material_instance_parent(mi, mat)
        unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(mi, "Tint", unreal.LinearColor(*color, 1))
        LIB.save_loaded_asset(mi)
        instances[name] = mi
    return mat, instances


def input_assets():
    def input_key(name):
        key = unreal.Key()
        key.set_editor_property("key_name", name)
        return key
    actions = {}
    for name in CONFIG["input"]:
        ia = asset("Input", f"IA_{name}", unreal.InputAction, unreal.InputAction_Factory())
        ia.set_editor_property("value_type", unreal.InputActionValueType.AXIS1D if name == "Move" else unreal.InputActionValueType.BOOLEAN)
        if name == "Pause":
            ia.set_editor_property("trigger_when_paused", True)
        actions[name] = ia
        LIB.save_loaded_asset(ia)
    imc = asset("Input", "IMC_Platformer", unreal.InputMappingContext, unreal.InputMappingContext_Factory())
    imc.unmap_all()
    mappings = []
    for key in ("D", "Right", "Gamepad_LeftX"):
        mapping = imc.map_key(actions["Move"], input_key(key))
        if key == "Gamepad_LeftX":
            mapping.set_editor_property("modifiers", [unreal.InputModifierDeadZone(imc)])
        mappings.append(mapping)
    for key in ("A", "Left"):
        mapping = imc.map_key(actions["Move"], input_key(key))
        mapping.set_editor_property("modifiers", [unreal.InputModifierNegate(imc)])
        mappings.append(mapping)
    for name in ("Jump", "Attack", "Interact", "Pause"):
        for key in CONFIG["input"][name]["keys"]:
            mappings.append(imc.map_key(actions[name], input_key(key)))
    # UE 5.7+ reads DefaultKeyMappings; the deprecated mappings array is not
    # used at runtime and would silently lose the per-key modifiers above.
    mapping_data = imc.get_editor_property("default_key_mappings")
    mapping_data.set_editor_property("mappings", mappings)
    imc.set_editor_property("default_key_mappings", mapping_data)
    LIB.save_loaded_asset(imc)
    return actions, imc


def import_sounds():
    sounds = {}
    for source in sorted((ROOT / "Assets/Audio").glob("*.wav")):
        path = f"{BASE}/Audio/{source.stem}"
        if not LIB.does_asset_exist(path):
            task = unreal.AssetImportTask()
            task.set_editor_property("filename", str(source))
            task.set_editor_property("destination_path", f"{BASE}/Audio")
            task.set_editor_property("automated", True)
            task.set_editor_property("save", True)
            TOOLS.import_asset_tasks([task])
        sounds[source.stem] = LIB.load_asset(path)
    return sounds


def text(position, value, size=25, color=(.5,.75,.85)):
    actor = spawn(unreal.TextRenderActor, position, "Sign_" + value[:18])
    comp = actor.get_component_by_class(unreal.TextRenderComponent)
    comp.set_text(value)
    comp.set_world_size(size)
    comp.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER)
    comp.set_text_render_color(unreal.Color(*[int(c*255) for c in color], 255))
    actor.set_actor_rotation(unreal.Rotator(0,90,0), False)
    return actor


def main():
    for folder in ("Characters", "Enemies", "Levels", "Blueprints", "Components", "Sprites", "Tiles", "Materials", "UI", "Audio", "Pickups", "Environment", "GameModes", "Input"):
        LIB.make_directory(f"{BASE}/{folder}")
    mat, colors = material()
    actions, imc = input_assets()
    sounds = import_sounds()
    parents = {
        "BP_Player": ("Characters", unreal.ScintillaPlayer),
        "BP_SideCamera": ("Blueprints", unreal.ScintillaCamera),
        "BP_PlatformerController": ("GameModes", unreal.ScintillaController),
        "BP_PlatformerGameMode": ("GameModes", unreal.ScintillaGameMode),
        "BP_PlatformerGameState": ("GameModes", unreal.ScintillaGameState),
        "BP_Platform": ("Environment", unreal.ScintillaPlatform),
        "BP_MovingPlatform": ("Environment", unreal.ScintillaMovingPlatform),
        "BP_Hazard": ("Environment", unreal.ScintillaHazard),
        "BP_Checkpoint": ("Environment", unreal.ScintillaCheckpoint),
        "BP_Goal": ("Environment", unreal.ScintillaGoal),
        "BP_City": ("Environment", unreal.ScintillaCity),
        "BP_Coin": ("Pickups", unreal.ScintillaCoin),
        "BP_PatrolEnemy": ("Enemies", unreal.ScintillaEnemy),
    }
    classes = {name: blueprint(folder,name,parent) for name,(folder,parent) in parents.items()}
    # Native UMG widget remains replaceable by an editable Widget Blueprint.
    factory = unreal.WidgetBlueprintFactory()
    factory.set_editor_property("parent_class", unreal.ScintillaHUD)
    hud = asset("UI", "WBP_HUD", unreal.WidgetBlueprint, factory)
    unreal.BlueprintEditorLibrary.compile_blueprint(hud)
    LIB.save_loaded_asset(hud)
    cdo = unreal.get_default_object(classes["BP_Player"])
    cdo.get_editor_property("body").set_material(0, colors["Player"])
    cdo.get_editor_property("eye").set_material(0, colors["Eye"])
    for field,name in (("jump_sound","Jump"),("land_sound","Land"),("damage_sound","Damage")):
        cdo.set_editor_property(field,sounds.get("S_"+name))
    movement = cdo.get_component_by_class(unreal.CharacterMovementComponent)
    movement.set_editor_property("max_walk_speed", CONFIG["movement"]["max_speed"])
    movement.set_editor_property("jump_z_velocity", CONFIG["movement"]["jump_velocity"])
    pc = unreal.get_default_object(classes["BP_PlatformerController"])
    for name, ia in actions.items():
        pc.set_editor_property(name.lower()+"_action",ia)
    pc.set_editor_property("mapping_context",imc)
    pc.set_editor_property("hud_class",hud.generated_class())
    gm = unreal.get_default_object(classes["BP_PlatformerGameMode"])
    gm.set_editor_property("default_pawn_class",classes["BP_Player"])
    gm.set_editor_property("player_controller_class",classes["BP_PlatformerController"])
    gm.set_editor_property("game_state_class",classes["BP_PlatformerGameState"])
    for name,(folder,_) in parents.items():
        LIB.save_asset(f"{BASE}/{folder}/{name}",False)
    level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    path = f"{BASE}/Levels/{CONFIG['level']['name']}"
    if LIB.does_asset_exist(path):
        raise RuntimeError("Level already exists: refusing to replace existing map. Use a deliberate incremental update.")
    if not level.new_level(path):
        raise RuntimeError("Cannot create prototype level")
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    world.get_world_settings().set_editor_property("default_game_mode", classes["BP_PlatformerGameMode"])
    city = spawn(classes["BP_City"], (0,0,0), "City_BlackoutToWarm")
    city.set_editor_property("color_material",mat)
    city.build_city()
    for comp in city.get_components_by_class(unreal.StaticMeshComponent):
        comp.set_material(0,colors["Window" if comp.get_name().startswith("Window") else "Sky" if comp.get_name()=="Backdrop" else "Dark"])
    spawn(unreal.PlayerStart, CONFIG["level"]["spawn"], "PlayerStart_Scintilla")
    for p in CONFIG["level"]["platforms"]:
        actor = spawn(classes["BP_Platform"], (p["x"]+p["width"]/2,0,p["top"]-30), "Platform_"+p["id"])
        surface = actor.get_editor_property("surface")
        surface.set_world_scale3d(unreal.Vector(p["width"]/100,2,.6))
        surface.set_material(0,colors["Steel"])
    bridge = CONFIG["level"]["moving_platform"]
    pos = list(bridge["start"]); pos[2] -= 15
    actor = spawn(classes["BP_MovingPlatform"],pos,"MovingPlatform_ServiceLift")
    actor.set_editor_property("end_offset",unreal.Vector(*[b-a for a,b in zip(bridge["start"],bridge["end"])]))
    actor.set_editor_property("speed",bridge["speed"])
    actor.set_editor_property("wait_seconds",bridge["wait_seconds"])
    actor.get_editor_property("surface").set_world_scale3d(unreal.Vector(bridge["width"]/100,1.5,.3))
    actor.get_editor_property("surface").set_material(0,colors["Eye"])
    for i,pos in enumerate(CONFIG["level"]["collectibles"]):
        coin = spawn(classes["BP_Coin"],pos,f"Energy_{i:02}")
        coin.get_editor_property("visual").set_material(0,colors["Eye"])
        coin.set_editor_property("collect_sound",sounds.get("S_Energy"))
    for i,pos in enumerate(CONFIG["level"]["checkpoints"]):
        checkpoint = spawn(classes["BP_Checkpoint"],pos,f"MaintenanceStation_{i}")
        checkpoint.get_editor_property("visual").set_material(0,colors["Checkpoint"])
        checkpoint.set_editor_property("activate_sound",sounds.get("S_Checkpoint"))
    for p in CONFIG["level"]["hazards"]:
        hazard = spawn(classes["BP_Hazard"],p["position"],"ExposedCable_"+p["id"])
        hazard.get_editor_property("visual").set_material(0,colors["Hazard"])
    kill = spawn(classes["BP_Hazard"], CONFIG["level"]["kill_zone"]["center"], "KillZone")
    kill.set_editor_property("instant_kill",True)
    kill.get_editor_property("trigger").set_box_extent(unreal.Vector(*CONFIG["level"]["kill_zone"]["extent"]))
    kill.get_editor_property("visual").set_visibility(False)
    for e in CONFIG["level"]["enemies"]:
        pos = list(e["position"]); pos[2]=27
        enemy = spawn(classes["BP_PatrolEnemy"],pos,"Drone_"+e["id"])
        enemy.set_editor_property("patrol_min_x",e["patrol_min_x"])
        enemy.set_editor_property("patrol_max_x",e["patrol_max_x"])
        enemy.get_editor_property("visual").set_material(0,colors["Enemy"])
        enemy.set_editor_property("death_sound",sounds.get("S_EnemyDeath"))
    goal = spawn(classes["BP_Goal"],CONFIG["level"]["goal"],"Generator_RestoreCity")
    goal.get_editor_property("visual").set_material(0,colors["Goal"])
    goal.set_editor_property("complete_sound",sounds.get("S_Complete"))
    text((380,-25,230),"SCINTILLA",46,(.1,1,.85))
    text((420,-25,160),"WORKSHOP 07 / BLACKOUT",19)
    text((3900,-25,250),"MAINTENANCE STATION",20)
    text((7280,-25,350),"RESTORE POWER TO THE CITY",26,(1,.65,.2))
    unreal.get_editor_subsystem(unreal.EditorActorSubsystem).set_selected_level_actors([])
    if not level.save_current_level():
        raise RuntimeError("Could not save level")
    LIB.save_directory(BASE,False,True)
    print("SCINTILLA_BOOTSTRAP_OK")


main()
