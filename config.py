# Machine name, or machine series
MACHINE_NAME = "Snapmaker J1"

SNAPMAKER_J1 = dict(
    name="Snapmaker J1",
    model="Snapmaker J1",
)

SNAPMAKER_ARTISAN = dict(
    name="Snapmaker Artisan",
    model="Snapmaker Artisan",
)

SNAPMAKER_2_A150_DUAL_EXTRUDER = dict(
    name="Snapmaker 2.0 A150 Dual Extruder",
    model="Snapmaker 2 Model A150",
)

SNAPMAKER_2_A250_DUAL_EXTRUDER = dict(
    name="Snapmaker 2.0 A250 Dual Extruder",
    model="Snapmaker 2 Model A250",
)

SNAPMAKER_2_A350_DUAL_EXTRUDER = dict(
    name="Snapmaker 2.0 A350 Dual Extruder",
    model="Snapmaker 2 Model A350",
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
