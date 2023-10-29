from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CreateUserForm
from .models import CounsellorInfo,AdminInfo,FinalTable
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
import datetime
from collections import defaultdict
from datetime import datetime


# Create your views here.

@login_required(login_url='login')
def home(request):
    return render(request, 'home/home.html')

@login_required(login_url='login')
def cdc(request):
    return render(request, 'home/cdc.html')

def loginPage(request):
    
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        context = {'username': username}

        if user is not None:
            login(request, user)
            if user.is_superuser:
                print("Superuser!!!!!!")
                return redirect('cdc')
            # return render(request, 'home/home.html', context)
            return redirect('home')
        else:
            messages.info(request, 'Username or Password is incorrect')
    return render(request, 'home/login.html')    



def registerPage(request):
    
    if request.user.is_authenticated:
        return redirect('home')

    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get("username")
            messages.success(request, "Account created successfully")
            return redirect('login')

    context = {'form': form}
    return render(request, 'home/signup.html', context)

def logoutUser(request):
    """
    This view function is responsible for logging out the user and redirecting to the login page.
    """
    logout(request)
    return redirect('login')

def DataAdder(request):

    if request.method == 'POST':

        # Store Personal Details

        batchDate = request.POST.get('batchDate')
        counsellorName = request.POST.get('counsellorName')
        numberOfFbMessages = request.POST.get('numberOfFbMessages')
        numberOfWebMessages = request.POST.get('numberOfWebMessages')
        numberOfFbAdmission = request.POST.get('numberOfFbAdmission')
        numberOfWebAdmission = request.POST.get('numberOfWebAdmission')


        details = CounsellorInfo.objects.create(
                user=User.objects.get(username=request.user.username),
                batchDate=batchDate,
                counsellorName=counsellorName,
                numberOfFbMessages=numberOfFbMessages,
                numberOfWebMessages=numberOfWebMessages,
                numberOfFbAdmission=numberOfFbAdmission,
                numberOfWebAdmission=numberOfWebAdmission,
               
            )
            
        details.save()
         
        context = {
            'data_added': True
        }
        return render(request, 'home/home.html', context)
    

    else:

        user = request.user
        context = {
            'data_added': False
        }
        
        return render(request, 'home/user.html', context)

def DataAdm(request):
    if request.method == 'POST':
        # Store Personal Details
        batchDate = request.POST.get('batchDate')
        FbExpense = request.POST.get('fbExpense')
        WebExpense = request.POST.get('webExpense')
        
        details = FinalTable.objects.create(
            batchDate=batchDate,
            fbExpense=FbExpense,
            webExpense=WebExpense,
        )
        details.save()
        
        context = {
            'data_added': True
        }
        return render(request, 'home/cdc.html', context)
    else:
        user = request.user
        context = {
            'data_added': False
        }
        return render(request, 'home/adm.html', context)




def DataFilter(request):
    username = request.user.username
    
    if request.user.is_superuser:
        counsellor_info_list = CounsellorInfo.objects.all()
        
        aggregated_data = defaultdict(lambda: {
            'sumOfNumberOfFbMessages': 0,
            'sumOfNumberOfWebMessages': 0,
            'sumOfNumberOfFbAdmission': 0,
            'sumOfNumberOfWebAdmission': 0,
            'sumOfFbExpense': 0,
            'sumOfWebExpense': 0,
        })

        for counsellor_info in counsellor_info_list:
            batch_date = counsellor_info.batchDate
            aggregated_data[batch_date]['sumOfNumberOfFbMessages'] += counsellor_info.numberOfFbMessages
            aggregated_data[batch_date]['sumOfNumberOfWebMessages'] += counsellor_info.numberOfWebMessages
            aggregated_data[batch_date]['sumOfNumberOfFbAdmission'] += counsellor_info.numberOfFbAdmission
            aggregated_data[batch_date]['sumOfNumberOfWebAdmission'] += counsellor_info.numberOfWebAdmission

        final_table_data = FinalTable.objects.all()

        for final_table_entry in final_table_data:
            batch_date = final_table_entry.batchDate  # Assuming 'date' is the date field in FinalTable
            aggregated_data[batch_date]['sumOfFbExpense'] = final_table_entry.fbExpense
            aggregated_data[batch_date]['sumOfWebExpense'] = final_table_entry.webExpense

        for batch_date, data in aggregated_data.items():
            sum_fb_messages = data['sumOfNumberOfFbMessages']
            sum_web_messages = data['sumOfNumberOfWebMessages']
            sum_fb_admission = data['sumOfNumberOfFbAdmission']
            sum_web_admission = data['sumOfNumberOfWebAdmission']
            sum_fb_expense = data['sumOfFbExpense']
            sum_web_expense = data['sumOfWebExpense']
            
            try:
                try:
                    admin_info = AdminInfo.objects.get(date=batch_date)
                except AdminInfo.MultipleObjectsReturned:
                    admin_info = AdminInfo.objects.filter(date=batch_date).first()

                counsellor_info= CounsellorInfo.objects.filter(batchDate=batch_date)
                admin_info.sumOfNumberOfFbMessages = sum_fb_messages
                admin_info.sumOfNumberOfWebMessages = sum_web_messages
                admin_info.sumOfNumberOfFbAdmission = sum_fb_admission
                admin_info.sumOfNumberOfWebAdmission = sum_web_admission
                
                # Calculate FB lead cost and Web lead cost
                admin_info.fbLeadCost = sum_fb_expense / sum_fb_messages if sum_fb_messages is not None and sum_fb_messages > 0 else 0
                admin_info.webLeadCost = sum_web_expense / sum_web_messages if sum_web_messages is not None and sum_web_messages > 0 else 0

                # Calculate FB CPA and Web CPA
                admin_info.fbCPA = sum_fb_expense / sum_fb_admission if sum_fb_admission is not None and sum_fb_admission > 0 else 0
                admin_info.webCPA = sum_web_expense / sum_web_admission if sum_web_admission is not None and sum_web_admission > 0 else 0
                admin_info.save()
                
            except AdminInfo.MultipleObjectsReturned:
                admin_infos = AdminInfo.objects.filter(date=batch_date)
                first_admin_info = admin_infos.first()
                first_admin_info.sumOfNumberOfFbMessages = sum_fb_messages
                first_admin_info.sumOfNumberOfWebMessages = sum_web_messages
                first_admin_info.sumOfNumberOfFbAdmission = sum_fb_admission
                first_admin_info.sumOfNumberOfWebAdmission = sum_web_admission
                first_admin_info.fbLeadCost = sum_fb_expense / sum_fb_messages if sum_fb_messages is not None and sum_fb_messages > 0 else 0
                first_admin_info.webLeadCost = sum_web_expense / sum_web_messages if sum_web_messages is not None and sum_web_messages > 0 else 0
                first_admin_info.fbCPA = sum_fb_expense / sum_fb_admission if sum_fb_admission is not None and sum_fb_admission > 0 else 0
                first_admin_info.webCPA = sum_web_expense / sum_web_admission if sum_web_admission is not None and sum_web_admission > 0 else 0
                first_admin_info.save()
                admin_infos.exclude(pk=first_admin_info.pk).delete()
                
            except ObjectDoesNotExist:
                admin_info = AdminInfo.objects.create(
                    sumOfNumberOfFbMessages=sum_fb_messages,
                    sumOfNumberOfWebMessages=sum_web_messages,
                    sumOfNumberOfFbAdmission=sum_fb_admission,
                    sumOfNumberOfWebAdmission=sum_web_admission,
                    fbLeadCost = sum_fb_expense / sum_fb_messages if sum_fb_messages is not None and sum_fb_messages > 0 else 0,
                    webLeadCost = sum_web_expense / sum_web_messages if sum_web_messages is not None and sum_web_messages > 0 else 0,
                    fbCPA = sum_fb_expense / sum_fb_admission if sum_fb_admission is not None and sum_fb_admission > 0 else 0,
                    webCPA = sum_web_expense / sum_web_admission if sum_web_admission is not None and sum_web_admission > 0 else 0,
                    date=batch_date
                )
                admin_info.save()

        details = AdminInfo.objects.all()
        final_table_data = FinalTable.objects.all()
        context = {'details': details, 'final_table_data': final_table_data, 'admin': True}
        return render(request, 'home/total.html', context)

    else:
        details = CounsellorInfo.objects.all()
        context = {'details': details, 'admin': False}
        return render(request, 'home/viewer.html', context)

def filter(request):
    username = request.user.username
    
    if request.user.is_superuser:
        admin = True
    else:
        admin = False

    if request.method == 'POST':
        date = request.POST.get('date')

        if admin:
            if not date:
                sum_data = CounsellorInfo.objects.aggregate(
                    sumOfNumberOfFbMessages=Sum('numberOfFbMessages'),
                    sumOfNumberOfWebMessages=Sum('numberOfWebMessages'),
                    sumOfNumberOfFbAdmission=Sum('numberOfFbAdmission'),
                    sumOfNumberOfWebAdmission=Sum('numberOfWebAdmission'),
                    
                )

                admin_info = AdminInfo(
                    sumOfNumberOfFbMessages=sum_data['sumOfNumberOfFbMessages'],
                    sumOfNumberOfWebMessages=sum_data['sumOfNumberOfWebMessages'],
                    sumOfNumberOfFbAdmission=sum_data['sumOfNumberOfFbAdmission'],
                    sumOfNumberOfWebAdmission=sum_data['sumOfNumberOfWebAdmission'],
                  
                )
                admin_info.save()

        if date:
            details = AdminInfo.objects.filter(batchDate=date)
        else:
            details = AdminInfo.objects.all()

        context = {'details': details, 'admin': admin}
        return render(request, 'home/viewer.html', context)
    else:
        details = CounsellorInfo.objects.all()
        context = {'details': details, 'admin': admin}
        return render(request, 'home/viewer.html', context)



def batch_detail_view(request):
    if request.method == 'POST':
        date = request.POST.get('batch_date')
        batch_date_obj = datetime.strptime(date, "%b. %d, %Y")
        formatted_batch_date = batch_date_obj.strftime("%Y-%m-%d")
        counsellor_info = CounsellorInfo.objects.filter(batchDate=formatted_batch_date)
        admin_info = AdminInfo.objects.filter(date=formatted_batch_date)
        final_info = FinalTable.objects.filter(batchDate=formatted_batch_date)
        amount_spent = 0
        returns = 0
        for counsellor in counsellor_info:
            amount_spent += counsellor.numberOfFbMessages * admin_info[0].fbLeadCost
            amount_spent += counsellor.numberOfWebMessages * admin_info[0].webLeadCost
            returns += (counsellor.numberOfFbAdmission + counsellor.numberOfWebAdmission) * 3500 - amount_spent
        
        amount_spent=round(amount_spent,2)
        returns=round(returns,2)
        CounsellorInfo.objects.filter(batchDate=formatted_batch_date).update(amount_spent=amount_spent,returns=returns)
        context = {'admin_info': admin_info, 'counsellor_info': counsellor_info, 'final_info': final_info,'amount_spent':amount_spent,'returns':returns}
        return render(request, 'home/main.html', context)


        