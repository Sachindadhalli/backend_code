from rest_framework.response import Response
import jwt


def permission_required():
    def _method_wrapper(view_method):
        def _arguments_wrapper(request, *args, **kwargs):
            try:
                public_key = open('jwt-key.pub').read()
                access_token = request.request.META['HTTP_AUTHORIZATION']
                access_token = access_token.replace("Bearer ", "")
            except Exception as e:
                return Response({"status": False, "message": 'Please Login before Accessing'}, status=401)
            try:
                print("----------------------------------")
                print(access_token,type(access_token))
                print("---------------------------")
                decorator_data = jwt.decode(access_token, public_key, algorithm='RS256')
            except Exception as e:
                return Response({"status": False, "message": 'UnAuthorised'}, status=401)
            request.request.META.update({'user_id': decorator_data["user_id"], "user_type": decorator_data["user_type"]})
            return view_method(request, *args, **kwargs)
        return _arguments_wrapper
    return _method_wrapper
