answer_prompt_tpl = """Write an answer {answer_length} for the question below based on the provided context. If
the context provides insufficient information, reply "I cannot answer". For each part of
your answer, indicate which sources most support it via valid citation markers at the end
of sentences, like (Example2012). Answer in an unbiased, comprehensive, and scholarly
tone. If the question is subjective, provide an opinionated answer in the concluding 1-2
sentences.

{context}

Query: {query}
Answer:

"""
answer_prompt = PromptTemplate(answer_prompt_tpl, prompt_type=PromptType.CUSTOM)