

def story_system_prompt(story_prompt, practical_guide):
    final_prompt = """
    You are a seasoned author with years of experience writing novels and stories for hollywood productions as well as
    complex and multi-layered tv shows. 
    You know about general story telling concepts from these general guidelines {practical_guide}.
    These are general instructions, you 
    can use any number of chapters that seem appropriate for the setting and are free to adjust the story according to the prompt.
    When writing a story, you always format it properly in markdown syntax for title and chapters that make sense.
    Your task is to write an engaging and emotionally resonant story. Use vivid, immersive prose and a clear, natural narrative flow.
    Avoid clichés; strive for emotional truth and authentic voice.
    This is the story prompt: {story_prompt}
    """.format(story_prompt=story_prompt, practical_guide=practical_guide)
    return final_prompt


def merge_prompt(prompt, additional_info):
    return """
    You are writing a prompt for a text−to−story model based on user feedback. The original prompt is {prompt}. The user has provided some additional information: 
    {additional_info}. Please write a new prompt for the text−to−story model. The new prompt should be a meaningful sentence or a paragraph that combines the original
    prompt and the additional information. Do not add any new information that is not mentioned in the prompt or the additional information. Make sure the information in the
    original prompt is not changed. Make sure the additional information is included in the new prompt. Make sure the new prompt is a description of a story. If the
    additional information or the original prompt specifically says that a thing does not exist in the story, you should make sure the new prompt mentions that this thing
    does not exist in the story. DO NOT generate rationale or anything that is not part of a description of the story.
    """.format(prompt=prompt, additional_info=additional_info)


def character_extraction_prompt(prompt):
    result = """
    Given a text−to−story prompt list out all the characters that are mentioned in the prompt.
    ∗∗ Explicit characters :∗∗ List all clearly stated characters within the prompt.
    ∗∗ Implicit characters :∗∗ Identify potential characters that are implied or strongly suggested by the prompt, even if not explicitly mentioned.
    The output should be list and each entry should be formated as a JSON dict with the following fields :
    
    "name": A name for the character.
    "importance_to_ask_score": The importance score of asking a question about this entity to reduce the uncertainty of the role of this entity in the story. Make sure that
    this is a number between 0 and 1, higher means more important. Consider these factors when assigning scores: 1. Increate the score for entities that are the primary
    focus or subject of the prompt; 2. increase the score for entities that could strongly influence the story; 3. significantly decrease the score for entities that are
     already well specified in the prompt; 4. significantly increase the score for implicit
    entities that are likely to appear in the story and their appearance can significantly impact the story.
    "description ": A short description of the character.
    Below is an example input and output pair:
    
    Example1:
    Input: {{
    "prompt": "Tell a story about a rabbit and a cat."
    }}
    Output: 
    {{
        "characters": [
            {{
                "name": "rabbit ",
                "importance_to_ask_score": 0.5,
                "description ": "a rabbit "
            }},
            {{
                "name": "cat",
                "importance_to_ask_score": 0.5,
                "description": "cat"
            }}
        ]
    }}
    
    Identify all the characters given the input given below. Strictly stick to the format.
    Input:
    {{
    "prompt": "{prompt}"
    }}
    Output:
    """.format(prompt=prompt)
    return result


def relation_extraction_prompt(prompt, characters):
    result = """
    Given a text−to−story prompt and a list of characters described in the prompt, your goal is to identify a list of character pairs that have relations between them. Ignore character
    pairs without relations. The output should be a json parse−able format (No comma after the last element of the list):
    
    Input:
    prompt: the prompt describing the story.
    characters: a list of characters mentioned in the story prompt.
    Output:
     name (str): The name of the relation. Use ‘character1−character2‘ as the format.
    description ( str ): A short description of the relation.
    
    importance_to_ask_score (float): The importance score of asking a question regarding this relation to reduce entropy. This is a number between 0 and 1, higher means more
    important. Assign a higher score if the two characters are very important, the relation between them is very unclear, and the relation is very important for the story.
    character_1 (str): The name of the first character.
    character_2 (str): The name of the second character.
    
    Below is an example input and output pair:
    
    Input: {{
    "prompt": "Tell me a story about a cat and his friend mouse.",
    "characters ": ["cat", "mouse"]
    }}
    Output:
    {{
        "relations": [
            {{
                "character_1": "cat",
                "character_2 ": "mouse",
                "description": "friends",
                "importance_to_ask_score": 0.5
            }}
        ]
    }}
    
    Identify relationships between characters given the input given below. Strictly stick to the format.
    Input: {{
    "prompt": "{prompt}",
    "characters ": {characters}
    }}
    Output:
    """.format(prompt=prompt, characters=characters)
    return result


def storyline_extraction_prompt(prompt):
    result = """
    Given a text−to−story prompt extract the structure of the story out of the prompt.
    The story has a three act structure. 
    -The first act is the setup or the inciting incident.
    -The second act is the confrontation or the complications.
    -The third act is the climax and resolution. 
    The content of each act is a short summary of the corresponding part of the story.
    The output should be a json parse−able format, and must have the following form:
    {{
        "storyline": [
            {{
                "Act": 1,
                "Description": "Setup / Inciting Incident",
                "Content": "...."
            }},
            {{
                "Act": 2,
                "Description": "Confrontation / Complications",
                "Content": "..."
            }},
            {{
                "Act": 3,
                "Description": "Climax & Resolution",
                "Content": "..."
            }}
        ]
    }}.
    Parse the storyline from the given prompt.
    Input:
    {{
    "prompt": "{prompt}"
    }}
    Output:
    """.format(prompt=prompt)
    return result


MEMO_PRACTICAL_GUIDE = """
Hero’s Journey & Three-Act Structure – Storytelling Framework (Based on Christopher Vogler & Joseph Campbell)

This guide summarizes the core ideas from Christopher Vogler’s 1985 memo, based on Joseph Campbell’s "The Hero with a Thousand Faces."
 It presents the Hero’s Journey as a flexible, psychological storytelling model rooted in universal mythic structure.
  It’s widely used in screenwriting and can be combined with the Three-Act Structure for effective narrative design.

--- HERO’S JOURNEY OVERVIEW ---

The Hero’s Journey is a universal narrative pattern reflecting deep psychological truths.
 All cultures tell variations of this story because it models internal transformation. 
 The characters (hero, mentor, shadow, shapeshifter) mirror Jungian archetypes from the human psyche.
  Stories using this structure resonate because they reflect core human questions: Who am I? What is my purpose? What is good or evil?

--- THE STAGES OF THE HERO’S JOURNEY ---

At the beginning of the story, the hero lives in their ordinary world—a familiar environment where life feels stable, but perhaps unfulfilled. Something then intrudes: a disruption, challenge, or threat that calls the hero to action. This is the call to adventure, which presents the opportunity—or demand—for change. Yet, the hero often resists this call at first. This refusal of the call may come from fear, duty, doubt, or a sense of inadequacy.
Soon after, the hero encounters a mentor—a wise figure or guiding influence who provides support, knowledge, or tools to help them begin. Empowered, the hero crosses the threshold, leaving behind the familiar and stepping into an unknown world filled with risk and potential.
As the journey unfolds, the hero encounters tests, makes allies, and discovers enemies, each shaping their growth and sharpening their identity. Eventually, the hero draws near to a place of deepest danger or transformation—the inmost cave—where they must confront a profound fear or hidden truth.
Here, the hero faces the ordeal, a central crisis that often feels like death—literal or symbolic. Emerging from this dark moment, the hero is changed. They gain a reward: a new power, insight, reconciliation, or treasure that marks a breakthrough.
However, the story doesn’t end there. The hero must now embark on the road back, returning toward the world they left—often facing pursuit or further challenge. One final trial awaits: a resurrection, where the hero is tested again at the highest stakes, proving they have truly transformed.
Finally, the hero returns, bringing back something of value, whether knowledge, healing, peace, or personal growth. Their world is changed, and so are they.

These steps are flexible. Stages can be rearranged, combined, or implied. What matters is the transformation of the hero and emotional resonance.

--- THREE-ACT STRUCTURE ---

Used in modern screenwriting, the Three-Act Structure provides pacing and turning points:

Act I – SETUP (~25%)
- Introduce characters, world, and the central conflict.
- Ends with the inciting incident and decision to embark on the journey.

Act II – CONFRONTATION (~50%)
- Rising tension. The hero learns, grows, and suffers setbacks.
- Midpoint: Emotional turning point or false victory/defeat.
- Ends with a major crisis or dark night of the soul.

Act III – RESOLUTION (~25%)
- Climax: Final confrontation.
- Denouement: The hero returns changed, and the world is altered.

--- KEY CONCEPTS TO REMEMBER ---

- The Hero’s Journey is a metaphor for psychological and emotional transformation.
- Archetypes like the mentor, shadow, shapeshifter, and threshold guardian represent internal forces.
- The “cave” may be literal or symbolic (e.g., a court trial, emotional trauma).
- Stories built on this structure can work across genres—epic fantasy, romance, sci-fi, or personal drama.
- Use this framework as a flexible tool, not a formula. Transformation is the heart of the journey.

This combined structure helps identify problems in floundering narratives and offers tools to create emotionally powerful, universally resonant stories.
"""