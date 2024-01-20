from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .form import CreateUserForm
from .models import CounsellorInfo,AdminInfo,FinalTable
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
import datetime
from collections import defaultdict
from datetime import datetime
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
import time

@login_required(login_url='login')
@csrf_protect
def home(request):
    return render(request, 'home/home.html')

@login_required(login_url='login')
@csrf_protect
def cdc(request):
    return render(request, 'home/cdc.html')

@csrf_protect
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




@csrf_protect
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



@csrf_protect
def logoutUser(request):
    """
    This view function is responsible for logging out the user and redirecting to the login page.
    """
    logout(request)
    return redirect('login')


@csrf_protect
def DataAdder(request):
    if request.method == 'POST':
        # Retrieve month and year from POST request
        month = request.POST.get('month')
        year = request.POST.get('year')
        counsellor_name = request.POST.get('counsellorName')
        fb_messages = request.POST.get('numberOfFbMessages')
        fb_admission = request.POST.get('numberOfFbAdmission')
        web_messages = request.POST.get('numberOfWebMessages')
        web_admission = request.POST.get('numberOfWebAdmission')
        social_media = request.POST.get('socialMedia')

        # Convert month and year to integers and handle invalid inputs
        try:
            month = int(month) if month else None
            year = int(year) if year else None
        except ValueError:
            messages.error(request, "Invalid month or year")
            return redirect('some-view')  # Replace with your actual redirect

        # Assuming you want to create or update the CounsellorInfo object based on the month and year
        if month and year:
            # Construct a date object from year and month, assuming day is the first of the month
            # You might need to adjust this based on how your application expects the date
            batch_date = datetime.date(year, month, 1)

            # Create CounsellorInfo object
            details = CounsellorInfo.objects.create(
                user=User.objects.get(username=request.user.username),
                batchDate=batch_date,
                counsellorName=counsellor_name,
                numberOfFbMessages=fb_messages,
                numberOfFbAdmission=fb_admission,
                numberOfWebMessages=web_messages,
                numberOfWebAdmission=web_admission,
                socialMedia=social_media,
            )
            
            details.save()
            
            context = {
                'data_added': True
            }
            time.sleep(10)  # Consider if this sleep is necessary for your application

            return render(request, 'home/home.html', context)

        else:
            # Handle cases where month or year is not provided
            messages.error(request, "Month and year are required")
            return redirect('some-view')  # Replace with your actual redirect

    else:
        user = request.user
        context = {
            'data_added': False,
            'counsellor_name': user.username  # Pass the current user's name to the context
        }
        return render(request, 'home/user.html', context)

@csrf_protect
def DataAdm(request):
    if request.method == 'POST':
        # Retrieve month and year from POST request
        month = request.POST.get('month')
        year = request.POST.get('year')
        FbExpense = request.POST.get('fbExpense')
        WebExpense = request.POST.get('webExpense')

        # Convert month and year to integers and handle invalid inputs
        try:
            month = int(month) if month else None
            year = int(year) if year else None
        except ValueError:
            messages.error(request, "Invalid month or year")
            return redirect('loginPage')  # Replace with your actual redirect

        # Assuming you want to create or update the FinalTable object based on the month and year
        if month and year:
            # Construct a date object from year and month, assuming day is the first of the month
            # You might need to adjust this based on how your application expects the date
            batchDate = datetime.date(year, month, 1)

            # Create or update the FinalTable object
            details, created = FinalTable.objects.update_or_create(
                batchDate=batchDate,
                defaults={
                    'fbExpense': FbExpense,
                    'webExpense': WebExpense,
                }
            )

            # Save if it's a new object
            if created:
                details.save()

            context = {
                'data_added': True
            }
            return render(request, 'home/cdc.html', context)

        else:
            # Handle cases where month or year is not provided
            messages.error(request, "Month and year are required")
            return redirect('loginPage')  # Replace with your actual redirect

    else:
        # Handle GET or other methods as needed
        context = {
            'data_added': False
        }
        return render(request, 'home/adm.html', context)




@csrf_protect
def DataFilter(request):
    username = request.user.username

    if request.user.is_superuser:
        # Retrieve month and year from request
        month = request.GET.get('month')
        year = request.GET.get('year')

        # Convert month and year to integers and handle invalid inputs
        try:
            month = int(month) if month else None
            year = int(year) if year else None
        except ValueError:
            messages.error(request, "Invalid month or year")
            return redirect('some-view')  # Replace with your actual redirect

        # Filter based on month and year
        if year and month:
            counsellor_info_list = CounsellorInfo.objects.filter(batchDate__year=year, batchDate__month=month)
            final_table_data = FinalTable.objects.filter(batchDate__year=year, batchDate__month=month)
        else:
            counsellor_info_list = CounsellorInfo.objects.all()
            final_table_data = FinalTable.objects.all()

        # Initialize aggregated data structure
        aggregated_data = defaultdict(lambda: {
            'sumOfNumberOfFbMessages': 0,
            'sumOfNumberOfFbAdmission': 0,
            'sumOfNumberOfWebMessages': 0,
            'sumOfNumberOfWebAdmission': 0,
            'socialMedia': 0,
            'sumOfFbExpense': 0,
            'sumOfWebExpense': 0,
        })

        # Aggregate data for each counsellor_info
        for counsellor_info in counsellor_info_list:
            batch_date = counsellor_info.batchDate
            data = aggregated_data[batch_date]
            data['sumOfNumberOfFbMessages'] += counsellor_info.numberOfFbMessages
            data['sumOfNumberOfFbAdmission'] += counsellor_info.numberOfFbAdmission
            data['sumOfNumberOfWebMessages'] += counsellor_info.numberOfWebMessages
            data['sumOfNumberOfWebAdmission'] += counsellor_info.numberOfWebAdmission
            data['socialMedia'] += counsellor_info.socialMedia if counsellor_info.socialMedia else 0

        # Aggregate data for FinalTable
        for final_table_entry in final_table_data:
            batch_date = final_table_entry.batchDate
            data = aggregated_data[batch_date]
            data['sumOfFbExpense'] += final_table_entry.fbExpense if final_table_entry.fbExpense else 0
            data['sumOfWebExpense'] += final_table_entry.webExpense if final_table_entry.webExpense else 0

        context = {'details': aggregated_data, 'final_table_data': final_table_data, 'admin': True}
        return render(request, 'home/total.html', context)

    else:
        # Non-superuser part
        month = request.GET.get('month')
        year = request.GET.get('year')

        # Convert month and year to integers and handle invalid inputs
        try:
            month = int(month) if month else None
            year = int(year) if year else None
        except ValueError:
            messages.error(request, "Invalid month or year")
            return redirect('some-view')  # Replace with your actual redirect

        # Filter based on month and year for non-superuser
        if year and month:
            details = CounsellorInfo.objects.filter(user=request.user, batchDate__year=year, batchDate__month=month)
        else:
            details = CounsellorInfo.objects.filter(user=request.user)

        context = {'details': details, 'admin': False}
        return render(request, 'home/viewer.html', context)


@csrf_protect
def filter(request):
    if request.user.is_superuser:
        admin = True
    else:
        admin = False

    if request.method == 'POST':
        # Retrieve month and year from POST request
        month = request.POST.get('month')
        year = request.POST.get('year')

        # Convert month and year to integers and handle invalid inputs
        try:
            month = int(month) if month else None
            year = int(year) if year else None
        except ValueError:
            messages.error(request, "Invalid month or year")
            return redirect('some-view')  # Replace with your actual redirect

        # Initialize details variable
        details = None

        if admin:
            # Filter based on month and year for AdminInfo
            if year and month:
                details = AdminInfo.objects.filter(date__year=year, date__month=month)
            elif year:  # Only year is provided
                details = AdminInfo.objects.filter(date__year=year)
            else:
                details = AdminInfo.objects.all()  # No specific filter, fetch all

            # Aggregate data if needed
            # Assuming you want to aggregate some data from details
            # Here's an example of how you might sum up some fields
            aggregated_data = details.aggregate(
                TotalFbMessages=Sum('sumOfNumberOfFbMessages'),
                TotalFbAdmissions=Sum('sumOfNumberOfFbAdmission'),
                TotalWebMessages=Sum('sumOfNumberOfWebMessages'),
                TotalWebAdmissions=Sum('sumOfNumberOfWebAdmission'),
                # Add more fields as needed
            )

            context = {'details': details, 'aggregated_data': aggregated_data, 'admin': admin}
            return render(request, 'home/total.html', context)

        else:
            # Filter based on month and year for CounsellorInfo
            if year and month:
                details = CounsellorInfo.objects.filter(user=request.user,  batchDate__year=year, batchDate__month=month)
            elif year:  # Only year is provided
                details = CounsellorInfo.objects.filter(user=request.user,  batchDate__year=year)
            else:
                details = CounsellorInfo.objects.filter(user=request.user)  # No specific filter, fetch all

            # Aggregate data if needed
            # Assuming you want to aggregate some data from details
            # Here's an example of how you might sum up some fields
            aggregated_data = details.aggregate(
                TotalFbMessages=Sum('numberOfFbMessages'),
                TotalFbAdmissions=Sum('numberOfFbAdmission'),
                TotalWebMessages=Sum('numberOfWebMessages'),
                TotalWebAdmissions=Sum('numberOfWebAdmission'),
                # Add more fields as needed
            )

            context = {'details': details, 'aggregated_data': aggregated_data, 'admin': admin}
            return render(request, 'home/viewer.html', context)


@csrf_protect
def batch_detail_view(request):
    if request.method == 'POST':
        month = request.POST.get('month')
        year = request.POST.get('year')
        month = int(month)
        year = int(year)
        counsellor_info = CounsellorInfo.objects.filter(
            batchDate__year=year,
            batchDate__month=month
        )
        admin_info = AdminInfo.objects.filter(
            date__year=year,
            date__month=month
        )
        final_info = FinalTable.objects.filter(
            batchDate__year=year,
            batchDate__month=month
        )
        amount_spent = 0
        returns = 0
        for counsellor in counsellor_info:
            amount_spent += counsellor.numberOfFbMessages * admin_info[0].fbLeadCost
            amount_spent += counsellor.numberOfWebMessages * admin_info[0].webLeadCost
            returns += (counsellor.numberOfFbAdmission + counsellor.numberOfWebAdmission) * 3500 - amount_spent
        
        amount_spent=round(amount_spent,2)
        returns=round(returns,2)
        CounsellorInfo.objects.filter( batchDate__year=year,
            batchDate__month=month).update(amount_spent=amount_spent,returns=returns)
        context = {'admin_info': admin_info, 'counsellor_info': counsellor_info, 'final_info': final_info,'amount_spent':amount_spent,'returns':returns}
        return render(request, 'home/main.html', context)