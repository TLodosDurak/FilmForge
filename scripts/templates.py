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
    template='''Determine the top 10 countries specifically related to given input, starting from the 10th best to the 1st. 
                Your response should be a valid JSON 3D array format, starting from the 10th place and ascending to the 1st. 
                The format should be as follows: [["Country"], ["Reason"], ["Fact"], ["Google Image Search Query"]], 
                with each country represented in a similar manner. The "Reason" should be concise, no more than three words, 
                explaining why the country is ranked at that position. The "Fact" is a brief fact or name related to the "Reason", 
                also limited to three words. The "Google Image Search Query" should be a suitable search term for images related to 
                the country and the topic, avoiding numbers unless it is a year, and should also be no more than three words Ensure 
                the response is in the correct order, with the 10th place first and the 1st place last.
                Question: Castles
                
                Answer:[[["Sweden"], ["Beautiful Architecture"], ["Visby Medieval Walls"], ["Sweden Castles"]], [["Scotland"], ["Historical Heritage"], ["Edinburgh Castle"], ["Scotland Castles"]], [["Germany"], ["Fairy Tale Castles"], ["Neuschwanstein Castle"], ["Germany Castles"]], [["Wales"], ["Impressive Fortresses"], ["Conwy Castle"], ["Wales Castles"]], [["France"], ["Château Country"], ["Château de Chambord"], ["France Castles"]], [["Spain"], ["Moorish Castles"], ["Alhambra Palace"], ["Spain Castles"]], [["England"], ["Tower of London"], ["Tower of London"], ["England Castles"]], [["Ireland"], ["Medieval Strongholds"], ["Blarney Castle"], ["Ireland Castles"]], [["Czech Republic"], ["Bohemian Castles"], ["Prague Castle"], ["Czech Republic Castles"]], [["Japan"], ["Japanese Castles"], ["Himeji Castle"], ["Japan Castles"]]]
                
                Question: Military Ranking
                
                Answer:[[["Turkey"], ["Regional Power]", ["Strategic Location]", "[Turkey Military"]], [["South Korea"], ["Technological Advancement"], ["K2 Black Panther"], ["South Korea Military"]], [["Germany"], ["Modern Armed Forces]", ["Bundeswehr"], ["Germany Military"], [["Israel"], ["Advanced Defense Systems"], ["Iron Dome"], ["Israel Military"]], [["Japan"], ["Self-Defense Forces"], ["JSDF"], ["Japan Military"]], [["India"], ["Large Military"], ["Indian Army"], ["India Military"]], [["Russia"], ["Nuclear Capabilities"], ["Russian Military"], ["Russia Military"]], [["China"], ["Growing Military Power"], ["PLA"], ["China Military"]], [["United Kingdom"], ["Global Power Projection"], ["Royal Navy"], ["UK Military"]], [["United States"], ["Superpower Status"], ["Pentagon"], ["US Military"]]]
                
                Question: {topic}
                
                Answer: Let's think step by step '''
)


fact_check_template = PromptTemplate(
    input_variables=['topic', 'response'],
    template='''Please fix the following ranking list, which needs to be represented in a 3D array.
            The ranking list contains countries ranked specifically related to "{topic}".
        The list needs to be sorted from 10th place to 1st place.
        
        Your task is to:
        1) Inspect the ranking list to see if it is in the correct order. If the list is not in the order of 10th place to 1st place, you will need to reverse it.
        2) Fact-check the list to ensure that the ranking is correct. If any of the rankings are incorrect, you will need to make the necessary changes to the list.
        3)Print only the new list with the corrected rankings, sorted from 10th place to 1st place.
        4)Make sure to complete the list if ranking list is incomplete, there might be missing brackets make sure they are added.
        Final Array should look like this with its contents,its a an array holding arrays which each contain 4 arrays: [[[...],[...],[...],[...]],[[...],[...],[...],[...]],[[...],[...],[...],[...]],[[...],[...],[...],[...]],[[...],[...],[...],[...]],[[...],[...],[...],[...]],[[...],[...],[...],[...]],[[...],[...],[...],[...]],[[...],[...],[...],[...]],[[...],[...],[...],[...]]]
        Note: The first element of each sub-array represents the name of the country, the second element represents the reason for ranking, the third element represents
        the category or topic being ranked, and the fourth element represents the Google image search query for the country (be sure to include adjectives like beautiful).
        
        Question:  [[["Brazil"], ["Jogo Bonito"], ["Campeonato Brasileiro"], ["Brazil Soccer"]], [["Belgium"], ["Rising Talent"], ["Jupiler Pro League"], ["Belgium Soccer"]], [["Portugal"], ["Skillful Players"], ["Primeira Liga"], ["Portugal Soccer"]], [["Netherlands"], ["Total Football"], ["Eredivisie"], ["Netherlands Soccer"]], [["France"], ["Competitive Teams"], ["Ligue 1"], ["France Soccer"]], [["Germany"], ["Attacking Football"], ["Bundesliga"], ["Germany Soccer"]], [["Italy"], ["Defensive Style"], ["Serie A"], ["Italy Soccer"]], [["Spain"], ["High Quality"], ["La Liga"], ["Spain Soccer"]], [["England"], ["Top Players"], ["Premier League"], ["England Soccer"]]]
        
        Answer: [[["England"], ["Top Players"], ["Premier League"], ["England Soccer"]], [["Spain"], ["High Quality"], ["La Liga"], ["Spain Soccer"]], [["Italy"], ["Defensive Style"], ["Serie A"], ["Italy Soccer"]], [["Germany"], ["Attacking Football"], ["Bundesliga"], ["Germany Soccer"]], [["France"], ["Competitive Teams"], ["Ligue 1"], ["France Soccer"]], [["Netherlands"], ["Total Football"], ["Eredivisie"], ["Netherlands Soccer"]], [["Portugal"], ["Skillful Players"], ["Primeira Liga"], ["Portugal Soccer"]], [["Belgium"], ["Rising Talent"], ["Jupiler Pro League"], ["Belgium Soccer"]], [["Brazil"], ["Jogo Bonito"], ["Campeonato Brasileiro"], ["Brazil Soccer"]]]
        
        Question: {response}
        
        Answer: '''

)

item_template1 = PromptTemplate(
    input_variables=['topic'],
    template='Provide a list of the top 10 items related to {topic} based on their attributes and their environment or origin, ranked from the one with the least of this attribute to the most. The response should be a valid JSON 3D array format, starting from the 10th place and ascending to the 1st.\
        Question: Soccer Players\
        \
        Answer: [[["Ferenc Puskás"], ["Prolific Scorer"], ["FIFA 1954"], ["Hungary"]],\
        [["Alfredo Di Stefano"], ["Versatile Forward"], ["FIFA 1960"], ["Argentina"]],\
        [["Franz Beckenbauer"], ["Commanding Defender"], ["FIFA 1974"], ["Germany"]],\
        [["Johan Cruyff"], ["Intelligent Forward"], ["FIFA 1974"], ["Netherlands"]],\
        [["Diego Maradona"], ["Amazing Playmaker"], ["FIFA 1986"], ["Argentina"]],\
        [["Pele"], ["Legendary Forward"], ["FIFA 1970"], ["Brazil"]],\
        [["Cristiano Ronaldo"], ["Powerful Striker"], ["FIFA 2018"], ["Portugal"]],\
        [["Lionel Messi"], ["Incredible Dribbler"], ["FIFA 2019"], ["Argentina"]],\
        [["Ronaldinho"], ["Skillful Player"], ["FIFA 2005"], ["Brazil"]],\
        [["Zinedine Zidane"], ["Elegant Midfielder"], ["FIFA 2000"], ["France"]]]\
        \
        Question: Fastest Cars\
        \
        Answer: [[["Dodge Challenger SRT Hellcat"], ["Fastest Muscle Car"], ["331 km/h"], ["United States"]],\
        [["Bentley Continental GT"], ["Fastest Luxury Car"], ["333 km/h"], ["United Kingdom"]],\
        [["Ferrari LaFerrari"], ["Fastest Hybrid Supercar"], ["350 km/h"], ["Italy"]],\
        [["Lamborghini Aventador SVJ"], ["Fastest Lamborghini"], ["351 km/h"], ["Italy"]],\
        [["Bugatti Veyron Super Sport"], ["Fastest Production Car"], ["431 km/h"], ["France"]],\
        [["Hennessey Venom GT"], ["Fastest Accelerating Car"], ["434 km/h"], ["United States"]],\
        [["SSC Ultimate Aero"], ["Former Fastest Production Car"], ["437 km/h"], ["United States"]],\
        [["Koenigsegg Jesko Absolut"], ["Fastest Koenigsegg"], ["532 km/h"], ["Sweden"]],\
        [["Bugatti Chiron Super Sport 300+"], ["Fastest Bugatti"], ["490 km/h"], ["France"]],\
        [["SSC Tuatara"], ["Current Fastest Production Car"], ["532.7 km/h"], ["United States"]]]\
        \
        Question: {topic}\
        \
        Answer: Let\'s think step by step '
)

item_fact_check_template = PromptTemplate(
    input_variables=['topic', 'response'],
    template='Please revise the provided 3D array ranking list related to "{topic}". The list should be ordered from 10th to 1st place based on the relevant attribute and their environment or origin.\
        \
        Tasks:\
        1) Complete the list if it\'s incomplete or missing brackets.\
        2) Check and reverse the list if it\'s not in the correct order based on the attribute.\
        3) Print the corrected list, sorted from 10th to 1st place based on the attribute.\
        \
        The final array should hold 10 sub-arrays, each containing 4 elements: [[["item"], ["reason for rank"], ["topic"], ["environment/origin"]], ..., [["item"], ["reason for rank"], ["topic"], ["environment/origin"]]].\
        \
        Question: Heaviest Animals , [[["African Elephant"], ["7,500 kg"], ["Loxodonta africana"], ["African Savannas"]],\
        [["Hippopotamus"], ["3,500 kg"], ["Hippopotamus amphibius"], ["African Rivers"]],\
        [["White Rhinoceros"], ["2,300 kg"], ["Ceratotherium simum"], ["African Grasslands"]],\
        [["Giraffe"], ["1,200 kg"], ["Giraffa camelopardalis"], ["African Savannas"]],\
        [["Grizzly Bear"], ["800 kg"], ["Ursus arctos"], ["North American Forests"]],\
        [["Polar Bear"], ["700 kg"], ["Ursus maritimus"], ["Arctic Region"]],\
        [["Asian Elephant"], ["5,400 kg"], ["Elephas maximus"], ["Asian Forests"]],\
        [["Walrus"], ["1,800 kg"], ["Odobenus rosmarus"], ["Arctic Region"]],\
        [["Gorilla"], ["200 kg"], ["Gorilla gorilla"], ["African Rainforests"]],\
        [["Giant Anteater"], ["90 kg"], ["Myrmecophaga tridactyla"], ["South American Grasslands"]]\
        \
        Answer:[[["Giant Anteater"], ["90 kg"], ["Myrmecophaga tridactyla"], ["South American Grasslands"]],\
        [["Gorilla"], ["200 kg"], ["Gorilla gorilla"], ["African Rainforests"]],\
        [["Walrus"], ["1,800 kg"], ["Odobenus rosmarus"], ["Arctic Region"]],\
        [["Asian Elephant"], ["5,400 kg"], ["Elephas maximus"], ["Asian Forests"]],\
        [["Polar Bear"], ["700 kg"], ["Ursus maritimus"], ["Arctic Region"]],\
        [["Grizzly Bear"], ["800 kg"], ["Ursus arctos"], ["North American Forests"]],\
        [["Giraffe"], ["1,200 kg"], ["Giraffa camelopardalis"], ["African Savannas"]],\
        [["White Rhinoceros"], ["2,300 kg"], ["Ceratotherium simum"], ["African Grasslands"]],\
        [["Hippopotamus"], ["3,500 kg"], ["Hippopotamus amphibius"], ["African Rivers"]],\
        [["African Elephant"], ["7,500 kg"], ["Loxodonta africana"], ["African Savannas"]]]\
        \
        Question: {topic}, {response}\
        \
        Answer: Let\'s think step by step '
)

hashtag_template = PromptTemplate(
    input_variables=['list'],
    template='''Create popular YouTube/TikTok hashtags from the given inputs. Use abbreviations for countries like USA, UK, and cities like NYC if available. No catchy phrases, keep it simple.
        
        Question: Alaska, Kodiak Bears, Norway, Honey Bears, Greenland, Arctic Bears, Japan, Asiatic Bears, China, Giant Pandas, Sweden, Black Bears, Finland, Finland Bears, Canada, Polar Bears, United States, Grizzly Bears, Russia, Brown Bears
        
        Answer: #Alaska #KodiakBears #Norway #HoneyBears #Greenland #ArcticBears #Japan #AsiaticBears #China #GiantPandas #Sweden #BlackBears #Finland #FinlandBears #Canada #PolarBears #USA #GrizzlyBears #Russia #BrownBears
        
        Question: {list}
        
        Answer: Let's think step by step '''
)


video_template_comparison = PromptTemplate(
    input_variables=['country1', 'country2'],
    template='''
        Compare the two given countries in a variety of aspects, including geography, population, history, culture, economy, politics,
        tourism, education, healthcare, and infrastructure. Each category should include a brief comparison point for each country.
        Your response should be a valid JSON 3D array format with each category represented similarly. The format should be as follows:
        [["Category"], ["Country1 Point"], ["Country2 Point"], ["Winner"], ["Google Image Search Query for Country1"], ["Google Image Search Query for Country2"]].
        The "Country1 Point" and "Country2 Point" should be concise, each no more than three words, explaining the main point of comparison for that category.
        The "Winner" should be the country that outperforms the other in that specific category. The "Google Image Search Query" for each country should be a
        suitable search term for images related to the country and the topic, avoiding numbers unless it is a year, and should also be no more than three words.
        Ensure the response is in the correct order with each category appropriately compared.
        
        Question: Turkey, Greece
        
        Answer: [[["Geography"], ["Mountainous Terrain"], ["Archipelago"], ["Greece"], ["Turkey Geography"], ["Greece Geography"]],
        [["Population"], ["Diverse Ethnicities"], ["Homogeneous"], ["Turkey"], ["Turkey Population"], ["Greece Population"]],
        [["History"], ["Ottoman Empire"], ["Classical Greece"], ["Greece"], ["Turkey History"], ["Greece History"]],
        [["Culture"], ["Turkish Cuisine"], ["Greek Cuisine"], ["Draw"], ["Turkish Cuisine"], ["Greek Cuisine"]],
        [["Economy"], ["Manufacturing Economy"], ["Tourism Economy"], ["Turkey"], ["Turkey Economy"], ["Greece Economy"]],
        [["Politics"], ["Presidential System"], ["Parliamentary Republic"], ["Draw"], ["Turkey Politics"], ["Greece Politics"]],
        [["Tourism"], ["Historical Sites"], ["Island Beaches"], ["Greece"], ["Turkey Tourism"], ["Greece Tourism"]],
        [["Education"], ["Public Education"], ["Compulsory Education"], ["Draw"], ["Turkey Education"], ["Greece Education"]],
        [["Healthcare"], ["Universal Healthcare"], ["National Healthcare"], ["Turkey"], ["Turkey Healthcare"], ["Greece Healthcare"]],
        [["Infrastructure"], ["Modern Infrastructure"], ["Ancient Infrastructure"], ["Turkey"], ["Turkey Infrastructure"], ["Greece Infrastructure"]]]
        
        Question: {country1}, {country2}
        
        Answer: Let's think step by step'''
)
