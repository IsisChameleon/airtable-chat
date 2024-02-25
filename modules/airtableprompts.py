from llama_index.core.prompts.base import PromptTemplate
from llama_index.core.prompts.prompt_type import PromptType

TEXT_TO_SQL_TMPL = (
    """Given an input question, create a syntactically correct {dialect} 
    query to run.
    You can order the results by a relevant column to return the most 
    interesting examples in the database.

    Pay attention to use only the column names that you can see in the schema description.
    Be careful to not query for columns that do not exist.
    Pay attention to which column is in which table.
    Also, qualify column names with the table name when needed.
    You are required to use the following format, each taking one line:

    Question: Question here
    SQLQuery: SQL Query to run

    Only use tables listed below.
    {schema}

    Infer the meaning of the columns from their name.

    In table "build_club_members", each member can list 4 skills in columns skill_1, skill_2, skill_3, skill_4.
    Here's the set of possible values these columns can take:
    'AI / ML specialist researcher',
    'AI Engineer',
    'Backend software dev',
    'Designer',
    'Domain expert',
    'Front end software dev',
    'Go to market',
    'Idea validating',
    'Product management'

    So when the Question mentions a semantically similar skill, please translate into one of the existing skill or a combination of similar skills.
    For example: 
    Question: What builders are software engineers?
    SQLQuery: SELECT * FROM build_club_members WHERE skill_1 = 'Backend software dev' OR skill_1 = 'Front end software dev' 
                OR skill_2 = 'Backend software dev' OR skill_2 = 'Front end software dev'
                OR skill_3 = 'Backend software dev' OR skill_3 = 'Front end software dev'
                OR skill_4 = 'Backend software dev' OR skill_4 = 'Front end software dev'

    Question: What builders are into UX Design?
    SQLQuery: SELECT * FROM build_club_members WHERE skill_1 = 'Designer' OR skill_2 = 'Designer' OR skill_3 = 'Designer' OR skill_4 = 'Designer'
    
    Question: Who works on ML algorithms?
    SQLQuery: SELECT * FROM build_club_members WHERE skill_1 = 'AI / ML specialist researcher' OR skill_2 = 'AI / ML specialist researcher'
    
    Question: What is the linkedin of Caesar De Keijzer?
    SQLQuery: SELECT linkedin_url FROM build_club_members WHERE lower(member_name) like 'caesar%de%keyzer'

    When the Question is about how many members have such and such features, use SELECT COUNT(*):
    Question: How many members are based in Sydney?
    SQLQuery: SELECT count(*) FROM build_club_members WHERE where lower(location) = 'sydney';

    Question: How many members are accepted into the club?
    SQLQuery: SELECT count(*) FROM build_club_members WHERE where member_acceptance_in_club = true;
    
    Question: {query_str}
    SQLQuery: 
    """
)

TEXT_TO_SQL_PROMPT = PromptTemplate(
    TEXT_TO_SQL_TMPL,
    prompt_type=PromptType.TEXT_TO_SQL,
)

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

TEXT_TO_SQL_TMPL2 = (
    """Given an input question, first create a syntactically correct {dialect} 
    query to run, then look at the results of the query and return the answer. 
    You can order the results by a relevant column to return the most 
    interesting examples in the database.

    Pay attention to use only the column names that you can see in the schema
    description.
    Be careful to not query for columns that do not exist.
    Pay attention to which column is in which table.
    Also, qualify column names with the table name when needed.
    You are required to use the following format, each taking one line:

    Question: Question here
    SQLQuery: SQL Query to run
    SQLResult: Result of the SQLQuery
    Answer: Final answer here

    Only use tables listed below.
    {schema}

    In table "build_club_members", each member can list 4 skills in columns skill_1, skill_2, skill_3, skill_4.
    Here's the set of possible values these columns can take:
    'AI / ML specialist researcher',
    'AI Engineer',
    'Backend software dev',
    'Designer',
    'Domain expert',
    'Front end software dev',
    'Go to market',
    'Idea validating',
    'Product management'
    
    So when the Question mentions a semantically similar skill, please translate into one of the existing skill or a combination of similar skills.
    For example: 
    Question: "What builders are software engineers?"
    SQLQuery: "SELECT member_name, linkedin_url FROM build_club_members WHERE skill_1 = 'Backend software dev' OR skill_1 = 'Front end software dev' 
                OR skill_2 = 'Backend software dev' OR skill_2 = 'Front end software dev'
                OR skill_3 = 'Backend software dev' OR skill_3 = 'Front end software dev'
                OR skill_4 = 'Backend software dev' OR skill_4 = 'Front end software dev'

    Question: "What builders are into UX Design?"
    SQLQuery: "SELECT member_name, linkedin_url FROM build_club_members WHERE skill_1 = 'Designer'
                OR skill_2 = 'Designer' 
                OR skill_3 = 'Designer'
                OR skill_4 = 'Designer'

    Question: {query_str}
    SQLQuery: 
    """
)

TEXT_TO_SQL_PROMPT2 = PromptTemplate(
    TEXT_TO_SQL_TMPL2,
    prompt_type=PromptType.TEXT_TO_SQL,
)

TEXT_TO_SQL_TMPL_old1 = (
    """Given an input question, first create a syntactically correct {dialect} 
    query to run, then look at the results of the query and return the answer. 
    You can order the results by a relevant column to return the most 
    interesting examples in the database.

    Pay attention to use only the column names that you can see in the schema description.
    Be careful to not query for columns that do not exist.
    Pay attention to which column is in which table.
    Also, qualify column names with the table name when needed.
    You are required to use the following format, each taking one line:

    Question: Question here
    SQLQuery: SQL Query to run
    SQLResult: Result of the SQLQuery
    Answer: Final answer here

    Only use tables listed below.
    {schema}

    In table "build_club_members", each member can list 4 skills in columns skill_1, skill_2, skill_3, skill_4.
    Here's the set of possible values these columns can take:
    'AI / ML specialist researcher',
    'AI Engineer',
    'Backend software dev',
    'Designer',
    'Domain expert',
    'Front end software dev',
    'Go to market',
    'Idea validating',
    'Product management'

    So when the Question mentions a semantically similar skill, please translate into one of the existing skill or a combination of similar skills.
    For example: 
    Question: What builders are software engineers?
    SQLQuery: SELECT member_name, linkedin_url FROM build_club_members WHERE skill_1 = 'Backend software dev' OR skill_1 = 'Front end software dev' 
                OR skill_2 = 'Backend software dev' OR skill_2 = 'Front end software dev'
                OR skill_3 = 'Backend software dev' OR skill_3 = 'Front end software dev'
                OR skill_4 = 'Backend software dev' OR skill_4 = 'Front end software dev'

    Question: What builders are into UX Design?
    SQLQuery: SELECT member_name, linkedin_url FROM build_club_members WHERE skill_1 = 'Designer' OR skill_2 = 'Designer' OR skill_3 = 'Designer' OR skill_4 = 'Designer'
    
    Question: Who works on ML algorithms?
    SQLQuery: SELECT member_name, linkedin_url FROM build_club_members WHERE skill_1 = 'AI / ML specialist researcher' OR skill_2 = 'AI / ML specialist researcher'
    Question: What is the linkedin of Eric Perez?
    SQLQuery: SELECT linkedin_url FROM build_club_members WHERE lower(member_name) = 'eric perez'

    When the Question is about how many members have such and such features, use SELECT COUNT(*):
    Question: How many members are based in Sydney?
    SQLQuery: SELECT count(*) FROM build_club_members WHERE lower(location) = 'sydney';
    Question: How many members are accepted (into the club?
    SQLQuery: SELECT count(*) FROM build_club_members WHERE member_acceptance_in_club = true;
    
    Question: {query_str}
    SQLQuery: 
    """
)