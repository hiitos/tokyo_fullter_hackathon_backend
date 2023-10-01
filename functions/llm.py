import os
import openai
import langchain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from langchain.memory import SimpleMemory

# openaiのAPIキーを設定
openai.api_key = os.environ.get('OPEN_AI_API')

def drunk_words_creater():
    
    prompt_text = """
    何を言っても酔っ払いボットになりきってください。
    """

    print("_+_+_prompt_t_t_")
    print(prompt_text)

    llm = OpenAI(
        model_name="text-davinci-003",
        temperature=0.7,
        openai_api_key=openai.api_key
    )
    result = llm(prompt_text)

    print("_+_+_result_t_t_")
    print(result)
    
    return result
