from langchain.prompts import PromptTemplate
# Contents of the JSON from OpenAI
# '[[["Country"], ["Why?"], ["What?"], ["google_image_search_query"]], [["Country"], ["Why?"], ["What?"], ["google_image_search_query"]],\
# [["Country"], ["Why?"], ["What?"], ["google_image_search_query"]], [["Country"], ["Why?"], ["What?"], ["google_image_search_query"]],\
# [["Country"], ["Why?"], ["What?"], ["google_image_search_query"]], [["Country"], ["Why?"], ["What?"], ["google_image_search_query"]],\
# [["Country"], ["Why?"], ["What?"], ["google_image_search_query"]], [["Country"], ["Why?"], ["What?"], ["google_image_search_query"]],\
# [["Country"], ["Why?"], ["What?"], ["google_image_search_query"]], [["Country"], ["Why?"], ["What?"], ["google_image_search_query"]]]'\
# Make Why? no more than 3 words, What? is a fact or name related to Why? and its also very concise no more than 3 words.\
# google_image_search_query is a google image search query that fits the country/topic as well as the What? if its an easy search (avoid numbers unless a year) also no more than 3 words\
# Make sure response is in the correct order! 10th place first and 1st place last!'
video_template4 = PromptTemplate(
    input_variables=['topic'],
    template='Determine the top 10 countries specifically related to given input, starting from the 10th best to the 1st. Your response should be a valid JSON 3D array format, starting from the 10th place and ascending to the 1st. The format should be as follows: [["Country"], ["Reason"], ["Fact"], ["Google Image Search Query"]], with each country represented in a similar manner. The "Reason" should be concise, no more than three words, explaining why the country is ranked at that position. The "Fact" is a brief fact or name related to the "Reason", also limited to three words. The "Google Image Search Query" should be a suitable search term for images related to the country and the topic, avoiding numbers unless it is a year, and should also be no more than three words Ensure the response is in the correct order, with the 10th place first and the 1st place last.\
    Input: Castles\
    \
    Output:[[["Sweden"], ["Beautiful Architecture"], ["Visby Medieval Walls"], ["Sweden Castles"]],\
    [["Scotland"], ["Historical Heritage"], ["Edinburgh Castle"], ["Scotland Castles"]],\
    [["Germany"], ["Fairy Tale Castles"], ["Neuschwanstein Castle"], ["Germany Castles"]],\
    [["Wales"], ["Impressive Fortresses"], ["Conwy Castle"], ["Wales Castles"]],\
    [["France"], ["Château Country"], ["Château de Chambord"], ["France Castles"]],\
    [["Spain"], ["Moorish Castles"], ["Alhambra Palace"], ["Spain Castles"]],\
    [["England"], ["Tower of London"], ["Tower of London"], ["England Castles"]],\
    [["Ireland"], ["Medieval Strongholds"], ["Blarney Castle"], ["Ireland Castles"]],\
    [["Czech Republic"], ["Bohemian Castles"], ["Prague Castle"], ["Czech Republic Castles"]],\
    [["Japan"], ["Japanese Castles"], ["Himeji Castle"], ["Japan Castles"]]]\
    Input: Military Ranking\
    \
    Output:[[["Turkey"], ["Regional Power]", ["Strategic Location]", "[Turkey Military"]],\
    [["South Korea"], ["Technological Advancement"], ["K2 Black Panther"], ["South Korea Military"]],\
    [["Germany"], ["Modern Armed Forces]", ["Bundeswehr"], ["Germany Military"],\
    [["Israel"], ["Advanced Defense Systems"], ["Iron Dome"], ["Israel Military"]],\
    [["Japan"], ["Self-Defense Forces"], ["JSDF"], ["Japan Military"]],\
    [["India"], ["Large Military"], ["Indian Army"], ["India Military"]],\
    [["Russia"], ["Nuclear Capabilities"], ["Russian Military"], ["Russia Military"]],\
    [["China"], ["Growing Military Power"], ["PLA"], ["China Military"]],\
    [["United Kingdom"], ["Global Power Projection"], ["Royal Navy"], ["UK Military"]],\
    [["United States"], ["Superpower Status"], ["Pentagon"], ["US Military"]]]\
    Input: {topic}\
    \
    Output: '
)


fact_check_template = PromptTemplate(
    input_variables=['topic', 'response'],
    template='Please fix the following ranking list, which needs to be represented in a 3D array.\
            The ranking list contains countries ranked specifically related to "{topic}".\
        The list needs to be sorted from 10th place to 1st place.\
        \
        Your task is to:\
        1) Inspect the ranking list to see if it is in the correct order. If the list is not in the order of 10th place to 1st place, you will need to reverse it.\
        2) Fact-check the list to ensure that the ranking is correct. If any of the rankings are incorrect, you will need to make the necessary changes to the list.\
        3)Print only the new list with the corrected rankings, sorted from 10th place to 1st place.\
        4)Make sure to complete the list if ranking list is incomplete, there might be missing brackets make sure they are added.\
        Final Array should look like this with its contents,its a an array holding arrays which each contain 4 arrays: [[[...],[...],[...],[...]],[[...],[...],[...],[...]],[[...],[...],[...],[...]],[[...],[...],[...],[...]],[[...],[...],[...],[...]],[[...],[...],[...],[...]],[[...],[...],[...],[...]],[[...],[...],[...],[...]],[[...],[...],[...],[...]],[[...],[...],[...],[...]]]\
        Note: The first element of each sub-array represents the name of the country, the second element represents the reason for ranking, the third element represents\
        the category or topic being ranked, and the fourth element represents the Google image search query for the country (be sure to include adjectives like beautiful).\
        \
        Input: [[["Malaysia"], ["Modern Equipment"], ["Scorpene Submarines"], ["Malaysia Military"]],\
                [["Afghanistan"], ["Military Power"], ["Afghan National Army"], ["Afghanistan Military"]],\
                [["Iraq"], ["Military Strength"], ["Iraqi Armed Forces"], ["Iraq Military"]],\
                [["Indonesia"], ["Large Navy"], ["KRI Sultan Hasanuddin"], ["Indonesia Military"]],\
                [["Algeria"], ["Strong Air Force"], ["Rafale Fighter Jets"], ["Algeria Military"]],\
                [["Egypt"], ["Large Army"], ["Egyptian Armed Forces"], ["Egypt Military"]],\
                [["United Arab Emirates"], ["Advanced Weapons"], ["F-16E/F"], ["UAE Military"]],\
                [["Saudi Arabia"], ["Military Spending"], ["F-15SA"], ["Saudi Arabia Military"]],\
                [["Iran"], ["Regional Influence"], ["IRGC"], ["Iran Military"]],\
                [["Pakistan"], ["Nuclear Arsenal"], ["K2 Black Panther"], ["Pakistan Military"]],\
                [["Turkey"], ["Modern Military"], ["Turkish Armed Forces"], ["Turkey Military\
        \
        Output: [[["Malaysia"], ["Modern Equipment"], ["Scorpene Submarines"], ["Malaysia Military"]],\
                [["Afghanistan"], ["Military Power"], ["Afghan National Army"], ["Afghanistan Military"]],\
                [["Iraq"], ["Military Strength"], ["Iraqi Armed Forces"], ["Iraq Military"]],\
                [["Indonesia"], ["Large Navy"], ["KRI Sultan Hasanuddin"], ["Indonesia Military"]],\
                [["Algeria"], ["Strong Air Force"], ["Rafale Fighter Jets"], ["Algeria Military"]],\
                [["Egypt"], ["Large Army"], ["Egyptian Armed Forces"], ["Egypt Military"]],\
                [["United Arab Emirates"], ["Advanced Weapons"], ["F-16E/F"], ["UAE Military"]],\
                [["Saudi Arabia"], ["Military Spending"], ["F-15SA"], ["Saudi Arabia Military"]],\
                [["Iran"], ["Regional Influence"], ["IRGC"], ["Iran Military"]],\
                [["Pakistan"], ["Nuclear Arsenal"], ["K2 Black Panther"], ["Pakistan Military"]],\
                [["Turkey"], ["Modern Military"], ["Turkish Armed Forces"], ["Turkey Military]]]\
        \
        Input:  [[["Brazil"], ["Jogo Bonito"], ["Campeonato Brasileiro"], ["Brazil Soccer"]],\
                [["Belgium"], ["Rising Talent"], ["Jupiler Pro League"], ["Belgium Soccer"]],\
                [["Portugal"], ["Skillful Players"], ["Primeira Liga"], ["Portugal Soccer"]],\
                [["Netherlands"], ["Total Football"], ["Eredivisie"], ["Netherlands Soccer"]],\
                [["France"], ["Competitive Teams"], ["Ligue 1"], ["France Soccer"]],\
                [["Germany"], ["Attacking Football"], ["Bundesliga"], ["Germany Soccer"]],\
                [["Italy"], ["Defensive Style"], ["Serie A"], ["Italy Soccer"]],\
                [["Spain"], ["High Quality"], ["La Liga"], ["Spain Soccer"]],\
                [["England"], ["Top Players"], ["Premier League"], ["England Soccer"]]]\
        \
        Output: [[["England"], ["Top Players"], ["Premier League"], ["England Soccer"]],\
                [["Spain"], ["High Quality"], ["La Liga"], ["Spain Soccer"]],\
                [["Italy"], ["Defensive Style"], ["Serie A"], ["Italy Soccer"]],\
                [["Germany"], ["Attacking Football"], ["Bundesliga"], ["Germany Soccer"]],\
                [["France"], ["Competitive Teams"], ["Ligue 1"], ["France Soccer"]],\
                [["Netherlands"], ["Total Football"], ["Eredivisie"], ["Netherlands Soccer"]],\
                [["Portugal"], ["Skillful Players"], ["Primeira Liga"], ["Portugal Soccer"]],\
                [["Belgium"], ["Rising Talent"], ["Jupiler Pro League"], ["Belgium Soccer"]],\
                [["Brazil"], ["Jogo Bonito"], ["Campeonato Brasileiro"], ["Brazil Soccer"]]]\
        \
        Input: \
        \
        Output: \
        \
        Input: {response}\
        \
        Output: '

)
