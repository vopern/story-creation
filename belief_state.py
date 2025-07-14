import prompts
import json


class BeliefState:
    """
    Keep track of the story content
    1. a merged prompt updated with all information about the story currently available
    2. a state dictionary containing structured information on characters, relations and story line.

    Updating prompt and states is done by calling an LLM with instructions.
    """

    def __init__(self, client, model):
        self.memory = []
        self.prompt = ""
        self.state = {}
        self.client = client
        self.model = model

    def merge_prompt(self, payload):
        """
        merge prompt with new payload
        """
        instruction = prompts.merge_prompt(prompt=self.prompt, additional_info=payload)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": instruction}
            ]
        )
        self.prompt = response.choices[0].message.content
        print('*** new prompt ***')
        print(self.prompt)

    def parse_state(self, entity):
        if entity == 'characters':
            instruction = prompts.character_extraction_prompt(prompt=self.prompt)
        elif entity == 'storyline':
            instruction = prompts.storyline_extraction_prompt(prompt=self.prompt)
        elif entity == 'relations':
            characters = self.state.get('characters', [])
            names = [c['name'] for c in characters]
            names = json.dumps(list(names))
            instruction = prompts.relation_extraction_prompt(prompt=self.prompt, characters=names)
        else:
            raise ValueError(f"Unknown entity {entity}")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": instruction},
            ],
            response_format={ "type": "json_object" }
        )
        state = response.choices[0].message.content
        try:
            state = json.loads(state)
            print('*** new state ***')
            self.state.update(state)
            print(self.state)

        except json.JSONDecodeError:
            print("Response was not valid JSON.")

    def update_from_text_input(self, question: str, answer: str):
        """
        Update prompt and all entities from a new question and response.
        """
        self.memory.append(f"question: '{question}'\n answer: '{answer}'")
        self.merge_prompt(self.memory[-1])
        self.parse_state('characters')
        self.parse_state('relations')
        self.parse_state('storyline')

    def update_from_structured_data(self, df, key):
        """
        Given a new status of an entity, update the prompt.
        """
        print(f'Updating information on {len(df)} records for key {key}.')
        self.state[key] = df.to_dict(orient='records')
        self.merge_prompt(json.dumps(self.state[key]))
