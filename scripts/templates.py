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
    template='''
    For a given input, determine the top 10 countries specifically related to given topic, starting from the best to the 10th.
    Your response should be in valid JSON format, a 3D array, with each element representing a country in descending order of relevance to the input.
    Each element of the array should have the following format: [["Country"], ["Fact"], ["Google Image Search Query"]],
    where "Country" is the name of the country, "Fact" represents a brief fact or name related to the country and the given input (limited to three words),
    and "Google Image Search Query" is a suitable search term for images related to the country and the topic (also no more than three words).
    Avoid numbers in the "Google Image Search Query" unless it is a year.
    Remember to always include a country in your response even if it's not mentioned in the question.

    Question: Castles

    Answer:[[["Sweden"], ["Visby Medieval Walls"], ["Sweden Castles"]], [["Scotland"], ["Edinburgh Castle"], ["Scotland Castles"]], [["Germany"], ["Neuschwanstein Castle"], ["Germany Castles"]], [["Wales"], ["Conwy Castle"], ["Wales Castles"]], [["France"], ["Château de Chambord"], ["France Castles"]], [["Spain"], ["Alhambra Palace"], ["Spain Castles"]], [["England"], ["Tower of London"], ["England Castles"]], [["Ireland"], ["Blarney Castle"], ["Ireland Castles"]], [["Czech Republic"], ["Prague Castle"], ["Czech Republic Castles"]], [["Japan"], ["Himeji Castle"], ["Japan Castles"]]]

    Question: Deadliest Insects

    Answer:[[['Colombia'], ['Kissing Bug'], ['Colombia Insects']], [['Mexico'], ['Kissing Bug'], ['Mexico Insects']], [['Indonesia'], ['Giant Centipede'], ['Indonesia Insects']], [['United States'], ['Kissing Bug'], ['US Insects']], [['China'], ['Asian Giant Hornet'], ['China Insects']], [['South Africa'], ['Tsetse Fly'], ['South Africa Insects']], [['Vietnam'], ['Giant Water Bug'], ['Vietnam Insects']], [['India'], ['Malaria Mosquito'], ['India Insects']], [['Australia'], ['Funnel-Web Spider'], ['Australia Insects']], [['Brazil'], ['Kissing Bug'], ['Brazil Insects']]]

    Question: {topic}

    Answer: Let's think step by step...
    '''
)
video_template20 = PromptTemplate(
    input_variables=['topic', 'list'],
    template='''
    For a given topic and an initial list of top 10 countries, determine the subsequent 10 countries (ranked 11-20) specifically related to the given topic, starting from the 11th to the 20th.
    Your response should be in valid JSON format, a 3D array, with each element representing a country in descending order of relevance to the input.
    Each element of the array should have the following format: [["Country"], ["Fact"], ["Google Image Search Query"]],
    where "Country" is the name of the country, "Fact" represents a brief fact or name related to the country and the given input (limited to three words),
    and "Google Image Search Query" is a suitable search term for images related to the country and the topic (also no more than three words).
    Avoid numbers in the "Google Image Search Query" unless it is a year.
    Remember to always include a country in your response even if it's not mentioned in the question or in the initial list.

    Question: Deadliest Insects, [['Colombia'], ['Kissing Bug'], ['Colombia Insects']], [['Mexico'], ['Kissing Bug'], ['Mexico Insects']], [['Indonesia'], ['Giant Centipede'], ['Indonesia Insects']], [['United States'], ['Kissing Bug'], ['US Insects']], [['China'], ['Asian Giant Hornet'], ['China Insects']], [['South Africa'], ['Tsetse Fly'], ['South Africa Insects']], [['Vietnam'], ['Giant Water Bug'], ['Vietnam Insects']], [['India'], ['Malaria Mosquito'], ['India Insects']], [['Australia'], ['Funnel-Web Spider'], ['Australia Insects']], [['Brazil'], ['Kissing Bug'], ['Brazil Insects']]
    Answer: [[['Peru'], ['Kissing Bug'], ['Peru Insects']], [['Kenya'], ['Malaria Mosquito'], ['Kenya Insects']], [['Thailand'], ['Asian Giant Hornet'], ['Thailand Insects']], [['Japan'], ['Asian Giant Hornet'], ['Japan Insects']], [['Cameroon'], ['Tsetse Fly'], ['Cameroon Insects']], [['Nigeria'], ['Tsetse Fly'], ['Nigeria Insects']], [['Ethiopia'], ['Malaria Mosquito'], ['Ethiopia Insects']], [['Malaysia'], ['Giant Centipede'], ['Malaysia Insects']], [['Congo'], ['Tsetse Fly'], ['Congo Insects']], [['Colombia'], ['bullet ant'], ['Colombia Insects']]]

    Question: {topic}, {list}
    Answer:
    ''')

statistic_template20 = PromptTemplate(
    input_variables=['topic', 'list'],
    template='''
    Given a ranked list of topics from 20th place to 1st place, I need you to generate plausible statistics related to each topic. The list of topics is as follows:

    Generate statistics in a way that it makes sense within the given ranking, even if they are approximations. The information should be represented in the following format: ['Statistics for Rank 20', 'Statistics for Rank 19', ... 'Statistics for Rank 2', 'Statistics for Rank 1'] Remember to include only the statistic in your response, country names are irrelevant. Make your answer short and concise. Do not include Country names in your response!
    Question:
    Countries with Fastest Birds
    [[['Bangladesh'], ['Pied Kingfisher'], ['Bangladesh Pied Kingfisher']], [['Colombia'], ['Andean Condor'], ['Colombia Andean Condor']], [['Egypt'], ['Egyptian Vulture'], ['Egypt Egyptian Vulture']], [['France'], ['Eurasian Hobby'], ['France Eurasian Hobby']], [['Japan'], ['Japanese Bush Warbler'], ['Japan Japanese Bush Warbler']], [['Russia'], ['Saker Falcon'], ['Russia Saker Falcon']], [['Saudi Arabia'], ['Sooty Falcon'], ['Saudi Arabia Sooty Falcon']], [['Spain'], ['Eurasian Hobby'], ['Spain Eurasian Hobby']], [['Uganda'], ['Grey-Crowned Crane'], ['Uganda Grey-Crowned Crane']], [['Zimbabwe'], ['Kori Bustard'], ['Zimbabwe Kori Bustard']], [['Brazil'], ['Hyacinth Macaw'], ['Brazil Hyacinth Macaw']], [['Canada'], ['Peregrine Falcon'], ['Canada Peregrine Falcon']], [['China'], ['White-Eared Pheasant'], ['China White-Eared Pheasant']], [['India'], ['Indian Peafowl'], ['India Indian Peafowl']], [['Mexico'], ['Roadrunner'], ['Mexico Roadrunner']], [['Australia'], ['Emu'], ['Australia Emu']], [['United States'], ['Peregrine Falcon'], ['United States Peregrine Falcon']], [['Namibia'], ['Kori Bustard'], ['Namibia Kori Bustard']], [['South Africa'], ['Secretary Bird'], ['South Africa Secretary Bird']], [['Kenya'], ['Somali Ostrich'], ['Kenya Somali Ostrich']]]
    Answer: ['Top speed of 40 mph', 'Top speed of 45 mph', 'Top speed of 50 mph', 'Top speed of 55 mph', 'Top speed of 60 mph', 'Top speed of 65 mph', 'Top speed of 70 mph', 'Top speed of 65 mph', 'Top speed of 70 mph', 'Top speed of 75 mph', 'Top speed of 80 mph', 'Top speed of 85 mph', 'Top speed of 90 mph', 'Top speed of 95 mph', 'Top speed of 100 mph', 'Top speed of 95 mph', 'Top speed of 100 mph', 'Top speed of 105 mph', 'Top speed of 110 mph', 'Top speed of 115 mph', 'Top speed of 120 mph']
    Question:
    {topic}
    {list}
    Answer: Let's think step by step.
    '''
)

statistic_template10 = PromptTemplate(
    input_variables=['topic', 'list'],
    template='''
    Given a ranked list of topics from 10th place to 1st place, I need you to generate plausible statistics related to each topic. The list of topics is as follows:

    Generate statistics in a way that it makes sense within the given ranking, even if they are approximations. The information should be represented in the following format: ['Statistics for Rank 10', 'Statistics for Rank 9', ... 'Statistics for Rank 2', 'Statistics for Rank 1'] Remember to include only the statistic in your response, country names are irrelevant. Make your answer short and concise. Do not include Country names in your response! Do not make user more than 3 words!
    Question:
    Countries with Fastest Birds
    [[['Brazil'], ['Hyacinth Macaw'], ['Brazil Hyacinth Macaw']], [['Canada'], ['Peregrine Falcon'], ['Canada Peregrine Falcon']], [['China'], ['White-Eared Pheasant'], ['China White-Eared Pheasant']], [['India'], ['Indian Peafowl'], ['India Indian Peafowl']], [['Mexico'], ['Roadrunner'], ['Mexico Roadrunner']], [['Australia'], ['Emu'], ['Australia Emu']], [['United States'], ['Peregrine Falcon'], ['United States Peregrine Falcon']], [['Namibia'], ['Kori Bustard'], ['Namibia Kori Bustard']], [['South Africa'], ['Secretary Bird'], ['South Africa Secretary Bird']], [['Kenya'], ['Somali Ostrich'], ['Kenya Somali Ostrich']]]
    Answer: ['Top speed of 85 mph', 'Top speed of 90 mph', 'Top speed of 95 mph', 'Top speed of 100 mph', 'Top speed of 95 mph', 'Top speed of 100 mph', 'Top speed of 105 mph', 'Top speed of 110 mph', 'Top speed of 115 mph', 'Top speed of 120 mph']
    Question:
    {topic}
    {list}
    Answer: Let's think step by step.
    '''
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

idea_template = PromptTemplate(
    input_variables=['list'],
    template='''Given the youtube short title below:
                {list} make 15 new suggestions that are about countries and with viral potential. Topics like military, history, culture. Stuff nationalist people would like to see.
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
