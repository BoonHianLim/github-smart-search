key_word_prompt = """You are a helpful assistant. Given a user query, extract the most relevant and concise keywords that would be useful for performing a GitHub repository search. 
The keywords should focus on technologies, programming languages, libraries, tools, or tasks mentioned in the query. 
Avoid common stop words or irrelevant phrases. 
List the keywords from the query that are most likely to yield relevant results when searching on GitHub.
Return the keywords as a comma-separated list.
"""

key_word_prompt_few_shots = """
You are a helpful assistant. Given a user query, extract a list of distinct keywords that can be used to search for relevant GitHub repositories. Each keyword or keyphrase should represent exactly one area of interest expressed by the user — such as a specific technology, tool, library, task, or research topic. Avoid general or ambiguous terms. Do not include multiple concepts in a single keyword. List the keywords from the query that are most likely to yield relevant results when searching on GitHub. Return the keywords as a comma-separated list.

Example 1:
User Query:

I'm a researcher exploring multi-modal large language models. I'm particularly interested in how models process both images and text, and I want to understand the current state-of-the-art methods in this area.

Keywords:
multi-modal LLM, vision-language models, multi-modal reasoning

Example 2:
User Query:

I'm working on building real-time object detection apps using TensorFlow and running them on mobile devices.

Keywords:
real-time object detection, TensorFlow, mobile deployment

Example 3:
User Query:

I want to explore open-source projects using Rust for systems programming, especially those that deal with networking or concurrency.

Keywords:
Rust, systems programming, networking, concurrency

Example 4:
User Query:

How can I create a chatbot using GPT models and integrate it into a Discord server?

Keywords:
chatbot, GPT, Discord integration

Example 5:
User Query:

I am a student studying SC4051 distributed systems in NTU, and i want to know what the seniors do for their project.

Keywords:
SC4051, distributed systems, NTU

Now extract the keywords from this user query:
User Query:

{{USER_QUERY_HERE}}

Keywords:
"""


def get_key_word_prompt_openai(query: str) -> list:
    """
    Function to get the prompt for extracting keywords from the user query.
    """
    return [
        {
            "role": "user",
            "content": key_word_prompt + "\n\n" + query
        }
    ]


def get_key_word_prompt_few_shots_openai(query: str) -> list:
    """
    Function to get the prompt for extracting keywords from the user query with few-shot examples.
    """
    return [
        {
            "role": "user",
            "content": key_word_prompt_few_shots.replace("{{USER_QUERY_HERE}}", query)
        }
    ]


SUMMARIZE_PROMPT = """You are a research assistant helping a user explore and understand a list of GitHub repositories related to a specific topic.
Each repository contains a README file describing the project, tool, or research contribution.
Your task is to analyze the list of READMEs and summarize the key findings, interesting patterns, and insightful highlights that may help the user discover useful tools, trends, or research directions.

Please provide:
* A concise summary of the overall theme of the repositories.
* A bulleted list of interesting features, innovations, or tools that appear across the repositories.
* Any common patterns or differences you observe in the purpose, implementation, or technologies used.
* If possible, mention notable authors, affiliations, or linked research papers that appear across projects.
* A final paragraph offering insights or suggestions for the user based on your analysis (e.g., which direction looks promising, tools worth trying, or papers to read).

Format your response for readability using clear sections and bullet points."""


def get_summarise_prompt_openai(readme: list[str]) -> list:
    """
    Function to get the prompt for summarising the README content.
    """
    return [
        {
            "role": "user",
            "content": SUMMARIZE_PROMPT + "\n\n" + "\n\n".join(readme)
        }
    ]


RESEARCH_ASSISTANT_ZERO_SHOT_SUMMARIZE_PROMPT = """You are a research assistant helping a user explore and understand a list of GitHub repositories related to a specific topic.
Each repository contains a README file describing the project, tool, or research contribution.
Your task is to analyze the list of READMEs and summarize the key findings, interesting patterns, and insightful highlights that may help the user discover useful tools, trends, or research directions.
The user is interested in {use_case} and wants to know more about the repositories related to this topic. Your analysis should focus on the most relevant aspects of the repositories that align with this use case, and you may ignore repositories that are not directly related to it.

Please provide:
* A concise summary of the overall theme of the repositories.
* A bulleted list of interesting features, innovations, or tools that appear across the repositories.
* Any common patterns or differences you observe in the purpose, implementation, or technologies used.
* If possible, mention notable authors, affiliations, or linked research papers that appear across projects.
* A final paragraph offering insights or suggestions for the user based on your analysis (e.g., which direction looks promising, tools worth trying, or papers to read).

Format your response for readability using clear sections and bullet points."""

TECHNICAL_ANALYST_ASSISTANT_ZERO_SHOT_SUMMARIZE_PROMPT = """You are a technical analyst assistant. I will provide you with multiple GitHub README contents, each corresponding to a different tool or library. Your task is to:

Identify the main purpose and functionality of each tool.

Extract the key features, supported technologies, and usage context.

Analyze the pros and cons of each tool based on the information given (and optionally your prior knowledge).

Compare the tools with respect to usability, integration flexibility, performance, and documentation quality.

Based on a given use case (provided at the end), recommend the most suitable tool(s) and justify your choice clearly.

My use case is: {use_case}
Your analysis should focus on the most relevant aspects of the repositories that align with this use case, and you may ignore repositories that are not directly related to it.

Format your response as:

```markdown
## Tool Summary
- Tool 1:
  - Purpose:
  - Key Features:
  - Pros:
  - Cons:

- Tool 2:
  ...

## Comparison Table (Optional)
| Tool       | Pros                      | Cons                      | Suitable for             |
|------------|---------------------------|---------------------------|--------------------------|
| Tool 1     | Easy to use, lightweight  | Lacks plugin system       | Simple projects          |

## Recommendation (Based on Use Case)
Given the use case: [insert use case here], the recommended tool is **Tool X** because...
```

Let's begin. Here are the README contents:
"""


def get_custom_summarise_prompt_openai(prompt: str, readme: list[str]) -> list:
    """
    Function to get the prompt for custom summarising the README content.
    """
    return [
        {
            "role": "user",
            "content": prompt + "\n\n" + "\n\n".join(readme)
        }
    ]


QUERY_REFINEMENT_PROMPT = """You are a helpful assistant that improves vague or informal user queries into clear, specific prompts suitable for searching GitHub repositories or summarizing their content.

The refined prompt should:
- Be concise and precise.
- Include any relevant domain keywords (e.g., course codes, tools, technologies).
- Specify the intent (e.g., “summarize the purpose of this repository”, “extract assignment-related details”).
- Reflect the user’s background if implied (e.g., student, developer, researcher).
- Return the refined prompt without any additional text.

Refine the following user query:"""


def get_query_refinement_prompt_openai(prompt: str) -> list:
    """
    Function to get the prompt for query refinement.
    """
    return [
        {
            "role": "user",
            "content": QUERY_REFINEMENT_PROMPT + "\n\n" + prompt
        }
    ]
