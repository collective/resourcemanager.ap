import json
import math
import requests
from requests import exceptions as exc
import urllib.parse
from PIL import Image
from plone import api
from plone.namedfile.file import NamedBlobImage
from Products.Five.browser import BrowserView
from zope.interface import implementer

from collective.resourcemanager.browser import search
from collective.resourcemanager.interfaces import ICollectiveResourcemanagerLayer


@implementer(ICollectiveResourcemanagerLayer)
class APSearch(BrowserView):
    """Search Associated Press
    """

    search_id = 'ap-search'

    def __init__(self, context, request):
        self.context = context
        self.request = request
        reg_prefix = 'resourcemanager.ap.settings.IAPKeys'
        self.rs_api_key = context.portal_registry['{0}.api_key'.format(reg_prefix)]
        self.image_metadata = []
        self.messages = []
        self.search_context = 'ap-search'

    def query_ap(self, query, search_token='', batch_size=20, batch=1):
        query_url = 'https://api.ap.org/media/v1.1/content/'
        key_param = 'apikey=' + self.rs_api_key
        if search_token and batch > 1:
            query_url += 'search?qt={0}&page={1}'.format(search_token, batch)
            request_url = query_url + '&' + key_param
        elif 'q=' in query:
            query_url += 'search?'
            options = '&page_size={}'.format(batch_size)
            request_url = query_url + query + options + '&' + key_param
        else:
            request_url = query_url + query + '?' + key_param
        try:
            response = requests.get(request_url, timeout=5)
        except (exc.ConnectTimeout, exc.ConnectionError, exc.ReadTimeout) as e:
            self.messages.append(str(e))
            return []
        if response.status_code != 200:
            self.messages.append(response.reason)
            return []
        try:
            return response.json()
        except ValueError:
            self.messages.append('The json returned from {0} is not valid'.format(
                query
            ))
            return []

    def parse_metadata(self, response):
        """Prep metadata dictionary for search results view
        """
        images = {}
        for item in response['data']['items']:
            if item['item']['type'] != 'picture':
                continue
            item_id = item['item']['altids']['itemid']
            main_size = item['item']['renditions']['main']
            images[item_id] = {
                'title': item['item']['headline'],
                'id': item_id,
                'creation_date': item['item']['firstcreated'],
                'file_extension': main_size['fileextension'],
                'image_size': '{0}x{1}'.format(
                    main_size['width'], main_size['height']),
                'url': item['item']['renditions']['preview']['href'] + '&apikey=' + self.rs_api_key,
                'metadata': item['item'],
                'additional_details': '$: ' + main_size.get('pricetag'),
            }
        return images

    def __call__(self):
        form = self.request.form
        search_term = form.get('rs_search')
        batch = int(form.get('batch'))
        extras = json.loads(form.get('extras', {}))
        search_token = extras.get('search_token', '')
        b_size = 20
        b_start = (batch - 1) * b_size + 1
        b_end = b_start + b_size
        self.search_context = self.request._steps[-1]
        if not form or not search_term:
            if form.get('type', '') == 'json':
                self.messages.append('There has been an error in the form')
                return json.dumps({
                    'search_context': self.search_context,
                    'errors': self.messages,
                    'metadata': self.image_metadata,
                    })
            return self.template()
        # do the search based on term or collection name
        if not search_term:
            self.messages.append('Missing search term')
        search_term = urllib.parse.quote_plus(form['rs_search'])
        query = 'q=type:picture+AND+{}'.format(search_term)
        response = self.query_ap(query, search_token, b_size, batch)
        if not response:
            if form.get('type', '') == 'json':
                return json.dumps({
                    'search_context': self.search_context,
                    'errors': self.messages,
                    'metadata': self.image_metadata,
                    })
            return self.template()
        search_token = response['id']
        num_results = response['data']['total_items']
        self.image_metadata = self.parse_metadata(response)
        if not self.image_metadata and not self.messages:
            self.messages.append("No images found")
        existing = search.existing_copies(self.context)
        for item in self.image_metadata:
            id = 'ap-{}'.format(self.image_metadata[item]['id'])
            self.image_metadata[item]['exists'] = id in existing
        if form.get('type', '') == 'json':
            return json.dumps({
                'search_context': self.search_context,
                'errors': self.messages,
                'metadata': self.image_metadata,
                'num_results': num_results,
                'b_start': b_start,
                'b_end': num_results > b_end and b_end or num_results,
                'num_batches': math.ceil(num_results / b_size),
                'curr_batch': batch,
                'copy_url': 'copy-img-from-ap',
                'extras': {'search_token': search_token},
                })
        return self.template()

    def collections(self):
        return []


class APCopy(BrowserView):
    """Copy selected media to the current folder
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        reg_prefix = 'resourcemanager.ap.settings.IAPKeys'
        self.rs_api_key = context.portal_registry['{0}.api_key'.format(reg_prefix)]
        self.rssearch = APSearch(context, request)

    def valid_image(self, img_url):
        # test if image url is valid
        try:
            request_url = img_url + '&apikey=' + self.rs_api_key
            img_response = requests.get(request_url)
        except (exc.ConnectTimeout, exc.ConnectionError):
            return None
        if img_response.status_code != 200:
            return None
        try:
            Image.open(requests.get(request_url, stream=True).raw)
        except OSError:
            return None
        return (img_response, request_url)

    def __call__(self):
        """Return original image size
           If function is 'geturl', return the image url
           If function is 'copyimage', copy image into the current folder
        """
        img_function = self.request.form.get('function')
        img_id = self.request.form.get('id')
        img_url = self.request.form.get('image')  # preview size
        if not img_url:
            return "Image ID not found"
        query = img_id
        response = self.rssearch.query_ap(query)
        if not response:
            return "Item not found"
        item = response['data']['item']
        img_metadata = ['{0}: {1}'.format(x, item[x]) for x in item]
        original_size_url = self.valid_image(item['renditions']['main']['href'])
        if not original_size_url:
            return "Item not found"
        if img_function == 'geturl':
            return json.dumps({
                'img_url': original_size_url[1],
                'img_id': 'ap-{}'.format(img_id),
                'description': item.get('description_caption',''),
                })
        if img_function == 'copyimage':
            blob = NamedBlobImage(
                data=original_size_url[0].content)
            new_image = api.content.create(
                type='Image',
                image=blob,
                container=search.get_container(self.context),
                title=self.request.form.get('title'),
                description=item['description_caption'],
                external_img_id='ap-{}'.format(img_id),
                resource_metadata='\n'.join(img_metadata),
            )
            return "Image copied to <a href='{0}/view'>{0}</a>".format(
                new_image.absolute_url())
        return "No action taken, did you pass in a function?"
