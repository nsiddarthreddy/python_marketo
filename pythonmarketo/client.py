from pythonmarketo.helper.http_lib import HttpLib
from pythonmarketo.helper.exceptions import MarketoException
import time


class MarketoClient:
    host = None
    client_id = None
    client_secret = None
    token = None
    expires_in = None
    valid_until = None
    token_type = None
    scope = None
    last_request_id = None
    API_CALLS_MADE = 0
    API_LIMIT = None

    def __init__(self, host, client_id, client_secret, api_limit=None):
        assert(host is not None)
        assert(client_id is not None)
        assert(client_secret is not None)
        self.host = host
        self.client_id = client_id
        self.client_secret = client_secret
        self.API_LIMIT = api_limit

    def execute(self, method, *args, **kargs):
        result = None
        if self.API_LIMIT and self.API_CALLS_MADE >= self.API_LIMIT:
            raise Exception({'message': 'API Calls exceded the limit : '
                            + str(self.API_LIMIT), 'code': '416'})

        '''
            max 10 rechecks
        '''
        for i in range(0, 10):
            try:
                method_map = {
                    'get_leads': self.get_leads,
                    'get_leads_by_listId': self.get_leads_by_listId,
                    'get_activity_types': self.get_activity_types,
                    'get_lead_activity': self.get_lead_activity,
                    'get_paging_token': self.get_paging_token,
                    'update_lead': self.update_lead,
                    'bulk_update_lead': self.bulk_update_leads,
                    'create_lead': self.create_lead,
                    'get_lead_activity_page': self.get_lead_activity_page,
                    'get_email_content_by_id': self.get_email_content_by_id,
                    'get_email_template_content_by_id': self.get_email_template_content_by_id,
                    'get_email_templates': self.get_email_templates,
                    'create_custom_activity': self.create_custom_activity,
                    'create_custom_object': self.create_custom_object,
                    'associate_lead': self.associate_lead,
                }

                result = method_map[method](*args, **kargs)
                self.API_CALLS_MADE += 1
            except MarketoException as e:
                '''
                601 -> auth token not valid
                602 -> auth token expired
                '''
                if e.code in ['601', '602']:
                    continue
                else:
                    raise Exception({'message': e.message, 'code': e.code})
            break
        return result

    def authenticate(self):
        if self.valid_until is not None and\
           self.valid_until > time.time():
            return
        args = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        data = HttpLib().get("https://" + self.host
                             + "/identity/oauth/token", args)
        if data is None:
            raise Exception("Empty Response")
        self.token = data['access_token']
        self.token_type = data['token_type']
        self.expires_in = data['expires_in']
        self.valid_until = time.time() + data['expires_in']
        self.scope = data['scope']

    def get_leads(self, filtr, values=[], fields=[]):
        self.authenticate()
        values = values.split() if type(values) is str else values
        args = {
            'access_token': self.token,
            'filterType': str(filtr),
            'filterValues': (',').join(values)
        }
        if len(fields) > 0:
            args['fields'] = ",".join(fields)
        data = HttpLib().get("https://" + self.host
                             + "/rest/v1/leads.json", args)
        if data is None:
            raise Exception("Empty Response")
        self.last_request_id = data['requestId']
        if not data['success']:
            raise MarketoException(data['errors'][0])
        return data['result']

    def get_email_templates(self, offset, maxreturn, status=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token,
            'offset': offset,
            'maxreturn': maxreturn
        }
        if status is not None:
            args['status'] = status
        data = HttpLib().get("https://" + self.host
                             + "/rest/asset/v1/emailTemplates.json", args)
        if data is None:
            raise Exception("Empty Response")
        self.last_request_id = data['requestId']
        if not data['success']:
            raise MarketoException(data['errors'][0])
        return data['result']

    def get_email_content_by_id(self, id):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        data = HttpLib().get("https://" + self.host + "/rest/asset/v1/email/"
                             + str(id) + "/content", args)
        if data is None:
            raise Exception("Empty Response")
        self.last_request_id = data['requestId']
        if not data['success']:
            raise MarketoException(data['errors'][0])
        return data['result']

    def get_email_template_content_by_id(self, id, status=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        if status is not None:
            args['status'] = status
        data = HttpLib().get("https://" + self.host
                             + "/rest/asset/v1/emailTemplate/" + str(id)
                             + "/content", args)

        if data is None:
            raise Exception("Empty Response")
        self.last_request_id = data['requestId']
        if not data['success']:
            raise MarketoException(data['errors'][0])
        return data['result']

    def get_leads_by_listId(self, listId=None, batchSize=None, fields=[]):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        if len(fields) > 0:
            args['fields'] = ",".join(fields)
        if batchSize:
            args['batchSize'] = batchSize
        result_list = []
        while True:
            data = HttpLib().get("https://" + self.host + "/rest/v1/list/"
                                 + str(listId) + "/leads.json", args)
            if data is None:
                raise Exception("Empty Response")
            self.last_request_id = data['requestId']
            if not data['success']:
                raise MarketoException(data['errors'][0])
            result_list.extend(data['result'])
            if len(data['result']) == 0 or 'nextPageToken' not in data:
                break
            args['nextPageToken'] = data['nextPageToken']
        return result_list

    def get_activity_types(self):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        data = HttpLib().get("https://" + self.host
                             + "/rest/v1/activities/types.json", args)
        if data is None:
            raise Exception("Empty Response")
        if not data['success']:
            raise MarketoException(data['errors'][0])
        return data['result']

    def get_lead_activity_page(self, activityTypeIds, nextPageToken, batchSize = None, listId = None):
        self.authenticate()
        activityTypeIds = activityTypeIds.split() if type(activityTypeIds) is str else activityTypeIds
        args = {
            'access_token': self.token,
            'activityTypeIds': ",".join(activityTypeIds),
            'nextPageToken': nextPageToken
        }
        if listId:
            args['listId'] = listId
        if batchSize:
            args['batchSize'] = batchSize
        data = HttpLib().get("https://" + self.host + "/rest/v1/activities.json", args)
        if data is None:
            raise Exception("Empty Response")
        if not data['success']:
            raise MarketoException(data['errors'][0])
        return data

    def get_lead_activity(self, activityTypeIds, sinceDatetime, batchSize = None, listId = None):
        activity_result_list = []
        nextPageToken = self.get_paging_token(sinceDatetime = sinceDatetime)
        moreResult = True
        while moreResult:
            result = self.get_lead_activity_page(activityTypeIds, nextPageToken, batchSize, listId)
            if result is None:
                break
            moreResult = result['moreResult']
            nextPageToken = result['nextPageToken']
            if 'result' in result:
                activity_result_list.extend(result['result'])

        return activity_result_list

    def get_paging_token(self, sinceDatetime):
        self.authenticate()
        args = {
            'access_token': self.token,
            'sinceDatetime': sinceDatetime
        }
        data = HttpLib().get("https://" + self.host + "/rest/v1/activities/pagingtoken.json", args)
        if data is None: raise Exception("Empty Response")
        if not data['success'] : raise MarketoException(data['errors'][0])
        return data['nextPageToken']


    def bulk_update_leads(self, lookupField, values):
        if len(values) > 300:
            raise Exception("Cannot bulk update more than 300 leads.")
        data = {
            'action': 'createOrUpdate',
            'lookupField': lookupField,
            'input': values
        }
        return self.post(data)

    def update_lead(self, lookupField, values, lookupValue=None):
        data = {
            'action': 'createOrUpdate',
            'lookupField': lookupField,
            'input': [values]
        }
        return self.post(data)

    def create_lead(self, lookupField, lookupValue, values):
        new_lead = dict(list({lookupField: lookupValue}.items()) + list(values.items()))
        data = {
            'action': 'createOnly',
            'lookupField': lookupField,
            'input': [new_lead]
        }
        return self.post(data)

    def create_custom_activity(self, values):
        self.authenticate()
        new_activity = dict(values.items())
        data = {
            "input": [new_activity]
        }

        api_url = "/rest/v1/activities/external.json"
        return self._post_custom(data, api_url)

    def create_custom_object(self, values, api_name):
        self.authenticate()
        new_activity = dict(values.items())
        data = new_activity
        api_url = "/rest/v1/customobjects/" + api_name + ".json"

        return self._post_custom(data, api_url)

    def associate_lead(self, lead_id, marketo_cookie):
        api_url = "/rest/v1/leads/" + lead_id + "/associate.json"
        data = None
        marketo_cookie = marketo_cookie.replace("&", "%26")
        return self._post_custom(data, api_url, marketo_cookie)

    def _post_custom(self, data, api_url, marketo_cookie=None):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        data = HttpLib().post("https://" + self.host +
                              api_url,
                              args, data, marketo_cookie)
        if not data['success']:
            raise MarketoException(data['errors'][0])
        return data

    def post(self, data):
        self.authenticate()

        args = {
            'access_token': self.token
        }
        data = HttpLib().post("https://" + self.host + "/rest/v1/leads.json" , args, data)
        if not data['success'] : raise MarketoException(data['errors'][0])
        return data
