SUMMARIZE_PROMPTING_METHOD = [
    "Normal"]
LLM_PROMPTING_METHOD = ["LLM: Query Refinement"]
TEMPLATE_PROMPTING_METHOD = [
    "Template: Research Assistant", "Template: Technical Analyst"]
SUMMARIZE_PROMPTING_METHOD.extend(LLM_PROMPTING_METHOD)
SUMMARIZE_PROMPTING_METHOD.extend(TEMPLATE_PROMPTING_METHOD)
