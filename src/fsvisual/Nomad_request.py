import requests
import json
import os
import random

base_url = 'http://nomad-lab.eu/prod/v1/api/v1'
base_path_raw = "C:/Fermisurfaces/"
number_of_entries = 20
max_byte_size = "1000000"

response = requests.post(
    f'{base_url}/entries/query',
    json={
        "owner":"visible","query":{"and":[{"results.method.simulation.program_name:any":["exciting"],"authors.name:any":["Qiang Fu"]},{"quantities:all":["results.method.simulation.program_name"]}]},"aggregations":{"results.material.elements:widget":{"terms":{"exclude_from_search":False,"update":True,"size":119,"type":"terms","changed":True,"quantity":"results.material.elements"}},"results.material.symmetry.space_group_symbol:1":{"terms":{"exclude_from_search":True,"update":True,"size":3,"type":"terms","changed":True,"quantity":"results.material.symmetry.space_group_symbol"}},"results.material.structural_type:2":{"terms":{"exclude_from_search":True,"update":True,"size":5,"type":"terms","include":["1D","2D","atom","bulk","molecule / cluster","surface"],"changed":True,"quantity":"results.material.structural_type"}},"results.method.simulation.program_name:3":{"terms":{"exclude_from_search":True,"update":True,"size":3,"type":"terms","changed":True,"quantity":"results.method.simulation.program_name"}},"results.material.symmetry.crystal_system:4":{"terms":{"exclude_from_search":True,"update":True,"size":5,"type":"terms","changed":True,"quantity":"results.material.symmetry.crystal_system"}},"upload_create_time:default_histogram":{"histogram":{"exclude_from_search":True,"update":True,"type":"histogram","buckets":30,"changed":True,"quantity":"upload_create_time"}},"external_db:scroll":{"terms":{"exclude_from_search":True,"update":True,"size":5,"type":"terms","changed":True,"quantity":"external_db"}},"datasets.dataset_name:scroll":{"terms":{"exclude_from_search":True,"update":True,"size":10,"type":"terms","changed":True,"quantity":"datasets.dataset_name"}}},"pagination":{"order_by":"upload_create_time","order":"desc","page_size":number_of_entries},"required":{"exclude":["quantities","sections"]}
        #"owner":"visible","query":{"and":[{"results.method.simulation.program_name:any":["exciting"],"authors.name:any":["Qiang Fu"],"results.material.elements:all":["Ti"]},{"quantities:all":["results.method.simulation.program_name"]}]},"aggregations":{"results.material.elements:widget":{"terms":{"exclude_from_search":False,"update":True,"size":119,"type":"terms","changed":True,"quantity":"results.material.elements"}},"results.material.symmetry.space_group_symbol:1":{"terms":{"exclude_from_search":True,"update":True,"size":5,"type":"terms","changed":True,"quantity":"results.material.symmetry.space_group_symbol"}},"results.material.structural_type:2":{"terms":{"exclude_from_search":True,"update":True,"size":7,"type":"terms","include":["1D","2D","atom","bulk","molecule / cluster","surface"],"changed":True,"quantity":"results.material.structural_type"}},"results.method.simulation.program_name:3":{"terms":{"exclude_from_search":True,"update":True,"size":5,"type":"terms","changed":True,"quantity":"results.method.simulation.program_name"}},"results.material.symmetry.crystal_system:4":{"terms":{"exclude_from_search":True,"update":True,"size":7,"type":"terms","changed":True,"quantity":"results.material.symmetry.crystal_system"}}},"pagination":{"page_size":200,"order_by":"upload_create_time","order":"desc","total":151},"required":{"exclude":["quantities","sections"]}
    })

i = 0
data = response.json()["data"]
for entry in data:
    i += 1
    try:
        files = entry["files"]
        files = [file for file in files if file.endswith(".bxsf")]

        if len(files) == 1:
            bxsf_file = files[0]
            bxsf_file = os.path.basename(bxsf_file)
            method = entry["results"]["method"]["simulation"]["dft"]["xc_functional_type"]
            entry_id = entry["entry_id"]

            element = entry["results"]["material"]["chemical_formula_descriptive"]
            structure_name = entry["results"]["material"]["symmetry"]["structure_name"]

            # Dateipfad
            if method == "GGA":

                functional_name = entry["results"]["method"]["simulation"]["dft"]["xc_functional_names"][0].split("_")[-1]
                if functional_name == "SOL":
                    functional_name = "PBEsol"
                else:
                    functional_name = "PBE"

                file_path = f'{base_path_raw}/GGA/Fermisurf_{element}_{structure_name}_{functional_name}_{entry_id}'
            elif method == "LDA":
                file_path = f'{base_path_raw}/LDA/Fermisurf_{element}_{structure_name}_{entry_id}'
            else:
                file_path = f'{base_path_raw}/unknown/Fermisurf_{element}_{structure_name}_{entry_id}'

            try:
                # Datei herunterladen.
                response2 = requests.get(f'https://nomad-lab.eu/prod/v1/api/v1/entries/{entry_id}/raw/{bxsf_file}?offset=0&length={max_byte_size}&decompress=true', stream=True)
                response.raise_for_status()

                # Datei speichern
                with open(file_path, "wb") as file:
                    for chunk in response2.iter_content(chunk_size=8192):
                        file.write(chunk)

                print(f"Datei wurde erfolgreich gespeichert: {file_path}")

            except requests.exceptions.RequestException as e:
                with open(f"{base_path_raw}/error.txt", 'a') as file:
                    file.write("Fehler beim Herunterladen, " + entry["entry_id"] + '\n')
    except:
        try:
            with open(f"{base_path_raw}/error.txt", 'a') as file:
                file.write(entry["entry_id"] + '\n')
        except KeyError:
            with open(f"{base_path_raw}/error.txt", 'a') as file:
                file.write("critical error")
with open(f"{base_path_raw}/error.txt", 'a') as file:
    file.write("Number of reviewed entries: " + str(i))





