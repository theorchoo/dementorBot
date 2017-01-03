import json
from watson_developer_cloud import AlchemyLanguageV1
from find import Finder


alchemy_language = AlchemyLanguageV1(api_key='9fe385d70a29406a5630bc82a834ec723d986091')
finder = Finder('sentences_and_words6.p','replies.p')

msg = ''

while (True):
    if msg == '':
        msg = "hi, tell me something..."

    input = raw_input(msg)

    print "parsing..."
    res = alchemy_language.combined(
                text=input,
                extract='entities,keywords,taxonomy,doc-sentiment',
                sentiment=1,
                max_items=4)

    print "finding evil reply..."
    evil_list, keywords, s = finder.find_answer(res)
    print "***" + evil_list.__str__() + "***" + str(s)

    if len(evil_list) < 6:
        msg = evil_list[-2]
    else:
        print "finding sentence..."
        print keywords
        path = finder.find_api(keywords)
        print path
        msg = finder.get(path[1],path[2])



# print res
# print res["docSentiment"]["score"]
# print res["taxonomy"][0]["label"]
# print res["entities"][0]["text"]
# print res["entities"][0]["relevance"]
# print res["keywords"][0]["text"]
# print res["keywords"][0]["relevance"]