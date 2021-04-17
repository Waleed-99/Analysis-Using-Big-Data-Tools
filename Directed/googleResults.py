import json

import pandas as pd

import requests

from pandas.io.json._normalize import nested_to_record


from urllib.parse import quote
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class googleResult(object):
   
    GET_METHOD = 'get'
    POST_METHOD = 'post'
    GENERAL_URL = 'https://trends.google.com/trends/api/explore'
    RELATED_QUERIES_URL = 'https://trends.google.com/trends/api/widgetdata/relatedsearches'

    def __init__(self, hl='en-US', tz=360, geo='', timeout=(2, 5), proxies='',
                 retries=0, backoff_factor=0, requests_args=None):
      
        # google rate limit
        self.google_rl = 'You have reached your quota limit'
        self.results = None
        # set user defined options used globally
        self.tz = tz
        self.hl = hl
        self.geo = geo
        self.kw_list = list()
        self.timeout = timeout
        self.proxies = proxies  # add a proxy option
        self.retries = retries
        self.backoff_factor = backoff_factor
        self.proxy_index = 0
        self.requests_args = requests_args or {}
        self.cookies = self.GetGoogleCookie()
        # intialize widget payloads
    
        self.related_queries_widget_list = list()

    def GetGoogleCookie(self):
    
        while True:
            if "proxies" in self.requests_args:
                try:
                    return dict(filter(lambda i: i[0] == 'NID', requests.get(
                        'https://trends.google.com/?geo={geo}'.format(
                            geo=self.hl[-2:]),
                        timeout=self.timeout,
                        **self.requests_args
                    ).cookies.items()))
                except:
                    continue
            else:
                if len(self.proxies) > 0:
                    proxy = {'https': self.proxies[self.proxy_index]}
                else:
                    proxy = ''
                try:
                    return dict(filter(lambda i: i[0] == 'NID', requests.get(
                        'https://trends.google.com/?geo={geo}'.format(
                            geo=self.hl[-2:]),
                        timeout=self.timeout,
                        proxies=proxy,
                        **self.requests_args
                    ).cookies.items()))
                except requests.exceptions.ProxyError:
                    print('Proxy error. Changing IP')
                    if len(self.proxies) > 1:
                        self.proxies.remove(self.proxies[self.proxy_index])
                    else:
                        print('No more proxies available. Bye!')
                        raise
                    continue

    def _get_data(self, url, method=GET_METHOD, trim_chars=0, **kwargs):
        s = requests.session()
        s.headers.update({'accept-language': self.hl})
        if len(self.proxies) > 0:
            self.cookies = self.GetGoogleCookie()
            s.proxies.update({'https': self.proxies[self.proxy_index]})
        if method == googleResult.POST_METHOD:
            response = s.post(url, timeout=self.timeout,
                              cookies=self.cookies, **kwargs,
                              **self.requests_args)  
        else:
            response = s.get(url, timeout=self.timeout, cookies=self.cookies,
                             **kwargs, **self.requests_args) 
        if response.status_code == 200 and 'application/json' in \
                response.headers['Content-Type'] or \
                'application/javascript' in response.headers['Content-Type'] or \
                'text/javascript' in response.headers['Content-Type']:
            content = response.text[trim_chars:]
            self.GetNewProxy()
            return json.loads(content)
        else:
            print("The request failed")

    def build_payload(self, kw_list, cat=0, timeframe='today 5-y', geo='',
                      gprop=''):

        self.kw_list = kw_list
        self.geo = geo or self.geo
        self.token_payload = {
            'hl': self.hl,
            'tz': self.tz,
            'req': {'comparisonItem': [], 'category': cat, 'property': gprop}
        }
        for kw in self.kw_list:
            keyword_payload = {'keyword': kw, 'time': timeframe,
                               'geo': self.geo}
            self.token_payload['req']['comparisonItem'].append(keyword_payload)
        self.token_payload['req'] = json.dumps(self.token_payload['req'])
        self._tokens()
        return

    def _tokens(self):
        widget_dict = self._get_data(
            url=googleResult.GENERAL_URL,
            method=googleResult.GET_METHOD,
            params=self.token_payload,
            trim_chars=4,
        )['widgets']
        first_region_token = True
        self.related_queries_widget_list[:] = []
        for widget in widget_dict:
            if 'RELATED_QUERIES' in widget['id']:
                self.related_queries_widget_list.append(widget)
        return

    def related_queries(self):
        
    
        related_payload = dict()
        result_dict = dict()
        for request_json in self.related_queries_widget_list:
          
            kw = request_json['request']['restriction'][
                'complexKeywordsRestriction']['keyword'][0]['value']
         
            related_payload['req'] = json.dumps(request_json['request'])
            related_payload['token'] = request_json['token']
            related_payload['tz'] = self.tz

           
            req_json = self._get_data(
                url=googleResult.RELATED_QUERIES_URL,
                method=googleResult.GET_METHOD,
                trim_chars=5,
                params=related_payload,
            )     

            try:
                top_df = pd.DataFrame(
                    req_json['default']['rankedList'][0]['rankedKeyword'])
                top_df = top_df[['query', 'value']]
            except KeyError:
                top_df = None

            result_dict[kw] = {'top': top_df}
        return result_dict

    def GetNewProxy(self):
            if self.proxy_index < (len(self.proxies) - 1):
                self.proxy_index += 1
            else:
                self.proxy_index = 0

    


   