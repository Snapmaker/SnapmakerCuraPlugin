# Machine name, or machine series
MACHINE_NAME = "Snapmaker J1"

SNAPMAKER_J1 = dict(
    name="Snapmaker J1",
)

SNAPMAKER_ARTISAN = dict(
    name="Snapmaker Artisan",
)


def is_machine_supported(machine_name: str) -> bool:
    if machine_name == SNAPMAKER_J1['name']:
        return True

    if machine_name == SNAPMAKER_ARTISAN['name']:
        return True

    return False
