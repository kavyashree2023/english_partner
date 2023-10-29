from django.db import models
from django.contrib.auth.models import User

class CounsellorInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    batchDate = models.DateField()
    counsellorName = models.CharField(max_length=255, null=True)
    numberOfFbMessages = models.IntegerField(null=True)
    numberOfWebMessages = models.IntegerField(null=True)
    numberOfFbAdmission = models.IntegerField(null=True)
    numberOfWebAdmission = models.IntegerField(null=True)
    amount_spent = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    returns = models.DecimalField(max_digits=10, decimal_places=2, null=True)

class AdminInfo(models.Model):
    date = models.DateField()   
    sumOfNumberOfFbMessages = models.IntegerField(null=True)
    sumOfNumberOfWebMessages = models.IntegerField(null=True)
    sumOfNumberOfFbAdmission = models.IntegerField(null=True)
    sumOfNumberOfWebAdmission = models.IntegerField(null=True)
    fbLeadCost=models.DecimalField(max_digits=10, decimal_places=2, null=True)
    webLeadCost=models.DecimalField(max_digits=10, decimal_places=2, null=True)
    fbCPA=models.DecimalField(max_digits=10, decimal_places=2, null=True)
    webCPA=models.DecimalField(max_digits=10, decimal_places=2, null=True)


class FinalTable(models.Model):
    batchDate = models.DateField()
    fbExpense = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    webExpense = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    counsellor_info = models.ForeignKey(CounsellorInfo, on_delete=models.CASCADE, null=True)

    

#  admin_info.amount_spent = (numberOfFbMessages*sumOfFbLeadCost)+(numberOfWebMessages*sumOfWebLeadCost) if sumOfFbLeadCost > 0 else 0,
#                 admin_info.returns = (((numberOfFbAdmission+numberOfWebAdmission)*3500)-amount_spent) if numberOfWebAdmission > 0 else 0,