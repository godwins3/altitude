from openai import OpenAI
from goha.translate import translate_lang
client = OpenAI()

def generate_response(msg_received):
    try:
        string = msg_received["message"]
        src_lang = msg_received["source_lang"]
        tgt_lang = msg_received["target_lang"]
    except KeyError as k:
        return {"Message": "A key for generating text is missing", "Error": str(k), "statusCode": 401}
    
    translated_text = translate_lang(string, src_lang, tgt_lang)

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": translated_text
                }
            ]
        )

        return {
            "message": "Response success",
            "data": completion.choices[0].message,
            "statusCode": 200
        }
    
    except Exception as e:
        return {
            "message": "Error generating text",
            "error": str(e),
            "statusCode": 500
        }
    
def generate_image(msg_received):
    try:
        string = msg_received["message"]
        src_lang = msg_received["source_lang"]
        tgt_lang = msg_received["target_lang"]
    except KeyError as k:
        return {"Message": "A key for generating image is missing", "Error": str(k), "statusCode": 401}

    translated_text = translate_lang(string, src_lang, tgt_lang)

    try:
        response = client.images.generate(
            prompt="A cute baby sea otter",
            n=2,
            size="1024x1024"
        )

        return {
            "message": "Response success",
            "data": response.data[0].url,
            "statusCode": 200
        }
    except Exception as e:
        return {
            "message": "Error generating text",
            "error": str(e),
            "statusCode": 500
        }
