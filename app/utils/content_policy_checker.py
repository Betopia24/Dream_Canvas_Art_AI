from app.core.config import config
import openai


def check_content_policy(text: str) -> bool:
    """
    Check if the given text complies with content policy using OpenAI API.
    
    Args:
        text (str): The text to be checked.
        
    Returns:
        bool: True if content is compliant, False otherwise.
    """
    api_key = config.OPEN_AI_API_KEY
    client = openai.OpenAI(api_key=api_key)
    system_prompt = """Check if the user prompt is one of the following types of content:

    NSFW or sexually explicit content

    This includes pornography, sexually suggestive roleplay, or fetish material.

    You may discuss topics related to sexual health, education, or consent in a factual, respectful, and non-graphic way.

    Illegal or harmful activities

    Never promote or instruct users in committing crimes, hacking, drug manufacturing, or any other illegal acts.

    You must also not generate content that could result in physical or emotional harm.

    Hate speech or harassment

    Do not generate content that promotes hatred, discrimination, or violence against individuals or groups based on race, ethnicity, nationality, religion, gender, sexual orientation, age, or disability.

    You must refuse any request that involves harassment, doxxing, or targeted attacks.

    Extreme violence or gore

    Do not create or describe excessively violent, gory, or graphically disturbing scenes.

    Discussions of violence may be permitted only in factual, educational, or literary analysis contexts — not for shock or gratification.

    Misinformation or deception

    Never deliberately generate or spread false information.

    When uncertain, clearly state the limits of your knowledge or verify information using credible sources.

    Self-harm or suicide promotion

    Never encourage or provide methods for self-harm, suicide, eating disorders, or similar behavior.

    If a user expresses distress, respond with empathy and direct them to professional or emergency help resources.

    Intellectual property violations

    return only a string "true" or "false" """

    response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": text}
                    ],
                    max_tokens=300,
                    temperature=0.7
                )

    return response.choices[0].message.content.strip().lower()
