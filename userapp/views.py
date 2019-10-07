from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import auth
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group, Permission
from django.core.exceptions import ObjectDoesNotExist
from fcm_django.models import FCMDevice

from . import models

import json
import requests

# Create your views here.

def index(request):
    username = request.user.username
    print(username)
    groups = []
    for g in request.user.groups.all():
        groups.append(g.name)
    print(groups)
    response = {
        'username' : username,
        'groups' : groups
    }
    return JsonResponse(response, safe=False)

#registration for user account
#there is no need for firefighter because firefighter should be always registered.
def registration(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        print(request.POST)
        if form.is_valid():
            user = form.save()
            #for default user building location, set it's building id to CSIE for default, or frontend will crash
            #firefighter should not register thorugh this view
            models.citizen.objects.create(user=user,
                                          fcm_token='', 
                                          building_id=models.building.objects.get(building_id='CSIE'), 
                                          floor_number=models.floor.objects.get(floor_id='CSIE_1F'))
            FCMDevice.objects.create(registration_id='',
                                    name=request.POST.get('username'),
                                    user=user,
                                    type='android')
            user.groups.add(Group.objects.get(name='citizens'))
            response = {
                'status' : 'success',
                'message' : 'successfully registered a new account',
            }
            return JsonResponse(response, safe=False)
        else:
            response = {
                'status' : 'failure',
                'message' : 'Failed to registered a new account, check if form is correct',
            }
            return JsonResponse(response, safe=False)
    else:
        form = UserCreationForm()
    return render(request, 'test/registration.html', {'form': form})

def login(request):
    if request.user.is_authenticated:
        response = {
            'status' : 'Invaild',
            'message' : 'You have already logged in',
        }
        return JsonResponse(response, safe=False)

    if request.method == 'POST':
        print(request.POST)
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        fcm_token = request.POST.get('fcm_token')
        user_type = request.POST.get('user_type')
        
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            if user_type is not None:
                groups = []
                for g in user.groups.all():
                    groups.append(g.name)

                if user_type not in groups:
                    response = {
                        'status' : 'failure',
                        'message' : 'User group not found',
                    }
                    return JsonResponse(response, safe=False)
                #update fcm_token each time user logging, because fcm token may change form reinstalling app.
                elif fcm_token is not None:
                    update_device = FCMDevice.objects.filter(user=user)
                    update_device.update(registration_id=fcm_token)
                    if user_type == 'citizens':
                        update_citizen = models.citizen.objects.filter(user=user)
                        #since FCM token is already stored in FCMDevice, this should be removed by re-construct DB
                        update_citizen.update(fcm_token=fcm_token)
                    if user_type == 'firefighters':
                        update_firefighter = models.firefighter.objects.filter(user=user)
                        update_firefighter.update(fcm_token=fcm_token)
            auth.login(request, user)
            response = {
                'status' : 'success',
                'message' : 'successfully logged in',
            }
            return JsonResponse(response, safe=False)
        else:
            response = {
                'status' : 'failure',
                'message' : 'Wrong username or password',
            }
            return JsonResponse(response, safe=False)
    else:
        return render(request, 'test/login.html')

def logout(request):
    if request.user.is_authenticated:
        auth.logout(request)
        response = {
            'status' : 'success',
            'message' : 'successfully logged out',
        }
        return JsonResponse(response, safe=False)
    else:
        response = {
            'status' : 'failure',
            'message' : 'You have not logged in',
        }
        return JsonResponse(response, safe=False)

#register user into building through QRcode by frontend
def register_building(request):
    if request.method == 'POST':
        print(request.POST)
        building_name = request.POST.get('building_name','')
        floor_name = request.POST.get('floor_name','')

        if request.user.is_authenticated:
            update_data = models.citizen.objects.filter(user=request.user)
            update_building = models.building.objects.get(building_id=building_name)
            update_floor = models.floor.objects.get(floor_id=floor_name)
            update_data.update(building_id=update_building, floor_number=update_floor)

            user = models.citizen.objects.get(user=request.user)
            update_bure = models.building_user_relation.objects.get(building=update_building, account=user)
            if update_bure is None:
                models.building_user_relation.objects.create(bure_id=1, 
                                                            building=update_building,
                                                            account=user)
            response = {
                'status' : 'success',
                'message' : 'successfully registered new building',
                'building_name' : building_name,
                'floor_name' : floor_name,
            }
            return JsonResponse(response, safe=False)
        else:
            response = {
                'status' : 'failure',
                'message' : 'user not login or invaild building or floor',
                'building_name' : building_name,
                'floor_name' : floor_name,
            }
            return JsonResponse(response, safe=False)
    else:
        return render(request, 'test/login.html')

#Send alarm to frontend userapp if RespPi catches an alarm through FCM
def notification(request):
    print(request.GET)
    node_id = request.GET.get('node_id')
    node = models.node.objects.get(node_id=node_id)
    if node is not None:
        #Get which node triggered alarm, and find user through database
        update_node = models.node.objects.filter(node_id=node_id)
        update_node.update(is_alive = False)
        #It's kind of messy, maybe the structure of DB can be better
        #find which floor through ftn(floor to node)
        ftn = models.floor_to_node.objects.get(node_id=node)
        floor = models.floor.objects.get(floor_id=ftn.floor_id)
        #find which floor through btf(building to floor)
        btf = models.building_to_floor.objects.get(floor_id=floor)
        building = models.building.objects.get(building_id=btf.building_id)
        print(floor.floor_id, str(floor.floor_plan))
        #find all user in that building
        boardcast = models.citizen.objects.filter(building_id=building)
        print(boardcast)

        message = {}
        for user in boardcast:
            try:
                device = FCMDevice.objects.get(user=user.user)
                message_body = "火災警報 大樓: " + str(building) + " 樓層: " + str(floor)
                message = {
                    "title" : "Fire alarm",
                    "body" : message_body,
                    "building_name" : str(building),
                    "floor_name" : str(floor),
                    "image" : str(floor.floor_plan)
                }
                print(message_body)
                device.send_message(data=message, title="Fire alarm", body=message_body)
            except ObjectDoesNotExist:
                return HttpResponse('No target user found')
        return JsonResponse(message)
    else:
        return HttpResponse('Node not found')

#RespPi should update node info on certain time interval
#TODO: should add some mechanic to check if a relay not working.
def handshake(request):
    print(request.GET)
    node_id = request.GET.get('node_id')
    gas_strength = request.GET.get('gas', 'null')
    temperature = request.GET.get('temp', 'null')
    node = models.node.objects.filter(node_id=node_id)
    if node is not None:
        node.update(gas=gas_strength, temperature=temperature)
        response = 'updated ' + node_id + ' successfully'
        return HttpResponse(response)
    else:
        return HttpResponse('Node does not exist')

#show current building infornmation for citizens
def show_current_info(request):
    if request.user.is_authenticated:
        groups = []
        for g in request.user.groups.all():
            groups.append(g.name)
        if 'citizens' in groups:
            user = models.citizen.objects.get(user=request.user)
            building_name = models.building.objects.get(building_id=user.building_id)
            floor_name = models.floor.objects.get(floor_id=user.floor_number)
            response = {
                'status' : 'success',
                'message' : 'Responsed building and floor',
                'building_name' : str(building_name),
                'floor_name' : str(floor_name),
            }
            return JsonResponse(response, safe=False)
        elif 'firefighters' in groups:
            return HttpResponse('you are firefighter')
    else:
        return render(request, 'test/login.html')

#show all registed building and it's info for users
#Note: response should append bottom up (from node to building)
#Don't forget to clear variable each time after you append 
def show_all_info(request):
    if request.user.is_authenticated:
        nodes = []
        floors = []
        buildings = []

        get_buildings = models.building.objects.none()
        groups = []
        for g in request.user.groups.all():
            groups.append(g.name)
        if 'firefighters' in groups:
            get_buildings = models.building.objects.all()
            print('firefighter')
        elif 'citizens' in groups:
            get_user = models.citizen.objects.get(user=request.user)
            get_building_user_relation = models.building_user_relation.objects.filter(account=get_user)
            print('citizen')
            print(get_building_user_relation)
            for each_bure in get_building_user_relation:
                get_building = models.building.objects.filter(building_id=each_bure.building)
                get_buildings |= get_building
        print(get_buildings)
        for each_building in get_buildings:
            btof = models.building_to_floor.objects.filter(building_id=each_building)
            print(btof)
            for each_btof in btof:
                floor = each_btof.floor_id
                fton = models.floor_to_node.objects.filter(floor_id=floor)
                for each_fton in fton:
                    node = each_fton.node_id
                    nodes.append({
                        "node_name" : str(node),
                        "node_gas_density" : node.gas,
                        "node_temperature" : node.temperature,
                        "node_alive" : node.is_alive
                    })
                floors.append({
                    "floor_name" : str(each_btof.floor_id),
                    "floor_plan" : str(floor.floor_plan),
                    "people_count" : len(models.citizen.objects.filter(floor_number=floor)),
                    "nodes" : nodes
                })
                nodes = []
            buildings.append({
                "building_name" : str(each_building),
                "floors" : floors
            })
            floors = []
        response = {
            "status" : "success",
            "message" : "Returned all buildings and floors and nodes",
            "buildings" : buildings
        }
        return JsonResponse(response, safe=False)
    else:
        return render(request, 'test/login.html')