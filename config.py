#!/usr/bin/env python3
"""
Veritas LLM Configuration Framework
模組化、可配置的LLM架構，支援為不同Agent選擇最適合的模型
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    # 測試模式：創建模擬的ChatOpenAI類
    class ChatOpenAI:
        def __init__(self, model="gpt-4", temperature=0.1, **kwargs):
            self.model_name = model
            self.temperature = temperature
            self.kwargs = kwargs
        
        def __repr__(self):
            return f"ChatOpenAI(model={self.model_name}, temperature={self.temperature})"

# 支援的LLM提供商
class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    LOCAL = "local"

# 模型效能級別
class ModelTier(Enum):
    BASIC = "basic"        # 基礎任務：格式轉換、資料擷取
    STANDARD = "standard"  # 標準任務：分析、規劃
    ADVANCED = "advanced"  # 高級任務：創作、編輯
    PREMIUM = "premium"    # 頂級任務：複雜推理、創新

@dataclass
class LLMConfig:
    """LLM配置類別"""
    provider: LLMProvider
    model_name: str
    temperature: float = 0.1
    max_tokens: Optional[int] = None
    tier: ModelTier = ModelTier.STANDARD
    cost_per_token: float = 0.0  # 每token成本（用於成本最佳化）
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            "provider": self.provider.value,
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "tier": self.tier.value,
            "cost_per_token": self.cost_per_token,
            "description": self.description
        }

# 預定義的LLM配置模板（基於最新OpenAI定價）
LLM_CONFIGS = {
    # 最新GPT-5系列模型
    "gpt-5": LLMConfig(
        provider=LLMProvider.OPENAI,
        model_name="gpt-5",
        temperature=0.1,
        tier=ModelTier.PREMIUM,
        cost_per_token=0.002625,  # $1.25 input + $10 output (假設1:3比例)
        description="最新旗艦模型，頂級推理和創作能力"
    ),
    
    "gpt-5-mini": LLMConfig(
        provider=LLMProvider.OPENAI,
        model_name="gpt-5-mini",
        temperature=0.1,
        tier=ModelTier.ADVANCED,
        cost_per_token=0.000625,  # $0.25 input + $2 output (假設1:3比例)
        description="GPT-5精簡版，高性價比的高級模型"
    ),
    
    "gpt-5-nano": LLMConfig(
        provider=LLMProvider.OPENAI,
        model_name="gpt-5-nano",
        temperature=0.1,
        tier=ModelTier.STANDARD,
        cost_per_token=0.000175,  # $0.05 input + $0.4 output (假設1:3比例)
        description="GPT-5輕量版，適合大規模部署"
    ),
    
    # GPT-4.1系列（最新定價）
    "gpt-4.1": LLMConfig(
        provider=LLMProvider.OPENAI,
        model_name="gpt-4.1",
        temperature=0.1,
        tier=ModelTier.ADVANCED,
        cost_per_token=0.0025,  # $2.0 input + $8 output (假設1:3比例)
        description="GPT-4.1標準版，平衡性能與成本"
    ),
    
    "gpt-4.1-mini": LLMConfig(
        provider=LLMProvider.OPENAI,
        model_name="gpt-4.1-mini",
        temperature=0.1,
        tier=ModelTier.STANDARD,
        cost_per_token=0.0005,  # $0.4 input + $1.6 output (假設1:3比例)
        description="GPT-4.1精簡版，經濟實用的選擇"
    ),
    
    "gpt-4.1-nano": LLMConfig(
        provider=LLMProvider.OPENAI,
        model_name="gpt-4.1-nano",
        temperature=0.1,
        tier=ModelTier.BASIC,
        cost_per_token=0.000125,  # $0.1 input + $0.4 output (假設1:3比例)
        description="GPT-4.1輕量版，最經濟的GPT-4.1選項"
    ),
    
    # GPT-4o系列
    "gpt-4o": LLMConfig(
        provider=LLMProvider.OPENAI,
        model_name="gpt-4o",
        temperature=0.1,
        tier=ModelTier.PREMIUM,
        cost_per_token=0.00375,  # $2.5 input + $10 output (假設1:3比例)
        description="GPT-4o多模態模型，支援圖像和文字"
    ),
    
    "gpt-4o-mini": LLMConfig(
        provider=LLMProvider.OPENAI,
        model_name="gpt-4o-mini",
        temperature=0.1,
        tier=ModelTier.BASIC,
        cost_per_token=0.0002625,  # $0.15 input + $0.6 output (假設1:3比例)
        description="GPT-4o精簡版，多模態功能的經濟選擇"
    ),
    
    # O系列推理模型
    "o3": LLMConfig(
        provider=LLMProvider.OPENAI,
        model_name="o3",
        temperature=0.1,
        tier=ModelTier.PREMIUM,
        cost_per_token=0.003,  # $2.0 input + $8 output (假設1:3比例)
        description="O3推理模型，專長複雜邏輯推理"
    ),
    
    "o3-mini": LLMConfig(
        provider=LLMProvider.OPENAI,
        model_name="o3-mini",
        temperature=0.1,
        tier=ModelTier.ADVANCED,
        cost_per_token=0.001925,  # $1.1 input + $4.4 output (假設1:3比例)
        description="O3精簡版，平衡推理能力與成本"
    ),
    
    # 經典模型保留
    "gpt-3.5-turbo": LLMConfig(
        provider=LLMProvider.OPENAI,
        model_name="gpt-3.5-turbo",
        temperature=0.1,
        tier=ModelTier.BASIC,
        cost_per_token=0.000625,  # $0.5 input + $1.5 output (假設1:3比例)
        description="經典高性價比模型，適合基礎任務"
    ),
    
    # 未來擴展的配置
    "claude-3": LLMConfig(
        provider=LLMProvider.ANTHROPIC,
        model_name="claude-3-sonnet-20240229",
        temperature=0.1,
        tier=ModelTier.ADVANCED,
        cost_per_token=0.000015,
        description="Anthropic Claude 3，擅長推理和分析"
    ),
}

# Agent專用LLM配置映射（基於最新模型）
AGENT_LLM_MAPPING = {
    "literature_scout": "gpt-4o-mini",        # 文獻搜集：基礎任務，重視速度和成本
    "synthesizer": "gpt-4.1-mini",            # 研究分析：標準任務，需要準確性
    "outline_planner": "o3-mini",             # 大綱規劃：高級任務，需要邏輯思維
    "academic_writer": "gpt-5-mini",          # 學術寫作：頂級任務，需要創造力
    "editor": "gpt-5",                       # 編輯審閱：頂級任務，需要語言精通
    "citation_formatter": "gpt-4.1-mini",    # 引文格式化：需要準確的URL解析和格式化
    "computational_scientist": "o3",          # 計算科學：頂級任務，需要邏輯推理和代碼生成
    "project_manager": "o3",                 # 專案管理：頂級任務，需要策略思維和決策能力
}

class LLMFactory:
    """LLM工廠類別，負責建立和管理LLM實例"""
    
    @staticmethod
    def create_llm(config_name: str, **overrides) -> ChatOpenAI:
        """
        根據配置名稱建立LLM實例
        
        Args:
            config_name: 配置名稱
            **overrides: 覆蓋預設配置的參數
            
        Returns:
            ChatOpenAI實例
        """
        if config_name not in LLM_CONFIGS:
            raise ValueError(f"未知的LLM配置: {config_name}")
        
        config = LLM_CONFIGS[config_name]
        
        # 應用覆蓋參數
        model_name = overrides.get("model_name", config.model_name)
        temperature = overrides.get("temperature", config.temperature)
        max_tokens = overrides.get("max_tokens", config.max_tokens)
        
        # 某些模型不支援自定義溫度，使用默認值 1.0
        if any(prefix in model_name for prefix in ["o3", "o1", "gpt-5"]):
            temperature = 1.0
        
        # 目前主要支援OpenAI，未來可擴展其他提供商
        if config.provider == LLMProvider.OPENAI:
            llm_params = {
                "model": model_name,
            }
            # 設定溫度參數
            llm_params["temperature"] = temperature
            if max_tokens:
                llm_params["max_tokens"] = max_tokens
                
            return ChatOpenAI(**llm_params)
        else:
            raise NotImplementedError(f"暫不支援提供商: {config.provider}")
    
    @staticmethod
    def create_agent_llm(agent_type: str, **overrides) -> ChatOpenAI:
        """
        為特定Agent類型創建優化的LLM實例
        
        Args:
            agent_type: Agent類型
            **overrides: 覆蓋默認配置的參數
            
        Returns:
            ChatOpenAI實例
        """
        if agent_type not in AGENT_LLM_MAPPING:
            print(f"⚠️ 未找到Agent '{agent_type}' 的專用配置，使用默認配置")
            config_name = "gpt-4.1"
        else:
            config_name = AGENT_LLM_MAPPING[agent_type]
        
        return LLMFactory.create_llm(config_name, **overrides)
    
    @staticmethod
    def get_model_info(config_name: str) -> Dict[str, Any]:
        """獲取模型配置信息"""
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
        根據任務覆雜度和成本考慮選擇最優配置
        
        Args:
            agent_type: Agent類型
            complexity_level: 覆雜度級別 ("low", "medium", "high", "auto")
            
        Returns:
            配置名稱
        """
        # 自動根據Agent類型判斷覆雜度
        if complexity_level == "auto":
            complexity_map = {
                "literature_scout": "low",         # 搜索任務相對簡單
                "synthesizer": "medium",           # 分析需要一定能力
                "outline_planner": "high",         # 規劃需要高級推理
                "academic_writer": "high",         # 寫作需要創造力
                "editor": "high",                  # 編輯需要語言精通
                "citation_formatter": "low",       # 格式化相對機械
                "computational_scientist": "high"  # 代碼生成和數據分析需要高級推理
            }
            complexity_level = complexity_map.get(agent_type, "medium")
        
        # 根據覆雜度選擇最經濟的配置
        if complexity_level == "low":
            return "gpt-3.5-turbo"  # 最經濟
        elif complexity_level == "medium":
            return "gpt-4.1"        # 平衡
        else:  # high
            return "gpt-4-turbo"    # 最強能力
    
    @staticmethod
    def create_budget_conscious_llm(agent_type: str, budget_tier: str = "balanced") -> ChatOpenAI:
        """
        創建預算友好的LLM實例
        
        Args:
            agent_type: Agent類型
            budget_tier: 預算級別 ("economy", "balanced", "premium")
            
        Returns:
            ChatOpenAI實例
        """
        budget_configs = {
            "economy": {
                "literature_scout": "gpt-4.1-nano",
                "synthesizer": "gpt-4.1-nano", 
                "outline_planner": "gpt-4.1-mini",
                "academic_writer": "gpt-5-nano",
                "editor": "gpt-5-nano",
                "citation_formatter": "gpt-4o-mini",
                "computational_scientist": "gpt-4.1-mini"
            },
            "balanced": AGENT_LLM_MAPPING,  # 使用默認配置
            "premium": {
                "literature_scout": "gpt-4o",
                "synthesizer": "gpt-5-mini",
                "outline_planner": "o3",
                "academic_writer": "gpt-5",
                "editor": "gpt-5",
                "citation_formatter": "gpt-4o",
                "computational_scientist": "o3"
            }
        }
        
        config_name = budget_configs[budget_tier].get(agent_type, "gpt-4.1")
        return LLMFactory.create_llm(config_name)
    
    @staticmethod
    def compare_configurations() -> Dict[str, Any]:
        """比較不同配置的成本和性能"""
        comparison = {}
        estimated_tokens = 1000  # 假設每個任務1000個token
        
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
                "cost_savings_vs_premium": 0  # 將在下面計算
            }
        
        # 計算相對於premium的成本節省
        premium_cost = comparison["premium"]["total_cost"]
        for tier in comparison:
            if tier != "premium":
                savings = (premium_cost - comparison[tier]["total_cost"]) / premium_cost * 100
                comparison[tier]["cost_savings_vs_premium"] = savings
        
        return comparison

def print_llm_configuration():
    """列印目前LLM配置概覽"""
    print("\n🧠 Veritas 多元智慧配置概覽")
    print("=" * 70)
    print(f"{'Agent類型':<20} {'使用模型':<15} {'效能級別':<10} {'預估成本/1K tokens'}")
    print("-" * 70)
    
    total_cost = 0
    for agent_type, config_name in AGENT_LLM_MAPPING.items():
        config = LLM_CONFIGS[config_name]
        cost = LLMFactory.estimate_cost(config_name, 1000)
        total_cost += cost
        print(f"{agent_type:<20} {config_name:<15} {config.tier.value:<10} ${cost:.4f}")
    
    print("-" * 70)
    print(f"{'總估算成本（每輪）':<45} ${total_cost:.4f}")
    print("=" * 70)

def print_budget_comparison():
    """打印不同預算級別的比較"""
    print("\n💰 預算級別對比分析")
    print("=" * 80)
    
    comparison = LLMFactory.compare_configurations()
    
    for tier, data in comparison.items():
        print(f"\n📊 {tier.upper()} 配置:")
        print(f"   總成本: ${data['total_cost']:.4f} (每輪)")
        if data['cost_savings_vs_premium'] > 0:
            print(f"   節省: {data['cost_savings_vs_premium']:.1f}% vs Premium")
        print("   Agent配置:")
        
        for agent, info in data['agents'].items():
            print(f"      {agent:<18}: {info['model']:<15} ({info['tier']} tier)")
    
    print("\n" + "=" * 80)
    print("💡 建議:")
    print("   • Economy: 適合大規模應用或預算緊張的場景")
    print("   • Balanced: 推薦配置，性能與成本的最佳平衡")  
    print("   • Premium: 適合對質量要求極高的重要任務")
    print("=" * 80)

if __name__ == "__main__":
    # 測試配置系統
    print_llm_configuration()
    print_budget_comparison()
    
    # 測試創建不同類型的LLM
    print("\n🧪 LLM創建測試:")
    for agent_type in ["literature_scout", "academic_writer"]:
        llm = LLMFactory.create_agent_llm(agent_type)
        config_name = AGENT_LLM_MAPPING[agent_type]
        print(f"  {agent_type}: {llm.model_name} (配置: {config_name})")
    
    # 測試預算友好配置
    print("\n💰 預算友好配置測試:")
    for tier in ["economy", "balanced", "premium"]:
        llm = LLMFactory.create_budget_conscious_llm("academic_writer", tier)
        print(f"  {tier} writer: {llm.model_name}")
    
    print("\n✅ 配置系統測試完成！")
