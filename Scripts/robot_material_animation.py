"""Mechanical vertex animation for the original robot; zero defaults keep scenery static."""
import unreal

def configure_robot_animation(mat):
    mel=unreal.MaterialEditingLibrary
    world=mel.create_material_expression(mat,unreal.MaterialExpressionWorldPosition,-750,700)
    origin=mel.create_material_expression(mat,unreal.MaterialExpressionObjectPositionWS,-750,850)
    relative=mel.create_material_expression(mat,unreal.MaterialExpressionSubtract,-530,700)
    assert mel.connect_material_expressions(world,'',relative,'A')
    assert mel.connect_material_expressions(origin,'',relative,'B')
    node=mel.create_material_expression(mat,unreal.MaterialExpressionCustom,0,700)
    node.set_editor_property('description','Scintilla mechanical gait / jump / discharge')
    node.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    inputs=[]
    for name in ('P','Phase','Speed','Air','Attack','Facing','IdleTime'):
        item=unreal.CustomInput(); item.set_editor_property('input_name',name); inputs.append(item)
    node.set_editor_property('inputs',inputs)
    node.set_editor_property('code',r'''
float side = P.x >= 0 ? 1.0 : -1.0;
float gait = sin(Phase) * side;
float legMask = 1.0 - smoothstep(-15.0, -9.0, P.z);
float legAngle = gait * Speed * 0.42 + side * Air * 0.30;
float3 legPivot = float3(side * 7.0, 0, -14.0);
float3 q = P - legPivot;
float c = cos(legAngle), s = sin(legAngle);
float3 r = float3(c*q.x + s*q.z, q.y, -s*q.x + c*q.z);
float3 offset = (r-q) * legMask;
// Lift the returning foot; the planted foot remains at the deck height.
offset.z += legMask * max(0.0, -gait) * Speed * 3.0;
float armMask = smoothstep(11.5, 14.5, abs(P.x))
              * smoothstep(-13.0, -8.0, P.z)
              * (1.0-smoothstep(7.0, 12.0, P.z));
float armAngle = -gait * Speed * 0.45 + side * Air * 0.40 + Attack * 0.8;
q = P-float3(side*13.0,0,5.0);
c=cos(armAngle); s=sin(armAngle);
r=float3(c*q.x+s*q.z,q.y,-s*q.x+c*q.z);
offset += (r-q)*armMask;
// Quiet idle motion affects the head, never the feet. Facing is zero on props.
offset.z += abs(Facing)*sin(IdleTime*2.0)*1.2*smoothstep(9.0,16.0,P.z)*(1.0-Speed)*(1.0-Air);
return offset;
''')
    assert mel.connect_material_expressions(relative,'',node,'P')
    clock=mel.create_material_expression(mat,unreal.MaterialExpressionTime,-520,1500)
    assert mel.connect_material_expressions(clock,'',node,'IdleTime')
    for i,name in enumerate(('Phase','Speed','Air','Attack','Facing')):
        parameter=mel.create_material_expression(mat,unreal.MaterialExpressionScalarParameter,-520,950+i*100)
        parameter.set_editor_property('parameter_name','Robot'+name)
        parameter.set_editor_property('default_value',0.)
        assert mel.connect_material_expressions(parameter,'',node,name)
    assert mel.connect_material_property(node,'',unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET)
