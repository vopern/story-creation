import os
from prompts import story_system_prompt, MEMO_PRACTICAL_GUIDE


def generate_story(client, prompt):
    """
    Generate a story from the merged prompt.
    """
    system_prompt = story_system_prompt(prompt, MEMO_PRACTICAL_GUIDE)
    response = client.chat.completions.create(
        model=os.getenv('MODEL_ID'),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
    )
    return response.choices[0].message.content


class QuestionAgent3:
    """
    A proactive agent for generating clarifying questions for multi-turn
    text-to-story generation.
    Questions & answers are used to update a belief graph which helps to generate a final prompt for story generation.
    The agent only keeps track of chat messages to generate new questions, but does not use the belief state,
    so the information flow is: chat => belief state.
    """
    def __init__(self, client, model):
        self.client = client
        self.model = model
        self.prompt = """
        You are a master storyteller, skilled in crafting narratives for short stories, plays, novels, and TV shows. 
        You know all about effective story telling from this well-known memo {practical_guide}.
        Your task is to create a brand new dramatic story. Gather input from the user on all you need to know.
        Your questions should be based on the chat history. They should be concise and direct.
        The questions should aim to learn more about the theme and setting of the story, characters, story arcs. Only propose
        about three questions in each round.
        """.format(practical_guide=MEMO_PRACTICAL_GUIDE)

        self.messages = [
            {"role": "system", "content": self.prompt},
            {"role": "assistant", "content": "What should the story be about?"}
        ]

    def generate_question(self):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages
            )
            assistant_reply = response.choices[0].message.content
        except Exception as e:
            assistant_reply = f"⚠️ Error: {e}"

        self.messages.append({"role": "assistant", "content": assistant_reply})

    def get_chat(self):
        chat = [{"role": "system", "content": "Chat history"}] + self.messages[1:]
        return chat

    def get_last_question(self):
        questions = [m for m in self.messages if m['role'] == 'assistant']
        if not questions:
            return "No questions asked yet."
        return questions[-1]['content']




