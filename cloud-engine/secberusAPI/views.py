from rest_framework import status
from rest_framework.response import Response
from rest_framework_jwt.views import *
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from secberusAPI.settings import client

class CustomObtainJSONWebToken(ObtainJSONWebToken):

    def post(self, request):
        serializer = self.get_serializer(
            data=request.data
        )
        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            token = serializer.object.get('token')
            response_data = jwt_response_payload_handler(token, user, request)
            return Response(response_data)
        return Response({
            "items": serializer.errors,
            "message": "Unable to login",
            }, status=status.HTTP_401_UNAUTHORIZED)


class CountryListView(GenericAPIView):

    permission_classes = (AllowAny,)
    def get(self, request):
        """
            API View that receives a GET request.
            and return the list of countries with country code.
        """
        query_line = "For data IN Countries SORT data.name\
                        RETURN {'name': data.name ,'code': data.code,\
                        'dialingCode' : data.dial_code}"
        q = client.api.cursor().post({"query": query_line})
        if q['code'] == 201:
            return Response(q['result'], status=status.HTTP_200_OK)
        else:
            return Response({
            "items": {},
            "message": q['result'],
            }, status=status.HTTP_400_BAD_REQUEST)

class StateListView(GenericAPIView):

    permission_classes = (AllowAny,)
    def get(self, request, countryCode):
        """
            API View that receives a Get with country code.
            It validates the country code and return the list of states.
        """

        query_line = "For data IN Countries FILTER data.code == '"\
                    +str(countryCode)+"' RETURN data.states"
        q = client.api.cursor().post({"query": query_line})
        if q['code'] == 201:
            return Response(q['result'][0], status=status.HTTP_200_OK)
        else:
            return Response({
            "items": {},
            "message": q['result'],
            }, status=status.HTTP_400_BAD_REQUEST)
