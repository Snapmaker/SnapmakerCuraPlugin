# Snapmaker Profiles

3D printing profiles for Snapmaker printers.


Working on:
- Snapmaker J1 profiles


## Scripts

- Import Cura profile:
 
```Shell
python -m scripts.import_curaprofile {Cura profile file} {output folder}
```

- Run checks on quality profile, and format it:

```Shell
python -m scripts.validate_machine_quality {quality file}
```