from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
import psycopg2
import math
import json
from django.db import connection, IntegrityError
from datetime import datetime, date
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F
from django.db.models import Q
from django.contrib.auth.models import auth
from .models import User, Items_categories, Districts, Statuses, Advertisments, Favorite_advertisments
from django.db import models


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
                        for k in range(1, j):
                            if phone_data[k] < '0' or phone_data[k] > '9':
                                error += 1
                                errors.append({"field": optional_parameters[i], "reasons": ["invalid phone number"]})
                        phone = data[optional_parameters[i]]

        email_unique = User.objects.all().filter(Q(email=mail)).count()

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

            user_registration = User.objects.create_user(username=parameters_values[0], first_name=parameters_values[1],
                                                         last_name=parameters_values[2], email=parameters_values[3],
                                                         password=parameters_values[4], city=city,
                                                         street=street, zip_code=zip_code,
                                                         phone=phone)

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


@csrf_exempt
def create_new_ad(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            try:
                data = json.loads(request.body.decode("utf-8"))
            except BaseException:
                response = JsonResponse({"errors": "missing_required_fields"})
                response.status_code = 422
                return response
            required_fields = ["name", "price", "description", "district", "city", "category", "status", "owner"]
            optional_fields = ["picture", "street", "zip_code"]
            errors = []
            for req in required_fields:
                if req not in data:
                    errors.append({req: "required"})
            else:
                if len(errors) != 0:
                    response = JsonResponse({"errors": errors})
                    response.status_code = 422
                    return response
            if request.user.id == int(data["owner"]):
                try:
                    category = Items_categories.objects.get(id=data["category"])
                    district = Districts.objects.get(name=data["district"])
                    status = Statuses.objects.get(name=data["status"])
                    owner = User.objects.get(id=data["owner"])
                except models.ObjectDoesNotExist:
                    response = JsonResponse({"errors": {"create_failed": "value_doesnt_exist"}})
                    response.status_code = 422
                    return response
                for field in optional_fields:
                    if field not in data:
                        data[field] = None
                new = Advertisments(
                    name=data["name"],
                    description=data["description"],
                    prize=data["price"],
                    picture=data["picture"],
                    city=data["city"],
                    street=data["street"],
                    zip_code=data["zip_code"],
                    category=category,
                    status=status,
                    district=district,
                    owner_id=owner.id
                )
                new.save()
                response = HttpResponse()
                response.status_code = 200
                return response
            else:
                response = JsonResponse({"errors": {"create_failed": "accesing_diferent_user"}})
                response.status_code = 403
                return response
        else:
            response = JsonResponse({"errors": {"create_failed": "no_user_is_logged_in"}})
            response.status_code = 401
            return response


@csrf_exempt
def add_favourite_ads(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            try:
                data = json.loads(request.body.decode("utf-8"))
            except BaseException:
                response = JsonResponse({"errors": "missing_required_fields"})
                response.status_code = 422
                return response
            required_fields = ["ad_id", "user_id"]
            errors = []
            for req in required_fields:
                if req not in data:
                    errors.append({req: "required"})
            else:
                if len(errors) != 0:
                    response = JsonResponse({"errors": errors})
                    response.status_code = 422
                    return response
            if request.user.id == int(data["user_id"]):
                try:
                    ad = Advertisments.objects.get(id=data["ad_id"])
                except models.ObjectDoesNotExist:
                    response = JsonResponse({"errors": {"add_failed": "ad_doesnt_exist"}})
                    response.status_code = 422
                    return response
                user = User.objects.get(id=data["user_id"])
                ad_unique = Favorite_advertisments.objects.all().filter(Q(ad_id=data["ad_id"], user_id=data["user_id"])).count()
                if ad_unique != 0:
                    response = JsonResponse({"errors": {"add_failed": "already_in_favorites"}})
                    response.status_code = 403
                    return response
                new = Favorite_advertisments(
                    ad_id=ad.id,
                    user_id=user.id
                )
                new.save()
                response = HttpResponse()
                response.status_code = 200
                return response
            else:
                response = JsonResponse({"errors": {"add_failed": "accesing_diferent_user"}})
                response.status_code = 403
                return response
        else:
            response = JsonResponse({"errors": {"create_failed": "no_user_is_logged_in"}})
            response.status_code = 401
            return response

@csrf_exempt
def update_profile(request):
    if request.method == 'PUT':
        if request.user.is_authenticated:
            try:
                data = json.loads(request.body.decode("utf-8"))
            except BaseException:
                response = JsonResponse({"errors": "missing_required_fields"})
                response.status_code = 422
                return response
            required_fields = ["user_id", "username", "first_name", "last_name"]
            optional_fields = ["city", "street", "zip_code", "phone", "district"]
            errors = []
            for req in required_fields:
                if req not in data:
                    errors.append({req: "required"})
            else:
                if len(errors) != 0:
                    response = JsonResponse({"errors": errors})
                    response.status_code = 422
                    return response
            if request.user.id == int(data["user_id"]):
                current_user = User.objects.get(id=data['user_id'])
                if current_user.deleted_at != None:
                    response = JsonResponse({"errors": {"update_failed": "user_doesnt_exist"}})
                    response.status_code = 422
                    return response
                if "city" not in data:
                    data["city"] = current_user.city
                if "street" not in data:
                    data["street"] = current_user.street
                if "zip_code" not in data:
                    data["zip_code"] = current_user.zip_code
                if "phone" not in data:
                    data["phone"] = current_user.phone
                if "district" not in data:
                    district = current_user.district
                else:
                    try:
                        district = Districts.objects.get(name=data["district"])
                    except models.ObjectDoesNotExist:
                        response = JsonResponse({"errors": {"update_failed": "value_doesnt_exist"}})
                        response.status_code = 422
                        return response
                """
                update hesla, emailu bude ked tak samostatny endpoint
                """
                try:
                    User.objects.filter(id=data['user_id']).update(
                        last_name=data["last_name"],
                        first_name=data["first_name"],
                        username=data["username"],
                        district=district,
                        city=data["city"],
                        street = data["street"],
                        zip_code = data["zip_code"],
                        phone = data["phone"]
                    )
                except IntegrityError:
                    response = JsonResponse({"errors": {"update_failed": "inavlid_value"}})
                    response.status_code = 422
                    return response
                response = HttpResponse()
                response.status_code = 200
                return response
            else:
                response = JsonResponse({"errors": {"update_failed": "accesing_diferent_user"}})
                response.status_code = 403
                return response
        else:
            response = JsonResponse({"errors": {"create_failed": "no_user_is_logged_in"}})
            response.status_code = 401
            return response


@csrf_exempt
def update_ad(request):
    if request.method == 'PUT':
        if request.user.is_authenticated:
            try:
                data = json.loads(request.body.decode("utf-8"))
            except BaseException:
                response = JsonResponse({"errors": "missing_required_fields"})
                response.status_code = 422
                return response
            required_fields = ["ad_id", "user_id", "name", "description", "price", "city", "category", "status", "district"]
            optional_fields = ["picture", "street", "zip_code"]
            errors = []
            for req in required_fields:
                if req not in data:
                    errors.append({req: "required"})
            else:
                if len(errors) != 0:
                    response = JsonResponse({"errors": errors})
                    response.status_code = 422
                    return response
            if request.user.id == int(data["user_id"]):
                try:
                    ad = Advertisments.objects.get(id=data["ad_id"])
                    district = Districts.objects.get(name=data["district"])
                    status = Statuses.objects.get(name=data["status"])
                    if ad.deleted_at != None:
                        raise models.ObjectDoesNotExist
                except models.ObjectDoesNotExist:
                    response = JsonResponse({"errors": {"update_failed": "value_doesnt_exist"}})
                    response.status_code = 422
                    return response

                if "picture" not in data:
                    data["picture"] = ad.picture
                if "street" not in data:
                    data["street"] = ad.street
                if "zip_code" not in data:
                    data["zip_code"] = ad.zip_code
                try:
                    Advertisments.objects.filter(id=data['ad_id']).update(
                        name=data["name"],
                        description =data["description"],
                        prize =data["price"],
                        picture =data["picture"],
                        city =data["city"],
                        street =data["street"],
                        zip_code =data["zip_code"],
                        category =data["category"],
                        status =status,
                        district = district
                    )
                except IntegrityError:
                    response = JsonResponse({"errors": {"update_failed": "invalid_value"}})
                    response.status_code = 422
                    return response
                response = HttpResponse()
                response.status_code = 200
                return response
            else:
                response = JsonResponse({"errors": {"add_failed": "accesing_diferent_user"}})
                response.status_code = 403
                return response
        else:
            response = JsonResponse({"errors": {"create_failed": "no_user_is_logged_in"}})
            response.status_code = 401
            return response