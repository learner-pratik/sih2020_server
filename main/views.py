from django.shortcuts import render,redirect
from django.http import JsonResponse
from .models import Login,Tasks,Researcher,Forest_employee,Animal,Camera
from .forms import addanimalform,addcameraform,addtaskform,addresearcherform
from background_task import background
import time
import subprocess
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Use a service account

###########API##############
# from .models import Snippet
from .serializers import Task_serializer
from django.http import Http404, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json

def login(request):
    # fun()
    # back()
    # with open('/home/ravi/python projects/sih2020/server/app/process.sh', 'rb') as file:
    #     script = file.read()
    # rc = subprocess.call(script, shell=True)
    request.session.flush()
    process = subprocess.Popen(['python', 'manage.py','process_tasks'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return render(request, "login.html", {})

def info(request):
    if request.method == 'POST':    
        user = request.POST.get('username')
        passw = request.POST.get('password')
        print(user,passw)
        if user =='admin' and passw=='admin123':
            return redirect('admin')
        else:
            try:
                data=Researcher.objects.get(username=user,password=passw)
                flag="r"
            except Researcher.DoesNotExist:
                try:
                    data=Forest_employee.objects.get(username=user,password=passw)
                    flag="f"
                except:
                    data = None
            # data=Researcher.objects.get(username=user,password=passw)
            print(data,flag)
            if data==None:
                return render(request, "login.html", {})
            if flag=="r":
                request.session['data']={'researcher_id':data.researcher_id}
                request.session['flag']="r"
                return redirect('researcher')
            else:
                request.session['data']={'forest_name':data.forest_name}
                if data.role=='employee':
                    request.session['flag']="e"
                else:
                    request.session['flag']="f"
                return redirect('forest_employee')
    # return render(request, "next.html", {})

def admin(request):
    animals=[]
    sdict={}
    slat={}
    slon={}
    x=Animal.objects.all()
    for y in x:
        animals.append(y.animal_info)
    animals=list(set(animals))
    for atype in animals:
        sdict[atype]=[]
        slat[atype]=[]
        slon[atype]=[]
        a=Animal.objects.filter(animal_info=atype)
        for i in a:
            sdict[atype].append(i.animal_id)
            slat[atype].append(i.latitude[-1])
            slon[atype].append(i.longitude[-1])
    print(sdict,slat,slon)
    return render(request,"admin.html",{"animals":animals,"sdict":sdict,"slat":slat,"slon":slon})
    
def researcher(request):
    data=request.session.get('data')
    print(data)
    r=Researcher.objects.get(researcher_id=data['researcher_id'])
    animals=r.animal
    print(animals)
    sdict={}
    slat={}
    slon={}
    for atype in animals:
        sdict[atype]=[]
        slat[atype]=[]
        slon[atype]=[]
        a=Animal.objects.filter(animal_info=atype)
        for i in a:
            sdict[atype].append(i.animal_id)
            slat[atype].append(i.latitude[-1])
            slon[atype].append(i.longitude[-1])
    print(sdict,slat,slon)
    return render(request,"researcher.html",{"animals":animals,"sdict":sdict,"slat":slat,"slon":slon})

def forest_employee(request):
    data=request.session.get('data')
    print(data)
    animals=[]
    sdict={}
    slat={}
    slon={}
    x=Animal.objects.all()
    for y in x:
        animals.append(y.animal_info)
    animals=list(set(animals))
    for atype in animals:
        sdict[atype]=[]
        slat[atype]=[]
        slon[atype]=[]
        a=Animal.objects.filter(animal_info=atype)
        for i in a:
            sdict[atype].append(i.animal_id)
            slat[atype].append(i.latitude[-1])
            slon[atype].append(i.longitude[-1])
    print(sdict,slat,slon)
    return render(request,"forest_employee.html",{"animals":animals,"sdict":sdict,"slat":slat,"slon":slon})
    
def task(request):
    for key, value in request.session.items():
        print('{} => {}'.format(key, value))
    flag=request.session.get("flag")
    if flag=="r":
        data=Tasks.objects.filter(task_from=request.session.get('data')['researcher_id'])
        return render(request,"task.html",{'data':data,'flag':flag})
    else:
        fn=request.session.get('data')['forest_name']
        data=[]
        d=Tasks.objects.filter(task_to=fn)
        s=Tasks.objects.filter(task_from=fn)
        print(s,d)
        for i in d:
            data.append(i)
        print(data,fn)
        for i in s:
            for j in range(len(data)):
                # print(data[j].task_id)
                if data[j]!=-1:
                    if i.task_id==data[j].task_id:
                        data[j]=-1
            data.append(i)
        data=list(filter(lambda a: a != -1, data))

        w=Forest_employee.objects.filter(forest_name=fn)
        print(w)
        # ind=0
        # for i in w:
        #     i.empid
    return render(request,"task.html",{'data':data,'flag':flag,"workers":w})# to be continued from forest officer

def addtask(request):
    for key, value in request.session.items():
        print('{} => {}'.format(key, value))
    if request.method == 'POST':
        print(request.POST)
        t=Tasks()
        count=Tasks.objects.count()
        t.task_id='id_'+(str(count+1))
        t.task_from=request.session.get('data')['researcher_id']
        t.task_info=request.POST.get("task_info")
        t.task_to=request.POST.get("task_to")
        t.status=request.POST.get("status")
        t.deadline=request.POST.get("deadline")
        print(t)
        t.save()
        # form = addtaskform(request.POST or None)
        # if form.is_valid():
        #     form.save()  
        return render(request,"done.html",{})
        # else:
        #     # form.errors.as_data()
        #     print('error',form.errors.as_data())
    forest_name=[]
    data=Forest_employee.objects.all()
    for i in data:
        forest_name.append(i.forest_name)
    forest_name=list(set(forest_name))
    return render(request,"addtask.html",{'forest_name':forest_name})

def assigntask(request):
    # for key, value in request.session.items():
    #     print('{} => {}'.format(key, value))
    if request.method == 'POST':
        print(request.POST)
        task=Tasks.objects.get(task_id=request.POST['task_id'])
        Tasks.objects.filter(task_id=request.POST["task_id"]).update(status="assigned")
        t=Tasks()
        t.task_id=task.task_id
        t.task_from=task.task_to
        t.task_info=task.task_info
        t.task_to=request.POST['task_to']
        t.status='assigned'
        t.deadline=task.deadline
        print(t)
        t.save()
    return HttpResponse(status=200)

def addanimal(request):
    if request.method == 'POST':
        print((request.POST['animal_id']))
        a=Animal()
        count=Animal.objects.count()
        # print(count)
        a.animal_id='id_'+(str(count+1))
        a.animal_name=request.POST['animal_name']
        a.animal_info=request.POST['animal_info']
        a.latitude=[0]
        a.longitude=[0]
        a.save()
        # form = addanimalform(request.POST or None)
        # if(False):
        # if form.is_valid():
        # form.save()
        #firebase#
        if not firebase_admin._apps:
            data = open('main/static/serviceAccount.json').read() #opens the json file and saves the raw contents
            jsonData = json.loads(data) #converts to a json structure

            cred = credentials.Certificate(jsonData)
            firebase_admin.initialize_app(cred)
        db = firestore.client()
        print(db,'id_'+(str(count+1)))
        animal = db.collection(u'animals').document('id_'+(str(count+1)))
        animal.set({
            u'latitude': 0,
            u'longitude': 0,
        })

        ##animal list##
        animals_list = db.collection(u'animals_list').document(request.POST['animal_info'])
        temp=animals_list.get()
        if temp.exists:
            print("yes")
            sel=temp.to_dict()
            print(sel['id'])
            tem=sel['id']
            tem.append('id_'+(str(count+1)))
            animals_list.update({'id':tem})
        else:
            print("no")
            animals_list.set({
                u'id':['id_'+(str(count+1))]
            })

        docs = db.collection(u'animals').stream()

        for doc in docs:
            print(f'{doc.id} => {doc.to_dict()}')
        #######
        
        return render(request,"done.html",{})  
    return render(request,"addanimal.html",{})

def addcamera(request):
    if request.method == 'POST':
        # form = addcameraform(request.POST or None)
        # if form.is_valid():
        #     form.save()  
        c=Camera()
        count=Camera.objects.count()
        c.camera_id='id_'+(str(count+1))
        c.latitude=request.POST['latitude']
        c.longitude=request.POST['longitude']
        c.status=request.POST['status']
        c.save()
        return render(request,"done.html",{})
    return render(request,"addcamera.html",{})

def addresearcher(request):
    if request.method == 'POST':
        # print(request.body)
        # form = addresearcherform(request.POST or None)
        r=Researcher()
        count=Researcher.objects.count()
        r.researcher_id='id_'+(str(count+1))
        r.researcher_name=request.POST['researcher_name']
        r.experience=request.POST['experience']
        r.qualification=request.POST['qualification']
        r.animal=request.POST['animal'].split(",")
        r.username=request.POST['username']
        r.password=request.POST['password']
        r.save()
        # if (False):
            # form.save() 
        return render(request,"done.html",{})
        # else:
        #     # form.errors.as_data()
        #     print('error',form.errors.as_data())
    data=Animal.objects.all()
    al=[]
    for i in data:
        al.append(i.animal_info)
    return render(request,"addresearcher.html",{"animal":al})

def researcherlist(request):
    data=Researcher.objects.all()
    return render(request,"researcherlist.html",{'data':data})

def location(request):
    print(request.POST['animals'])
    animals=request.POST['animals'].split(",")
    sdict={}
    slat={}
    slon={}
    for atype in animals:
        sdict[atype]=[]
        slat[atype]=[]
        slon[atype]=[]
        a=Animal.objects.filter(animal_info=atype)
        for i in a:
            sdict[atype].append(i.animal_id)
            slat[atype].append(i.latitude[-1])
            slon[atype].append(i.longitude[-1])
    print(sdict,slat,slon)
    return JsonResponse({"sdict":sdict,"slat":slat,"slon":slon})
    # return HttpResponse({"sdict":sdict,"slat":slat,"slon":slon},content_type="application/json")

def geojson(request):
    data = open('main/static/Neighbourhoods.geojson').read() #opens the json file and saves the raw contents
    data = json.loads(data)

    return JsonResponse(data, safe=False)

def editresearcher(request,id="0"):
    print(id)
    if request.method == 'POST':
        d=Researcher.objects.get(researcher_id=id).delete()
        r=Researcher()
        r.researcher_id=id
        r.researcher_name=request.POST['researcher_name']
        r.experience=request.POST['experience']
        r.qualification=request.POST['qualification']
        r.animal=request.POST['animal'].split(",")
        r.username=request.POST['username']
        r.password=request.POST['password']
        r.save()
        # if (False):
            # form.save() 
        return render(request,"done.html",{})
    r=Researcher.objects.get(researcher_id=id)
    ra=set(r.animal)
    data=Animal.objects.all()
    al=[]
    for i in data:
        if i.animal_info not in ra: 
            al.append(i.animal_info)
    al=list(set(al))
    ra=list(ra)
    resa=ra[0]
    for i in range(1,len(ra)):
        resa+=","+ra[i]
    return render(request,"editresearcher.html",{"r":r,"animal":al,"resa":resa})

@background(schedule=2)
def back():
    a=0
    while(a<10):
        a+=1
        print(a)
        l=Login()
        l.username='pratik'
        l.password='pratik'
        l.save()
        time.sleep(3)


def fun():
    print('call')
    return

###############API#################
class give_task(APIView):
    def post(self,request,format=json):
        print(request.data)
        snippets = Tasks.objects.filter(task_to=request.data[0],status='assigned')
        serializer = Task_serializer(snippets, many=True)
        # return render(request,"appdata.html",{'data':serializer.data})
        return Response(serializer.data)
        # print(serializer.data)
        # return Response({"data":[{"id":10},{"id":103}]})

class manage_task(APIView):
    # def get(self,request,format=None):
    #     print(request.data)
    #     snippets = Tasks.objects.filter(task_to=request.data)
    #     serializer = Task_serializer(snippets, many=True)
    #     # return render(request,"appdata.html",{'data':serializer.data})
    #     # return Response(serializer.data)
    #     return Response({'data':['a','b','asd']})

    def post(self, request, format=None):
        print(type(request.data))
        if type(request.data) is list:
            print(len(request.data))
            for i in range(len(request.data)):
                serializer = Task_serializer(data=request.data[i])
                print("posting",serializer)
                if serializer.is_valid():
                    print("valid",request.data[i]['task_id'])
                    Tasks.objects.get(task_id=request.data[i]['task_id'],task_to=request.data[i]['task_to']).delete()
                    Tasks.objects.filter(task_id=request.data[i]['task_id'],task_to=request.data[i]['task_from']).update(status='complete')
                    serializer.save()

            return Response([], status=status.HTTP_201_CREATED)
        else:
            serializer = Task_serializer(data=request.data)
            print("posting",serializer)
            if serializer.is_valid():
                print("valid",request.data['task_id'])
                Tasks.objects.get(task_id=request.data['task_id'],task_to=request.data['task_to']).delete()
                Tasks.objects.filter(task_id=request.data['task_id'],task_to=request.data['task_from']).update(status='complete')
                serializer.save()
                
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class manage_login(APIView):
    # def get(self,request,format=None):
    #     print(request.data)
    #     data={"id":10}
    #     print("get")
    #     return Response(data,status=status.HTTP_201_CREATED)

    def post(self,request,format=None):
        print(request.data)
        try:
            d=Forest_employee.objects.get(username=request.data['username'],password=request.data['password'])
            st=d.empid+'-'+d.name
            data={"id":st}
            print("post")
        except Forest_employee.DoesNotExist:
            data={"id":"-1"}
        return Response(data,status=status.HTTP_201_CREATED)

# class give_location(APIView):
#     def post(self,request,format=None):
#         print(request.POST['animals'])
#         animals=request.POST['animals']
#         sdict={}
#         slat={}
#         slon={}
#         for atype in animals:
#             sdict[atype]=[]
#             slat[atype]=[]
#             slon[atype]=[]
#             a=Animal.objects.filter(animal_info=atype)
#             for i in a:
#                 sdict[atype].append(i.animal_id)
#                 slat[atype].append(i.latitude[-1])
#                 slon[atype].append(i.longitude[-1])
#         print(sdict,slat,slon)
#         return({"sdict":sdict,"slat":slat,"slon":slon})