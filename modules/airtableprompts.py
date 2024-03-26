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
    'Front end software dev',
    'Go to market',
    'Idea validating',
    'Product management'

    So when the Question mentions a semantically similar skill, please translate into one of the existing skill or a combination of similar skills.
    For example: 
    Question: What builders are software engineers?
    SQLQuery: SELECT id, name, linkedin_url FROM build_club_members WHERE skill_1 = 'Backend software dev' OR skill_1 = 'Front end software dev' 
                OR skill_2 = 'Backend software dev' OR skill_2 = 'Front end software dev'
                OR skill_3 = 'Backend software dev' OR skill_3 = 'Front end software dev'
                OR skill_4 = 'Backend software dev' OR skill_4 = 'Front end software dev'

    Question: What builders are into UX Design?
    SQLQuery: SELECT id, name, linkedin_url FROM build_club_members WHERE skill_1 = 'Designer' OR skill_2 = 'Designer' OR skill_3 = 'Designer' OR skill_4 = 'Designer'
    
    Question: Who works on ML algorithms?
    SQLQuery: SELECT id, name, linkedin_url FROM build_club_members WHERE skill_1 = 'AI / ML specialist researcher' OR skill_2 = 'AI / ML specialist researcher'
    
    Question: What is the linkedin of Caesar De Keijzer?
    SQLQuery: SELECT id, name, linkedin_url FROM build_club_members WHERE lower(member_name) like 'caesar%de%keyzer'

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