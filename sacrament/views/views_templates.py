from django.shortcuts import render,redirect
from django.http import HttpResponse
from sacrament.models import Profile,Baptism,Confirmation,Marriage,Minister, SacramentModel,Sponsor
from parishsystem.enums import Status,Sacrament,Gender
from sacrament.forms import ProfileModelForm, BaptismModelForm, ConfirmationModelForm, MarriageModelForm ,SponsorModelForm ,formset_factory,RequiredFormSet,Submit_Form
from django.http import JsonResponse
from django.core import serializers
from sacrament.tables import BaptismTable, ConfirmationTable, MarriageTable
from finance.forms import InvoiceModelForm_Application, InvoiceItemModelForm_Application
from finance.models import Invoice, InvoiceItem, ItemType
from datetime import datetime
from scheduling.models import Schedule
from ..serializer import ProfileSerializer
import json
from django.contrib.auth.decorators import login_required

@login_required(login_url='/login/')
def index(request):
    return render(request,"sacrament/side_bar.html")

@login_required(login_url='/login/')
def add_baptism_application(request):
    context= {}
    SponsorFormset = formset_factory(SponsorModelForm ,formset=RequiredFormSet, extra=1, can_delete=True)
    if(request.method == "POST"):
        profile_form = ProfileModelForm(request.POST,prefix="profile")
        baptism_form = BaptismModelForm(request.POST,prefix="baptism")
        sponsor_formset = SponsorFormset(request.POST) 
        invoice_form = InvoiceModelForm_Application(request.POST,prefix="invoice")
        invoice_item_form = InvoiceItemModelForm_Application(request.POST,prefix="invoice_item")

        print(invoice_form)
        print(invoice_item_form)

        if profile_form.is_valid() and baptism_form.is_valid() and invoice_form.is_valid() and invoice_item_form.is_valid() and sponsor_formset.is_valid():
            profile = profile_form.save()
            baptism = baptism_form.save(commit=False)
            baptism.profile = profile
            baptism.status = SacramentModel.PENDING
            baptism.save()
            for form in sponsor_formset:
                if(form.is_valid()):
                    if(form.is_empty()):
                        print("EMPTY<<<<<<<<<<<<")
                        pass
                    else:
                        print("NOT EMPTY<<<<<<<<<<<")
                        f = form.save()
                        f.baptism = baptism
                        f.save()
            invoice = invoice_form.save(commit=False)
            invoice.profile_A = profile
            invoice.date_issued = datetime.now().date()
            invoice.save()
            item = invoice_item_form.save(commit=False)
            item.invoice= invoice

            item.item_type = ItemType.objects.get(name="Baptism")
            item.quantity = 1
            item.balance = item.balance-item.amount_paid-item.discount
            item.save()
            return redirect("sacrament:add-baptism-application") 
        else:
            context['BaptismModelForm']= baptism_form
            context['ProfileModelForm']= profile_form
            context['SponsorFormset']= sponsor_formset
            context['InvoiceModelForm_Application']= invoice_form
            context['InvoiceItemModelForm_Application']= invoice_item_form
            context['Submit_Form']= Submit_Form()
            return render(request,"sacrament/application_baptism.html",context) 
    else:
        try:
            suggested_price = ItemType.objects.get(name="Baptism").suggested_price
        except ItemType.DoesNotExist:
            item_type = ItemType(name="Baptism", suggested_price=0)
            item_type.save()
            suggested_price = ItemType.objects.get(name="Baptism").suggested_price

        context['BaptismModelForm']= BaptismModelForm(prefix="baptism")
        context['ProfileModelForm']= ProfileModelForm(prefix="profile")
        context['SponsorFormset']= SponsorFormset()
        context['InvoiceModelForm_Application']= InvoiceModelForm_Application(prefix="invoice")
        context['InvoiceItemModelForm_Application']= InvoiceItemModelForm_Application(prefix="invoice_item", initial={'balance':suggested_price})
        context['Submit_Form']= Submit_Form()
        return render(request,"sacrament/application_baptism.html",context) 
    
@login_required(login_url='/login/')
def add_confirmation_application(request):
    context= {}
    SponsorFormset = formset_factory(SponsorModelForm ,formset=RequiredFormSet, extra=1, can_delete=True)
    if(request.method == "POST"):
        profile_form = ProfileModelForm(request.POST,prefix="profile")
        confirmation_form = ConfirmationModelForm(request.POST,prefix="confirmation")
        sponsor_formset = SponsorFormset(request.POST) 
        invoice_form = InvoiceModelForm_Application(request.POST,prefix="invoice")
        invoice_item_form = InvoiceItemModelForm_Application(request.POST,prefix="invoice_item")
        if profile_form.is_valid() and confirmation_form.is_valid() and invoice_form.is_valid() and invoice_item_form.is_valid() and sponsor_formset.is_valid():
            profile = None
            if(request.POST.get("profile_ID")!=""):
                profile_id = int(request.POST.get("profile_ID"))
                profile = Profile.objects.get(id=profile_id)
            else:
                profile = profile_form.save()
            confirmation = confirmation_form.save(commit=False)
            confirmation.profile = profile
            confirmation.status = SacramentModel.PENDING
            confirmation.save()
            for form in sponsor_formset:
                if(form.is_valid()):
                    f = form.save()
                    f.confirmation = confirmation
                    f.save()
            invoice = invoice_form.save(commit=False)
            invoice.profile_A = profile
            invoice.date_issued = datetime.now().date()
            invoice.save()
            item = invoice_item_form.save(commit=False)
            item.invoice= invoice
            item.item_type = ItemType.objects.get(name="Confirmation")
            item.balance = item.balance-item.amount_paid-item.discount
            item.quantity = 1
            item.save()
            return redirect("sacrament:add-confirmation-application") 
        else:
            if(not sponsor_formset.is_valid()):
                context['SponsorError']="Firstname, Lastname, and Residence are required"
            context['ConfirmationModelForm']= confirmation_form
            context['ProfileModelForm']= profile_form
            context['SponsorFormset']= sponsor_formset
            context['InvoiceModelForm_Application']= invoice_form
            context['InvoiceItemModelForm_Application']= invoice_item_form
            context['Submit_Form']= Submit_Form()
            return render(request,"sacrament/application_confirmation.html",context) 
    else:
        try:
            suggested_price = ItemType.objects.get(name="Confirmation").suggested_price
        except ItemType.DoesNotExist:
            item_type = ItemType(name="Confirmation", suggested_price=0)
            item_type.save()
            suggested_price = ItemType.objects.get(name="Confirmation").suggested_price

        context['ConfirmationModelForm']= ConfirmationModelForm(prefix="confirmation")
        context['ProfileModelForm']= ProfileModelForm(prefix="profile")
        context['SponsorFormset']= SponsorFormset()
        context['InvoiceModelForm_Application']= InvoiceModelForm_Application(prefix="invoice")
        context['InvoiceItemModelForm_Application']= InvoiceItemModelForm_Application(prefix="invoice_item", initial={'balance':suggested_price})
        context['Submit_Form']= Submit_Form()
        return render(request,"sacrament/application_confirmation.html",context)

@login_required(login_url='/login/')
def add_marriage_application(request):
    context={}
    SponsorFormset = formset_factory(SponsorModelForm ,formset=RequiredFormSet, extra=1, can_delete=True)
    if(request.method=="POST"):
        groom_form = ProfileModelForm(request.POST,prefix="groom")
        bride_form = ProfileModelForm(request.POST,prefix="bride")
        marriage_form = MarriageModelForm(request.POST,prefix="marriage")
        sponsor_formset = SponsorFormset(request.POST) 
        invoice_form = InvoiceModelForm_Application(request.POST,prefix="invoice")
        invoice_item_form = InvoiceItemModelForm_Application(request.POST,prefix="invoice_item")
        if groom_form.is_valid() and bride_form.is_valid() and marriage_form.is_valid() and invoice_form.is_valid() and invoice_item_form.is_valid() and sponsor_formset.is_valid():
            bride = None
            groom = None
            if(request.POST.get("groom_ID")!=""):
                groom_id = int(request.POST.get("groom_ID"))
                groom = Profile.objects.get(id=groom_id)
            else:
                groom = groom_form.save()
            
            if(request.POST.get("bride_ID")!=""):
                bride_id = int(request.POST.get("bride_ID"))
                bride = Profile.objects.get(id=bride_id)
            else:
                bride = bride_form.save()

            marriage = marriage_form.save(commit=False)
            marriage.groom_profile = groom
            marriage.bride_profile = bride
            marriage.status = SacramentModel.PENDING
            marriage.save()
            if(sponsor_formset.is_valid()):    
                for form in sponsor_formset:
                    f = form.save()
                    f.marriage = marriage
                    f.save()
            invoice = invoice_form.save(commit=False)
            invoice.profile_A = groom
            invoice.profile_B = bride
            invoice.date_issued = datetime.now().date()
            invoice.save()
            item = invoice_item_form.save(commit=False)
            item.invoice= invoice
            item.item_type = ItemType.objects.get(name="Marriage")
            item.balance = item.balance-item.amount_paid-item.discount
            item.quantity = 1
            item.save()
            return redirect("sacrament:add-marriage-application")
        else:
            if(not sponsor_formset.is_valid()):
                context['SponsorError']="Firstname, Lastname, and Residence are required"
            context['MarriageModelForm']= marriage_form
            context['GroomModelForm']= groom_form
            context['BrideModelForm']= bride_form
            context['SponsorFormset']= sponsor_formset
            context['InvoiceModelForm_Application']= invoice_form
            context['InvoiceItemModelForm_Application']= invoice_item_form
            context['Submit_Form']= Submit_Form()
            return render(request,"sacrament/application_marriage.html",context)
    else:
        try:
            suggested_price = ItemType.objects.get(name="Marriage").suggested_price
        except ItemType.DoesNotExist:
            item_type = ItemType(name="Marriage", suggested_price=0)
            item_type.save()
            suggested_price = ItemType.objects.get(name="Marriage").suggested_price

        context['MarriageModelForm']= MarriageModelForm(prefix="marriage")
        context['GroomModelForm']= ProfileModelForm(initial={'gender':Profile.MALE},prefix="groom")
        context['BrideModelForm']= ProfileModelForm(initial={'gender':Profile.FEMALE},prefix="bride")
        context['SponsorFormset']= SponsorFormset()
        context['InvoiceModelForm_Application']= InvoiceModelForm_Application(prefix="invoice")
        context['InvoiceItemModelForm_Application']= InvoiceItemModelForm_Application(prefix="invoice_item", initial={'balance':suggested_price})
        context['Submit_Form']= Submit_Form()
        return render(request,"sacrament/application_marriage.html",context)

"""
    MANUAL WAY= KEEP FOR REFERENCE
    if request.method == 'POST':
        profile = Profile.objects.get_or_create(
            first_name = request.POST['first_name'],
            middle_name = request.POST['middle_name'],
            last_name = request.POST['last_name'],
            suffix = request.POST['suffix'],
            birthdate = request.POST['birthdate'],
            gender = request.POST['gender'],
            birthplace = request.POST['birthplace'],
            residence = request.POST['residence']
        )  

        baptism = Baptism.objects.create(
            minister = request.POST['minister'],
            profile = profile,
            legitimacy = request.POST['legitimacy']
        )
        return HttpResponse("hello")
    else:
        ministers = Minister.objects.exclude(status = Status.INACTIVE)
        legitimacy = Baptism.
        context['ministers'] = ministers
        return render(request,"sacrament/application_baptism.html",context)
    """
from django_tables2 import RequestConfig

@login_required(login_url='/login/')
def view_records_baptism(request):
    table = BaptismTable(Baptism.objects.all())
    RequestConfig(request,paginate={'per_page': 20}).configure(table)
    context = {
        "table":table,
    }
    return render(request, "sacrament/records_baptism.html", context)

@login_required(login_url='/login/')
def view_records_confirmation(request):
    table = ConfirmationTable(Confirmation.objects.all())
    RequestConfig(request,paginate={'per_page': 20}).configure(table)
    context = {
        "table":table,
    }   
    return render(request, "sacrament/records_confirmation.html", context)

@login_required(login_url='/login/')
def view_records_marriage(request):
    table = MarriageTable(Marriage.objects.all())
    RequestConfig(request,paginate={'per_page': 20}).configure(table)
    context = {
        "table":table,
    }   
    return render(request, "sacrament/records_marriage.html", context)

@login_required(login_url='/login/')
def view_baptism_detail(request, bap_id):
    pass

@login_required(login_url='/login/')
def get_ministers(request):
    m = Minister.objects.filter(first_name__contains = request.GET.get('q')) | Minister.objects.filter( middle_name__contains = request.GET.get('q')) | Minister.objects.filter( last_name__contains = request.GET.get('q'))# last_name = request.GET.get('q'))
    
    ministers = {"results" : []}
    for x in m:
        ministers["results"].append({
            "id":x.id,
            "text":f"{x.last_name}, {x.first_name or '' } {x.middle_name or '' } {x.suffix or '' }"   
    })

    return JsonResponse(ministers)

@login_required(login_url='/login/')
def get_ministers_by_id(request,id):
    m = Minister.objects.get(id=id)
    minister = {"results" : []}
    minister["results"].append({
        "id":m.id,
        "text":f"{m.last_name}, {m.first_name or '' } {m.middle_name or '' } {m.suffix or '' }"   
    })
    return JsonResponse(minister)

@login_required(login_url='/login/')
def get_profiles(request):
    a =  Profile.objects.filter(first_name__contains = request.GET.get('q')).filter( middle_name__contains = request.GET.get('q'))
    b =  Profile.objects.filter( middle_name__contains = request.GET.get('q')).filter( last_name__contains = request.GET.get('q'))
    c =  Profile.objects.filter( last_name__contains = request.GET.get('q')).filter(first_name__contains = request.GET.get('q'))
    p = a|b|c 
    profiles={"results":[]}
    for x in p:
        profiles["results"].append({
            "id":x.id,
            "text":f"{x.last_name}, {x.first_name or '' } {x.middle_name or '' } {x.suffix or '' }"   
    })
    return JsonResponse(profiles)

@login_required(login_url='/login/')
def get_grooms(request):
    a =  Profile.objects.filter(first_name__contains = request.GET.get('q')).filter( middle_name__contains = request.GET.get('q')).filter(gender = Gender.MALE)
    b =  Profile.objects.filter( middle_name__contains = request.GET.get('q')).filter( last_name__contains = request.GET.get('q')).filter(gender = Gender.MALE)
    c =  Profile.objects.filter( last_name__contains = request.GET.get('q')).filter(first_name__contains = request.GET.get('q')).filter(gender = Gender.MALE)
    p = a|b|c 
    #p = Profile.objects.filter(first_name__contains = request.GET.get('q')) | Profile.objects.filter( middle_name__contains = request.GET.get('q')) | Profile.objects.filter( last_name__contains = request.GET.get('q'))
    profiles={"results":[]}
    for x in p:
        profiles["results"].append({
            "id":x.id,
            "text":f"{x.last_name}, {x.first_name or '' } {x.middle_name or '' } {x.suffix or '' }"   
    })
    return JsonResponse(profiles)

@login_required(login_url='/login/')
def get_brides(request):
    a =  Profile.objects.filter(first_name__contains = request.GET.get('q')).filter( middle_name__contains = request.GET.get('q')).filter(gender = Gender.FEMALE)
    b =  Profile.objects.filter( middle_name__contains = request.GET.get('q')).filter( last_name__contains = request.GET.get('q')).filter(gender = Gender.FEMALE)
    c =  Profile.objects.filter( last_name__contains = request.GET.get('q')).filter(first_name__contains = request.GET.get('q')).filter(gender = Gender.FEMALE)
    p = a|b|c 
    #p = Profile.objects.filter(first_name__contains = request.GET.get('q')) | Profile.objects.filter( middle_name__contains = request.GET.get('q')) | Profile.objects.filter( last_name__contains = request.GET.get('q'))
    profiles={"results":[]}
    for x in p:
        profiles["results"].append({
            "id":x.id,
            "text":f"{x.last_name}, {x.first_name or '' } {x.middle_name or '' } {x.suffix or '' }"   
    })
    return JsonResponse(profiles)

@login_required(login_url='/login/')
def get_profile(request,id):
    profile = Profile.objects.get(id=id)
    profile_qs = None
    baptism_qs = None
    #confirmation_qs = None
    # marriage_qs = None
    try:
        profile_qs = profile
    except Profile.DoesNotExist:
        profile_qs = []
    
    try:
        baptism_qs = Baptism.objects.get(profile = profile_qs.id)
    except Baptism.DoesNotExist:
        baptism_qs = []
    
    # try:
    #     confirmation_qs = Confirmation.objects.get(profile = profile_qs.id)
    # except Confirmation.DoesNotExist:
    #     confirmation_qs = []
    
    # try:
    #     try:
    #         marriage_qs = Marriage.objects.get(groom_profile = profile) 
    #     except:
    #         marriage_qs = Marriage.objects.get(bride_profile = profile)
    # except Marriage.DoesNotExist:
    #     marriage_qs = []

    data = [profile_qs,baptism_qs,]#confirmation_qs,marriage_qs]
    json_return ="["
    for x in data:
        try:
            json = serializers.serialize("json",[x,])
            json_return += json[1:-1]+","
        except:
            pass
    json_return = json_return[:-1] + "]"
    return HttpResponse(json_return)
