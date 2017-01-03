import sys
import math

import os

import dementorBot.settings
import graph
import networkx as nx
from nltk.corpus import wordnet as wn
from datetime import datetime
import RAKE

rake = RAKE.Rake(os.path.join(dementorBot.settings.BASE_DIR, 'chat/finder_p/SmartStoplist.txt'))

class Finder():

    def __init__(self,file,replies):
        print("loading graph...")
        self.g = graph.loadGraph(file)
        self.g.remove_node("tom")
        print("loaded!")

        print("loading replies graph...")
        self.gb = graph.loadGraph(replies)
        print("loaded!")

    def _get_h(self,b):
        try:
            b_syn = wn.synsets(b)[0]
        except:
            def h(a,b):
                return 0.1
            return h

        def h(a,k):
            try:
                a_syn = wn.synsets(a)[0]
                s = (0.8 - a_syn.path_similarity(b_syn))
            except:
                return 0.1

            # print s
            return s

        return h

    def get(self,a,b):
        return self.g[a][b]


    def _find(self,a,b,astar=False,custom=''):
        if a in self.g and b in self.g:
            if astar and custom != '' and custom in self.g:
                return nx.astar_path(self.g,a,b,self._get_h(custom))

            return nx.dijkstra_path(self.g,a,b)
        else:
            return None

    def find_api(self, end_keywords):
        print end_keywords
        print self.g.neighbors("SOURCE_API")

        if "DEST_API" in self.g:
            self.g.remove_node("DEST_API")

        for item in end_keywords:
            self.g.add_edge("DEST_API",item["text"],weight=item["relevance"])

        # return self._find("SOURCE_API","DEST_API",True,end_keywords[0]["text"])
        return self._find("SOURCE_API","DEST_API",False)

    def find_answer(self,obj):
        if "SOURCE_INPUT" in self.gb:
            self.gb.remove_node("SOURCE_INPUT")

        if "SOURCE_API" in self.g:
            self.g.remove_node("SOURCE_API")

        for tax in obj["taxonomy"]:
            if float(tax["score"]) >= 0.08:
                t = tax["label"].split('/')[-1]
                self.gb.add_edge(t,"SOURCE_INPUT",weight=(1.2 - float(tax["score"])) )
                self.g.add_edge(t,"SOURCE_API",weight=(1.2 - float(tax["score"])) )

        for ent in obj["entities"]:
            self.gb.add_edge(ent["text"],"SOURCE_INPUT", weight=(1.2 - float(ent["relevance"])))
            self.g.add_edge(ent["text"],"SOURCE_API", weight=(1.2 - float(ent["relevance"])))

        for key in obj["keywords"]:
            self.gb.add_edge(key["text"],"SOURCE_INPUT", weight=(1.2 - float(key["relevance"])))
            self.g.add_edge(key["text"],"SOURCE_API", weight=(1.2 - float(key["relevance"])))

        if "SOURCE_INPUT" not in self.gb:
            for w, r in rake.run(obj["text"]):
                try:
                    r = 1.0 / r
                except:
                    r = 20000

                self.gb.add_edge(w, "SOURCE_INPUT", weight=r)
                self.g.add_edge(w, "SOURCE_API", weight=r)
                self.gb.add_edge(w, "well.. if thats what helps you sleep at night", weight=1)
                self.gb.add_edge("FINAL_EVIL", "well.. if thats what helps you sleep at night", weight=1)

        path = nx.dijkstra_path(self.gb,"SOURCE_INPUT","FINAL_EVIL")
        strength = 0
        for i in range(len(path)-1):
            strength += self.gb[path[i]][path[i+1]]["weight"]

        e_keywords = []
        for k in self.gb.neighbors(path[-2]):
            if k != "FINAL_EVIL":
                e_keywords.append({"text":k, "relevance":self.gb[path[-2]][k]["weight"]})

        return path,e_keywords,strength


# while (True):
#     input = raw_input("enter 2 words:")
#
#     if input == 'q':
#         sys.exit()
#
#     args = input.split(',')
#
#     print("searching 1... | %s" % str(datetime.now()))
#     list = find(g,args[0],args[1],False)
#     print("searching 2... | %s" % str(datetime.now()))
#     list2 = find(g,args[0],args[1],True)
#     print("finished search.  | %s\n\n" % str(datetime.now()))
#
#     for i in range(len(list)-1):
#         print list[i] + " >> " + list[i+1] + "  |||  " + g[list[i]][list[i+1]]["text"] + str(g[list[i]][list[i+1]]["weight"])
#
#     for i in range(len(list2)-1):
#         print list2[i] + " >> " + list2[i+1] + "  |||  " + g[list2[i]][list2[i+1]]["text"] + str(g[list2[i]][list2[i+1]]["weight"])
#
#     print("\n\n")
