#!/usr/bin/env python3
"""
测试 Veritas LLM 配置系统
"""

import sys
import os

# 添加当前目录到路径，以便导入config模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 模拟 langchain_openai.ChatOpenAI
class MockChatOpenAI:
    def __init__(self, model="gpt-4", temperature=0.1, **kwargs):
        self.model_name = model
        self.temperature = temperature
        self.kwargs = kwargs
    
    def __repr__(self):
        return f"MockChatOpenAI(model={self.model_name}, temperature={self.temperature})"

# 替换原始导入
import config
config.ChatOpenAI = MockChatOpenAI

def test_llm_configurations():
    """测试LLM配置系统"""
    print("🧪 Veritas v2.0 LLM配置系统测试")
    print("=" * 60)
    
    # 测试配置信息展示
    config.print_llm_configuration()
    
    # 测试预算比较
    config.print_budget_comparison()
    
    # 测试模型创建
    print("\n🔧 模型创建测试:")
    print("-" * 40)
    
    for agent_type in ["literature_scout", "academic_writer", "editor"]:
        try:
            llm = config.LLMFactory.create_agent_llm(agent_type)
            config_name = config.AGENT_LLM_MAPPING[agent_type]
            tier = config.LLM_CONFIGS[config_name].tier.value
            print(f"✅ {agent_type:<18}: {llm.model_name} ({tier} tier)")
        except Exception as e:
            print(f"❌ {agent_type:<18}: Error - {e}")
    
    # 测试预算友好配置
    print("\n💰 预算级别测试:")
    print("-" * 40)
    
    for tier in ["economy", "balanced", "premium"]:
        try:
            llm = config.LLMFactory.create_budget_conscious_llm("academic_writer", tier)
            print(f"✅ {tier:<10} writer: {llm.model_name}")
        except Exception as e:
            print(f"❌ {tier:<10} writer: Error - {e}")
    
    # 测试成本分析
    print("\n📊 成本分析测试:")
    print("-" * 40)
    
    for model_name in ["gpt-3.5-turbo", "gpt-4.1", "gpt-4-turbo"]:
        cost = config.LLMFactory.estimate_cost(model_name, 1000)
        model_info = config.LLMFactory.get_model_info(model_name)
        tier = model_info.get('tier', 'unknown')
        print(f"📈 {model_name:<15}: ${cost:.4f}/1K tokens ({tier})")
    
    print("\n✅ 所有测试完成！")
    print("🎯 Veritas 现在是真正的「模型无关」智能平台！")
    print("=" * 60)

if __name__ == "__main__":
    test_llm_configurations()
