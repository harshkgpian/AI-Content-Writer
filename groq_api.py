from groq import Groq
import ast

client = Groq(api_key="YOUR_API_KEY")
model = "llama3-8b-8192"

def summarize(text):
    instruction = (
        "As a senior content writer, you are tasked with generating relevant pointers based on the given text.\n"
        "Focus on the most relevant information and provide important links or citations for each point.\n"
        "Ensure each pointer is concise and includes a relevant citation or link to further information.\n"
        "Do not include introductory phrases such as 'Here are the pointers' or 'Following are the citations.'\n"
        "Instead, directly present the pointers with the corresponding links or citations."
    )


    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"{instruction}\n Here is the text: {text}\n Do not give any heading or ending sentence, just give the summarized text.",
            }
        ],
        model=model,
    )

    return chat_completion.choices[0].message.content, chat_completion.usage.total_tokens

def generate_keywords(topic):
    
# Define the tool for checking relevance of keywords
    check_relevance = {
        "type": "function",
        "function": {
            "name": "Check Relevance",
            "description": "From the keywords extracted, check relevance of a website using countvectorizer",
            "parameters": {
                "type": "object",
                "properties": {
                    "keywords": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "List of single-word SEO keywords"
                    }
                },
                "required": ["keywords"],
            },
        },
    }

    # Prior message from the system providing context
    system_message = {
        "role": "system",
        "content": (
            "You are an AI model assisting a Senior SEO Specialist. Your objective is to generate relevant single-word SEO keywords "
            "based on a given blog topic. These keywords will be used to assess the relevance of scraped websites."
        )
    }

    # Instruction for generating single-word SEO keywords
    instruction = {
        "role": "user",
        "content": (
            "As a Senior SEO Specialist, you are tasked with generating specifications based on the blog topic and information scraped from websites.\n"
            "Your objective is to analyze the blog topic to provide relevant single-word SEO keywords.\n\n"
            "Step 1: Analysis. Conduct a thorough analysis of the blog topic to identify key themes and concepts.\n"
            "Step 2: Specification. Generate relevant single-word SEO keywords based on the analysis.\n\n"
            f"Topic: {topic}\n\n"
            "Ensure the keywords are single words and directly relevant to the topic."
        )
    }

    # Create the chat completion
    chat_completion = client.chat.completions.create(
        messages=[
            system_message,
            instruction,
        ],
        model=model,
        tools=[check_relevance]
    )

    # Extract the keywords from the tool call arguments
    keywords = ast.literal_eval(chat_completion.choices[0].message.tool_calls[0].function.arguments)["keywords"]

    return keywords, chat_completion.usage.total_tokens


def generate_web_search_queries(topic):

    web_search_and_scrape_tool = {
        "type": "function",
        "function": {
            "name": "Perform Web Search and Scrape",
            "description": "Perform a Google search using the provided queries and scrape the websites to gather relevant information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "queries": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "List of Google search queries to perform."
                    }
                },
                "required": ["queries"]
            }
        }
    }
    # Prior message from the system providing context
    system_message = {
        "role": "system",
        "content": (
            "You are an AI model tasked with assisting a Senior SEO Specialist. Your objective is to help generate Google search queries "
            "based on the given blog topic. The generated queries will be used to find relevant articles to scrape for content creation."
        )
    }

    # Instruction for generating Google search queries
    instruction = {
        "role": "user",
        "content": (
            "You are a Senior SEO Specialist tasked with generating relevant Google search queries based on a blog topic.\n"
            "Your goal is to find the best articles to scrape for content creation.\n\n"
            "Step 1: Analyze the blog topic to identify key themes and concepts.\n"
            "Step 2: Generate a list of relevant Google search queries based on the analysis. Each query should be specific and targeted to find articles that provide comprehensive information on the topic.\n\n"
            f"Topic: {topic}\n\n"
            "Ensure the queries are highly relevant to the topic and are likely to return articles with valuable insights."
        )
    }

    # Create the chat completion
    chat_completion = client.chat.completions.create(
        messages=[
            system_message,
            instruction,
        ],
        model=model,
        tools=[web_search_and_scrape_tool]
    )

    # Extract the queries from the tool call arguments
    queries = ast.literal_eval(chat_completion.choices[0].message.tool_calls[0].function.arguments)["queries"]

    return queries, chat_completion.usage.total_tokens

def specifications(topic, summary):
    instruction = (
        "As a Senior Specification Agent and SEO specialist, you are responsible for generating specifications for blog posts based on the topic and scraped content.\n"
        "Your task is to analyze the topic and the content gathered from web scraping to provide relevant specifications for the blog post.\n\n"
        f"Step 1: Analysis. Conduct a thorough analysis of the blog topic {topic} and the summary of information gathered from web scraping to identify key themes, concepts, and requirements.\n"
        "Step 2: Specification. Generate specifications based on the analysis, including:\n"
        "- Target Audience: Specify the target audience based on the content.\n"
        "- SEO Keywords: Identify relevant SEO keywords from the content.\n"
        "- Tone and Style: Recommend the tone and style that would best suit the audience and the content.\n\n"
        f"Here is the summary of the scraped content:\n{summary}\n\n"
        "Based on the analysis, here are the specifications for the blog post:\n"
        "Please provide these specifications to the Content Writer Agent for crafting the blog post.\n"
        "Ensure the specifications align with the topic and the content gathered from web scraping.\n"
        "Happy specifying!"
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": instruction,
            }
        ],
        model=model,
    )

    return chat_completion.choices[0].message.content, chat_completion.usage.total_tokens

def write_blog_post(topic, summary, specification, words):
    instruction = (
        f"You are a Senior Content Writer tasked with creating an SEO-optimized blog post in {words + 100} words.\n"
        "As a seasoned writer, you're expected to leverage your expertise and skills to produce high-quality content that resonates with our audience.\n\n"
        "Step 1: Analysis. Utilize your research skills to analyze the topic, summary, and specifications to understand the requirements.\n"
        "Step 2: Generation. Draw upon your creativity and writing expertise to generate a well-structured blog post that incorporates the provided information.\n\n"
        f"Here is the topic: {topic}\n"
        f"Here is the summary/suggestion, feel free to discard any part if its not relevant: {summary}\n"
        f"Here are the number of words: {words}\n"
        f"Here are the specifications:\n{specification}\n\n"
        "As a senior writer, you're expected to demonstrate your mastery of writing skills, including attention to detail, creativity, and SEO knowledge.\n"
        "Craft a blog post that showcases your expertise and meets the specified requirements.\n"
        "Provide the blog post, showcasing your writing prowess."
    )
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": instruction,
            }
        ],
        model=model,
    )

    return chat_completion.choices[0].message.content, chat_completion.usage.total_tokens
def edit_and_proofread(topic, generated_blog_post):
    # Instruction for editing and proofreading the generated blog post
    instruction = (
        "As an Editor and Proofreader, your role is to elevate the quality of the content to meet our standards of excellence. "
        "The blog post crafted by our Specialist Blog Writer serves as the foundation for your enhancements.\n\n"
        "Step 1: Review. Immerse yourself in the topic and the generated blog post, understanding its purpose and intended audience.\n"
        "Step 2: Edit. Enhance the clarity, coherence, and overall flow of the content by rectifying any grammatical errors, inconsistencies, or awkward phrasing.\n"
        "Step 3: Proofread. Scrutinize every word and punctuation mark, ensuring accuracy, consistency, and adherence to our style guidelines.\n\n"
        f"Topic: {topic}\n\n"
        "Here is the blog post crafted by our Specialist Blog Writer for your meticulous review and refinement:\n"
        f"{generated_blog_post}\n\n"
        "After your careful scrutiny and enhancements, the blog post will be ready to captivate and inform our audience.\n"
        "Your dedication to excellence is integral to our commitment to delivering exceptional content."
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f" generate a blog post on the provided topi : {topic}. "
            },
            {
                "role": "user",
                "content": instruction,
            }
        ],
        model=model,
    )

    return chat_completion.choices[0].message.content, chat_completion.usage.total_tokens


def ask_follow_up_question(topic, blog):
    # Define the tool for question generation
    question_generation_tool = {
        "type": "function",
        "function": {
            "name": "Generate Question",
            "description": "Generate a follow-up question related to the given topic based on the provided content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The topic of the blog."
                    },
                    "blog": {
                        "type": "string",
                        "description": "The content of the blog."
                    }
                },
                "required": ["topic", "blog"],
            },
        },
    }

    instruction = (
        "As an AI agent, your task is to ask a follow-up question related to the given blog topic based on the provided blog content. "
        "The question should encourage further exploration of the topic and engage the reader."
        f" Topic: {topic}\n Blog: {blog}"
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": instruction,
            }
        ],
        model=model,
        tools=[question_generation_tool]  # Include the question generation tool
    )
    ques = ast.literal_eval(chat_completion.choices[0].message.tool_calls[0].function.arguments)["blog"]

    return ques, chat_completion.usage.total_tokens