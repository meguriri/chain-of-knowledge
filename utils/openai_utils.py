import openai
import os

def call_openai_api(model, input_text, max_tokens=256, temperature=0, n=1):
    #API Key
    openai.api_key = os.getenv("OPENAI_API_KEY")
    #?
    error_times = 0
    
    #尝试5次？
    while error_times < 5:
        #选择模型
        try:
            #text-davinci模型
            if "text-davinci" in model:
                # InstructGPT models, text completion
                response = openai.Completion.create(
                    model=model,
                    prompt=input_text,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    n=n,
                )
                return [response, response["choices"][0]["text"]]
            
            #gpt模型
            elif "gpt-" in model:
                # ChatGPT models, chat completion
                #创建请求
                response = openai.ChatCompletion.create(
                    #模型类型
                    model=model,
                    #消息内容
                    messages = [
                        #设置行为
                        {"role": "system", "content": "You are a helpful assistant."},
                        #有user和assistant两类交替进行，填入question
                        {"role": "user", "content": input_text}
                    ],
                    #回答的文本（子词）长度
                    max_tokens=max_tokens,
                    #温度，越低越确定，越高越随机，这里设置为0
                    temperature=temperature,
                    #生成的响应数，设置为1个回答
                    n=n,
                    #超时时间，60秒
                    timeout=60,
                    request_timeout=60,
                )
                return [response, response["choices"][0]["message"]["content"]]
            else:
                raise Exception("Invalid model name")
        #错误
        except Exception as e:
            print('Retry due to:', e)
            error_times += 1
            continue
        
    return None

