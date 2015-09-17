from pythonmarketo.client import MarketoClient
import json

mc = MarketoClient(host = <HOST>, 
                   client_id = <CLIENT_ID>, 
                   client_secret = <CLIENT_SECRET>)



activity_result_list = []
nextPageToken = mc.get_paging_token(sinceDatetime = "2015-01-01")
moreResult = True
count = 1
while moreResult:
    result = mc.get_lead_activity_page('30', nextPageToken, None, None)
    print(result, count)
    count += 1 
    if result is None:
        break
    moreResult = result['moreResult']
    nextPageToken = result['nextPageToken']
    if 'result' in result:
        activity_result_list.extend(result['result'])


result = mc.execute(method='create_custom_activity',
                    values={'leadId': <leadId>, 'activityTypeId': <activityTypeId>,
                            'primaryAttributeValue': <primaryAttributeValue>,
                            'attributes': [{'name': <name>, 'value': <value>}]})
