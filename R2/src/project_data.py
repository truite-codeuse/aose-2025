from __future__ import annotations
from typing_extensions import TypedDict, TYPE_CHECKING
from os import environ
import requests

from dotenv import load_dotenv

if TYPE_CHECKING:
	from .sentence_matcher import DocumentDict



ProjectID = str
ProjectData = TypedDict(
	"ProjectData",
	{
		"author"      : str | tuple[str,str] | tuple[str,str,str],
		"title"       : str,
		"description" : str,
		"elements"    : list[str], # scenarios
		"options"     : list[str],
	},
	total = True,
)
ProjectsDict = dict[ProjectID, ProjectData]

# The elements and options fields should be filled by pinging rAIson
RAISON_PROJECTS : ProjectsDict = {
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
	},
	"PRJ17575" : {
		"author" : ("Thanina Ait Ferhat", "Lynda Benkerrou", "Maram Beddouihech"),
		"title": "ARG",
		"description": (
			"A Leave Management System that enhances the processing of employee leave "
			"requests with a focus on conditional decision-making within an organization. "
			"The system ensures that leave approvals are compliant with varying organizational "
			"policies tailored to different types of leave."
		),
		"elements": [],
		"options": [],
	},
	"PRJ17775" : {
		"author" : "Kamilia Benlamara",
		"title" : "Claim Resolver",
		"description" : (
			"This project provides an automated decision-making system to manage customer "
			"claims efficiently by generating automatic responses such as rejection, replacement, "
			"or refund. The system evaluates each claim scenario according to predefined conditions, "
			"including proof validity, stock availability, and adherence to deadlines, ensuring "
			"fair, consistent, and transparent outcomes."
		),
		"elements" : [],
		"options" : [],
	},
	"PRJ15425": {
		"author": "Cheikh Tidiane Diouf",
		"title": "Remboursement",
		"description": (
			"Reimbursement of employees' transportation tickets in a company involves covering part or all "
			"of their commuting expenses. This policy helps reduce travel costs for employees using public "
			"transport or other eligible transportation methods."
		),
		"elements": [],
		"options": [],
	},
	"PRJ12375": {
		"author": ("Latifou Yaya", "Abdou Aziz Thiam"),
		"title": "Automatisation des Services RH : Tri Automatique des CVs",
		"description": (
			# "This project aims to automate the CV sorting process to optimize recruitment procedures and "
			# "help human resources (HR) offices gain time. "
			"This project leverages advanced natural language processing algorithms to analyze CVs in real time, extracting key information such as skills, experiences, and educational qualifications. By automating the initial screening process, it not only minimizes human error but also ensures a consistent evaluation of all candidates. Furthermore, the system centralizes candidate data into an easily accessible database, enabling HR teams to quickly identify top talent and streamline the recruitment process. This enhanced efficiency allows HR professionals to focus more on strategic decision-making and less on time-consuming administrative tasks, ultimately contributing to a more effective hiring process."
		),
		"elements": [],
		"options": [],
	},
	"PRJ17525": {
		"author": ("Florian Posez", "Theophile Romieu"),
		"title": "Bluesky Automod",
		"description": (
			"Automatic moderation for Bluesky. Detects skeets on a webpage and decides if the skeet "
			"should be moderated (hidden) or not given some conditions (banwords, followed accounts, "
			"virality, etc.)."
		),
		"elements": [],
		"options": [],
	},
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

def document_dict_from_project_dict(projects: ProjectsDict) -> DocumentDict:
	result = {
		project_id: [project["description"]] + project["elements"] + project["options"]
		for project_id, project in projects.items()
	}
	return result




if __name__ == "__main__":
	update_raison_projects_data()
	print(RAISON_PROJECTS)
