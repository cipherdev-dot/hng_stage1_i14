import httpx
import asyncio
from typing import Dict

class ExternalAPIError(Exception):
    def __init__(self, api_name: str):
        self.api_name = api_name
        super().__init__(f"{api_name} returned an invalid response")

def classify_age_group(age: int) -> str:
    if 0 <= age <= 12:
        return "child"
    elif 13 <= age <= 19:
        return "teenager"
    elif 20 <= age <= 59:
        return "adult"
    else:
        return "senior"

async def fetch_profile_data(name: str) -> Dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        genderize_task = client.get(f"https://api.genderize.io?name={name}")
        agify_task = client.get(f"https://api.agify.io?name={name}")
        nationalize_task = client.get(f"https://api.nationalize.io?name={name}")
        
        responses = await asyncio.gather(genderize_task, agify_task, nationalize_task)
        
        genderize_data = responses[0].json()
        agify_data = responses[1].json()
        nationalize_data = responses[2].json()
    
    # Validate Genderize response
    if genderize_data.get("gender") is None or genderize_data.get("count", 0) == 0:
        raise ExternalAPIError("Genderize")
    
    # Validate Agify response
    if agify_data.get("age") is None:
        raise ExternalAPIError("Agify")
    
    # Validate Nationalize response
    countries = nationalize_data.get("country", [])
    if not countries or len(countries) == 0:
        raise ExternalAPIError("Nationalize")
    
    # Get highest probability country
    top_country = max(countries, key=lambda x: x["probability"])
    
    # Classify age group
    age = agify_data["age"]
    age_group = classify_age_group(age)
    
    return {
        "name": name,
        "gender": genderize_data["gender"],
        "gender_probability": genderize_data["probability"],
        "sample_size": genderize_data["count"],
        "age": age,
        "age_group": age_group,
        "country_id": top_country["country_id"],
        "country_probability": top_country["probability"]
    }
