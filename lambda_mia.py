import json
import os
import openai

openai.api_key = os.environ['openai_api_key']

def lambda_handler(event, context):

    dialogflow_data = event['queryResult']['queryText']
    output_contexts = event['queryResult']['outputContexts']
    
    conversation_history_context = None
    for context in output_contexts:
        if 'conversation_history' in context['name']:
            conversation_history_context = context
            break

    if conversation_history_context:
        conversation_history = conversation_history_context.get('parameters', {}).get('conversationHistory', [])
    else:
        conversation_history = []
        
    if not conversation_history:
        conversation_history = [{"role": "system", "content": "Hello, I am Mia, your virtual English teacher! I specialize in teaching Latinx students through chat and messaging apps. My classes are designed to be interactive and dynamic, featuring creative exercises and personalized feedback tailored to your unique needs and learning style. Each response will include questions to guide your learning, starting with easy questions and increasing the difficulty based on your correct answers. I also use OpenAI's sentiment analysis technology to gauge and respond to your emotions, providing the right level of support and encouragement as you progress through each lesson. Together, we will improve your English language skills and achieve your learning goals!"}]
    
    conversation_history.append({'role': 'user', 'content': dialogflow_data})
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        max_tokens=100,
        n=1,
        temperature=0.8,
        top_p=1,
        messages = conversation_history
    )

    response_text = response['choices'][0]['message']['content'].strip()
    conversation_history.append({'role': 'assistant', 'content': response_text})

    return {
        'fulfillmentText': response_text,
        'outputContexts': [
            {
                'name': event['session'] + '/contexts/conversation_history',
                'lifespanCount': 5,
                'parameters': {
                    'conversationHistory': conversation_history
                }
            }
        ]
    }