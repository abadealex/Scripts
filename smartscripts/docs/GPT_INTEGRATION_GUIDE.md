
---

### 📄 `docs/GPT_INTEGRATION_GUIDE.md`

```markdown
# GPT Integration Guide

This document outlines how to integrate GPT-4 (or compatible LLMs) into SmartScripts for explanation generation and feedback.

## 🔧 Setup

### 1. API Access

- Supported: OpenAI (GPT-4/3.5), Azure OpenAI
- Required keys:
  - `OPENAI_API_KEY`
  - Optional: `OPENAI_ORG_ID`

Set via environment variables or `.env` file.

### 2. Python Client

Dependencies (add to `requirements.txt`):

```bash
openai>=1.0.0
tiktoken
