from ollama import ChatResponse, chat
import json

def get_llm_verdict(zone_id: str, gas_type : str, gas_ppm : float, permits : list) -> dict:
    permit_details = [f"{p['work_type']} by {p['assigned_team']}" for p in permits]

    prompt = f"""
            You are an industrial safety AI for a heavy manufacturing plant in India.
            Return ONLY a JSON object, no explanation, no markdown, no thinking.

            Situation:
            - Zone: {zone_id}
            - Gas detected: {gas_type} at {gas_ppm} PPM
            - Active permits: {', '.join(permit_details)}

            Safety thresholds:
            - CO is dangerous above 25 PPM with hot work. Below that with good ventilation is SAFE.
            - H2S above 10 PPM with any permit is CRITICAL. Below is manageable.
            - O2 below 19.5% with confined space permit is CRITICAL.
            - CH4 above 5% LEL with hot work is CRITICAL.
            - SO2 above 5 PPM with any permit is CRITICAL.

            Evaluate the situation carefully. If gas levels are elevated but still within safe working limits, return OPERATIONS_CLEAR.
            Only return CRITICAL_HAZARD_VIOLATION if the combination of gas level and permit type creates genuine danger.

            Return exactly:
            {{"status_code": "CRITICAL_HAZARD_VIOLATION" or "OPERATIONS_CLEAR", "reason": "one line in English", "audio_phrase_hindi": "short Hindi warning for walkie talkie, empty string if OPERATIONS_CLEAR"}}
        """
    
    response : ChatResponse = chat(
        model="qwen3:0.6b",
        messages=[{"role": "user", "content" : prompt}],
        options={"num_predict": 200, "temperature": 0}
    )

    raw = response["message"]["content"]
    raw = raw[raw.find("{"):raw.rfind("}")+1]

    return json.loads(raw)

# result = get_llm_verdict(
#     zone_id="battery_4",
#     gas_type="CO",
#     gas_ppm=2.4,
#     permits=[{"work_type": "hot_work", "assigned_team": "Contractor Team B"}]
# )

# print(result)