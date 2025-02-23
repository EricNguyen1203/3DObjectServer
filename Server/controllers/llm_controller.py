from openai import OpenAI
from Server.env_setup import EnvUtil


class LLMJsonParser:
  def __init__(self):
    self.client = OpenAI(
      base_url="https://openrouter.ai/api/v1",
      api_key=EnvUtil.LLM_API_KEY,
    )
    self.prompt=[
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "You are the best token extraction in the world, could you extract the description into json which has format. max_face_num has range in 10000 to 90000 depend on complexity of description. if there are no required in description let size (small, medium, large), color, material(normal, wood, steel, plastic,...) in default"
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
              "max_face_nums": 10000
            }
          }
        ]
      }
    ]
    self.model="google/gemma-2-9b-it:free"
    self.functions = {
        "model_name": "extracted_model_name",
        "prompt": "optimize user prompt",
        "description": {
          "size": "extracted_model_name",
          "color": "extracted_model_color",
          "material": "extracted_model_material",
        },
        "max_face_nums": 10000
      }


  def json_parse(self, prompt: str) -> str or None:
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
                        )
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
                            "max_face_nums": 10000
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                      # Add user input dynamically
                    }
                ]
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









