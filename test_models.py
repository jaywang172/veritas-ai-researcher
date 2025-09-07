#!/usr/bin/env python3
"""
測試所有模型是否正常工作
"""

from config import LLMFactory, AGENT_LLM_MAPPING

def test_all_models():
    print("🧪 測試所有 Agent 模型...")
    
    for agent_type, model_name in AGENT_LLM_MAPPING.items():
        try:
            print(f"  測試 {agent_type} ({model_name})...", end="")
            llm = LLMFactory.create_agent_llm(agent_type)
            print(" ✅")
        except Exception as e:
            print(f" ❌ 錯誤: {e}")

if __name__ == "__main__":
    test_all_models()
