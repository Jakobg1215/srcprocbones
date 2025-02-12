
import bpy
from sys import float_info
from math import degrees, radians, acos, pi, sin, atan2, cos
from mathutils import Euler, Matrix, Vector, Quaternion

bl_info = {
    "name": "Source Engine Procedural Bones",
    "category": "Animation",
    "description": "A panel that helps create procedural bones for source engine models.",
    "author": "Jakobg1215",
    "version": (2, 1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Src Proc Bones",
    "tracker_url": "https://github.com/Jakobg1215/srcprocbones/issues",
}

# region Properties


class QuaternionProceduralTriggerProperty(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default="New Trigger", name="Name", description="The name of the trigger")
    weight: bpy.props.FloatProperty()
    tolerance: bpy.props.FloatProperty(default=radians(90.0), precision=6, soft_min=0.0, unit="ROTATION",
                                       description="The angle cone the control bone angle to the angle trigger to activate the trigger")
    trigger_angle: bpy.props.FloatVectorProperty(precision=6, unit="ROTATION", name="Trigger Angle",
                                                 description="The angle the control bone should be at to activate the trigger")
    target_angle: bpy.props.FloatVectorProperty(precision=6, unit="ROTATION", name="Target Angle",
                                                description="The angle the target bone will be set to when the trigger is active")
    target_position: bpy.props.FloatVectorProperty(precision=6, name="Target Position", description="The added offset position when the trigger is active")


class QuaternionProceduralProperty(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default="New Quaternion Procedural", name="Name", description="The name of the quaternion procedural")
    target_bone: bpy.props.StringProperty(name="Target Bone", description="The bone that will be procedurally animated")
    control_bone: bpy.props.StringProperty(name="Control Bone", description="The bone that will drive the target bone")
    override_position: bpy.props.BoolProperty(default=False, description="Allows to override the position of the target bone")
    position_override: bpy.props.FloatVectorProperty(precision=6, name="Position", description="The offset position of the target bone's parent")
    distance: bpy.props.FloatProperty(soft_min=0.0, soft_max=100.0,
                                      description="The percentage of the control bone's position offset from its parent added to the target bone's position")
    triggers: bpy.props.CollectionProperty(type=QuaternionProceduralTriggerProperty)
    active_trigger: bpy.props.IntProperty(name="Active Trigger")
    preview: bpy.props.BoolProperty()


class JiggleProceduralProperty(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default="New Jiggle Procedural", name="Name", description="The name of the jiggle procedural")
    target_bone: bpy.props.StringProperty(name="Target Bone", description="The bone that will be procedurally animated")
    tip_flex_type: bpy.props.EnumProperty(items=[("NONE", "None", ""), ("RIGID", "Rigid", ""), ("FLEXIBLE", "Flexible", "")],
                                          default="FLEXIBLE", name="Tip Flex Type", description="The rotational type of the jiggle procedural")
    length: bpy.props.FloatProperty(soft_min=0.0, default=10.0, name="Length", description="The length of jiggle procedural")
    tip_mass: bpy.props.FloatProperty(soft_min=0.0, name="Tip Mass", description="The weight of tip of jiggle procedural")
    yaw_stiffness: bpy.props.FloatProperty(soft_min=0.0, soft_max=1000.0, default=100.0, name="Yaw Stiffness", description="")
    yaw_damping: bpy.props.FloatProperty(soft_min=0.0, soft_max=1000.0, name="Yaw Damping", description="")
    pitch_stiffness: bpy.props.FloatProperty(soft_min=0.0, soft_max=1000.0, default=100.0, name="Pitch Stiffness", description="")
    pitch_damping: bpy.props.FloatProperty(soft_min=0.0, soft_max=1000.0, name="Pitch Damping", description="")
    along_constraint: bpy.props.EnumProperty(items=[("NONE", "None", ""), ("CONSTRAINT", "Constraint", "")],
                                             default="CONSTRAINT", name="Along Constraint", description="")
    along_stiffness: bpy.props.FloatProperty(soft_min=0.0, soft_max=1000.0, default=100.0, name="Pitch Stiffness", description="")
    along_damping: bpy.props.FloatProperty(soft_min=0.0, soft_max=1000.0, name="Pitch Damping", description="")
    angle_constraint: bpy.props.EnumProperty(items=[("NONE", "None", ""), ("CONSTRAINT", "Constraint", "")], name="Angle Constraint", description="")
    angle_limit: bpy.props.FloatProperty(soft_min=0.0, unit="ROTATION", name="Angle Limit", description="")
    yaw_constraint: bpy.props.EnumProperty(items=[("NONE", "None", ""), ("CONSTRAINT", "Constraint", "")], name="Yaw Constraint", description="")
    yaw_minimum: bpy.props.FloatProperty(soft_max=0.0, unit="ROTATION", name="Yaw Minimum", description="")
    yaw_maximum: bpy.props.FloatProperty(soft_min=0.0, unit="ROTATION", name="Yaw Maximum", description="")
    pitch_constraint: bpy.props.EnumProperty(items=[("NONE", "None", ""), ("CONSTRAINT", "Constraint", "")], name="Pitch Constraint", description="")
    pitch_minimum: bpy.props.FloatProperty(soft_max=0.0, unit="ROTATION", name="Pitch Minimum", description="")
    pitch_maximum: bpy.props.FloatProperty(soft_min=0.0, unit="ROTATION", name="Pitch Maximum", description="")
    base_flex_type: bpy.props.EnumProperty(items=[("NONE", "None", ""), ("SPRING", "Spring", ""),
                                           ("BOING", "Boing", "")], name="Base Flex Type", description="")
    base_mass: bpy.props.FloatProperty(name="Base Mass", description="")
    base_stiffness: bpy.props.FloatProperty(soft_min=0.0, soft_max=1000.0, default=100.0, name="Base Stiffness", description="")
    base_damping: bpy.props.FloatProperty(soft_min=0.0, soft_max=1000.0, name="Base Damping", description="")
    base_minimum_left: bpy.props.FloatProperty(soft_max=0.0, default=-100.0, name="Base Minimum Left", description="")
    base_maximum_left: bpy.props.FloatProperty(soft_min=0.0, default=100.0, name="Base Maximum Left", description="")
    base_friction_left: bpy.props.FloatProperty(soft_min=0.0, name="Base Friction Left", description="")
    base_minimum_up: bpy.props.FloatProperty(soft_max=0.0, default=-100.0, name="Base Minimum Up", description="")
    base_maximum_up: bpy.props.FloatProperty(soft_min=0.0, default=100.0, name="Base Maximum Up", description="")
    base_friction_up: bpy.props.FloatProperty(soft_min=0.0, name="Base Friction Up", description="")
    base_minimum_forward: bpy.props.FloatProperty(soft_max=0.0, default=-100.0, name="Base Minimum Forward", description="")
    base_maximum_forward: bpy.props.FloatProperty(soft_min=0.0, default=100.0, name="Base Minimum Forward", description="")
    base_friction_forward: bpy.props.FloatProperty(soft_min=0.0, name="Base Friction Forward", description="")
    boing_impact_speed: bpy.props.FloatProperty(soft_min=0.0, default=100.0, name="Boing Impact Speed", description="")
    boing_impact_angle: bpy.props.FloatProperty(soft_min=0.0, unit="ROTATION", default=radians(45.0), name="Boing Impact Angle", description="")
    boing_damping_rate: bpy.props.FloatProperty(soft_min=0.0, default=0.25, name="Boing Damping Rate", description="")
    boing_frequency: bpy.props.FloatProperty(soft_min=0.0, default=30.0, name="Boing Frequency", description="")
    boing_amplitude: bpy.props.FloatProperty(soft_min=0.0, default=0.35, name="Boing Amplitude", description="")
    preview: bpy.props.BoolProperty()


class SourceProceduralBoneDataProperty(bpy.types.PropertyGroup):
    quaternion_procedurals: bpy.props.CollectionProperty(type=QuaternionProceduralProperty)
    active_quaternion_procedural: bpy.props.IntProperty(name="Active Quaternion Procedural")
    jiggle_procedurals: bpy.props.CollectionProperty(type=JiggleProceduralProperty)
    active_jiggle_procedural: bpy.props.IntProperty(name="Active Jiggle Procedural")

# endregion


def matrix_transpose(matrix):
    translation = Vector((matrix[0][3], matrix[1][3], matrix[2][3]))
    row_x = Vector((matrix[0][0], matrix[1][0], matrix[2][0]))
    row_y = Vector((matrix[0][1], matrix[1][1], matrix[2][1]))
    row_z = Vector((matrix[0][2], matrix[1][2], matrix[2][2]))

    return Matrix(([matrix[0][0], matrix[1][0], matrix[2][0], -translation.dot(row_x)],
                   [matrix[0][1], matrix[1][1], matrix[2][1], -translation.dot(row_y)],
                   [matrix[0][2], matrix[1][2], matrix[2][2], -translation.dot(row_z)],
                   [matrix[0][3], matrix[1][3], matrix[2][3], matrix[3][3]]))


# region Quaternion Procedural Operators


class AddQuaternionProceduralOperator(bpy.types.Operator):
    bl_idname = "source_procedural.quaternion_add"
    bl_label = "Add Quaternion Procedural"
    bl_description = "Adds a new quaternion procedural"

    def execute(self, context):
        source_procedural_bone_data = context.object.source_procedural_bone_data

        source_procedural_bone_data.quaternion_procedurals.add()
        source_procedural_bone_data.active_quaternion_procedural = len(source_procedural_bone_data.quaternion_procedurals) - 1

        return {"FINISHED"}


class RemoveQuaternionProceduralOperator(bpy.types.Operator):
    bl_idname = "source_procedural.quaternion_remove"
    bl_label = "Remove Quaternion Procedural"
    bl_description = "Removes the selected quaternion procedural"

    @classmethod
    def poll(cls, context):
        source_procedural_bone_data = context.object.source_procedural_bone_data

        return len(source_procedural_bone_data.quaternion_procedurals) != 0

    def execute(self, context):
        source_procedural_bone_data = context.object.source_procedural_bone_data
        active_quaternion_procedural = source_procedural_bone_data.quaternion_procedurals[source_procedural_bone_data.active_quaternion_procedural]

        active_quaternion_procedural.preview = False
        source_procedural_bone_data.quaternion_procedurals.remove(source_procedural_bone_data.active_quaternion_procedural)

        if source_procedural_bone_data.active_quaternion_procedural > 0:
            source_procedural_bone_data.active_quaternion_procedural -= 1

        return {"FINISHED"}


class PreviewQuaternionProceduralOperator(bpy.types.Operator):
    bl_idname = "source_procedural.quaternion_preview"
    bl_label = "Preview Quaternion Procedural"
    bl_description = "Previews the selected quaternion procedural"

    def __init__(self):
        self.active_quaternion_procedural = None
        self.timer = None

    @classmethod
    def poll(cls, context):
        source_procedural_bone_data = context.object.source_procedural_bone_data
        active_quaternion_procedural = source_procedural_bone_data.quaternion_procedurals[source_procedural_bone_data.active_quaternion_procedural]

        return len(active_quaternion_procedural.triggers) > 0

    def execute(self, context):
        source_procedural_bone_data = context.object.source_procedural_bone_data
        active_quaternion_procedural = source_procedural_bone_data.quaternion_procedurals[source_procedural_bone_data.active_quaternion_procedural]

        if not active_quaternion_procedural.preview:
            active_quaternion_procedural.preview = True
            self.active_quaternion_procedural = active_quaternion_procedural
            self.timer = context.window_manager.event_timer_add(1.0 / context.scene.render.fps, window=context.window)
            context.window_manager.modal_handler_add(self)
            return {"RUNNING_MODAL"}

        active_quaternion_procedural.preview = False
        self.cancel(context)

        return {"FINISHED"}

    def modal(self, context, event):
        if event.type != "TIMER":
            return {"PASS_THROUGH"}

        if context.object is None or context.object.type != "ARMATURE":
            self.cancel(context)
            return {"FINISHED"}

        active_quaternion_procedural = self.active_quaternion_procedural

        if not active_quaternion_procedural.preview:
            self.cancel(context)
            return {"FINISHED"}

        if len(active_quaternion_procedural.triggers) == 0:
            self.cancel(context)
            return {"FINISHED"}

        target_bone = context.object.pose.bones.get(active_quaternion_procedural.target_bone)
        if target_bone is None:
            self.cancel(context)
            return {"FINISHED"}
        control_bone = context.object.pose.bones.get(active_quaternion_procedural.control_bone)
        if control_bone is None:
            self.cancel(context)
            return {"FINISHED"}

        if target_bone is None or control_bone is None:
            self.cancel(context)
            return {"FINISHED"}

        if target_bone == control_bone:
            self.cancel(context)
            return {"FINISHED"}

        if target_bone.parent is None or control_bone.parent is None:
            self.cancel(context)
            return {"FINISHED"}

        weights = [i for i in range(32)]
        scale = 0.0

        transpose_parent = matrix_transpose(control_bone.parent.bone.matrix_local)
        parent_space = transpose_parent @ control_bone.bone.matrix_local
        current_rotation = parent_space @ control_bone.matrix_basis
        for index, trigger in enumerate(active_quaternion_procedural.triggers):
            if trigger.tolerance <= float_info.epsilon:
                self.report({"ERROR"}, f"\"{trigger.name}\" Tolerance Is Too Small")
                self.cancel(context)
                return {"FINISHED"}

            dot = abs(Euler(trigger.trigger_angle).to_quaternion().dot(current_rotation.to_quaternion()))
            dot = min(max(dot, -1.0), 1.0)
            weights[index] = 1.0 - (2.0 * acos(dot) * (1.0 / trigger.tolerance))
            weights[index] = max(0.0, weights[index])
            scale += weights[index]

        if scale <= 0.001:
            for trigger in active_quaternion_procedural.triggers:
                trigger.weight = 0.0

            active_trigger = active_quaternion_procedural.triggers[0]
            active_trigger.weight = 1.0

            target_rotation = Euler(active_trigger.target_angle).to_matrix()
            target_bone_transposed = matrix_transpose(target_bone.bone.matrix_local)

            if not active_quaternion_procedural.override_position:
                base_position = (matrix_transpose(target_bone.parent.bone.matrix_local) @ target_bone.bone.matrix_local).to_translation()
                target_translation = Matrix.Translation(base_position + Vector(active_trigger.target_position))
                target_bone.matrix_basis = target_bone_transposed @ target_bone.parent.bone.matrix_local @ target_translation @ target_rotation.to_4x4()
                return {"PASS_THROUGH"}

            override_position = Vector(active_quaternion_procedural.position_override)
            distance = active_quaternion_procedural.distance / 100.0
            control_bone_position = (matrix_transpose(control_bone.parent.bone.matrix_local) @ control_bone.bone.matrix_local).to_translation() * distance
            target_translation = Matrix.Translation(override_position + control_bone_position + Vector(active_trigger.target_position))
            target_bone.matrix_basis = target_bone_transposed @ target_bone.parent.bone.matrix_local @ target_translation @ target_rotation.to_4x4()
            return {"PASS_THROUGH"}

        scale = 1.0 / scale

        quat = Quaternion((0.0, 0.0, 0.0, 0.0))
        pos = Vector((0.0, 0.0, 0.0))

        for index, trigger in enumerate(active_quaternion_procedural.triggers):
            if weights[index] == 0.0:
                trigger.weight = 0.0
                continue

            s = weights[index] * scale
            trigger.weight = s
            target_quaternion = Euler(trigger.target_angle).to_quaternion()
            target_position = Vector(trigger.target_position)

            quat.x += s * target_quaternion.x
            quat.y += s * target_quaternion.y
            quat.z += s * target_quaternion.z
            quat.w += s * target_quaternion.w

            pos.x += s * target_position.x
            pos.y += s * target_position.y
            pos.z += s * target_position.z

        target_rotation = quat.normalized().to_matrix()
        target_bone_transposed = matrix_transpose(target_bone.bone.matrix_local)

        if not active_quaternion_procedural.override_position:
            base_position = (matrix_transpose(target_bone.parent.bone.matrix_local) @ target_bone.bone.matrix_local).to_translation()
            target_translation = Matrix.Translation(base_position + pos)
            target_bone.matrix_basis = target_bone_transposed @ target_bone.parent.bone.matrix_local @ target_translation @ target_rotation.to_4x4()
            return {"PASS_THROUGH"}

        override_position = Vector(active_quaternion_procedural.position_override)
        distance = active_quaternion_procedural.distance / 100.0
        control_bone_position = (matrix_transpose(control_bone.parent.bone.matrix_local) @ control_bone.bone.matrix_local).to_translation() * distance
        target_translation = Matrix.Translation(override_position + control_bone_position + pos)
        target_bone.matrix_basis = target_bone_transposed @ target_bone.parent.bone.matrix_local @ target_translation @ target_rotation.to_4x4()
        return {"PASS_THROUGH"}

    def cancel(self, context):
        if self.timer is not None:
            context.window_manager.event_timer_remove(self.timer)
            self.timer = None

        if self.active_quaternion_procedural is not None:
            self.active_quaternion_procedural.preview = False
            self.active_quaternion_procedural = None


class CopyQuaternionProceduralOperator(bpy.types.Operator):
    bl_idname = "source_procedural.quaternion_copy"
    bl_label = "Copy Quaternion Procedural"
    bl_description = "Copies the selected quaternion procedural to the clipboard"

    @classmethod
    def poll(cls, context):
        source_procedural_bone_data = context.object.source_procedural_bone_data
        active_quaternion_procedural = source_procedural_bone_data.quaternion_procedurals[source_procedural_bone_data.active_quaternion_procedural]

        return len(active_quaternion_procedural.triggers) > 0

    def execute(self, context):
        source_procedural_bone_data = context.object.source_procedural_bone_data
        active_quaternion_procedural = source_procedural_bone_data.quaternion_procedurals[source_procedural_bone_data.active_quaternion_procedural]
        target_bone = context.object.pose.bones[active_quaternion_procedural.target_bone]
        control_bone = context.object.pose.bones[active_quaternion_procedural.control_bone]

        current_position = (matrix_transpose(target_bone.parent.bone.matrix_local) @ target_bone.bone.matrix_local).to_translation()

        if active_quaternion_procedural.override_position:
            current_position = Vector(active_quaternion_procedural.position_override)

        def get_string_after_dot(input_string):
            parts = input_string.split(".", 1)
            if len(parts) > 1:
                return parts[1]
            return input_string

        target_bone_name = get_string_after_dot(target_bone.name)
        target_bone_parent_name = get_string_after_dot(target_bone.parent.name)
        control_bone_parent_name = get_string_after_dot(control_bone.parent.name)
        control_bone_name = get_string_after_dot(control_bone.name)
        procedural_string = f"<helper> {target_bone_name} {target_bone_parent_name} {control_bone_parent_name} {control_bone_name}\n"

        procedural_string += f"<display> 0 0 0 {active_quaternion_procedural.distance if active_quaternion_procedural.override_position else 0}\n"

        procedural_string += f"<basepos> {current_position.x} {current_position.y} {current_position.z}\n"

        procedural_string += "<rotateaxis> 0 0 0\n"

        procedural_string += "<jointorient> 0 0 0\n"

        for trigger in active_quaternion_procedural.triggers:
            trigger_angle = " ".join([str(degrees(r)) for r in trigger.trigger_angle])
            target_angle = " ".join([str(degrees(r)) for r in trigger.target_angle])
            target_position = " ".join([str(p) for p in trigger.target_position])
            procedural_string += f"<trigger> {degrees(trigger.tolerance)} {trigger_angle} {target_angle} {target_position}\n"

        context.window_manager.clipboard = procedural_string

        return {"FINISHED"}

# endregion

# region Quaternion Procedural Trigger Operators


class AddQuaternionProceduralTriggerOperator(bpy.types.Operator):
    bl_idname = "source_procedural.quaternion_trigger_add"
    bl_label = "Add Quaternion Procedural Trigger"
    bl_description = "Adds a new trigger"

    @classmethod
    def poll(cls, context):
        source_procedural_bone_data = context.object.source_procedural_bone_data
        active_quaternion_procedural = source_procedural_bone_data.quaternion_procedurals[source_procedural_bone_data.active_quaternion_procedural]

        return len(active_quaternion_procedural.triggers) < 32

    def execute(self, context):
        source_procedural_bone_data = context.object.source_procedural_bone_data
        active_quaternion_procedural = source_procedural_bone_data.quaternion_procedurals[source_procedural_bone_data.active_quaternion_procedural]

        active_quaternion_procedural.triggers.add()
        active_quaternion_procedural.active_trigger = len(active_quaternion_procedural.triggers) - 1

        return {"FINISHED"}


class RemoveQuaternionProceduralTriggerOperator(bpy.types.Operator):
    bl_idname = "source_procedural.quaternion_trigger_remove"
    bl_label = "Remove Quaternion Procedural Trigger"
    bl_description = "Removes the selected trigger"

    @classmethod
    def poll(cls, context):
        source_procedural_bone_data = context.object.source_procedural_bone_data
        active_quaternion_procedural = source_procedural_bone_data.quaternion_procedurals[source_procedural_bone_data.active_quaternion_procedural]

        return len(active_quaternion_procedural.triggers) != 0

    def execute(self, context):
        source_procedural_bone_data = context.object.source_procedural_bone_data
        active_quaternion_procedural = source_procedural_bone_data.quaternion_procedurals[source_procedural_bone_data.active_quaternion_procedural]

        active_quaternion_procedural.triggers.remove(active_quaternion_procedural.active_trigger)

        if active_quaternion_procedural.active_trigger > 0:
            active_quaternion_procedural.active_trigger -= 1

        return {"FINISHED"}


class MoveUpQuaternionProceduralTriggerOperator(bpy.types.Operator):
    bl_idname = "source_procedural.quaternion_trigger_move_up"
    bl_label = "Move Up Quaternion Procedural Trigger"
    bl_description = "Moves the selected trigger up"

    @classmethod
    def poll(cls, context):
        source_procedural_bone_data = context.object.source_procedural_bone_data
        active_quaternion_procedural = source_procedural_bone_data.quaternion_procedurals[source_procedural_bone_data.active_quaternion_procedural]

        return active_quaternion_procedural.active_trigger > 0

    def execute(self, context):
        source_procedural_bone_data = context.object.source_procedural_bone_data
        active_quaternion_procedural = source_procedural_bone_data.quaternion_procedurals[source_procedural_bone_data.active_quaternion_procedural]

        active_quaternion_procedural.triggers.move(active_quaternion_procedural.active_trigger, active_quaternion_procedural.active_trigger - 1)
        active_quaternion_procedural.active_trigger -= 1

        return {"FINISHED"}


class MoveDownQuaternionProceduralTriggerOperator(bpy.types.Operator):
    bl_idname = "source_procedural.quaternion_trigger_move_down"
    bl_label = "Move Down Quaternion Procedural Trigger"
    bl_description = "Moves the selected trigger down"

    @classmethod
    def poll(cls, context):
        source_procedural_bone_data = context.object.source_procedural_bone_data
        active_quaternion_procedural = source_procedural_bone_data.quaternion_procedurals[source_procedural_bone_data.active_quaternion_procedural]

        return active_quaternion_procedural.active_trigger < len(active_quaternion_procedural.triggers) - 1

    def execute(self, context):
        source_procedural_bone_data = context.object.source_procedural_bone_data
        active_quaternion_procedural = source_procedural_bone_data.quaternion_procedurals[source_procedural_bone_data.active_quaternion_procedural]

        active_quaternion_procedural.triggers.move(active_quaternion_procedural.active_trigger, active_quaternion_procedural.active_trigger + 1)
        active_quaternion_procedural.active_trigger += 1

        return {"FINISHED"}


class SetTriggerQuaternionProceduralTriggerOperator(bpy.types.Operator):
    bl_idname = "source_procedural.quaternion_trigger_set_trigger"
    bl_label = "Set Trigger Quaternion Procedural Trigger"
    bl_description = "Sets the trigger angle of the selected trigger to the current angle of the control bone"

    @classmethod
    def poll(cls, context):
        return context.mode == "POSE"

    def execute(self, context):
        source_procedural_bone_data = context.object.source_procedural_bone_data
        active_quaternion_procedural = source_procedural_bone_data.quaternion_procedurals[source_procedural_bone_data.active_quaternion_procedural]
        control_bone = context.object.pose.bones[active_quaternion_procedural.control_bone]

        transpose_parent = matrix_transpose(control_bone.parent.bone.matrix_local)
        parent_space = transpose_parent @ control_bone.bone.matrix_local
        current_rotation = parent_space @ control_bone.matrix_basis
        active_quaternion_procedural.triggers[active_quaternion_procedural.active_trigger].trigger_angle = current_rotation.to_euler()

        return {"FINISHED"}


class SetAngleQuaternionProceduralTriggerOperator(bpy.types.Operator):
    bl_idname = "source_procedural.quaternion_trigger_set_angle"
    bl_label = "Set Angle Quaternion Procedural Trigger"
    bl_description = "Sets the target angle of the selected trigger to the current angle of the target bone"

    @classmethod
    def poll(cls, context):
        return context.mode == "POSE"

    def execute(self, context):
        source_procedural_bone_data = context.object.source_procedural_bone_data
        active_quaternion_procedural = source_procedural_bone_data.quaternion_procedurals[source_procedural_bone_data.active_quaternion_procedural]
        target_bone = context.object.pose.bones[active_quaternion_procedural.target_bone]

        transpose_parent = matrix_transpose(target_bone.parent.bone.matrix_local)
        parent_space = transpose_parent @ target_bone.bone.matrix_local
        current_rotation = parent_space @ target_bone.matrix_basis
        active_quaternion_procedural.triggers[active_quaternion_procedural.active_trigger].target_angle = current_rotation.to_euler()

        return {"FINISHED"}


class SetPositionQuaternionProceduralTriggerOperator(bpy.types.Operator):
    bl_idname = "source_procedural.quaternion_trigger_set_position"
    bl_label = "Set Position Quaternion Procedural Trigger"
    bl_description = "Sets the target position of the selected trigger to the current position of the target bone"

    @classmethod
    def poll(cls, context):
        return context.mode == "POSE"

    def execute(self, context):
        source_procedural_bone_data = context.object.source_procedural_bone_data
        active_quaternion_procedural = source_procedural_bone_data.quaternion_procedurals[source_procedural_bone_data.active_quaternion_procedural]
        control_bone = context.object.pose.bones[active_quaternion_procedural.control_bone]
        target_bone = context.object.pose.bones[active_quaternion_procedural.target_bone]

        base_position = (matrix_transpose(target_bone.parent.bone.matrix_local) @ target_bone.bone.matrix_local).to_translation()
        current_position = ((matrix_transpose(target_bone.parent.bone.matrix_local) @
                            target_bone.bone.matrix_local) @ target_bone.matrix_basis).to_translation()

        if not active_quaternion_procedural.override_position:
            active_quaternion_procedural.triggers[active_quaternion_procedural.active_trigger].target_position = current_position - base_position
            return {"FINISHED"}

        override_position = Vector(active_quaternion_procedural.position_override)
        distance = active_quaternion_procedural.distance / 100.0
        control_bone_position = (matrix_transpose(control_bone.parent.bone.matrix_local) @ control_bone.bone.matrix_local).to_translation() * distance

        active_quaternion_procedural.triggers[active_quaternion_procedural.active_trigger].target_position = current_position - \
            override_position - control_bone_position
        return {"FINISHED"}


class PreviewQuaternionProceduralTriggerOperator(bpy.types.Operator):
    bl_idname = "source_procedural.quaternion_trigger_preview"
    bl_label = "Preview Quaternion Procedural Trigger"
    bl_description = "Sets the trigger angle, target angle, and target position of the selected trigger"

    @classmethod
    def poll(cls, context):
        return context.mode == "POSE"

    def execute(self, context):
        source_procedural_bone_data = context.object.source_procedural_bone_data
        active_quaternion_procedural = source_procedural_bone_data.quaternion_procedurals[source_procedural_bone_data.active_quaternion_procedural]
        active_trigger = active_quaternion_procedural.triggers[active_quaternion_procedural.active_trigger]
        control_bone = context.object.pose.bones[active_quaternion_procedural.control_bone]
        target_bone = context.object.pose.bones[active_quaternion_procedural.target_bone]

        trigger_rotation = Euler(active_trigger.trigger_angle).to_matrix()
        control_bone_transposed = matrix_transpose(control_bone.bone.matrix_local).to_3x3()
        control_bone.matrix_basis = (control_bone_transposed @ control_bone.parent.bone.matrix_local.to_3x3() @ trigger_rotation).to_4x4()

        target_rotation = Euler(active_trigger.target_angle).to_matrix()
        target_bone_transposed = matrix_transpose(target_bone.bone.matrix_local)

        if not active_quaternion_procedural.override_position:
            base_position = (matrix_transpose(target_bone.parent.bone.matrix_local) @ target_bone.bone.matrix_local).to_translation()
            target_translation = Matrix.Translation(base_position + Vector(active_trigger.target_position))
            target_bone.matrix_basis = target_bone_transposed @ target_bone.parent.bone.matrix_local @ target_translation @ target_rotation.to_4x4()
            return {"FINISHED"}

        override_position = Vector(active_quaternion_procedural.position_override)
        distance = active_quaternion_procedural.distance / 100.0
        control_bone_position = (matrix_transpose(control_bone.parent.bone.matrix_local) @ control_bone.bone.matrix_local).to_translation() * distance
        target_translation = Matrix.Translation(override_position + control_bone_position + Vector(active_trigger.target_position))
        target_bone.matrix_basis = target_bone_transposed @ target_bone.parent.bone.matrix_local @ target_translation @ target_rotation.to_4x4()
        return {"FINISHED"}

# endregion

# region Jiggle Procedural Operators


class AddJiggleProceduralOperator(bpy.types.Operator):
    bl_idname = "source_procedural.jiggle_add"
    bl_label = "Add Jiggle Procedural"
    bl_description = "Adds a new jiggle procedural"

    def execute(self, context):
        source_procedural_bone_data = context.object.source_procedural_bone_data

        source_procedural_bone_data.jiggle_procedurals.add()
        source_procedural_bone_data.active_jiggle_procedural = len(source_procedural_bone_data.jiggle_procedurals) - 1

        return {"FINISHED"}


class RemoveJiggleProceduralOperator(bpy.types.Operator):
    bl_idname = "source_procedural.jiggle_remove"
    bl_label = "Remove Jiggle Procedural"
    bl_description = "Removes the selected jiggle procedural"

    @classmethod
    def poll(cls, context):
        source_procedural_bone_data = context.object.source_procedural_bone_data

        return len(source_procedural_bone_data.jiggle_procedurals) != 0

    def execute(self, context):
        source_procedural_bone_data = context.object.source_procedural_bone_data
        active_jiggle_procedural = source_procedural_bone_data.jiggle_procedurals[source_procedural_bone_data.active_jiggle_procedural]

        active_jiggle_procedural.preview = False
        source_procedural_bone_data.jiggle_procedurals.remove(source_procedural_bone_data.active_jiggle_procedural)

        if source_procedural_bone_data.active_jiggle_procedural > 0:
            source_procedural_bone_data.active_jiggle_procedural -= 1

        return {"FINISHED"}


class PreviewJiggleProceduralOperator(bpy.types.Operator):
    bl_idname = "source_procedural.jiggle_preview"
    bl_label = "Preview Jiggle Procedural"
    bl_description = "Previews the selected jiggle procedural"

    def __init__(self):
        self.active_jiggle_procedural = None
        self.timer = None
        self.delta_time = 0.0
        self.tip_position = Vector()
        self.tip_velocity = Vector()
        self.last_left = Vector()

    def execute(self, context):
        source_procedural_bone_data = context.object.source_procedural_bone_data
        active_jiggle_procedural = source_procedural_bone_data.jiggle_procedurals[source_procedural_bone_data.active_jiggle_procedural]

        if not active_jiggle_procedural.preview:
            active_jiggle_procedural.preview = True
            self.active_jiggle_procedural = active_jiggle_procedural

            self.delta_time = 1.0 / context.scene.render.fps
            self.timer = context.window_manager.event_timer_add(self.delta_time, window=context.window)

            target_bone = context.object.pose.bones[active_jiggle_procedural.target_bone]
            goal_matrix = target_bone.bone.matrix_local
            goal_base_position = goal_matrix.col[3].to_3d()
            goal_left = goal_matrix.col[0].to_3d()
            goal_forward = goal_matrix.col[2].to_3d()

            self.tip_position = goal_base_position + active_jiggle_procedural.length * goal_forward
            self.last_left = goal_left
            self.base_position = goal_base_position
            self.last_base_position = goal_base_position

            if active_jiggle_procedural.base_flex_type == "SPRING":
                self.report({"WARNING"}, "Spring Base Flex Not Implemented Yet")

            if active_jiggle_procedural.base_flex_type == "BOING":
                self.report({"WARNING"}, "Boing Base Flex Not Implemented Yet")

            context.window_manager.modal_handler_add(self)
            return {"RUNNING_MODAL"}

        active_jiggle_procedural.preview = False
        self.cancel(context)

        return {"FINISHED"}

    def modal(self, context, event):
        if event.type != "TIMER":
            return {"PASS_THROUGH"}

        if context.object is None or context.object.type != "ARMATURE":
            self.cancel(context)
            return {"FINISHED"}

        active_jiggle_procedural = self.active_jiggle_procedural

        if not active_jiggle_procedural.preview:
            self.cancel(context)
            return {"FINISHED"}

        target_bone = context.object.pose.bones.get(active_jiggle_procedural.target_bone)
        if not target_bone:
            self.cancel(context)
            return {"FINISHED"}

        bone_matrix = target_bone.matrix.normalized()
        goal_matrix = target_bone.bone.matrix_local
        goal_base_position = bone_matrix.col[3].to_3d()
        goal_left = goal_matrix.col[0].to_3d()
        goal_up = goal_matrix.col[1].to_3d()
        goal_forward = goal_matrix.col[2].to_3d()
        goal_tip = goal_base_position + active_jiggle_procedural.length * goal_forward

        if active_jiggle_procedural.tip_flex_type == "RIGID" or active_jiggle_procedural.tip_flex_type == "FLEXIBLE":
            tip_acceleration = Vector()
            tip_acceleration.z -= active_jiggle_procedural.tip_mass

            if active_jiggle_procedural.tip_flex_type == "FLEXIBLE":
                error = goal_tip - self.tip_position
                local_error = Vector((goal_left.dot(error), goal_up.dot(error), goal_forward.dot(error)))
                local_velocity = Vector((goal_left.dot(self.tip_velocity), goal_up.dot(self.tip_velocity), goal_forward.dot(self.tip_velocity)))

                yaw_acceleration = active_jiggle_procedural.yaw_stiffness * local_error.x - active_jiggle_procedural.yaw_damping * local_velocity.x
                pitch_acceleration = active_jiggle_procedural.pitch_stiffness * local_error.y - active_jiggle_procedural.pitch_damping * local_velocity.y

                if active_jiggle_procedural.along_constraint == "CONSTRAINT":
                    tip_acceleration += yaw_acceleration * goal_left + pitch_acceleration * goal_up
                else:
                    along_acceleration = active_jiggle_procedural.along_stiffness * local_error.z - active_jiggle_procedural.along_damping * local_velocity.z
                    tip_acceleration += yaw_acceleration * goal_left + pitch_acceleration * goal_up + along_acceleration * goal_forward

            self.tip_velocity += tip_acceleration * self.delta_time
            self.tip_position += self.tip_velocity * self.delta_time

            if active_jiggle_procedural.yaw_constraint == "CONSTRAINT" or active_jiggle_procedural.pitch_constraint == "CONSTRAINT":
                along = self.tip_position - goal_base_position
                local_along = Vector((goal_left.dot(along), goal_up.dot(along), goal_forward.dot(along)))
                local_velocity = Vector((goal_left.dot(self.tip_velocity), goal_up.dot(self.tip_velocity), goal_forward.dot(self.tip_velocity)))

                if active_jiggle_procedural.yaw_constraint == "CONSTRAINT":
                    yaw_error = atan2(local_along.x, local_along.z)

                    is_at_limit = False
                    yaw = 0.0

                    if yaw_error < active_jiggle_procedural.yaw_minimum:
                        is_at_limit = True
                        yaw = active_jiggle_procedural.yaw_minimum
                    elif yaw_error > active_jiggle_procedural.yaw_maximum:
                        is_at_limit = True
                        yaw = active_jiggle_procedural.yaw_maximum

                    if is_at_limit:
                        sin_yaw = sin(yaw)
                        cos_yaw = cos(yaw)

                        yaw_matrix = Matrix(((cos_yaw, 0.0, sin_yaw, 0.0),
                                            (0.0, 1.0, 0.0, 0.0,),
                                            (-sin_yaw, 0.0, cos_yaw, 0.0),
                                            (0.0, 0.0, 0.0, 1.0)))

                        limit_matrix = goal_matrix @ yaw_matrix
                        limit_left = limit_matrix.col[0].to_3d()
                        limit_up = limit_matrix.col[1].to_3d()
                        limit_forward = limit_matrix.col[2].to_3d()
                        limit_along = Vector((limit_left.dot(along), limit_up.dot(along), limit_forward.dot(along)))

                        self.tip_position = goal_base_position + limit_along.y * limit_up + limit_along.z * limit_forward
                        self.tip_velocity = Vector()

                        along = self.tip_position - goal_base_position
                        local_along = Vector((goal_left.dot(along), goal_up.dot(along), goal_forward.dot(along)))
                        local_velocity = Vector((goal_left.dot(self.tip_velocity), goal_up.dot(self.tip_velocity), goal_forward.dot(self.tip_velocity)))

                if active_jiggle_procedural.pitch_constraint == "CONSTRAINT":
                    pitch_error = atan2(local_along.y, local_along.z)

                    is_at_limit = False
                    pitch = 0.0

                    if pitch_error < active_jiggle_procedural.pitch_minimum:
                        is_at_limit = True
                        pitch = active_jiggle_procedural.pitch_minimum
                    elif pitch_error > active_jiggle_procedural.pitch_maximum:
                        is_at_limit = True
                        pitch = active_jiggle_procedural.pitch_maximum

                    if is_at_limit:
                        sin_pitch = sin(pitch)
                        cos_pitch = cos(pitch)

                        pitch_matrix = Matrix(((1.0, 0.0, 0.0, 0.0),
                                               (0.0, cos_pitch, sin_pitch, 0.0,),
                                               (0.0, -sin_pitch, cos_pitch, 0.0),
                                               (0.0, 0.0, 0.0, 1.0)))

                        limit_matrix = goal_matrix @ pitch_matrix
                        limit_left = limit_matrix.col[0].to_3d()
                        limit_up = limit_matrix.col[1].to_3d()
                        limit_forward = limit_matrix.col[2].to_3d()
                        limit_along = Vector((limit_left.dot(along), limit_up.dot(along), limit_forward.dot(along)))

                        self.tip_position = goal_base_position + limit_along.x * limit_left + limit_along.z * limit_forward
                        self.tip_velocity = Vector()

            forward = (self.tip_position - goal_base_position).normalized()

            if active_jiggle_procedural.angle_constraint == "CONSTRAINT":
                dot = forward.dot(goal_forward)

                if dot > -1.0 and dot < 1.0:
                    angle_between = acos(dot)
                    if dot < 0.0:
                        angle_between = 2.0 * pi - angle_between

                    if angle_between > active_jiggle_procedural.angle_limit:
                        max_between = active_jiggle_procedural.length * sin(active_jiggle_procedural.angle_limit)
                        delta = (goal_tip - self.tip_position).normalized()
                        self.tip_position = goal_tip - max_between * delta
                        forward = (self.tip_position - goal_base_position).normalized()

            if active_jiggle_procedural.along_constraint == "CONSTRAINT":
                self.tip_position = goal_base_position + active_jiggle_procedural.length * forward
                self.tip_velocity -= self.tip_velocity.dot(forward) * forward

            left = goal_up.cross(forward).normalized()
            if left.dot(self.last_left) < 0.0:
                left = -left
            self.last_left = left

            up = forward.cross(left)

            bone_matrix[0][0] = left.x
            bone_matrix[1][0] = left.y
            bone_matrix[2][0] = left.z
            bone_matrix[0][1] = up.x
            bone_matrix[1][1] = up.y
            bone_matrix[2][1] = up.z
            bone_matrix[0][2] = forward.x
            bone_matrix[1][2] = forward.y
            bone_matrix[2][2] = forward.z

        target_bone.matrix = bone_matrix
        return {"PASS_THROUGH"}

    def cancel(self, context):
        if self.timer is not None:
            context.window_manager.event_timer_remove(self.timer)
            self.timer = None

        if self.active_jiggle_procedural is not None:
            self.active_jiggle_procedural.preview = False
            self.active_jiggle_procedural = None


class CopyJiggleProceduralOperator(bpy.types.Operator):
    bl_idname = "source_procedural.jiggle_copy"
    bl_label = "Copy Jiggle Procedural"
    bl_description = "Copies the selected jiggle procedural to the clipboard"

    def execute(self, context):
        source_procedural_bone_data = context.object.source_procedural_bone_data
        active_jiggle_procedural = source_procedural_bone_data.jiggle_procedurals[source_procedural_bone_data.active_jiggle_procedural]
        target_bone = context.object.pose.bones[active_jiggle_procedural.target_bone]

        procedural_string = f"$jigglebone \"{target_bone.name}\" {{\n"

        if active_jiggle_procedural.tip_flex_type == "RIGID":
            procedural_string += "\tis_rigid {\n"
            procedural_string += f"\t\tlength {active_jiggle_procedural.length}\n"
            procedural_string += f"\t\ttip_mass {active_jiggle_procedural.tip_mass}\n"

        if active_jiggle_procedural.tip_flex_type == "FLEXIBLE":
            procedural_string += "\tis_flexible {\n"
            procedural_string += f"\t\tlength {active_jiggle_procedural.length}\n"
            procedural_string += f"\t\ttip_mass {active_jiggle_procedural.tip_mass}\n"
            procedural_string += f"\t\tyaw_stiffness {active_jiggle_procedural.yaw_stiffness}\n"
            procedural_string += f"\t\tyaw_damping {active_jiggle_procedural.yaw_damping}\n"
            procedural_string += f"\t\tpitch_stiffness {active_jiggle_procedural.pitch_stiffness}\n"
            procedural_string += f"\t\tpitch_damping {active_jiggle_procedural.pitch_damping}\n"

            if active_jiggle_procedural.along_constraint == "NONE":
                procedural_string += "\t\tallow_length_flex\n"
                procedural_string += f"\t\talong_stiffness {active_jiggle_procedural.along_stiffness}\n"
                procedural_string += f"\t\talong_damping {active_jiggle_procedural.along_damping}\n"

        if active_jiggle_procedural.tip_flex_type == "RIGID" or active_jiggle_procedural.tip_flex_type == "FLEXIBLE":
            if active_jiggle_procedural.angle_constraint == "CONSTRAINT":
                procedural_string += f"\t\tangle_constraint {degrees(active_jiggle_procedural.angle_limit)}\n"

            if active_jiggle_procedural.yaw_constraint == "CONSTRAINT":
                procedural_string += f"\t\tyaw_constraint {degrees(active_jiggle_procedural.yaw_minimum)} {degrees(active_jiggle_procedural.yaw_maximum)}\n"

            if active_jiggle_procedural.pitch_constraint == "CONSTRAINT":
                procedural_string += f"\t\tpitch_constraint {degrees(active_jiggle_procedural.pitch_minimum)} {degrees(active_jiggle_procedural.pitch_maximum)}\n"

            procedural_string += "\t}\n"

        if active_jiggle_procedural.base_flex_type == "SPRING":
            procedural_string += "\thas_base_spring {\n"

            procedural_string += f"\t\tbase_mass {active_jiggle_procedural.base_mass}\n"
            procedural_string += f"\t\tstiffness {active_jiggle_procedural.base_stiffness}\n"
            procedural_string += f"\t\tdamping {active_jiggle_procedural.base_damping}\n"
            procedural_string += f"\t\tleft_constraint {active_jiggle_procedural.base_minimum_left} {active_jiggle_procedural.base_maximum_left}\n"
            procedural_string += f"\t\tleft_friction {active_jiggle_procedural.base_friction_left}\n"
            procedural_string += f"\t\tup_constraint {active_jiggle_procedural.base_minimum_up} {active_jiggle_procedural.base_maximum_up}\n"
            procedural_string += f"\t\tup_friction {active_jiggle_procedural.base_friction_up}\n"
            procedural_string += f"\t\tforward_constraint {active_jiggle_procedural.base_minimum_forward} {active_jiggle_procedural.base_maximum_forward}\n"
            procedural_string += f"\t\tforward_friction {active_jiggle_procedural.base_friction_forward}\n"

            procedural_string += "\t}\n"

        if active_jiggle_procedural.base_flex_type == "BOING":
            procedural_string += "\tis_boing {\n"

            procedural_string += f"\t\timpact_speed {active_jiggle_procedural.boing_impact_speed}\n"
            procedural_string += f"\t\timpact_angle {degrees(active_jiggle_procedural.boing_impact_angle)}\n"
            procedural_string += f"\t\tdamping_rate {active_jiggle_procedural.boing_damping_rate}\n"
            procedural_string += f"\t\tfrequency {active_jiggle_procedural.boing_frequency}\n"
            procedural_string += f"\t\tamplitude {active_jiggle_procedural.boing_amplitude}\n"

            procedural_string += "\t}\n"

        procedural_string += "}\n"

        context.window_manager.clipboard = procedural_string

        return {"FINISHED"}


# endregion

# region UI


class QuaternionProceduralList(bpy.types.UIList):
    bl_idname = "OBJECT_UL_QuaternionProcedural"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", emboss=False, icon_value=icon)


class QuaternionProceduralTriggerList(bpy.types.UIList):
    bl_idname = "OBJECT_UL_QuaternionProceduralTrigger"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", emboss=False, icon_value=icon)

        source_procedural_bone_data = context.object.source_procedural_bone_data
        active_quaternion_procedural = source_procedural_bone_data.quaternion_procedurals[source_procedural_bone_data.active_quaternion_procedural]
        if active_quaternion_procedural.preview:
            layout.label(text=f"Weight: {item.weight * 100:.2f}%")


class QuaternionProceduralPanel(bpy.types.Panel):
    bl_category = "Src Proc Bones"
    bl_label = "Quaternion Procedurals"
    bl_idname = "VIEW3D_PT_QuaternionProcedural"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == "ARMATURE"

    def draw(self, context):
        layout = self.layout
        source_procedural_bone_data = context.object.source_procedural_bone_data

        row = layout.row(align=True)
        row.template_list(QuaternionProceduralList.bl_idname, "", source_procedural_bone_data,
                          "quaternion_procedurals", source_procedural_bone_data, "active_quaternion_procedural")

        col = row.column(align=True)
        col.operator(AddQuaternionProceduralOperator.bl_idname, text="", icon="ADD")
        col.operator(RemoveQuaternionProceduralOperator.bl_idname, text="", icon="REMOVE")

        if len(source_procedural_bone_data.quaternion_procedurals) == 0:
            return

        active_quaternion_procedural = source_procedural_bone_data.quaternion_procedurals[source_procedural_bone_data.active_quaternion_procedural]

        col = layout.column(align=True)
        col.prop(active_quaternion_procedural, "name", text="")

        box = col.box()
        row = box.row(align=True)
        row.label(text="Target Bone:")
        row.prop_search(active_quaternion_procedural, "target_bone", context.object.pose, "bones", text="")
        row.label(text="Control Bone:")
        row.prop_search(active_quaternion_procedural, "control_bone", context.object.pose, "bones", text="")

        target_bone = context.object.pose.bones.get(active_quaternion_procedural.target_bone)
        control_bone = context.object.pose.bones.get(active_quaternion_procedural.control_bone)

        if target_bone is None or control_bone is None:
            return

        if target_bone == control_bone:
            return

        if target_bone.parent is None or control_bone.parent is None:
            return

        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(active_quaternion_procedural, "override_position", text="Override Position")
        if active_quaternion_procedural.override_position:
            row.prop(active_quaternion_procedural, "position_override", text="")
            col.prop(active_quaternion_procedural, "distance", text="Distance")

        box.operator(PreviewQuaternionProceduralOperator.bl_idname, text="Preview Procedural", depress=active_quaternion_procedural.preview)

        box.operator(CopyQuaternionProceduralOperator.bl_idname, text="Copy Procedural")

        row = box.row(align=True)
        row.template_list(QuaternionProceduralTriggerList.bl_idname, "", active_quaternion_procedural,
                          "triggers", active_quaternion_procedural, "active_trigger")
        col = row.column(align=True)
        col.operator(AddQuaternionProceduralTriggerOperator.bl_idname, text="", icon="ADD")
        col.operator(RemoveQuaternionProceduralTriggerOperator.bl_idname, text="", icon="REMOVE")
        col.separator()
        col.operator(MoveUpQuaternionProceduralTriggerOperator.bl_idname, text="", icon="TRIA_UP")
        col.operator(MoveDownQuaternionProceduralTriggerOperator.bl_idname, text="", icon="TRIA_DOWN")

        if len(active_quaternion_procedural.triggers) == 0:
            return

        active_trigger = active_quaternion_procedural.triggers[active_quaternion_procedural.active_trigger]

        col = box.box().column(align=True)
        col.prop(active_trigger, "name", text="")
        col.prop(active_trigger, "tolerance", text="Tolerance")

        row = col.row(align=True)
        row.prop(active_trigger, "trigger_angle", text="Trigger")
        row.operator(SetTriggerQuaternionProceduralTriggerOperator.bl_idname, text="Set")

        row = col.row(align=True)
        row.prop(active_trigger, "target_angle", text="Angle")
        row.operator(SetAngleQuaternionProceduralTriggerOperator.bl_idname, text="Set")

        row = col.row(align=True)
        row.prop(active_trigger, "target_position", text="Position")
        row.operator(SetPositionQuaternionProceduralTriggerOperator.bl_idname, text="Set")

        col.operator(PreviewQuaternionProceduralTriggerOperator.bl_idname, text="Preview Trigger")


class JiggleProceduralList(bpy.types.UIList):
    bl_idname = "OBJECT_UL_JiggleProcedural"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", emboss=False, icon_value=icon)


class JiggleProceduralPanel(bpy.types.Panel):
    bl_category = "Src Proc Bones"
    bl_label = "Jiggle Procedurals"
    bl_idname = "VIEW3D_PT_JiggleProcedural"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == "ARMATURE"

    def draw(self, context):
        layout = self.layout
        source_procedural_bone_data = context.object.source_procedural_bone_data

        row = layout.row(align=True)
        row.template_list(JiggleProceduralList.bl_idname, "", source_procedural_bone_data,
                          "jiggle_procedurals", source_procedural_bone_data, "active_jiggle_procedural")

        col = row.column(align=True)
        col.operator(AddJiggleProceduralOperator.bl_idname, text="", icon="ADD")
        col.operator(RemoveJiggleProceduralOperator.bl_idname, text="", icon="REMOVE")

        if len(source_procedural_bone_data.jiggle_procedurals) == 0:
            return

        active_jiggle_procedural = source_procedural_bone_data.jiggle_procedurals[source_procedural_bone_data.active_jiggle_procedural]

        col = layout.column(align=True)
        col.prop(active_jiggle_procedural, "name", text="")

        box = col.box()
        row = box.row(align=True)
        row.prop_search(active_jiggle_procedural, "target_bone", context.object.pose, "bones", text="")

        target_bone = context.object.pose.bones.get(active_jiggle_procedural.target_bone)

        if target_bone is None:
            return

        box.operator(PreviewJiggleProceduralOperator.bl_idname, text="Preview Procedural", depress=active_jiggle_procedural.preview)
        box.operator(CopyJiggleProceduralOperator.bl_idname, text="Copy Procedural")

        col = box.column(align=True)
        col.label(text="Tip Flex Type")
        col.prop(active_jiggle_procedural, "tip_flex_type", text="")

        if active_jiggle_procedural.tip_flex_type == "RIGID" or active_jiggle_procedural.tip_flex_type == "FLEXIBLE":
            col = col.box().column(align=True)

            col.prop(active_jiggle_procedural, "length")
            col.prop(active_jiggle_procedural, "tip_mass")

            if active_jiggle_procedural.tip_flex_type == "FLEXIBLE":
                col.prop(active_jiggle_procedural, "yaw_stiffness")
                col.prop(active_jiggle_procedural, "yaw_damping")
                col.prop(active_jiggle_procedural, "pitch_stiffness")
                col.prop(active_jiggle_procedural, "pitch_damping")

                col.label(text="Along Constraint")
                col.prop(active_jiggle_procedural, "along_constraint", text="")
                if active_jiggle_procedural.along_constraint == "NONE":
                    col.prop(active_jiggle_procedural, "along_stiffness")
                    col.prop(active_jiggle_procedural, "along_damping")

            col.label(text="Angle Constraint")
            col.prop(active_jiggle_procedural, "angle_constraint", text="")
            if active_jiggle_procedural.angle_constraint == "CONSTRAINT":
                col.prop(active_jiggle_procedural, "angle_limit")

            col.label(text="Yaw Constraint")
            col.prop(active_jiggle_procedural, "yaw_constraint", text="")
            if active_jiggle_procedural.yaw_constraint == "CONSTRAINT":
                row = col.row(align=True)
                row.prop(active_jiggle_procedural, "yaw_minimum")
                row.prop(active_jiggle_procedural, "yaw_maximum")

            col.label(text="Pitch Constraint")
            col.prop(active_jiggle_procedural, "pitch_constraint", text="")
            if active_jiggle_procedural.pitch_constraint == "CONSTRAINT":
                row = col.row(align=True)
                row.prop(active_jiggle_procedural, "pitch_minimum")
                row.prop(active_jiggle_procedural, "pitch_maximum")

        col = box.column(align=True)
        col.label(text="Base Flex Type")
        col.prop(active_jiggle_procedural, "base_flex_type", text="")
        if active_jiggle_procedural.base_flex_type == "SPRING":
            col = col.box().column(align=True)

            col.prop(active_jiggle_procedural, "base_mass")
            col.prop(active_jiggle_procedural, "base_stiffness")
            col.prop(active_jiggle_procedural, "base_damping")
            col.label(text="Left Constraint")
            row = col.row(align=True)
            row.prop(active_jiggle_procedural, "base_minimum_left", text="")
            row.prop(active_jiggle_procedural, "base_maximum_left", text="")
            col.prop(active_jiggle_procedural, "base_friction_left")
            col.label(text="Up Constraint")
            row = col.row(align=True)
            row.prop(active_jiggle_procedural, "base_minimum_up", text="")
            row.prop(active_jiggle_procedural, "base_maximum_up", text="")
            col.prop(active_jiggle_procedural, "base_friction_up")
            col.label(text="Forward Constraint")
            row = col.row(align=True)
            row.prop(active_jiggle_procedural, "base_minimum_forward", text="")
            row.prop(active_jiggle_procedural, "base_maximum_forward", text="")
            col.prop(active_jiggle_procedural, "base_friction_forward")

        if active_jiggle_procedural.base_flex_type == "BOING":
            col = col.box().column(align=True)

            col.prop(active_jiggle_procedural, "boing_impact_speed")
            col.prop(active_jiggle_procedural, "boing_impact_angle")
            col.prop(active_jiggle_procedural, "boing_damping_rate")
            col.prop(active_jiggle_procedural, "boing_frequency")
            col.prop(active_jiggle_procedural, "boing_amplitude")


# endregion


def register():
    # Properties
    bpy.utils.register_class(QuaternionProceduralTriggerProperty)
    bpy.utils.register_class(QuaternionProceduralProperty)
    bpy.utils.register_class(JiggleProceduralProperty)
    bpy.utils.register_class(SourceProceduralBoneDataProperty)

    # Quaternion Procedural Operators
    bpy.utils.register_class(AddQuaternionProceduralOperator)
    bpy.utils.register_class(RemoveQuaternionProceduralOperator)
    bpy.utils.register_class(PreviewQuaternionProceduralOperator)
    bpy.utils.register_class(CopyQuaternionProceduralOperator)

    # Quaternion Procedural Trigger Operators
    bpy.utils.register_class(AddQuaternionProceduralTriggerOperator)
    bpy.utils.register_class(RemoveQuaternionProceduralTriggerOperator)
    bpy.utils.register_class(MoveUpQuaternionProceduralTriggerOperator)
    bpy.utils.register_class(MoveDownQuaternionProceduralTriggerOperator)
    bpy.utils.register_class(SetTriggerQuaternionProceduralTriggerOperator)
    bpy.utils.register_class(SetAngleQuaternionProceduralTriggerOperator)
    bpy.utils.register_class(SetPositionQuaternionProceduralTriggerOperator)
    bpy.utils.register_class(PreviewQuaternionProceduralTriggerOperator)

    # Jiggle Procedural Operators
    bpy.utils.register_class(AddJiggleProceduralOperator)
    bpy.utils.register_class(RemoveJiggleProceduralOperator)
    bpy.utils.register_class(PreviewJiggleProceduralOperator)
    bpy.utils.register_class(CopyJiggleProceduralOperator)

    # UI
    bpy.utils.register_class(QuaternionProceduralList)
    bpy.utils.register_class(QuaternionProceduralTriggerList)
    bpy.utils.register_class(QuaternionProceduralPanel)
    bpy.utils.register_class(JiggleProceduralList)
    bpy.utils.register_class(JiggleProceduralPanel)

    bpy.types.Object.source_procedural_bone_data = bpy.props.PointerProperty(type=SourceProceduralBoneDataProperty)


def unregister():
    # Properties
    bpy.utils.unregister_class(QuaternionProceduralTriggerProperty)
    bpy.utils.unregister_class(QuaternionProceduralProperty)
    bpy.utils.unregister_class(JiggleProceduralProperty)
    bpy.utils.unregister_class(SourceProceduralBoneDataProperty)

    # Quaternion Procedural Operators
    bpy.utils.unregister_class(AddQuaternionProceduralOperator)
    bpy.utils.unregister_class(RemoveQuaternionProceduralOperator)
    bpy.utils.unregister_class(PreviewQuaternionProceduralOperator)
    bpy.utils.unregister_class(CopyQuaternionProceduralOperator)

    # Quaternion Procedural Trigger Operators
    bpy.utils.unregister_class(AddQuaternionProceduralTriggerOperator)
    bpy.utils.unregister_class(RemoveQuaternionProceduralTriggerOperator)
    bpy.utils.unregister_class(MoveUpQuaternionProceduralTriggerOperator)
    bpy.utils.unregister_class(MoveDownQuaternionProceduralTriggerOperator)
    bpy.utils.unregister_class(SetTriggerQuaternionProceduralTriggerOperator)
    bpy.utils.unregister_class(SetAngleQuaternionProceduralTriggerOperator)
    bpy.utils.unregister_class(SetPositionQuaternionProceduralTriggerOperator)
    bpy.utils.unregister_class(PreviewQuaternionProceduralTriggerOperator)

    # Jiggle Procedural Operators
    bpy.utils.unregister_class(AddJiggleProceduralOperator)
    bpy.utils.unregister_class(RemoveJiggleProceduralOperator)
    bpy.utils.unregister_class(PreviewJiggleProceduralOperator)
    bpy.utils.unregister_class(CopyJiggleProceduralOperator)

    # UI
    bpy.utils.unregister_class(QuaternionProceduralList)
    bpy.utils.unregister_class(QuaternionProceduralTriggerList)
    bpy.utils.unregister_class(QuaternionProceduralPanel)
    bpy.utils.unregister_class(JiggleProceduralList)
    bpy.utils.unregister_class(JiggleProceduralPanel)

    del bpy.types.Object.source_procedural_bone_data
