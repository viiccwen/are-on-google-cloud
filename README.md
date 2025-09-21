# Agent Reliability Engineering on Google Cloud: Principles for Trustworthy AI Agents

> Still in Progress...

本專案展示如何在 **Google Cloud** 上建構與驗證 **Agent Reliability Engineering (ARE)** 的核心理念，並透過 **Vertex AI Evaluation, Cloud Monitoring, Guardrails, CI/CD** 實現 **可靠、可觀測、具安全性的 AI Agent**。

## Background

隨著 AI Agents 在決策、問答、自動化場景中廣泛應用，**可靠性 (Reliability)** 已成為關鍵挑戰。  
**ARE (Agent Reliability Engineering)** 借鑑 SRE (Site Reliability Engineering) 的思維，提出以下五大面向：

1. **品質 (Quality)** – 評估 Agent 的回應正確性與一致性  
2. **行為 (Behavior)** – 監控功能呼叫、回應邏輯與合規性  
3. **成本 (Cost)** – 控制 Token 用量、選擇合適模型  
4. **安全 (Security)** – 防範 Prompt Injection 與資料洩漏  
5. **CI/CD** – 將自動化測試與持續驗證納入部署流程  

---

## Infrastructure
> Waiting for it...

## Functionality
> Waiting for it...

## 🔍 ARE 的應用

* **品質 (Quality)**：使用 **Vertex AI Evaluation** 評估 RAG 回答可信度
* **行為 (Behavior)**：Cloud Monitoring 追蹤 Function Calls
* **成本 (Cost)**：記錄 Token 使用量，測試不同模型選擇策略
* **安全 (Security)**：建立 **Prompt Injection Guardrails**
* **CI/CD**：將自動化測試與監控指標整合進 Cloud Build 流程

## 🚀 Demo

1. Clone project

```
git clone https://github.com/viiccwen/are-on-google-cloud.git
cd /are-on-google-cloud
```

2. 進入虛擬環境
> 確保你有 `uv` 和 `gcloud`

```
uv sync
source .venv/bin/activate
```

## Visualization

* **Cloud Monitoring Dashboard**：
  * Function Call 成功率
  * RAG 查詢命中率
  * 平均延遲 / 回應時間

* **BigQuery Analysis**：
  * 儲存與分析查詢日誌
  * 偵測高錯誤率或異常模式