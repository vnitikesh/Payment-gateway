from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.conf import settings
from .models import Transaction, Loans
from paytm import Checksum
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User






@login_required(login_url = '/login/')
def initiate_payment(request):
    if request.method == "POST":

        try:

            username = request.user.username
            amount = int(request.POST.get('amount'))
            user = User.objects.filter(username = username).first()





        except:
            return render(request, 'payments/pay.html', context={'error': 'Wrong Account Details or amount'})

        transaction = Transaction.objects.create(made_by=user, amount=amount)
        transaction.save()
        merchant_key = settings.PAYTM_SECRET_KEY

        params = (
            ('MID', settings.PAYTM_MERCHANT_ID),
            ('ORDER_ID', str(transaction.order_id)),
            ('CUST_ID', str(transaction.made_by.email)),
            ('TXN_AMOUNT', str(transaction.amount)),
            ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
            ('WEBSITE', settings.PAYTM_WEBSITE),
            ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
            ('CALLBACK_URL', 'http://127.0.0.1:8000/callback/'),

        )

        paytm_params = dict(params)
        checksum = Checksum.generate_checksum(paytm_params, merchant_key)

        transaction.checksum = checksum
        transaction.save()

        paytm_params['CHECKSUMHASH'] = checksum
        #print('SENT: ', checksum)
        return render(request, 'payments/redirect.html', context=paytm_params)

    loan = Loans.objects.filter(status = True).all()
    loan_count = 0
    for i in loan:
        loan_count += 1
    return render(request, 'payments/pay.html',{'loan':loan, 'loan_count':loan_count})


@csrf_exempt

def callback(request):
    # paytm will send you post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]
    order_id = response_dict['ORDERID']
    #print(type(response_dict['TXNAMOUNT']))
    amount = int(float(response_dict['TXNAMOUNT']))


    verify = Checksum.verify_checksum(response_dict, settings.PAYTM_SECRET_KEY, checksum)
    if verify:
        #print("verified")
        if response_dict['RESPCODE'] == '01':
            print('order successful')
            #We are filtering order_id over here coz of its unique behaviour, since the amount may not be unique.
            trans = Transaction.objects.filter(order_id = order_id, amount = amount).get()
            a = trans.amount

            l = Loans.objects.filter(amount = a).get()
            l.status = False
            l.save()
        else:
            print('order was not successful because' + response_dict['RESPMSG'])
    else:
        print('order was not successful because' + response_dict['RESPMSG'])
    #Uncomment the below commented statement if you want to check the response items.
    return render(request, 'payments/callback.html', {'response': response_dict})
    #return redirect('pay')
