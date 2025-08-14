import requests
import json

BASE_URL = "https://soilhealth4.dac.gov.in/"
HEADERS = {
    "Content-Type": "application/json",
    "Origin": "https://www.soilhealth.dac.gov.in",
    "Referer": "https://www.soilhealth.dac.gov.in/",
}

def run_query(operation_name, query, variables):
    payload = {
        "operationName": operation_name,
        "variables": variables,
        "query": query
    }
    r = requests.post(BASE_URL, headers=HEADERS, data=json.dumps(payload))
    r.raise_for_status()
    return r.json()["data"]

# Get all States
state_query = """
query GetState($getStateId: String, $code: String) {
  getState(id: $getStateId, code: $code)
}
"""
states = run_query("GetState", state_query, {})["getState"]

for state in states:
    state_id = state["_id"]
    state_name = state.get("name", "Unknown")
    print(f"State: {state_name} ({state_id})")

    # Get Districts for State
    district_query = """
    query GetdistrictAndSubdistrictBystate(
      $getdistrictAndSubdistrictBystateId: String,
      $name: String,
      $state: ID,
      $subdistrict: Boolean,
      $code: String,
      $aspirationaldistrict: Boolean
    ) {
      getdistrictAndSubdistrictBystate(
        id: $getdistrictAndSubdistrictBystateId,
        name: $name,
        state: $state,
        subdistrict: $subdistrict,
        code: $code,
        aspirationaldistrict: $aspirationaldistrict
      )
    }
    """
    districts = run_query(
        "GetdistrictAndSubdistrictBystate",
        district_query,
        {"state": state_id}
    )["getdistrictAndSubdistrictBystate"]

    for district in districts:
        district_id = district["_id"]
        district_name = district.get("name", "Unknown")
        print(f"  District: {district_name} ({district_id})")

        # Get Blocks for District
        block_query = """
        query GetBlocks(
          $getBlocksId: String,
          $name: String,
          $code: String,
          $state: ID,
          $district: ID,
          $subdistrict: ID,
          $aspirationalblock: Boolean
        ) {
          getBlocks(
            id: $getBlocksId,
            name: $name,
            code: $code,
            state: $state,
            district: $district,
            subdistrict: $subdistrict,
            aspirationalblock: $aspirationalblock
          )
        }
        """
        blocks = run_query(
            "GetBlocks",
            block_query,
            {"state": state_id, "district": district_id}
        )["getBlocks"]

        for block in blocks:
            block_id = block["_id"]
            block_name = block.get("name", "Unknown")
            print(f"    Block: {block_name} ({block_id})")

            # Get Villages for Block
            village_query = """
            query GetVillageBydistrict(
              $getVillageBydistrictId: String,
              $name: String,
              $state: String,
              $district: ID,
              $subdistrict: String,
              $block: String,
              $code: String
            ) {
              getVillageBydistrict(
                id: $getVillageBydistrictId,
                name: $name,
                state: $state,
                district: $district,
                subdistrict: $subdistrict,
                block: $block,
                code: $code
              )
            }
            """
            villages = run_query(
                "GetVillageBydistrict",
                village_query,
                {"state": state_id, "district": district_id, "block": block_id}
            )["getVillageBydistrict"]

            for village in villages:
                village_id = village["_id"]
                village_name = village.get("name", "Unknown")
                print(f"      Village: {village_name} ({village_id})")

                # Get Nutrient Data for this Village
                nutrient_query = """
                query GetNutrientDashboardForPortal(
                $state: ID,
                $district: ID,
                $block: ID,
                $village: ID,
                $cycle: String,
                $count: Boolean
                ) {
                getNutrientDashboardForPortal(
                    state: $state,
                    district: $district,
                    block: $block,
                    village: $village,
                    cycle: $cycle,
                    count: $count
                  )
                }
                """

                nutrient_data = run_query(
                    "GetNutrientDashboardForPortal",
                    nutrient_query,
                    {
                        "state": state_id,
                        "district": district_id,
                        "block": block_id,
                        "village": village_id,
                        "cycle": "2023-24"
                    }
                )#["getNutrientDashboardForPortal"]

                print(f"        Nutrient Data: {nutrient_data}")