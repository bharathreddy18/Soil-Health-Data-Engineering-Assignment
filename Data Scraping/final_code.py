import os
import pandas as pd
import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S', filename='data_scraping.log', filemode='w')

BASE_URL = "https://soilhealth4.dac.gov.in/"
HEADERS = {
    "Content-Type": "application/json",
    "Origin": "https://www.soilhealth.dac.gov.in",
    "Referer": "https://www.soilhealth.dac.gov.in/",
}
CYCLES = ["2023-24", "2024-25"]

def run_query(operation_name, query, variables):
    payload = {
        "operationName": operation_name,
        "query": query,
        "variables": variables
    }
    r = requests.post(BASE_URL, headers=HEADERS, json=payload)
    r.raise_for_status()
    return r.json()["data"]

# State query
state_query = """
query GetState {
  getState
}
"""

# District query
district_query = """
query GetdistrictAndSubdistrictBystate(
  $state: ID
) {
  getdistrictAndSubdistrictBystate(
    state: $state
  )
}
"""

# Block query
block_query = """
query GetBlocks(
  $state: ID,
  $district: ID
) {
  getBlocks(
    state: $state,
    district: $district
  )
}
"""

# Village query
village_query = """
query GetVillageBydistrict(
  $state: String,
  $district: ID,
  $block: String
) {
  getVillageBydistrict(
    state: $state,
    district: $district,
    block: $block
  )
}
"""

# Nutrient data query
nutrient_query = """
query GetNutrientDashboardForPortal(
  $state: ID,
  $district: ID,
  $block: ID,
  $village: ID,
  $cycle: String
) {
  getNutrientDashboardForPortal(
    state: $state,
    district: $district,
    block: $block,
    village: $village,
    cycle: $cycle
  ) 
}
"""

# Base data directory
data_dir = os.path.join(os.getcwd(), "data", "raw")
os.makedirs(data_dir, exist_ok=True)

for cycle in CYCLES:
    print(f"Processing Cycle: {cycle}")
    states = run_query("GetState", state_query, {})["getState"]

    for state in states:
        state_id = state["_id"]
        state_name = state.get("name", "Unknown").strip().replace("/", "_")

        districts = run_query(
            "GetdistrictAndSubdistrictBystate",
            district_query,
            {"state": state_id}
        )["getdistrictAndSubdistrictBystate"]

        for district in districts:
            district_id = district["_id"]
            district_name = district.get("name", "Unknown").strip().replace("/", "_")

            blocks = run_query(
                "GetBlocks",
                block_query,
                {"state": state_id, "district": district_id}
            )["getBlocks"]

            for block in blocks:
                block_id = block["_id"]
                block_name = block.get("name", "Unknown").strip().replace("/", "_")

                print(f"Processing Block: {state_name} / {district_name} / {block_name}")
                block_rows = []

                villages = run_query(
                    "GetVillageBydistrict",
                    village_query,
                    {"state": state_id, "district": district_id, "block": block_id}
                )["getVillageBydistrict"]

                for village in villages:
                    village_id = village["_id"]
                    village_name = village.get("name", "Unknown")

                    nutrient_data = run_query(
                        "GetNutrientDashboardForPortal",
                        nutrient_query,
                        {
                            "state": state_id,
                            "district": district_id,
                            "block": block_id,
                            "village": village_id,
                            "cycle": cycle
                        }
                    )["getNutrientDashboardForPortal"]

                    flattened_data = []
                    existing_villages = set()

                    for item in nutrient_data:
                        v_name = item['village']['name']

                        if v_name in existing_villages:
                            continue

                        flat_dict = {'cycle': cycle, 'state': state_name, 'district': district_name,'block': block_name,'village': v_name}

                        if item.get('results'):
                            for key, val in item.items():
                                if key == 'results':
                                    for sub_key, sub_val in val.items():
                                        for sub_key2, sub_val2 in sub_val.items():
                                            col_name = f"{sub_key}_{sub_key2}"
                                            flat_dict[col_name] = sub_val2
                        
                        flattened_data.append(flat_dict)
                        existing_villages.add(v_name)


                # Save CSV
                folder_path = os.path.join(data_dir, cycle, state_name, district_name)
                os.makedirs(folder_path, exist_ok=True)
                filename = block_name.split('-')[0].strip().replace(" ", "_") + ".csv"
                filepath = os.path.join(folder_path, filename)
                df = pd.DataFrame(flattened_data)
                if not df.empty:
                    df.to_csv(filepath, index=False)
                    print(f"{cycle}/{state_name}/{district_name}/{filename} saved with {len(flattened_data)} records.")
                else:
                    logging.info(f"No data found for {cycle}/{state_name}/{district_name}/{block_name}. Skipping.....")