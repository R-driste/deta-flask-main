import openai

# Replace 'KEY' with actual OpenAI API key
openai.api_key = 'KEY'

def transcribe_audio(audio_data):
    response = openai.Transcription.create(
        audio=audio_data,
        engine='whisper',
        language='en'
    )
    text = response['transcriptions'][0]['text']
    return text

def summarize_text(text):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=text,
        temperature=0.7,
        max_tokens=200
    )
    summary = response.choices[0].text.strip()
    return summary

def outline_text(text):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt="Outline:\n" + text,
        temperature=0.7,
        max_tokens=200
    )
    bullet_points = response.choices[0].text.strip()
    return bullet_points
