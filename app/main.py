from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import asyncio
from moderation import check_policy
from further_info_analyzer import get_further_info_fc_pydantic_schema
from final_plan_generator import get_final_plan
from time_series_tasks_generator import get_time_series_data_tool_call
from time_series_tasks_generator import Tasks
from further_info_analyzer import FurtherInfoResponse
app = FastAPI(title="AI Planning Service", version="1.0.0")

# Allow all CORS origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Request & Response Models
# ---------------------------

class GoalRequest(BaseModel):
    goal: str
    plan: str

class FinalPlanRequest(BaseModel):
    goal: str
    info_needed: List[Dict]

class FinalPlanResponse(BaseModel):
    plan: str

class TimeSeriesPlanRequest(BaseModel):
    user_goal: str
    user_plan: str
    further_info: Dict
    final_plan: str

# ---------------------------
# API Endpoints
# ---------------------------

@app.post("/check-policy/", summary="Check if the provided goal and plan comply with our policies")

async def check_policy_endpoint(request: GoalRequest):
    try:
        # Wrap the synchronous function using asyncio.to_thread
        result = await asyncio.to_thread(check_policy, request.goal, request.plan)
        return {"compliant": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Policy check failed: {str(e)}")

@app.post("/get-further-info/", response_model=FurtherInfoResponse, summary="Analyze input to determine further information requirements")
async def further_info_endpoint(request: GoalRequest):
    try:
        result = await asyncio.to_thread(get_further_info_fc_pydantic_schema, request.goal, request.plan)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get further info: {str(e)}")

@app.post("/get-final-plan/", response_model=FinalPlanResponse, summary="Generate a final plan based on user input")
async def final_plan_endpoint(request: FinalPlanRequest):
    try:
        # Here we assume the user's additional details come as a list of dicts
        user_details = request.info_needed
        result = await asyncio.to_thread(get_final_plan, request.goal, user_details)
        return {"plan": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plan generation failed: {str(e)}")

@app.post("/get-time-series/", response_model=Tasks, summary="Generate time series data from the final plan")
async def time_series_endpoint(request: TimeSeriesPlanRequest):
    try:
        result = await asyncio.to_thread(get_time_series_data_tool_call, request.user_goal, request.user_plan, request.further_info, request.final_plan)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Time series generation failed: {str(e)}")

# ---------------------------
# Run the service
# ---------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)