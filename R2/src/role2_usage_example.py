from typing import TypedDict, Literal
import requests

from pydantic import BaseModel


PORT_R2 = 8002

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

def call_R2_for_scenario_matching_all_matches(user_input : str, threshold : float = 0.5) -> list[PayloadFor_ScenarioMatchingAgent]:
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



if __name__ == "__main__":
	user_input = "I want to buy a car"
	result1 = call_R2_for_ad(user_input)
	print(result1)
	result2 = call_R2_for_scenario_matching_all_matches(user_input)
	print(result2)
	result3 = call_R2_for_scenario_matching_best_match(user_input)
	print(result3)
