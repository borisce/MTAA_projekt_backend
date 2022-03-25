from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
import psycopg2
import math
import json
from django.db import connection
from datetime import datetime, date
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F
from django.db.models import Q
from django.contrib.auth.models import auth
from .models import User


@csrf_exempt
def register(request):
    # POST request

    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        data = json.loads(body_unicode)

        len_list = len(data)

        # nazvy parametrov ktore musia byt v body
        required_parameters = ["user_name", "first_name", "last_name", "email", "password"]
        optional_parameters = ["city", "street", "zipcode", "phone"]

        # pole v ktorom budu ulozene hodnoty parametrov
        parameters_values = []

        errors = []

        error = 0

        for i in range(5):
            # ziskanie hodnot textovych parametrov
            if required_parameters[i] in data:
                if i == 3:
                    mail = data[required_parameters[i]]
                    j = len(mail)
                    dot = 0
                    at = 0
                    at_position = 0
                    dot_position = 0
                    for k in range(j):
                        if mail[k] == '@' and at == 0:
                            at = 1
                            at_position = k
                            continue
                        if mail[k] == '.' and dot == 0 and at != 0:
                            dot = 1
                            dot_position = k
                            continue
                        if mail[k] == '@' and at != 0:
                            print("1")
                            error += 1
                            errors.append({"field": required_parameters[i], "reasons": ["invalid mail"]})
                        if mail[k] == '.' and dot != 0:
                            print("2")
                            error += 1
                            errors.append({"field": required_parameters[i], "reasons": ["invalid mail"]})
                    if at_position > dot_position:
                        print("3")
                        error += 1
                        errors.append({"field": required_parameters[i], "reasons": ["invalid mail"]})

                parameters_values.append(data[required_parameters[i]])

            else:
                error += 1
                errors.append({"field": required_parameters[i], "reasons": ["required"]})

            city = None
            street = None
            zip_code = None
            phone = None

            for i in range(4):
                # ziskanie hodnot textovych parametrov
                if optional_parameters[i] in data:
                    if i == 0:
                        city = data[optional_parameters[i]]
                    if i == 1:
                        street = data[optional_parameters[i]]
                    if i == 2:
                        zip_code = data[optional_parameters[i]]
                    if i == 3:
                        phone_data = data[optional_parameters[i]]
                        j = len(phone_data)
                        if phone_data[0] != '+':
                            if phone_data[0] < '0' or phone_data[0] > '9':
                                error += 1
                                errors.append({"field": optional_parameters[i], "reasons": ["invalid phone number"]})
                        for k in range(1,j):
                            if phone_data[k] < '0' or phone_data[k] > '9':
                                error += 1
                                errors.append({"field": optional_parameters[i], "reasons": ["invalid phone number"]})
                        phone = data[optional_parameters[i]]


        email_unique =User.objects.all().filter(Q(email=mail)).count()

        if email_unique != 0:
            error += 1
            errors.append({"field": "email", "reasons": ["not_unique"]})

        user_name_unique = User.objects.all().filter(Q(username=data["user_name"])).count()

        if user_name_unique != 0:
            error += 1
            errors.append({"field": "user_name", "reasons": ["not_unique"]})


            # ak je nejaky parameter vadny alebo nie je zadany vrati sa error
        if error != 0:
            result = {
                "errors": errors
            }
            response = JsonResponse(result)
            response.status_code = 422
        else:


            # pridanie zaznamu do databazy

            user_registration = User.objects.create_user(username = parameters_values[0], first_name = parameters_values[1],
                                     last_name = parameters_values[2], email = parameters_values[3],
                                     password = parameters_values[4], city = city,
                                     street = street, zip_code = zip_code,
                                     phone = phone)

            user_registration.save()


            response = HttpResponse()

            response.status_code = 201

        return response

@csrf_exempt
def login(request):
    # POST request

    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        data = json.loads(body_unicode)

        errors = []

        error = 0

        if "user_name" in data:
            username = data["user_name"]
        else:
            error += 1
            errors.append({"field": "user_name", "reasons": ["required"]})

        if "password" in data:
            password = data["password"]
        else:
            error += 1
            errors.append({"field": "password", "reasons": ["required"]})

        if error != 0:
            result = {
                "errors": errors
            }
            response = JsonResponse(result)
            response.status_code = 401

            return response
        else:

            if request.user.is_authenticated:
                errors.append({"login failed": "user already logged in"})

                result = {
                    "errors": errors
                }

                response = JsonResponse(result)
                response.status_code = 403

                return response

            else:

                user = auth.authenticate(username=username, password=password)

                if user is not None:
                    auth.login(request, user)

                    response = HttpResponse()
                    response.status_code = 200

                    return response

                else:

                    errors.append({"login failed": "invalid credentials"})


                    result = {
                            "errors": errors
                    }

                    response = JsonResponse(result)
                    response.status_code = 401

                    return response


@csrf_exempt
def logout(request):
    # POST request

    if request.method == 'POST':
        if request.user.is_authenticated:
            auth.logout(request)

            response = HttpResponse()
            response.status_code = 200

            return response

        else:
            print("idee")
            errors = []

            errors.append({"logout_failed": "no_user_is_logged_in"})

            result = {
                "errors": errors
            }

            response = JsonResponse(result)
            response.status_code = 401

            return response


