import networkx as nx
import cPickle as pickle
import csv
import os
# import pymongo
# from pymongo import MongoClient
import csv,codecs, cStringIO
import itertools as it

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """
    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

def save_object(obj, filename):
    with open(filename, 'wb') as output:
        pickle.dump(obj, output, -1)

def tsvToGraph():
    graph = nx.Graph()
    # tsv to edges - with creation of new node objects
    for file in os.listdir('seealsotsv/'):
        with open('seealsotsv/'+file, 'rb') as f:
            print(file)
            reader = UnicodeReader(f, delimiter='\t')
            i = 1
            for row in reader:
                if row[0] == 'source':
                    continue

                graph.add_edge(row[0],row[1])
                print i
                i += 1

    save_object(graph, 'graph.p')


def loadGraph(filename):
    with open(filename, 'rb') as input:
        graph = pickle.load(input)

    return graph


# def mongo_to_graph(g):
#     i = 1
#     client = MongoClient()
#     db = client.sentences
#     collection = db.tb
#     cur = collection.find({"$where": "this.keywords.length > 1"})
#
#     for doc in cur:
#         sentence = doc['string']
#         combs = it.combinations(doc['keywords'], 2)
#
#         for comb in combs:
#             r = (comb[0]['strength'] + comb[1]['strength'] + 0.15) * 2
#
#             if not (comb[0]['word'] in g and comb[1]['word'] in g[comb[0]['word']]) \
#                     or g[comb[0]['word']][comb[1]['word']]['weight'] > r:
#                 g.add_edge(comb[0]['word'], comb[1]['word'], weight=r, text=sentence)
#
#         if i % 10000 == 0:
#             print i
#         i += 1
#
# def rep_mongo_to_graph(g):
#     i = 1
#     client = MongoClient()
#     db = client.sentences
#     collection = db.bad
#     cur = collection.find({})
#     FINAL= "FINAL_EVIL"
#
#     for doc in cur:
#         sentence = doc['string']
#         g.add_edge(sentence,FINAL,weight=doc["sent"])
#
#         keys = doc['keywords']
#         for key in keys:
#             g.add_edge(key["word"],sentence, weight=key["strength"])
#
#         taxs = doc["taxonomy"]
#         for tax in taxs:
#             t = tax["label"].split('/')[-1]
#             g.add_edge(t,sentence,weight=tax["strength"])
#
#         print i
#         i += 1


def make_tax_graph(g):
    i = 1
    with open('taxonomy.csv', 'rb') as f:
        reader = UnicodeReader(f)
        for row in reader:
            print i

            if row[1] != '':
                g.add_edge(row[0],row[1],weight=0.8)
                if row[2] != '':
                    g.add_edge(row[1],row[2],weight=0.7)
                    if row[3] != '':
                        g.add_edge(row[2],row[3],weight=0.6)
                        if row[4] != '':
                            g.add_edge(row[3],row[4],weight=0.5)

            i += 1

if __name__ == "__main__":
    g = nx.Graph()
    # g = loadGraph('taxonomy.p')
    # rep_mongo_to_graph(g)
    g.add_edge("a231","bbbb")
    g.add_edge("a231","cccc")
    print g.neighbors("a231")
    # save_object(g,'replies.p')
