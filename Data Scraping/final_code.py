import os
import pandas as pd
import requests
import logging
from pathlib import Path
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S', filename='data_scraping.log', filemode='w')

BASE_URL = "https://soilhealth4.dac.gov.in/"
HEADERS = {
    "Content-Type": "application/json",
    "Origin": "https://www.soilhealth.dac.gov.in",
    "Referer": "https://www.soilhealth.dac.gov.in/",
}
CYCLES = ["2023-24", "2024-25"]
CHECKPOINT_FILE = "checkpoint.json"
MAX_TRIES = 3

# Initialize the checkpoint file if not there already
def init_checkpoint():
    if not os.path.exists(CHECKPOINT_FILE):
        checkpoint = {
            "last_cycle": None,
            "last_state": None,
            "last_district": None,
            "last_block": None,
            "fail_count": 0
        }
        with open(CHECKPOINT_FILE, 'w') as f:
            json.dump(checkpoint, f)

# Saves the current processing block
def save_checkpoint(cycle, state_id, state_name, district_id, district_name, block_id, block_name, fail_count=0):
    checkpoint = {
        "last_cycle": cycle,
        "last_state": {'id': state_id, 'name': state_name},
        "last_district": {'id': district_id, 'name': district_name},
        "last_block": {'id': block_id, 'name': block_name},
        "fail_count": fail_count
    }
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump(checkpoint, f, indent=2)

# loads the checkpoint (where we left off)
def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, 'r') as f:
            return json.load(f)
    return {"last_cycle": None, "last_state": None, "last_district": None, "last_block": None, "fail_count": 0}

# sends request to url and gets back response
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

# Nutrient query
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

def main():
    init_checkpoint()
    checkpoint = load_checkpoint()
    skip_until = checkpoint['last_cycle'] is not None   # Returns boolean

    # creates the data directory
    data_dir = Path.cwd()/"data"/"raw"
    os.makedirs(data_dir, exist_ok=True)

    for cycle in CYCLES:
        try:
            print(f"Processing Cycle: {cycle}")
            states = run_query("GetState", state_query, {})["getState"]

            for state in states:
                try:
                    state_id = state["_id"]
                    state_name = state.get("name", "Unknown").strip().replace("/", "_")

                    districts = run_query(
                        "GetdistrictAndSubdistrictBystate",
                        district_query,
                        {"state": state_id}
                    )["getdistrictAndSubdistrictBystate"]

                    for district in districts:
                        try:
                            district_id = district["_id"]
                            district_name = district.get("name", "Unknown").strip().replace("/", "_")

                            blocks = run_query(
                                "GetBlocks",
                                block_query,
                                {"state": state_id, "district": district_id}
                            )["getBlocks"]

                            for block in blocks:
                                try:
                                    block_id = block["_id"]
                                    block_name = block.get("name", "Unknown").strip().replace("/", "_")

                                    # Checks if are ahead of the checkpoint
                                    if skip_until:
                                        if (checkpoint['last_cycle'] == cycle and
                                            checkpoint['last_state']['id'] == state_id and
                                            checkpoint['last_district']['id'] == district_id and
                                            checkpoint['last_block']['id'] == block_id):

                                            # If error in scraping same block for 3 times(MAX_TRIES) in a row, we skip this and continue to next block.
                                            if checkpoint.get('fail_count', 0) >= MAX_TRIES:
                                                logging.info(f"Skipping {cycle}/{state_name}/{district_name}/{block_name} after 3 failed attempts.")
                                                skip_until = True
                                                continue
                                            else:
                                                skip_until = False
                                        else:
                                            print(f'Skipping {cycle}/{state_name}/{district_name}/{block_name} (checkpoint not reached).')
                                            continue

                                    folder_path = os.path.join(data_dir, cycle, state_name, district_name)
                                    os.makedirs(folder_path, exist_ok=True)
                                    filename = block_name.split('-')[0].strip().replace(" ", "_") + ".csv"
                                    filepath = os.path.join(folder_path, filename)

                                    # If the block already exists, we skip and continue to next one
                                    if os.path.exists(filepath):
                                        logging.info(f"Skipping {cycle}/{state_name}/{district_name}/{block_name} - file already exists.")
                                        print(f"skipping {cycle}/{state_name}/{district_name}/{block_name} (already saved).")
                                        continue
                                    
                                    # Save checkpoint before processing
                                    save_checkpoint(cycle, state_id, state_name, district_id, district_name, block_id, block_name)

                                    print(f"Processing Block: {cycle} / {state_name} / {district_name} / {block_name}")
                                    flattened_data = []
                                    existing_villages = set()

                                    villages = run_query(
                                        "GetVillageBydistrict",
                                        village_query,
                                        {"state": state_id, "district": district_id, "block": block_id}
                                    )["getVillageBydistrict"]

                                    for village in villages:
                                        try:
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

                                            for item in nutrient_data:
                                                v_name = item['village']['name']

                                                if v_name in existing_villages:
                                                    continue

                                                flat_dict = {
                                                    'cycle': cycle,
                                                    'state': state_name, 
                                                    'district': district_name,
                                                    'block': block_name,
                                                    'village': v_name
                                                }

                                                if item.get('results'):
                                                    for key, val in item.items():
                                                        if key == 'results':
                                                            for sub_key, sub_val in val.items():
                                                                for sub_key2, sub_val2 in sub_val.items():
                                                                    col_name = f"{sub_key}_{sub_key2}"
                                                                    flat_dict[col_name] = sub_val2
                                                
                                                flattened_data.append(flat_dict)
                                                existing_villages.add(v_name)
                                        except Exception as e:
                                            logging.error(f"Village loop failed for {village_name} in {cycle}/{state_name}/{district_name}/{block_name}: {e}", exc_info=True)

                                    # Saves the data to csv
                                    df = pd.DataFrame(flattened_data)
                                    if not df.empty:
                                        df.to_csv(filepath, index=False)
                                        print(f"{cycle}/{state_name}/{district_name}/{filename} saved with {len(flattened_data)} records.")
                                        save_checkpoint(cycle, state_id, state_name, district_id, district_name, block_id, block_name, 0)
                                    else:
                                        logging.info(f"No data found for {cycle}/{state_name}/{district_name}/{block_name}. Skipping.....")
                                except Exception as e:
                                    checkpoint = load_checkpoint()
                                    fail_count = checkpoint.get('fail_count', 0) + 1
                                    save_checkpoint(cycle, state_id, state_name, district_id, district_name, block_id, block_name, fail_count)
                                    if fail_count >= MAX_TRIES:
                                        logging.error(f"Block failed 3 times, skipping {cycle}/{state_name}/{district_name}/{block_name}.")
                                        continue
                                    logging.error(f"Block loop failed for {cycle}/{state_name}/{district_name}/{block_name}: {e}", exc_info=True)
                        except Exception as e:
                            logging.error(f"District loop failed for {cycle}/{state_name}/{district_name}: {e}", exc_info=True)
                except Exception as e:
                    logging.error(f"State loop failed for {cycle}/{state_name}: {e}", exc_info=True)
        except Exception as e:
            logging.error(f"Cycle loop failed for {cycle}: {e}", exc_info=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        checkpoint = load_checkpoint()
        fail_count = checkpoint.get('fail_count', 0) + 1
        save_checkpoint(
            checkpoint['last_cycle'],
            checkpoint['last_state']['id'], checkpoint['last_state']['name'],
            checkpoint['last_district']['id'], checkpoint['last_district']['name'],
            checkpoint['last_block']['id'], checkpoint['last_block']['name'],
            fail_count
        )
        logging.error(f"An error occurred: {e}", exc_info=True)
        print(f"An error occurred: {e}")