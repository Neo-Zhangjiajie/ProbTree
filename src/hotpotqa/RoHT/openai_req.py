import openai
import requests
import time
import os
import json, jsonlines

class OpenaiReq():
    def __init__(self):
        self.url = "http://103.238.162.37:9072/completion/no_cache"
        self.cache = {}
        self.cache_path = "./cache.jsonl"
        if os.path.exists(self.cache_path):
            with open(self.cache_path, "r") as f:
                for i, line in enumerate(f):
                    #print(i+1)
                    datum = json.loads(line.strip())
                    self.cache[tuple(datum["input"])] = datum["response"]
                f.close()
    
    def req2openai(self, prompt, model="text-davinci-003", temperature=0, max_tokens=128, stop=None, logprobs=1, use_cache=True):
        input = (prompt, model, max_tokens, stop, logprobs)
        if use_cache and isinstance(prompt, str) and temperature == 0 and input in self.cache:
            return self.cache[input], True
        for i in range(3):
            try:
                response = requests.post(self.url, json = {
                    "model": model,
                    "prompt": prompt,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stop": stop,
                    "logprobs": logprobs,
                    "user_token": "ce99b124-4258-11ee-a59a-9cc2c4278efc"
                })
                if response.status_code != 200:
                    raise Exception(response.text)
                break
            except Exception as e:
                err_msg = str(e)
                print(e)
                if "reduce your prompt" in err_msg: # this is because the input string too long
                    if type(prompt) == list:
                        return ['too long' for _ in range(len(prompt))], False 
                    else:
                        return ['too long'], False
        response = response.json()['choices']
        if temperature == 0:
            if isinstance(prompt, str):
                prompt = [prompt]
            for prompt, res in zip(prompt, response):
                input = (prompt, model, max_tokens, stop, logprobs)
                if input not in self.cache:
                    self.cache[input] = [res]
                    with open(self.cache_path, "a") as f:
                        f.write("%s\n"%json.dumps({"input": input, "response": [res]}))
                        f.close()
        return response, True

if __name__ == "__main__":
    caller = OpenaiReq()
    res = caller.req2openai("你好", use_cache=True)
    print(res)
    
    