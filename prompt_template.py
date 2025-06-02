from typing import List, Dict

class PromptTemplate:
    def __init__(self):
        """
        初始化提示词模板管理器
        """
        self.system_prompt = """你是一个提示词优化专家。根据给定的案例文本和期望提取文本，生成多个不同的提示词模板。
        每个模板都应该能够引导AI从类似文本中提取相似的信息。请确保模板具有多样性，并使用不同的提示策略。"""
    
    def get_template_generation_prompt(self, example_text: str, expected_output: str, last_prompt: str = "", n: int = 5) -> Dict[str, List[Dict[str, str]]]:
        """
        获取生成模板的提示词
        :param example_text: 案例文本
        :param expected_output: 案例期望提取文本
        :param last_prompt: 上一次的提示词
        :param n: 生成的模板数量
        :return: 包含messages的字典
        """
        user_prompt = f"""案例文本：
{example_text}

期望提取文本：
{expected_output}

上一版提示词：
{last_prompt}

请生成{n}个不同的提示词模板，每个模板都应该能够从类似的文本中提取相似的信息。
每个模板请用分隔符‘___________’分隔。"""

        return {
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }

    def separate_generation_prompt(self, response_text: str) -> List[str]:
        """
        解析模型返回的响应，提取模板
        :param response_text: 模型返回的文本
        :return: 提示词模板列表
        """
        templates = []
        for chunk in response_text.split('___________'):
            template = chunk.strip()
            if template:
                templates.append(template)
        return templates

    def format_template(self, template: str, text: str) -> str:
        """
        格式化模板，将文本插入到模板中
        :param template: 提示词模板
        :param text: 要插入的文本
        :return: 格式化后的提示词
        """
        return template.replace("{text}", text) 

    def get_similarity_prompt(self, text: str, expected_output: str) -> str:
        """
        获取相似度评估提示词
        :param text: 文本
        :param expected_output: 期望输出
        :return: 相似度评估提示词
        """
        return f"""请评估以下两段文本的相似度，给出0-1之间的分数，1表示完全相同，0表示完全不同。
只需要返回分数，不需要其他解释。

文本1：
{expected_output}

文本2：
{text}"""


    def get_generality_prompt(self, template: str) -> str:
        """
        获取通用性评估提示词
        :param template: 提示词模板
        :return: 通用性评估提示词
        """
        return f"""请评估以下提示词模板的通用性，给出0-1之间的分数。
1表示模板非常通用，可以应用于各种类似场景；0表示模板过于特定，难以迁移到其他场景。
只需要返回分数，不需要其他解释。

提示词模板：
{template}"""

    