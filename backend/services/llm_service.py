from ollama import ChatResponse, chat
import json

def get_llm_verdict(zone_id: str, gas_type : str, gas_ppm : float, permits : list) -> dict:
    permit_details = [f"{p['work_type']} by {p['assigned_team']}" for p in permits]

    prompt = f"""
            You are an industrial safety AI for a heavy manufacturing plant.
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
            {{"status_code": "CRITICAL_HAZARD_VIOLATION" or "OPERATIONS_CLEAR", "reason": "one line in English", "audio_phrase": "short English warning phrase for walkie talkie, empty string if OPERATIONS_CLEAR"}}
        """
    
    try:
        response : ChatResponse = chat(
            model="qwen3:0.6b",
            messages=[{"role": "user", "content" : prompt}],
            options={"num_predict": 200, "temperature": 0}
        )

        raw = response["message"]["content"]
        if "{" in raw and "}" in raw:
            raw = raw[raw.find("{"):raw.rfind("}")+1]
            data = json.loads(raw)
            # Guarantee English audio_phrase across all fields
            phrase = data.get("audio_phrase") or data.get("audio_phrase_hindi") or ""
            data["audio_phrase"] = phrase
            data["audio_phrase_hindi"] = phrase
            return data
    except Exception as e:
        print(f"[LLM ERROR/FALLBACK] Qwen inference failed ({e}), using deterministic safety fallback.")

    # Deterministic fallback evaluation if Ollama/model fails or is unavailable
    status_code = "OPERATIONS_CLEAR"
    reason = f"{gas_type} detected at {gas_ppm} PPM, currently manageable under standard safety protocol."
    audio_phrase = ""

    permit_types = [p["work_type"].upper() for p in permits]
    is_hot_work = any("HOT_WORK" in pt or "WELDING" in pt for pt in permit_types)
    is_confined = any("CONFINED_SPACE" in pt for pt in permit_types)

    if (gas_type == "CO" and gas_ppm > 25 and is_hot_work) or \
       (gas_type == "H2S" and gas_ppm > 10) or \
       (gas_type == "O2" and gas_ppm < 19.5 and is_confined) or \
       (gas_type == "CH4" and gas_ppm > 5 and is_hot_work) or \
       (gas_type == "SO2" and gas_ppm > 5):
        status_code = "CRITICAL_HAZARD_VIOLATION"
        reason = f"{gas_type} at {gas_ppm} PPM with active work permit ({', '.join(permit_types)}) creates immediate danger."
        audio_phrase = f"Warning! Evacuate {zone_id} immediately! High {gas_type} hazard detected."

    return {
        "status_code": status_code,
        "reason": reason,
        "audio_phrase": audio_phrase,
        "audio_phrase_hindi": audio_phrase
    }