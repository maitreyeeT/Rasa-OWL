from owlready2 import *
import types

class OwlQuery:

    def __init__(self, ontology_path):
        self.onto = get_ontology(ontology_path).load()


    def search_suggestions(self, need):
        """
        Searches actions in the ontology that fulfills a particular need
        :param need: the onto.Need
        :return: a list of onto.Action
        """
        onto = self.onto
        return onto.search(is_a=onto.Act, serves=need)


    def utterances(self, things):
        """
        Get the utterances for the given owl.Thing
        :param things: list of owl.Thing objects
        :return: the utterance property of the given things
        """
        return [t.utterance[0] if hasattr(t, 'utterance') else None for t in things]


    def actions_bows(self, sort_fcn=lambda x: 0):
        """
        Get the bag of words and utterances for all onto.Action in the ontology
        :param sort_fcn: function to score the bag of words
        :return: list of onto.Action ordered by similarity using sort_fcn
        """
        onto = self.onto
        actions = onto.search(type=onto.Act)
        bows = [(t,
                 set(t.bagOfWords[0].split(',')),
                 self.utterances((t,))[0]
                 ) for t in actions
                if hasattr(t, 'bagOfWords') and hasattr(t, 'utterance') and len(t.bagOfWords) > 0]

        bows.sort(key=lambda x: sort_fcn(x[1]), reverse=True)

        utterances = [t[0] for t in bows]

        return utterances




    def add_activity(self,actions):
        onto = self.onto
        with onto:
            Activity = types.new_class("Activity",(owlready2.Thing))
            activity = Activity("Activity_1", namespace=onto, hasAction=actions)




