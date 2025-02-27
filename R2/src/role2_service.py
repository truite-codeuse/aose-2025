
from uvicorn                 import run as uvc_run
from pydantic                import BaseModel
from fastapi                 import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from nltk                    import sent_tokenize


from .project_data     import (
	ProjectID,
	RAISON_PROJECTS,
	update_raison_projects_data,
	document_dict_from_project_dict,
	ProjectsDict,
)
from .sentence_matcher import (
	DocumentDict,
	ScoresDict,
	ModelQueryKey,
	MeanMode_Literal,
	WNDistanceMode_Literal,
	load_all_models,
	get_sentence_matching_scores,
)



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



app = FastAPI(swagger_ui_parameters={"syntaxHighlight": False})

# useful for when frontend is hosted on a different domain
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],  # Change this to the origin(s) of your React app
    allow_credentials = True,
    allow_methods     = ["GET", "POST"],
    allow_headers     = ["*"],
)


@app.post("/match", response_model=ScoresDict)
def match_endpoint(request: PayloadFor_SentenceMatcher):
	"""
	Receives a configuration body for the sentence matcher, processes the matching
	using the chosen algorithm, and returns the matching scores as a dictionary.
	"""
	safe_documents = (
		document_dict_from_project_dict(RAISON_PROJECTS)
		if request.documents is None else
		request.documents
	)
	scores = get_sentence_matching_scores(
		MODELS,
		safe_documents,
		[request.user_input],
		request.model,
		request.mean_mode,
		request.dist_mode,
		request.alpha,
		request.epsilon,
	)
	return scores


@app.post("/match_for_ad", response_model=PayloadFor_AdAgent)
def match_ad_endpoint(request: RawUserInput):
	"""
	Receives a user input and returns the similarities between the user input
	and the descriptions of the projects.
	"""
	scores = get_sentence_matching_scores(
		MODELS,
		document_dict_from_project_dict(RAISON_PROJECTS),
		[request.user_input],
	)
	result = PayloadFor_AdAgent(user_input=request.user_input, similarities=scores)
	return result


@app.post("/match_for_scenario", response_model=list[PayloadFor_ScenarioMatchingAgent])
def match_scenario_endpoint(request: RawUserInput):
	"""
	Receives a user input and returns the matched scenarios.
	"""
	input_sentences = sent_tokenize(request.user_input)
	scores = get_sentence_matching_scores(
		MODELS,
		document_dict_from_project_dict(RAISON_PROJECTS),
		input_sentences,
		model_key = "sbert",
	)
	if request.get_max:
		matched_projects = [list(scores.items())[0][0]]
	else:
		matched_projects = [
			project_id
			for project_id, score in scores.items()
			if score > request.threshold
		]
	result = [
		PayloadFor_ScenarioMatchingAgent(
			project_id = matched_project,
			user_input = input_sentences,
		)
		for matched_project in matched_projects
	]
	print(scores)
	return result

@app.get("/project_data", response_model=ProjectsDict)
def get_project_data():
	"""
	Returns the data of all projects.
	"""
	return RAISON_PROJECTS

if __name__ == "__main__":
	PORT   = 8002
	MODELS = load_all_models()
	print("SUCCESS: Loaded models")
	update_raison_projects_data()
	print(RAISON_PROJECTS)
	uvc_run(app, port=PORT, host="0.0.0.0")
