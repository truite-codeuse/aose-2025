from __future__ import annotations
from typing import TypedDict
from os import environ
import requests

from dotenv import load_dotenv


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

# The elements and options fields should be filled by pinging rAIson
RAISON_PROJECTS : dict[ProjectID, ProjectData] = {
	"PRJ17225": {
		"author"      : "Tristan Duquesne",
		"title"       : "What fair price should buyer pay to seller ?",
		"description" : (
			"This project's context is a compute-for-hire platform, where individuals can rent out "
			"machines or systems to other for tasks like data analysis, software testing, web scraping, "
			"crypto mining, etc. If there is a conflict on work rendered, this project provides "
			"different alternative outcomes as to how the conflict between the buying and the selling "
			"party should be resolved."
		),
		"elements"    : [],
		"options"     : [],
	},
	"PRJ17775": {
		"author"      : "Kamilia Benlamara",
		"title"       : "TODO",
		"description" : "TODO",
		"elements"    : [],
		"options"     : [],
	},
	"PRJ15875": {
		"author"      : ("Mohamed Azzaoui", "Nassim Lattab"),
		"title"       : "AI-CHATBOT",
		"description" : (
			"An intelligent customer service chatbot designed to handle order tracking, returns, "
			"refunds, and claims. It provides clear and reliable responses, streamlining customer "
			"support while reducing workload on service teams."
		),
		"elements"    : [],
		"options"     : [],
	},
	"PRJ16725" : {
		"author" : "Daniel Latorre",
		"title"  : "Auto-Moderator",
		"description" : (
			"This project creates an auto-moderator for a streaming platform, enabling "
			"automatic responses to various situations in the live chat. The model bases "
			"its decisions on sentiment analysis, emotion analysis, and insult detection, "
			"as well as the user's history of previous actions."
		),
		"elements"    : [],
		"options"     : [],
	}
	# "Thanina Ait Ferhat"
	# "Lynda Benkerrou"
	# "Maram Beddouihech"
	# "Cheikh Tidiane Diouf"
	# "Florian Posez"
	# "Theophile Romieu"
	# "Abdou Aziz Thiam"
	# "Latifou Yaya"
}



load_dotenv('.env')
RAISON_API_KEY = environ.get('RAISON_API_KEY')

RAISON_API_HEADERS = {
	"x-api-key": RAISON_API_KEY,
	"Content-Type": "application/json"
}

def build_project_url(project_id: ProjectID) -> str:
	return f"https://api.ai-raison.com/executions/{project_id}/latest"

def get_project_data(id: ProjectID) -> tuple[list[str], list[str]]:
	url      = build_project_url(id)
	response = requests.get(url, headers = RAISON_API_HEADERS)
	data     = response.json()
	elements = [e["label"] for e in data.get("elements", [])]
	options  = [o["label"] for o in data.get("options",  [])]
	return elements, options

def update_raison_projects_data():
	for project_id in RAISON_PROJECTS:
		elements, options = get_project_data(project_id)
		RAISON_PROJECTS[project_id]["elements"] = elements
		RAISON_PROJECTS[project_id]["options"]  = options

update_raison_projects_data()
print(RAISON_PROJECTS)
