import re
from typing import List, Optional, Tuple
from openai import OpenAI
from env_setup import EnvUtil


class ModelInfo:
    def __init__(self, name, desc):
        self.name = name
        self.desc = desc


class LLMJsonParser:

    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=EnvUtil.LLM_API_KEY,
        )
        self.prompt = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "You are the best token extraction in the world, could you extract the description into json which has format. max_face_num has range in 10000 to 90000 depend on complexity of description. if there are no required in description let size (small, medium, large), color, material(normal, wood, steel, plastic,...) in default",
                    },
                    {
                        "type": "json",
                        "info": {
                            "model_name": "base",
                            "description": {
                                "size": "medium",
                                "color": "black",
                                "material": "normal",
                            },
                            "max_face_nums": 10000,
                        },
                    },
                ],
            }
        ]
        self.model = "deepseek/deepseek-chat-v3-0324:free"

    def json_parse(self, prompt: str) -> Optional[str]:
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "You are the best token extraction AI in the world. Extract the description into JSON format with model name and Description."
                            "`model_name` should be in format snake case depend on main object in context, for example: the fox jump over the window `model_name` should be: `the_fox` and if it not specified please guess the object then add object name in to `model_name` example: `something`, `thing`, should be specific `model_name`: `the_door` or any object you can guess"
                            " `max_face_num` should be between 10000 and 90000, depending on complexity of object in description example an apple `max_face_num` should be `10000` and the car should be `90000`."
                            " If not specified in prompt please use DEFAULT VALUES: `size`: `medium`(small, medium, large), `color` : `dark` (red, green, blue,...), `material`: `normal` (normal, wood, steel, plastic, etc.)."
                            "other fields not in below format no need to add to the json"
                            "Please output only JSON not in ``` ``` or ANYTHING else"
                        ),
                    },
                    {
                        "type": "json",
                        "info": {
                            "model_name": "base",
                            "description": {
                                "size": "medium",
                                "color": "black",
                                "material": "normal",
                            },
                            "max_face_nums": 10000,
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt,
                        # Add user input dynamically
                    },
                ],
            }
        ]

        try:
            completion = self.client.chat.completions.create(
                extra_headers={},
                extra_body={},
                model=self.model,
                response_format={"type": "json_object"},  # Force JSON response
                messages=messages,
            )

            if completion and completion.choices:
                response = completion.choices[0].message.content
                print(f"Model Response: {response}")
                return response

        except Exception as e:
            print(f"Error during JSON parsing: {e}")

        return None  # Return None if there is an error

    def json_parse_story(self, title: str, prompt: str) -> List[str]:
        pages = [p.strip() for p in prompt.split("\n") if p.strip()]

        combined_story = "\n".join([f"{i+1}. {page}" for i, page in enumerate(pages)])

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "You are the best scene description AI in the world.\n"
                            "Generate a simple, vivid, and short scene description for each numbered story below.\n"
                            "Do NOT describe humans or human activities like handshake, playing sports, ... and emotions, or actions done by people.\n"
                            "Do NOT describe people or group of people activities like handshake, playing sports, anything else... and emotions, or actions done by people.\n"
                            "Only describe the background/environment like rooms, furniture, objects, lighting, etc.\n"
                            "Respond with the list of scene descriptions numbered 1 to N, matching the order of the input.\n"
                            "\n"
                            f"title: {title}\n"
                            f"stories:\n{combined_story}\n"
                            "\n"
                            "Output:"
                        ),
                    }
                ],
            }
        ]

        try:
            completion = self.client.chat.completions.create(
                model=self.model, messages=messages
            )

            if completion and completion.choices:
                response = completion.choices[0].message.content.strip()
                print("Model Response:", response)

                # Split model response by lines starting with numbers (1., 2., etc.)
                import re

                scenes = re.findall(r"\d+\.\s*(.+)", response)
                return scenes

        except Exception as e:
            print(f"Error generating scenes: {e}")

        return []

    def json_parse_characters(
        self, title: str, story: str
    ) -> List[List[Tuple[str, str]]]:
        pages = [p.strip() for p in story.split("\n") if p.strip()]
        combined_story = "\n".join([f"{i+1}. {page}" for i, page in enumerate(pages)])

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "You are the best character detach and character description AI in the world.\n"
                            "Generate a simple, vivid, and short description of ALL characters for each character in each sentence.\n"
                            "Only describe full body description, emotion and activity.\n"
                            "Respond with the list of characters and descriptions for each sentence in format [`character_name_1`-`character_description_1`, `character_name_2`-`character_description_2`] "
                            "(example: [narrator-a short boy with a hat wants to communicate with everyone in the classroom, mom_or_dad-A tall, warm parent speaking calmly with another adult, their posture relaxed but attentive]). Numbered 1 to N, matching the order of the input.\n"
                            "\n"
                            f"title: {title}\n"
                            f"stories:\n{combined_story}\n"
                            "\n"
                            "Output:"
                        ),
                    }
                ],
            }
        ]

        try:
            completion = self.client.chat.completions.create(
                model=self.model, messages=messages
            )

            if completion and completion.choices:
                response = completion.choices[0].message.content.strip()
                print("Model Response:", response)

                pattern = r"\d+\.\s*\[([^\]]+)\]"
                matches = re.findall(pattern, response)

                result: List[List[Tuple[str, str]]] = []

                for match in matches:
                    group: List[Tuple[str, str]] = []
                    items = [item.strip() for item in match.split(",")]
                    for item in items:
                        if "-" in item:
                            name, desc = item.split("-", 1)
                            group.append((name.strip(), desc.strip()))
                    result.append(group)

                return result

        except Exception as e:
            print(f"Error generating characters: {e}")

        return []
