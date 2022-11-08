
# Ignore some keys that they shouldn't be in quality definition.
IGNORED_QUALITY_KEYS = {
    # layer height
    "adaptive_layer_height_enabled",  # should be =false

    # wall
    "fill_outline_gaps",  # =True
    "wall_material_flow",
    "wall_line_width_x",  # unable to set
    "xy_offset",

    # top/bottom

    # infill
    "infill_line_width",  # =line_width
    "infill_overlap_mm",  # =formula
    "infill_wipe_dist",  # =formula

    # bridge
    "bridge_fan_speed_2",
    "bridge_fan_speed_3",
    "bridge_skin_density_2",
    "bridge_skin_density_3",
    "bridge_skin_speed_2",
    "bridge_skin_speed_3",

    # travel
    "travel_retract_before_outer_wall",  # =False
    "retraction_count_max",
    "retraction_extrusion_window",

    # z seam
    "z_seam_type",
    "z_seam_x",
    "z_seam_y",

    # cooling
    "cool_fan_full_layer",  # =2
    "cool_fan_speed",  # =100

    # adhesion
    "adhesion_type",  # =skirt

    # support
    "support_enable",  # =False, per-object
    "support_extruder_nr",

    # material
    "skin_material_flow",

    # mesh fix
    "carve_multiple_volumes",  # true by default
    "multiple_mesh_overlap",  # 0.15 by default

    # blackmagic?
    "relative_extrusion",

    # deprecated in Cura 5
    "outer_inset_first",
    "speed_equalize_flow_enabled",
    "speed_equalize_flow_max",
    "travel_compensate_overlapping_walls_enabled",
}

# We use a unified quality keys to ensure every quality instances share
# the same key set. Thus we won't miss something when modifying them.
QUALITY_KEYS = {
    # layer height
    "layer_height",
    "layer_height_0",

    # wall
    "wall_thickness",
    "wall_line_count",
    "infill_before_walls",
    "optimize_wall_printing_order",
    "wall_overhang_angle",
    "wall_overhang_speed_factor",

    # top/bottom
    "bottom_layers",
    "top_bottom_thickness",
    "bottom_thickness",
    "top_layers",
    "top_bottom_pattern",
    "top_bottom_pattern_0",
    "initial_layer_line_width_factor",

    # infill
    "infill_pattern",  # triangle
    "infill_sparse_density",

    # speed
    "speed_slowdown_layers",
    "skirt_brim_speed",  # TODO: check again
    "speed_print",
    "speed_layer_0",
    "speed_print_layer_0",
    "speed_wall",
    "speed_wall_0",
    "speed_wall_x",
    "speed_topbottom",
    "speed_infill",
    "speed_travel",
    "speed_travel_layer_0",
    "speed_prime_tower",

    # bridge
    "bridge_settings_enabled",
    "bridge_enable_more_layers",  # we'd like to set it to False in all qualities
    "bridge_wall_material_flow",  # =100
    "bridge_wall_speed",  # =50
    "bridge_skin_material_flow",  # =100
    "bridge_skin_speed", # =50

    # travel
    "travel_avoid_distance",
    "travel_avoid_supports",
    "retraction_combing",  # =no_outer_surfaces, at least for J1
    "retraction_amount",
    "retraction_speed",
    "retraction_hop_enabled",
    "retraction_hop_only_when_collides",

    # z seam
    "z_seam_type",
    "z_seam_position",

    # Acceleration
    # different qualities can set different accelerations
    "acceleration_enabled",
    "acceleration_layer_0",
    "acceleration_print",
    "acceleration_topbottom",
    "acceleration_travel_layer_0",
    "acceleration_travel",
    "acceleration_wall",
    "acceleration_wall_0",
    "acceleration_wall_x",
    "acceleration_prime_tower",

    # cooling
    "cool_min_layer_time",
    "cool_min_speed",

    # adhesion
    "brim_line_count",  # lower
    "skirt_gap",  # use smaller gap
    "skirt_line_count",

    # material
    "material_bed_temperature",  # should be different for different materials TODO: re-check this later
    "material_bed_temperature_layer_0",
    "material_print_temperature",
    "material_print_temperature_layer_0",
    "material_standby_temperature",
    "material_initial_print_temperature",
    "material_final_print_temperature",

    # dual
    "prime_tower_enable",  # defaults to False
    "prime_tower_position_x",
    "prime_tower_position_y",
    "switch_extruder_retraction_amount",
    "switch_extruder_retraction_speeds",  # no use
    "switch_extruder_retraction_speed",

    # exp
    "slicing_tolerance",  # default middle, we use inclusive
}
