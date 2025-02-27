from typing_extensions import TypedDict, Literal
import requests

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import nltk

PORT_R1  = 8000
PORT_R2  = 8002
PORT_R4  = 8004
PORT_R5  = 8005
PORT_R6  = 8006
PORT_R8  = 8008
PORT_R10 = 8010

# Copy-pasted from R2

ProjectID = str
ProjectData = TypedDict(
	"ProjectData",
	{
		"author"      : str | tuple[str,str],
		"title"       : str,
		"description" : str,
		"elements"    : list[str], # scenarios
		"options"     : list[str],
	},
	total = True,
)
ProjectsDict = dict[ProjectID, ProjectData]

InputText       = list[str]
DocumentID      = str
DocumentContent = list[str]
DocumentDict    = dict[DocumentID, DocumentContent]
ScoresDict      = dict[ProjectID, float]

SentenceModel_Literal = Literal[
	"sbert",
	"google-use-large",
	"google-use-lite",
]
LexiconModel_Literal  = Literal[
	"wordnet",
	"word2vec",
	"glove",
]
ModelQueryKey = SentenceModel_Literal | LexiconModel_Literal

MeanMode_Literal = Literal[
	"arithmetic",
	"softmax",
	"harmonic",
]
WNDistanceMode_Literal = Literal[
	"path",
	"leacock-chodorow",
	"wu-palmer",
	"resnik",
	"jiang-conrath",
	"lin",
]

class PayloadFor_AdAgent(BaseModel):
	user_input   : str
	similarities : ScoresDict

class PayloadFor_ScenarioMatchingAgent(BaseModel):  # corresponds to MatchRequest in R5
	project_id: ProjectID
	user_input: list[str]

class PayloadFor_SentenceMatcher(BaseModel):
	user_input : str
	documents  : DocumentDict           | None
	model      : ModelQueryKey          | None
	mean_mode  : MeanMode_Literal       | None
	dist_mode  : WNDistanceMode_Literal | None
	alpha      : float                  | None
	epsilon    : float                  | None

class PayloadFor_rAIsonAdapter(BaseModel):  # corresponds to MatchRequest in R6
	project_id: str
	user_input: list[str]
	matched_scenarios: list[str]
	info: str


class RawUserInput(BaseModel):
	user_input : str
	get_max    : bool  = False
	threshold  : float = 0.5



def call_R2_for_ad(user_input : str) -> PayloadFor_AdAgent:
	route = "match_for_ad"
	headers = {"Content-Type": "application/json"}
	body = {"user_input": user_input}
	response = requests.post(f"http://localhost:{PORT_R2}/{route}", headers = headers, json = body)
	response.raise_for_status()
	result = PayloadFor_AdAgent(**response.json())
	return result

def call_R2_for_scenario_matching_all_matches(
	user_input : str,
	threshold  : float = 0.5,
) -> list[PayloadFor_ScenarioMatchingAgent]:
	route = "match_for_scenario"
	headers = {"Content-Type": "application/json"}
	body_obj = RawUserInput(user_input = user_input, threshold = threshold)
	body = body_obj.model_dump()
	response = requests.post(f"http://localhost:{PORT_R2}/{route}", headers = headers, json = body)
	response.raise_for_status()
	result = [PayloadFor_ScenarioMatchingAgent(**match_data) for match_data in response.json()]
	return result

def call_R2_for_scenario_matching_best_match(user_input : str) -> PayloadFor_ScenarioMatchingAgent:
	route = "match_for_scenario"
	headers = {"Content-Type": "application/json"}
	body_obj = RawUserInput(user_input = user_input)
	body_obj.get_max = True
	body = body_obj.model_dump()
	response = requests.post(f"http://localhost:{PORT_R2}/{route}", headers = headers, json = body)
	response.raise_for_status()
	best_match = response.json()[0]
	result = PayloadFor_ScenarioMatchingAgent(**best_match)
	return result

def call_R2_for_project_data() -> ProjectsDict:
	route = "project_data"
	headers = {"Content-Type": "application/json"}
	response = requests.get(f"http://localhost:{PORT_R2}/{route}", headers = headers)
	response.raise_for_status()
	result = response.json()
	return result

def call_R4_check_query(session_id : str, user_input : str) -> bool:
	route = "classify_input"
	headers = {"Content-Type": "application/json"}
	body = {"session_id": session_id, "user_message": user_input}
	response = requests.post(f"http://localhost:{PORT_R4}/{route}", headers = headers, json = body)
	response.raise_for_status()
	result = response.json()
	return result

def call_R1_simple(session_id : str, user_input : str) -> str:
	route = "generate"
	headers = {"Content-Type": "application/json"}
	body = {"session_id": session_id, "user_message": user_input}
	response = requests.post(f"http://localhost:{PORT_R1}/{route}", headers = headers, json = body)
	response.raise_for_status()
	result = response.json()["response"]
	return result

def call_R5_for_scenario_matching(payload : PayloadFor_ScenarioMatchingAgent) -> PayloadFor_rAIsonAdapter:
	route = "match"
	headers = {"Content-Type": "application/json"}
	body = payload.model_dump()
	response = requests.post(f"http://localhost:{PORT_R5}/{route}", headers = headers, json = body)
	response.raise_for_status()
	result = PayloadFor_rAIsonAdapter(**response.json())
	return result

def call_R6_for_raison(payload: PayloadFor_rAIsonAdapter) -> str:
	route = "find_solution"
	headers = {"Content-Type": "application/json"}
	body = payload.model_dump()
	response = requests.post(f"http://localhost:{PORT_R6}/{route}", headers = headers, json = body)
	response.raise_for_status()
	result = response.json()["text"]
	return result



#################
# Main pipeline #
#################

SessionID = str
SessionStatus = Literal[
	"check_casual_or_query",
	"casual_chat_call_llm",
	"casual_chat_return_llm_response",
	"query_chat_call_sentence_matcher_for_ad_agent",
	"query_chat_call_ad_agent",
	"query_chat_return_llm_ad_response",
	"query_chat_call_sentence_matcher_for_service_agent_id",
	"query_chat_call_scenario_recognizing_agent",
	"query_chat_call_raison_adapter",
	"query_chat_return_raison_response",
]


def middleware_pipeline(
	session_id : SessionID,
	user_input : str,
)-> str:
	"""
	Orchestrates the entire pipeline:
	- if in the "check_casual_or_query" mode, calls R4 to see whther the user is
	   just talking or asking for help
	- if in the "casual_chat_call_llm" mode, calls R1 LLM to generate a response
	- if in the "casual_chat_return_llm_response" mode, returns the LLM response to GUI
	- if in the "query_chat_call_sentence_matcher_for_ad_agent" mode, calls R2 to
	   match the user input with project descriptions
	- if in the "query_chat_call_ad_agent" mode, calls R8 to get the ad for the relevant services
	- if in the "query_chat_return_llm_ad_response" mode, returns the R8 response to GUI
	- if in the "query_chat_call_sentence_matcher_for_service_agent_id" mode, calls R2 to
	    get the matching project ID
	- if in the "query_chat_call_scenario_recognizing_agent" mode, calls R5 to match the user
	    input with scenarios
	- if in the "query_chat_call_raison_adapter" mode, calls R6 to get run the scenario choice on rAIson
	- if in the "query_chat_return_raison_response" mode, returns the R6 response to GUI
	"""
	if session_id not in ONGOING_STATUSES:
		ONGOING_STATUSES[session_id] = ("check_casual_or_query", None)
	previous_status               = ONGOING_STATUSES[session_id][0]
	project_id : ProjectID | None = ONGOING_STATUSES[session_id][1]
	current_status : SessionStatus
	if previous_status in [
		"check_casual_or_query",
		"casual_chat_return_llm_response",
		"query_chat_return_raison_response",
	]:
		current_status = "check_casual_or_query"
		project_id = None
	elif previous_status == "query_chat_return_llm_ad_response":
		current_status = "query_chat_call_sentence_matcher_for_service_agent_id"
	else:
		raise ValueError(f"Invalid previous status: {previous_status}")
	if current_status == "check_casual_or_query":
		bool_response = call_R4_check_query(session_id, user_input)
		if bool_response:
			print("R4: Query detected")
			current_status = "query_chat_call_sentence_matcher_for_ad_agent"
		else:
			print("R4: Casual talk detected")
			current_status = "casual_chat_call_llm"
		if current_status == "casual_chat_call_llm":
			text_response = call_R1_simple(session_id, user_input)
			current_status = "casual_chat_return_llm_response"
			result = text_response
		elif current_status == "query_chat_call_sentence_matcher_for_ad_agent":
			# ranked_matched_services = call_R2_for_ad(user_input)
			# current_status = "query_chat_call_ad_agent"
			# ad_text = call_R8_for_ad(session_id, ranked_matched_services)
			# matches = call_R2_for_scenario_matching_all_matches(user_input, threshold = 0.0)
			matches = [PayloadFor_ScenarioMatchingAgent(
				project_id = project_id,
				user_input = nltk.sent_tokenize(user_input),
			)]
			print(f"R2: Found {len(matches)} matches for ads: {matches}")
			if len(matches) == 0:
				result = (
					"I'm sorry, I couldn't find any relevant services that could help you. "
					"But maybe I could help you with something else ?"
				)
				current_status = "check_casual_or_query"
			else:
				project_id = matches[0].project_id
				projects_desc = [PROJECTS_DATA[match.project_id]["description"] for match in matches]
				ad_text = "Hm, I think you might be interested in some of our services !\n" + "\n".join(projects_desc)
				result = (
					ad_text + "\n\nPlease let me know if any of these might interest you, and "
					"also tell us how we could be of help (describe your situation)."
				)
				current_status = "query_chat_return_llm_ad_response"
		else:
			raise ValueError(f"Invalid current status: {current_status}")
	elif current_status == "query_chat_call_sentence_matcher_for_service_agent_id":
		best_matched_service = call_R2_for_scenario_matching_best_match(user_input)
		print(f"R2: best matched service {best_matched_service}")
		current_status = "query_chat_call_scenario_recognizing_agent"
		scenarios = call_R5_for_scenario_matching(best_matched_service)
		print(f"R5: scenarios {scenarios}")
		current_status = "query_chat_call_raison_adapter"
		raison_response = call_R6_for_raison(scenarios)
		print(f"R6: raison_response {raison_response}")
		current_status = "query_chat_return_raison_response"
		result = raison_response + "\nWill you be need anything else ?"
	else:
		raise ValueError(f"Invalid current status: {current_status}")
	ONGOING_STATUSES[session_id] = (current_status, project_id)
	return result



##################
# API definition #
##################

app = FastAPI(swagger_ui_parameters={"syntaxHighlight": False})

# useful for when frontend is hosted on a different domain
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],  # Change this to the origin(s) of your React app
    allow_credentials = True,
    allow_methods     = ["POST"],
    allow_headers     = ["*"],
)

class BrokerPayload(BaseModel):
	session_id: SessionID
	user_input: str

@app.post("/pipeline", response_model=str)
def pipeline_endpoint(request: BrokerPayload):
	"""
	Receives a session ID and a user input, and returns the response generated by the pipeline.
	"""
	session_id = request.session_id
	user_input = request.user_input
	response = middleware_pipeline(session_id, user_input)
	return response


if __name__ == "__main__":
	PROJECTS_DATA : ProjectsDict = call_R2_for_project_data()
	ONGOING_STATUSES : dict[SessionID, tuple[SessionStatus, ProjectID | None]] = {}
	uvicorn.run(app, host="0.0.0.0", port=PORT_R10)
