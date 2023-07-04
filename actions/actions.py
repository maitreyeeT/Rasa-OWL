from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from owl_query_manager import *
from embeddings import GloveEmbedding
import numpy as np
from scipy.spatial.distance import cosine
#
#
class painScale(Action):
#
     def name(self) -> Text:
         return "action_pain_scale"
#
     def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        pain_category = tracker.get_slot("number")
        if pain_category <= 5:
            dispatcher.utter_message("Pain is low. You can do some stretching or rest a bit.")
        else:
            dispatcher.utter_message("Pain is high. You should see the nurse.")
        return []

class owlReasoner(Action):
    def name(self) -> Text:
        return "action_handleStressNews"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.get_intent_of_latest_message()
        print(intent)
        if intent == "affirm_toTalk":
            onto = OwlQuery("/home/maitreyee/ForNaoExp2.owl")
            query_onto = onto.utterances(onto.search_suggestions(onto.onto.Social_wellbeing))
            dispatcher.utter_message(f'Why don\'t you try to {" or manybe also ".join(query_onto)} to discuss the situation')
            return []

class ManageWellbeing(Action):
    def name(self) -> Text:
        return "action_ManageWellbeing"

    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:
        onto = OwlQuery("/home/maitreyee/ForNaoExp2.owl")
        intent = tracker.get_intent_of_latest_message()
        print(intent)
        if intent == "provideInfo_Notwell":
            user_utterance = {'talk', 'sleep'}
            similarity_fun = lambda onto_bow: len(user_utterance.intersection(onto_bow))
            alternatives = onto.actions_bows(similarity_fun)
            dispatcher.utter_message(f'Would you like to {alternatives[0].utterance[0]}')

        elif intent == "deny_and_breakfast":
            user_utterance = {'eat', 'breakfast'}
            similarity_fun = lambda onto_bow: len(user_utterance.intersection(onto_bow))
            alternatives = onto.actions_bows(similarity_fun)
            dispatcher.utter_message(f'Okay no problem. What would you {alternatives[0].utterance[0]}')
            return []


class ProposeAction(Action):
    def name(self) -> Text:
        return "action_ProposeAction"

    def get_embedding(self, words):
        glove = GloveEmbedding('common_crawl_840')
        embedngs = np.vstack([np.array(glove.emb(word)).reshape(-1) for word in words])
        embedngs = embedngs.sum(axis=0) / len(words)
        return embedngs


    def get_compare_function(self, need):
        def cmp(bow):
            nonlocal need
            score = cosine(self.get_embedding(bow), self.get_embedding(need))
            return -score
        return cmp

    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:
        need_slot = tracker.get_slot('need')
        onto = OwlQuery("/home/maitreyee/ForNaoExp2.owl")

        if need_slot is not None:
            sorted_actions = onto.actions_bows(self.get_compare_function(need_slot.split(' ')))

            proposed = sorted_actions[0]
            dispatcher.utter_message(f'I would suggest to {proposed.utterance[0]}. Do you want me to schedule an activity?')

        else:
            dispatcher.utter_message(f'I didn\'t find any suggestion in my database.')