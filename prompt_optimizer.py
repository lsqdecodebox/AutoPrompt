import os
from typing import List, Dict, Tuple
import numpy as np
from prompt_template import PromptTemplate
import requests
import re

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url

    def chat_completions_create(self, model: str, messages: List[Dict[str, str]], temperature: float = 0.8) -> Dict:
        """
        使用Ollama API创建聊天完成
        """
        data = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "seed": 101,
                "temperature": temperature
            },
        }
        print("______chat_completions_create______")    
        print("=====request data=====\n", data)
        response = requests.post(f"{self.base_url}/api/chat", json=data)
        response.raise_for_status()
        result = response.json()
        print("=====response data=====\n", result)
        return self.get_raw_text(result)
         
    def get_raw_text(self, result: Dict) -> str:
        return result["message"]["content"]

    def transform_response_to_openai_format(self, result: Dict) -> Dict:
        # 转换为与OpenAI API类似的格式
        return {
            "choices": [{
                "message": {
                    "content": result["message"]["content"]
                }
            }]
        }
        
    def remove_think_tags(self, text: str) -> str:
        """
        移除文本中的思维链部分（<think>标签之间的内容）
        :param text: 包含思维链的原始文本
        :return: 移除思维链后的文本
        
        示例:
        输入: "这是开头<think>这是思维过程</think>这是结论"
        输出: "这是开头这是结论"
        """
        
        # 使用非贪婪模式匹配<think>标签及其内容
        pattern = r'<think>.*?</think>'
        # 移除所有匹配到的内容
        cleaned_text = re.sub(pattern, '', text, flags=re.DOTALL)
        # 移除可能产生的多余空行
        cleaned_text = re.sub(r'\n\s*\n', '\n', cleaned_text)
        return cleaned_text.strip()

class PromptOptimizer:
    def __init__(self, model_name: str = "qwen3:30b", base_url: str = "http://localhost:11434"):
        """
        初始化提示词优化器
        :param model_name: Ollama模型名称
        :param base_url: Ollama API地址
        """
        self.model_name = model_name
        self.client = OllamaClient(base_url=base_url)
        self.prompt_template = PromptTemplate()

    def generate_prompt_templates(self, example_text: str, expected_output: str, last_prompt: str, n: int = 5) -> List[str]:
        """
        生成多个提示词模板
        :param example_text: 案例文本
        :param expected_output: 案例期望提取文本
        :param target_text: 目标文本
        :param n: 生成的模板数量
        :return: 提示词模板列表
        """
        prompts = self.prompt_template.get_template_generation_prompt(example_text, expected_output,last_prompt, n)
        
        response = self.client.chat_completions_create(self.model_name, prompts["messages"])

        # print(response)
        return self.prompt_template.separate_generation_prompt(self.client.remove_think_tags(response))

    def generate_responses(self, templates: List[str], example_text: str) -> List[str]:
        """
        使用生成的模板生成案例回答
        :param templates: 提示词模板列表
        :param example_text: 案例文本
        :return: 生成的回答列表
        """
        responses = []
        for template in templates:
            # prompt = self.prompt_template.format_template(template, example_text)
            response = self.client.chat_completions_create(self.model_name, [{"role": "system", "content": template},{"role": "user", "content": example_text}])
            responses.append(self.client.remove_think_tags(response))
        return responses

    def generate_response(self, template: str, example_text: str) ->  str:
        """
        使用生成的模板生成案例回答
        :param templates: 提示词模板列表
        :param example_text: 案例文本
        :return: 生成的回答列表
        """
        response = self.client.chat_completions_create(self.model_name, [{"role": "system", "content": template},{"role": "user", "content": example_text}])
        return self.client.remove_think_tags(response)

    def evaluate_responses(self, responses: List[str], expected_output: str, templates: List[str]) -> Tuple[str, str, float, float]:
        """
        使用大模型评估生成的回答与期望输出的相似度，以及模板的通用性
        :param responses: 生成的回答列表
        :param expected_output: 期望输出
        :param templates: 提示词模板列表
        :return: (最佳提示词模板, 最佳回答, 相似度分数, 通用性分数)
        """
        print("______evaluate_responses______")
        # 1. 评估回答相似度
        similarities = []
        for response in responses:
            prompt = self.prompt_template.get_similarity_prompt(response, expected_output)
            response = self.client.chat_completions_create(
                self.model_name,
                [{"role": "user", "content": prompt}],
                temperature=0.2
            )
            try:
                score = float(self.client.remove_think_tags(response.strip()))
                similarities.append(score)
            except ValueError:
                print("=====error=====\n", response)
                similarities.append(0.0)

        # 2. 评估模板通用性
        generalities = []
        for template in templates:
            prompt = self.prompt_template.get_generality_prompt(template)
            result = self.client.chat_completions_create(
                self.model_name,
                [{"role": "user", "content": prompt}],
                temperature=0.2
            )
            try:
                score = float(self.client.remove_think_tags(response.strip()))
                generalities.append(score)
            except ValueError:
                print("=====error=====\n", response)
                generalities.append(0.0)

        # 3. 综合评分 (相似度权重0.7，通用性权重0.3)
        combined_scores = [0.7 * sim + 0.3 * gen for sim, gen in zip(similarities, generalities)]
        best_idx = max(range(len(combined_scores)), key=lambda i: combined_scores[i])

        return templates, responses, similarities, generalities, best_idx

    def optimize(self, example_text: str, expected_output: str, target_text: str, last_prompt: str = '无', n: int = 5) -> Dict:
        """
        执行完整的提示词优化流程
        :param example_text: 案例文本
        :param expected_output: 案例期望提取文本
        :param target_text: 目标文本
        :param last_prompt: 待优化的提示词
        :param n: 生成的模板数量
        :return: 优化结果
        """
        # 1. 生成提示词模板
        templates = self.generate_prompt_templates(example_text, expected_output, last_prompt, n)
        print("=====templates=====\n", templates)
        
        # 2. 生成案例回答
        responses = self.generate_responses(templates, example_text)
        print("=====responses=====\n", responses)
        
        # 3. 评估回答
        templates, responses, similarities, generalities, best_idx = self.evaluate_responses(responses, expected_output, templates)

        # 4. 生成最佳回答
        best_response = self.generate_response(templates[best_idx], example_text)
        print("=====best_response=====\n", best_response)

        return {
            "best_template": templates[best_idx],
            "best_response": responses[best_idx],
            "best_similarity_score": float(similarities[best_idx]),
            "best_generality_score": float(generalities[best_idx]),
            "all_templates": templates,
            "all_responses": responses,
            "all_similarities": similarities,
            "all_generalities": generalities,
            "result_response": best_response
        }



if __name__ == "__main__":
    # 使用示例
    optimizer = PromptOptimizer()
    
    example_text = """小明今年8岁，身高130cm，体重28kg，是一名小学二年级的学生。
他每天都准时完成作业，最喜欢的科目是数学，经常在数学竞赛中获奖。"""
    
    expected_output = """姓名：小明
年龄：8岁
身高：130cm
体重：28kg
年级：小学二年级
特点：准时完成作业，喜欢数学，经常在数学竞赛中获奖"""
    
    target_text = """张华是一名高三学生，今年17岁，身高175cm，体重65kg。
他学习刻苦，尤其擅长物理，曾在省级物理竞赛中获得一等奖。"""

    # 定义待优化的提示词
    last_prompt = """请从给定文本中提取人物信息，按以下格式输出：
姓名：
年龄：
身高：
体重：
年级：
特点："""
    
    result = optimizer.optimize(example_text, expected_output, target_text, last_prompt)
    
    print("最佳提示词模板：")
    print(result["best_template"])
    print("\n最佳回答：")
    print(result["best_response"])
    print(f"\n相似度分数：{result['best_similarity_score']:.4f}")
    print(f"通用性分数：{result['best_generality_score']:.4f}")
    print("\n生成的结果：")
    print(result["result_response"])