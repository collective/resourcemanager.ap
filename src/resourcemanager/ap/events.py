import logging
import transaction
from plone import api

from resourcemanager.ap.search import APSearch

logger = logging.getLogger("AssociatedPress")


def store_image_metadata(obj, event):
    resource_id = obj.external_img_id
    if 'ap-' not in resource_id:
        return
    apsearch = APSearch(obj, obj.REQUEST)
    response = apsearch.query_ap(resource_id.replace('ap-', ''))
    item = response['data']['item']
    if not obj.title:
        obj.title = item.get('title', '')
    if not obj.description:
        obj.description = item.get('description_caption', '')
    # rs_data = img_data['resource_metadata']
    obj.resource_metadata = item
    obj.rights = item.get('copyrightnotice', '')
    obj.reindexObject()

