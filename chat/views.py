import json
import os
from django.shortcuts import render
from django.http import JsonResponse,HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from watson_developer_cloud import AlchemyLanguageV1
import dementorBot.settings
from chat.finder_p.find import Finder

alchemy_language = AlchemyLanguageV1(api_key='9fe385d70a29406a5630bc82a834ec723d986091')
s = os.path.join(dementorBot.settings.BASE_DIR, 'chat/finder_p/sentences_and_words6.p')
r = os.path.join(dementorBot.settings.BASE_DIR, 'chat/finder_p/replies.p')
finder = Finder(s,r)

@csrf_exempt
def find(request):
    if request.method == 'POST':
        if not request.body:
            return HttpResponseBadRequest()

        res = json.loads(request.body)
        evil_list, keywords, s = finder.find_answer(res)
        path = finder.find_api(keywords)
        sentences = []
        for i in range(1,len(path)-2):
            sentences.append(finder.get(path[i],path[i+1]))

        return JsonResponse({'evil_list': evil_list, 'keywords' : keywords, 'score' : s, 'path':path, 'sentences':sentences})

    return HttpResponseBadRequest()


@csrf_exempt
def watson(request):
    if request.method == 'POST':
        if not request.body:
            return HttpResponseBadRequest()

        text = json.loads(request.body)
        res = alchemy_language.combined(
            text=text[0],
            extract='entities,keywords,taxonomy,doc-sentiment',
            show_source_text=True,
            sentiment=1,
            max_items=4)

        return JsonResponse(res)

    return HttpResponseBadRequest()