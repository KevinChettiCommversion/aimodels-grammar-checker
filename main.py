from happytransformer import HappyTextToText, TTSettings
import config
import mysql.connector
import pandas as pd
import spacy

try:
    def getDataFromSQL():

        mydb = mysql.connector.connect(
                    host=config.host,
                    port=config.port,
                    user=config.username,
                    password=config.password,
                    database=config.database
                )
        selectQuery = "select * from chat_transcript_ai limit 100;"
        data = pd.read_sql(selectQuery,mydb)
        print(data["user_type"].value_counts())
        data = data[data["user_type"]=="agent"]
        data = data[["chat_id","text"]]
        data["text"] = data["text"].str.strip()

        print(data.head())
        return data


except Exception as e:
    print(e)

nlp = spacy.load("en_core_web_md")
# text = "Hi.My name is Timmy.   What is yours? Its nice to see you !Hoping to see you soon, ok"

#
data = getDataFromSQL()
data["Grammar"] = ""
AIGeneratedResponse_list = []
happy_tt = HappyTextToText("T5", "vennify/t5-base-grammar-correction")
args = TTSettings(num_beams=5, min_length=1)

for index, row in data.iterrows():
    Agent_response = str(row["text"])
    doc = nlp(Agent_response)

    for Agent_response_single_message in doc.sents:
        Agent_response_single_message = Agent_response_single_message.text
        appendedResponseFromAgent = """grammar: """ + Agent_response_single_message
        print(Agent_response_single_message)


        result = happy_tt.generate_text(appendedResponseFromAgent, args=args)
        AIGeneratedResponse = result.text
        AIGeneratedResponse = AIGeneratedResponse.strip()

        if Agent_response_single_message != AIGeneratedResponse:
            print("Missmatch")

            print(result.text)
            print("Length of Agent response : ",len(str(Agent_response_single_message)))
            print("Length of Agent response : ", len(str(AIGeneratedResponse)))
            data.at[index, 'grammar'] = "Error"
            data.at[index, 'AI_Response'] = AIGeneratedResponse

        else:
            print("Match")
            data.at[index, 'grammar'] = ""
            data.at[index, 'AI_Response'] = ""



        print("-------------------------------")
        #print(result) # This sentence has bad grammar.
data.to_excel("Data.xlsx")