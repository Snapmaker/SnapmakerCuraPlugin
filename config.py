SNAPMAKER_2_A150_DUAL_EXTRUDER = dict(
    name="Snapmaker 2.0 A150 Dual Extruder",
    model="Snapmaker 2 Model A150",
    header_version=0,  # default is 1
)

SNAPMAKER_2_A250_DUAL_EXTRUDER = dict(
    name="Snapmaker 2.0 A250 Dual Extruder",
    model="Snapmaker 2 Model A250",
    header_version=0,
)

SNAPMAKER_2_A350_DUAL_EXTRUDER = dict(
    name="Snapmaker 2.0 A350 Dual Extruder",
    model="Snapmaker 2 Model A350",
    header_version=0,
)

SNAPMAKER_J1 = dict(
    name="Snapmaker J1",
    model="Snapmaker J1",
    header_version=1,  # default is 1
)

SNAPMAKER_ARTISAN = dict(
    name="Snapmaker Artisan",
    model="Snapmaker Artisan",
    header_version=1,
)

SNAPMAKER_DISCOVER_MACHINES = [
    SNAPMAKER_J1,
    SNAPMAKER_ARTISAN,
    SNAPMAKER_2_A150_DUAL_EXTRUDER,
    SNAPMAKER_2_A250_DUAL_EXTRUDER,
    SNAPMAKER_2_A350_DUAL_EXTRUDER,
]


def is_machine_discover_supported(machine_name: str) -> bool:
    return machine_name in [machine['name'] for machine in SNAPMAKER_DISCOVER_MACHINES]
