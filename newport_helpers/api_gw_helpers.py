class APIGWHelpers():
    def __init__(self, *args, **kwargs):
        return

    def api_gw_get_url_from_name(self, session, name):
        """

        :param session:
        :param name:
        :return:
        """
        gw = session.client('apigateway')
        response = gw.get_rest_apis()
        for api in response["items"]:
            if name in api['name']:
                item = api
        id = item['id']

        api_endpoint = "{}.execute-api.{}.amazonaws.com".format(id, 'us-east-1')

        return api_endpoint
