from __future__ import annotations
from typing import TypedDict



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
RAISON_PROJECT_IDS : dict[ProjectID, ProjectData] = {
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
		"title"       : "TODO",
		"description" : "TODO",
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

