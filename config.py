#!/usr/bin/env python3
"""
Veritas LLM Configuration Framework
模块化、可配置的LLM架构，支持为不同Agent选择最适合的模型
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    # 测试模式：创建模拟的ChatOpenAI类
    class ChatOpenAI:
        def __init__(self, model="gpt-4", temperature=0.1, **kwargs):
            self.model_name = model
            self.temperature = temperature
            self.kwargs = kwargs
        
        def __repr__(self):
            return f"ChatOpenAI(model={self.model_name}, temperature={self.temperature})"

# 支持的LLM提供商
class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    LOCAL = "local"

# 模型性能级别
class ModelTier(Enum):
    BASIC = "basic"        # 基础任务：格式转换、数据提取
    STANDARD = "standard"  # 标准任务：分析、规划
    ADVANCED = "advanced"  # 高级任务：创作、编辑
    PREMIUM = "premium"    # 顶级任务：复杂推理、创新

@dataclass
class LLMConfig:
    """LLM配置类"""
    provider: LLMProvider
    model_name: str
    temperature: float = 0.1
    max_tokens: Optional[int] = None
    tier: ModelTier = ModelTier.STANDARD
    cost_per_token: float = 0.0  # 每token成本（用于成本优化）
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "provider": self.provider.value,
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "tier": self.tier.value,
            "cost_per_token": self.cost_per_token,
            "description": self.description
        }

# 预定义的LLM配置模板
LLM_CONFIGS = {
    # OpenAI Models
    "gpt-4-turbo": LLMConfig(
        provider=LLMProvider.OPENAI,
        model_name="gpt-4-1106-preview",
        temperature=0.1,
        tier=ModelTier.PREMIUM,
        cost_per_token=0.00003,
        description="最强大的GPT-4模型，适合复杂推理和创作任务"
    ),
    
    "gpt-4": LLMConfig(
        provider=LLMProvider.OPENAI,
        model_name="gpt-4",
        temperature=0.1,
        tier=ModelTier.ADVANCED,
        cost_per_token=0.00003,
        description="平衡性能与成本，适合编辑和高质量写作"
    ),
    
    "gpt-4.1": LLMConfig(
        provider=LLMProvider.OPENAI,
        model_name="gpt-4.1",
        temperature=0.1,
        tier=ModelTier.STANDARD,
        cost_per_token=0.000015,
        description="当前默认模型，性能稳定可靠"
    ),
    
    "gpt-3.5-turbo": LLMConfig(
        provider=LLMProvider.OPENAI,
        model_name="gpt-3.5-turbo",
        temperature=0.1,
        tier=ModelTier.BASIC,
        cost_per_token=0.000002,
        description="高性价比模型，适合基础任务和数据处理"
    ),
    
    # 未来可扩展的配置
    "claude-3": LLMConfig(
        provider=LLMProvider.ANTHROPIC,
        model_name="claude-3-sonnet-20240229",
        temperature=0.1,
        tier=ModelTier.ADVANCED,
        cost_per_token=0.000015,
        description="Anthropic Claude 3，擅长推理和分析"
    ),
}

# Agent专用LLM配置映射
AGENT_LLM_MAPPING = {
    "literature_scout": "gpt-3.5-turbo",      # 文献搜集：基础任务，重视速度和成本
    "synthesizer": "gpt-4.1",                 # 研究分析：标准任务，需要准确性
    "outline_planner": "gpt-4",               # 大纲规划：高级任务，需要逻辑思维
    "academic_writer": "gpt-4-turbo",         # 学术写作：顶级任务，需要创造力
    "editor": "gpt-4-turbo",                  # 编辑审阅：顶级任务，需要语言精通
    "citation_formatter": "gpt-3.5-turbo",   # 引文格式化：基础任务，重视准确性
}

class LLMFactory:
    """LLM工厂类，负责创建和管理LLM实例"""
    
    @staticmethod
    def create_llm(config_name: str, **overrides) -> ChatOpenAI:
        """
        根据配置名称创建LLM实例
        
        Args:
            config_name: 配置名称
            **overrides: 覆盖默认配置的参数
            
        Returns:
            ChatOpenAI实例
        """
        if config_name not in LLM_CONFIGS:
            raise ValueError(f"未知的LLM配置: {config_name}")
        
        config = LLM_CONFIGS[config_name]
        
        # 应用覆盖参数
        model_name = overrides.get("model_name", config.model_name)
        temperature = overrides.get("temperature", config.temperature)
        max_tokens = overrides.get("max_tokens", config.max_tokens)
        
        # 目前主要支持OpenAI，未来可扩展其他提供商
        if config.provider == LLMProvider.OPENAI:
            llm_params = {
                "model": model_name,
                "temperature": temperature,
            }
            if max_tokens:
                llm_params["max_tokens"] = max_tokens
                
            return ChatOpenAI(**llm_params)
        else:
            raise NotImplementedError(f"暂不支持提供商: {config.provider}")
    
    @staticmethod
    def create_agent_llm(agent_type: str, **overrides) -> ChatOpenAI:
        """
        为特定Agent类型创建优化的LLM实例
        
        Args:
            agent_type: Agent类型
            **overrides: 覆盖默认配置的参数
            
        Returns:
            ChatOpenAI实例
        """
        if agent_type not in AGENT_LLM_MAPPING:
            print(f"⚠️ 未找到Agent '{agent_type}' 的专用配置，使用默认配置")
            config_name = "gpt-4.1"
        else:
            config_name = AGENT_LLM_MAPPING[agent_type]
        
        return LLMFactory.create_llm(config_name, **overrides)
    
    @staticmethod
    def get_model_info(config_name: str) -> Dict[str, Any]:
        """获取模型配置信息"""
        if config_name not in LLM_CONFIGS:
            return {}
        
        config = LLM_CONFIGS[config_name]
        return config.to_dict()
    
    @staticmethod
    def list_available_models() -> Dict[str, str]:
        """列出所有可用的模型配置"""
        return {name: config.description for name, config in LLM_CONFIGS.items()}
    
    @staticmethod
    def estimate_cost(config_name: str, estimated_tokens: int) -> float:
        """估算使用成本"""
        if config_name not in LLM_CONFIGS:
            return 0.0
        
        config = LLM_CONFIGS[config_name]
        return config.cost_per_token * estimated_tokens
    
    @staticmethod
    def get_cost_optimized_config(agent_type: str, complexity_level: str = "auto") -> str:
        """
        根据任务复杂度和成本考虑选择最优配置
        
        Args:
            agent_type: Agent类型
            complexity_level: 复杂度级别 ("low", "medium", "high", "auto")
            
        Returns:
            配置名称
        """
        # 自动根据Agent类型判断复杂度
        if complexity_level == "auto":
            complexity_map = {
                "literature_scout": "low",      # 搜索任务相对简单
                "synthesizer": "medium",        # 分析需要一定能力
                "outline_planner": "high",      # 规划需要高级推理
                "academic_writer": "high",      # 写作需要创造力
                "editor": "high",               # 编辑需要语言精通
                "citation_formatter": "low"     # 格式化相对机械
            }
            complexity_level = complexity_map.get(agent_type, "medium")
        
        # 根据复杂度选择最经济的配置
        if complexity_level == "low":
            return "gpt-3.5-turbo"  # 最经济
        elif complexity_level == "medium":
            return "gpt-4.1"        # 平衡
        else:  # high
            return "gpt-4-turbo"    # 最强能力
    
    @staticmethod
    def create_budget_conscious_llm(agent_type: str, budget_tier: str = "balanced") -> ChatOpenAI:
        """
        创建预算友好的LLM实例
        
        Args:
            agent_type: Agent类型
            budget_tier: 预算级别 ("economy", "balanced", "premium")
            
        Returns:
            ChatOpenAI实例
        """
        budget_configs = {
            "economy": {
                "literature_scout": "gpt-3.5-turbo",
                "synthesizer": "gpt-3.5-turbo", 
                "outline_planner": "gpt-4.1",
                "academic_writer": "gpt-4",
                "editor": "gpt-4",
                "citation_formatter": "gpt-3.5-turbo"
            },
            "balanced": AGENT_LLM_MAPPING,  # 使用默认配置
            "premium": {
                "literature_scout": "gpt-4.1",
                "synthesizer": "gpt-4",
                "outline_planner": "gpt-4-turbo",
                "academic_writer": "gpt-4-turbo",
                "editor": "gpt-4-turbo",
                "citation_formatter": "gpt-4.1"
            }
        }
        
        config_name = budget_configs[budget_tier].get(agent_type, "gpt-4.1")
        return LLMFactory.create_llm(config_name)
    
    @staticmethod
    def compare_configurations() -> Dict[str, Any]:
        """比较不同配置的成本和性能"""
        comparison = {}
        estimated_tokens = 1000  # 假设每个任务1000个token
        
        for tier in ["economy", "balanced", "premium"]:
            total_cost = 0
            tier_config = {}
            
            for agent_type in AGENT_LLM_MAPPING.keys():
                if tier == "economy":
                    config_name = LLMFactory.get_cost_optimized_config(agent_type, "low")
                elif tier == "premium":
                    config_name = LLMFactory.get_cost_optimized_config(agent_type, "high")
                else:
                    config_name = AGENT_LLM_MAPPING[agent_type]
                
                cost = LLMFactory.estimate_cost(config_name, estimated_tokens)
                total_cost += cost
                tier_config[agent_type] = {
                    "model": config_name,
                    "cost": cost,
                    "tier": LLM_CONFIGS[config_name].tier.value
                }
            
            comparison[tier] = {
                "total_cost": total_cost,
                "agents": tier_config,
                "cost_savings_vs_premium": 0  # 将在下面计算
            }
        
        # 计算相对于premium的成本节省
        premium_cost = comparison["premium"]["total_cost"]
        for tier in comparison:
            if tier != "premium":
                savings = (premium_cost - comparison[tier]["total_cost"]) / premium_cost * 100
                comparison[tier]["cost_savings_vs_premium"] = savings
        
        return comparison

def print_llm_configuration():
    """打印当前LLM配置概览"""
    print("\n🧠 Veritas 多元智能配置概览")
    print("=" * 70)
    print(f"{'Agent类型':<20} {'使用模型':<15} {'性能级别':<10} {'预估成本/1K tokens'}")
    print("-" * 70)
    
    total_cost = 0
    for agent_type, config_name in AGENT_LLM_MAPPING.items():
        config = LLM_CONFIGS[config_name]
        cost = LLMFactory.estimate_cost(config_name, 1000)
        total_cost += cost
        print(f"{agent_type:<20} {config_name:<15} {config.tier.value:<10} ${cost:.4f}")
    
    print("-" * 70)
    print(f"{'总估算成本 (每轮)':<45} ${total_cost:.4f}")
    print("=" * 70)

def print_budget_comparison():
    """打印不同预算级别的比较"""
    print("\n💰 预算级别对比分析")
    print("=" * 80)
    
    comparison = LLMFactory.compare_configurations()
    
    for tier, data in comparison.items():
        print(f"\n📊 {tier.upper()} 配置:")
        print(f"   总成本: ${data['total_cost']:.4f} (每轮)")
        if data['cost_savings_vs_premium'] > 0:
            print(f"   节省: {data['cost_savings_vs_premium']:.1f}% vs Premium")
        print("   Agent配置:")
        
        for agent, info in data['agents'].items():
            print(f"      {agent:<18}: {info['model']:<15} ({info['tier']} tier)")
    
    print("\n" + "=" * 80)
    print("💡 建议:")
    print("   • Economy: 适合大规模应用或预算紧张的场景")
    print("   • Balanced: 推荐配置，性能与成本的最佳平衡")  
    print("   • Premium: 适合对质量要求极高的重要任务")
    print("=" * 80)

if __name__ == "__main__":
    # 测试配置系统
    print_llm_configuration()
    print_budget_comparison()
    
    # 测试创建不同类型的LLM
    print("\n🧪 LLM创建测试:")
    for agent_type in ["literature_scout", "academic_writer"]:
        llm = LLMFactory.create_agent_llm(agent_type)
        config_name = AGENT_LLM_MAPPING[agent_type]
        print(f"  {agent_type}: {llm.model_name} (配置: {config_name})")
    
    # 测试预算友好配置
    print("\n💰 预算友好配置测试:")
    for tier in ["economy", "balanced", "premium"]:
        llm = LLMFactory.create_budget_conscious_llm("academic_writer", tier)
        print(f"  {tier} writer: {llm.model_name}")
    
    print("\n✅ 配置系统测试完成！")
