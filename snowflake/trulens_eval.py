import os
import sys
import numpy as np
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import RAG
from functools import partial
from snowflake.core._root import Root
from snowflake.cortex import Complete
from utils.secret_loader import get_secret
from trulens.providers.cortex import Cortex
from utils.sessions import SnowflakeConnector
from trulens.feedback import GroundTruthAgreement
from trulens.core import TruSession, Feedback, Select
from trulens.apps.custom import instrument, TruCustomApp


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
        resp = my_service.search(query=query, columns=["CHUNKS"], limit=self._limit_to_retirve)

        if resp.results:
            return [curr["CHUNKS"] for curr in resp.results]
        else:
            return []

    @instrument
    def generate_completion(self, query: str, context_str: str) -> str:
        prompt = self.create_prompt(query, context_str)
        return Complete("mistral-large2", prompt)

    @instrument
    def query(self, query: str) -> str:
        context_str = self.retrieve_context(query)
        return self.generate_completion(query, context_str)


query = input("Ask a question: ")

if not query:
    print("No query provided. Exiting...")
    sys.exit(0)
else:
    sfConnect = SnowflakeConnector()
    session = sfConnect.get_session()
    root = Root(session)
    rag = RAG(root, session)
    sess_Tru = TruSession()
    

    data = {
        "query": [
            "What is law?",
            "What is Section 302 in IPC?",
            "Tell me about Section 376 in IPC?",
        ],
        "query_id": ["1", "2", "3"],
        "expected_response": [
            "What is Law?",
            "Section 302 - Murder",
            "Section 376 - Rape",
        ],
        "expected_chunks": [
            [
                {
                    "text": "Law refers to the system of rules that a country or community recognizes as regulating the actions of its members and which it may enforce by the imposition of penalties.",
                    "title": "What is Law?",
                    "expected_score": 0.9,
                }
            ],
            [
                {
                    "text": "Section 302 of the Indian Penal Code (IPC) defines the punishment for murder, which is a capital punishment or life imprisonment.",
                    "title": "Section 302 - Murder",
                    "expected_score": 0.8,
                }
            ],
            [
                {
                    "text": "Section 376 of the Indian Penal Code deals with the punishment for the crime of rape, prescribing rigorous imprisonment and a fine.",
                    "title": "Section 376 - Rape",
                    "expected_score": 0.8,
                }
            ],
        ],
    }

    df = pd.DataFrame(data)

    sess_Tru.add_ground_truth_to_dataset(
        dataset_name="test_dataset_ir",
        ground_truth_df=df,
        dataset_metadata={"domain": "Random IR dataset"},
    )

    ground_truth_df = sess_Tru.get_ground_truth("test_dataset_ir")

    provider = Cortex(
        session,
        model_engine="mistral-large2",
    )

    retrieved_chunks = [rag.retrieve_context(query)]

    GroundTruthAgreement(ground_truth_df, provider=provider).precision_at_k(
        query, retrieved_chunks
    )

    GroundTruthAgreement(ground_truth_df, provider=provider).recall_at_k(
        query, retrieved_chunks
    )

    f_groundedness = (
        Feedback(
            partial(
                provider.groundedness_measure_with_cot_reasons, use_sent_tokenize=False
            ),
            name="Groundedness",
        )
        .on(Select.RecordCalls.retrieve_context.rets[:].collect())
        .on_output()
    )

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
        app_name="snowflake LawAdvicer",
        app_version="v1.1",
        feedbacks=[f_answer_relevance, f_context_relevance, f_coherence],
    )

    with tru_rag as recording:
        response = rag.query(query)

    sess_Tru.run_dashboard()
