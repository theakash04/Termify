import os
import sys
import numpy as np
from tqdm import tqdm

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from snowflake.core._root import Root
from snowflake.main import RAG
from snowflake.cortex import Complete, CompleteOptions
from utils.secret_loader import get_secret
from trulens.providers.cortex import Cortex
from utils.sessions import SnowflakeConnector
from trulens.core import TruSession, Feedback, Select
from trulens.apps.custom import instrument, TruCustomApp
from trulens.dashboard import run_dashboard


class RAG(RAG):
    def __init__(self, root, session, limit_to_retirve=5):
        self.root = root
        self.session = session
        self._limit_to_retirve = limit_to_retirve

    @instrument
    def retrieve_context(self, query: str) -> dict:
        if not self.root or not self.session:
            return {
                "input": query,
                "response": "Something unexpected happened. Contact customer support.",
            }

        # Accessing the Snowflake Cortex search service
        my_service = (
            self.root.databases[get_secret("SNOWFLAKE_DATABASE")]
            .schemas[get_secret("SNOWFLAKE_SCHEMA")]
            .cortex_search_services[get_secret("SNOWFLAKE_CORTEX_SEARCH_SERVICE")]
        )

        # Searching and building context
        resp = my_service.search(query=query, columns=["DATA"], limit=self._limit_to_retirve)

        if resp.results:
            return [curr["DATA"] for curr in resp.results]
        else:
            return ["No relevent Information found"]
    
    @instrument
    def create_prompt(self, query:str, context_str: list)-> str:
        prompt = f"""
        You are an expert assistant for interpreting privacy policies and terms and conditions.Your name is Termify Provide clear, factual, and detailed answers based only on the following inputs:
        - **Context:** Relevant information for the current conversation.
        If the answer is not in the context, say you don’t have the information. Do not reference or explain the context. Respond courteously to casual greetings.
        Context: {context_str}
        Question: {query}
        Answer:
        """
        return prompt

    @instrument
    def generate_completion(self, query: str, context_str: str) -> str:
        prompt = self.create_prompt(query, context_str)
        options = CompleteOptions(
            temperature=0.2,       # Add some randomness for creativity
            top_p=0.3             # Limit the token set to the top 90% cumulative probability
        )
        return Complete("mistral-large2", prompt, options=options)

    @instrument
    def ask_query(self, query: str) -> str:
        context_str = self.retrieve_context(query)
        return self.generate_completion(query, context_str)


Ask = input("should I start evaluating with the given sets of question? ('y' or 'n'): ")


if Ask not in ['Y', 'y', 'yes', 'Yes', 'YES']:
    print("No query provided. Exiting...")
    sys.exit(0)
else:
    sfConnect = SnowflakeConnector()
    session = sfConnect.get_session()
    root = Root(session)
    rag = RAG(root, session)
    sess_Tru = TruSession()

    provider = Cortex(
        session,
        model_engine="mistral-large2",
    )

    queries = [
        "How does Facebook use my data when I log in with my account?",
        "What happens to my data when I delete my Instagram profile?",
        "Does Amazon track what I browse even if I don't make a purchase?",
        "How does Google use my location data when I use Google Maps?",
        "Can I stop Netflix from recommending shows based on my watch history?",
        "Why does Twitter ask for my phone number and what do they do with it?",
        "Does Apple sell my data to other companies or use it for advertising?",
        "How can I opt out of personalized ads on YouTube?",
        "Does Microsoft store my voice recordings from Cortana, and for how long?",
        "Why does Uber require my GPS location even when I am not in a ride?",
        "What is TikTok doing with the data it collects from my device?",
        "Does Spotify listen to what I say outside of the app for improving recommendations?",
        "Can Snapchat access my photos without me sending them to someone?",
        "What are my rights to request a copy of my data from Google?",
        "How does Amazon Alexa know what I’m saying even when I haven’t activated it?",
        "Does Facebook share my posts with advertisers even if I don't allow targeted ads?",
        "What does Instagram do with my phone number after I enter it to verify my account?",
        "Why does Amazon ask for my address when I only want to browse items?",
        "If I use Google search, does it track what I search for even if I don't have a Google account?",
        "Can Netflix see what shows I watch and use that to recommend others, even if I don't share my viewing history?",
        "Why does Twitter keep sending me notifications about people I don’t follow?",
        "Does Apple track my location even when I'm not using any apps?",
        "If I don’t want personalized ads, how can I stop YouTube from showing them?",
        "Does Microsoft collect my voice data when I use Windows, even when I don’t ask Cortana anything?",
        "Why does Uber need my location when I’m not actively using the app?",
        "Why does TikTok ask for access to my contacts and photos? What do they do with them?",
        "Is Spotify listening to my voice or tracking what I say outside the app to make recommendations?",
        "Can Snapchat see my location and pictures even if I haven’t shared anything with anyone?",
        "How do I know what personal data Google is storing about me, and how can I delete it?",
        "Why does Amazon Alexa sometimes record my conversations, even when I haven’t activated it?",
        "Do my browsing habits on Chrome get shared with Google for targeted ads?",
        "Can Facebook access my private messages and photos even if they’re not shared publicly?",
        "What happens to my data when I unsubscribe from email newsletters from a company?",
        "If I delete my account on Twitter, how long do they keep my data?",
        "Does my activity on apps like Instagram and Facebook get sold to other companies?",
    ]

    # Feedback: Context Relevance
    f_context_relevance = (
        Feedback(provider.context_relevance, name="Context Relevance")
        .on_input()
        .on(Select.RecordCalls.retrieve_context.rets[:])
        .aggregate(np.mean)
    )

    # Feedback: Answer Relevance
    f_answer_relevance = (
        Feedback(provider.relevance, name="Answer Relevance")
        .on_input()
        .on_output()
        .aggregate(np.mean)
    )

    # Feedback: Coherence
    f_coherence = Feedback(
        provider.coherence_with_cot_reasons, name="Coherence"
    ).on_output()

    # Initializing the TruCustomApp
    tru_rag = TruCustomApp(
        rag,
        app_name="Termify",
        app_version="v1.2.1",
        feedbacks=[f_answer_relevance, f_context_relevance, f_coherence],
    )

    with tru_rag as recording:
        for query in tqdm(queries, desc="Questions", ascii=True):
            response = rag.ask_query(query)

    run_dashboard(session=sess_Tru, port=8080, _watch_changes=True)
