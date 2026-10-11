"""Update only this prototype's owned visuals and validate its assets."""
import unreal

lib = unreal.EditorAssetLibrary
path = "/Game/Platformer/Levels/L_Platformer_Prototype"
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not level.load_level(path):
    raise RuntimeError("Prototype map missing")
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for actor in actors.get_all_level_actors():
    if isinstance(actor, unreal.ScintillaEnemy):
        pos = actor.get_actor_location()
        pos.z = 27
        actor.set_actor_location(pos, False, False)
    if isinstance(actor, unreal.ScintillaCity):
        for comp in actor.get_components_by_class(unreal.StaticMeshComponent):
            pos = comp.get_editor_property("relative_location")
            pos.y = -abs(pos.y)
            comp.set_relative_location(pos, False, False)
    if isinstance(actor, unreal.TextRenderActor) and actor.get_actor_label().startswith("Sign_"):
        pos = actor.get_actor_location()
        pos.y = 25
        actor.set_actor_location(pos, False, False)
        actor.set_actor_rotation(unreal.Rotator(0,90,0), False)
player_bp = lib.load_asset("/Game/Platformer/Characters/BP_Player")
player = unreal.get_default_object(player_bp.generated_class())
player.get_editor_property("eye").set_relative_location(unreal.Vector(8,17,12),False,False)
lib.save_loaded_asset(player_bp,False)
for data in unreal.AssetRegistryHelpers.get_asset_registry().get_assets_by_path("/Game/Platformer",True):
    asset = data.get_asset()
    if isinstance(asset, unreal.Blueprint):
        unreal.BlueprintEditorLibrary.compile_blueprint(asset)
        lib.save_loaded_asset(asset,False)
level.save_current_level()
lib.save_directory("/Game/Platformer",False,True)
print("SCINTILLA_FINALIZE_OK")
